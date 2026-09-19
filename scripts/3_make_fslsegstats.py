#!/usr/bin/env python3
"""
Build segstats.json files that `fslsegstats2nidm` can read.

`fsl_seg_to_nidm.fslutils.read_fsl_stats` expects each entry of the JSON to be
an *indexable sequence* of ``[n_voxels, volume_mm3]``::

    {
        "Background": [119948727, 170800.0],
        "Left-Thalamus-Proper": [3483, 3483.0],
        ...
    }

It accesses ``value[0]`` (voxel count) and ``value[1]`` (volume in mm^3), so a
dict such as ``{"voxels": 3483, "volume_ml": 0.0}`` raises ``KeyError: 0``.

The structure names must also exactly match the keys in
``fsl_seg_to_nidm/mapping_data/fsl-cde.json``, i.e.:

    Background, csf, gray, white,
    {Left,Right}-{Thalamus-Proper, Caudate, Putamen, Pallidum, Hippocampus,
                  Amygdala, Accumbens-area}

Note that Brain-Stem (FIRST label 16) has no data element and is skipped.

Usage:
    # recompute segstats.json from the FSL FIRST/FAST segmentations
    python make_segstats.py -d /path/to/derivatives/fsl

    # only some subjects
    python make_segstats.py -d /path/to/derivatives/fsl -s sub-01 sub-02

    # just rewrite existing dict-style segstats.json into the list format
    python make_segstats.py -d /path/to/derivatives/fsl --from-json
"""

import argparse
import json
import sys
from pathlib import Path

# FIRST (all_fast_firstseg) label -> data element structure name.
# Label 16 (Brain-Stem) is intentionally absent: no FSL CDE exists for it.
FIRST_LABELS = {
    10: "Left-Thalamus-Proper",
    11: "Left-Caudate",
    12: "Left-Putamen",
    13: "Left-Pallidum",
    17: "Left-Hippocampus",
    18: "Left-Amygdala",
    26: "Left-Accumbens-area",
    49: "Right-Thalamus-Proper",
    50: "Right-Caudate",
    51: "Right-Putamen",
    52: "Right-Pallidum",
    53: "Right-Hippocampus",
    54: "Right-Amygdala",
    58: "Right-Accumbens-area",
}

# FAST (pveseg/seg) tissue labels
FAST_LABELS = {1: "csf", 2: "gray", 3: "white"}

# Order used when writing the JSON file
STRUCTURE_ORDER = (
    ["Background"]
    + [FIRST_LABELS[k] for k in sorted(FIRST_LABELS)]
    + ["csf", "gray", "white"]
)


def _counts(img):
    """Return {label: n_voxels} and the voxel volume in mm^3 for a label image."""
    import numpy as np

    data = np.asanyarray(img.dataobj).astype(np.int32, copy=False)
    labels, counts = np.unique(data, return_counts=True)
    zooms = img.header.get_zooms()[:3]
    voxel_volume = float(zooms[0]) * float(zooms[1]) * float(zooms[2])
    return dict(zip(labels.tolist(), counts.tolist())), voxel_volume


def compute_segstats(session_dir: Path) -> dict:
    """Compute voxel counts / volumes (mm^3) from FIRST and FAST outputs."""
    import nibabel as nib

    first_files = sorted(session_dir.glob("*_FIRST_all_fast_firstseg.nii.gz"))
    fast_files = sorted(session_dir.glob("*_FAST_seg.nii.gz"))
    if not fast_files:
        fast_files = sorted(session_dir.glob("*_FAST_pveseg.nii.gz"))

    if not first_files and not fast_files:
        raise FileNotFoundError(
            f"No FIRST/FAST segmentation images found in {session_dir}"
        )

    stats = {}

    if fast_files:
        counts, vox_vol = _counts(nib.load(str(fast_files[0])))
        # Background is taken from the FAST tissue segmentation
        stats["Background"] = counts.get(0, 0), vox_vol
        for label, name in FAST_LABELS.items():
            stats[name] = counts.get(label, 0), vox_vol

    if first_files:
        counts, vox_vol = _counts(nib.load(str(first_files[0])))
        for label, name in FIRST_LABELS.items():
            stats[name] = counts.get(label, 0), vox_vol

    # [n_voxels, volume_mm3] as required by read_fsl_stats
    return {
        name: [int(nvox), round(nvox * vox_vol, 4)]
        for name, (nvox, vox_vol) in (
            (n, stats[n]) for n in STRUCTURE_ORDER if n in stats
        )
    }


def convert_existing(segstats_path: Path) -> dict:
    """Rewrite an existing dict-style segstats.json into the list format."""
    with open(segstats_path) as fp:
        data = json.load(fp)

    converted = {}
    for name, value in data.items():
        if isinstance(value, dict):
            nvox = int(value.get("voxels", 0))
            if "volume_mm3" in value:
                volume = float(value["volume_mm3"])
            else:
                # volume_ml -> mm^3
                volume = float(value.get("volume_ml", 0.0)) * 1000.0
        elif isinstance(value, (list, tuple)):
            nvox, volume = int(value[0]), float(value[1])
        else:
            raise ValueError(f"Unsupported value for {name!r}: {value!r}")
        converted[name] = [nvox, round(volume, 4)]

    ordered = {n: converted.pop(n) for n in STRUCTURE_ORDER if n in converted}
    ordered.update(converted)  # keep anything unexpected at the end
    return ordered


def validate(stats: dict) -> list:
    """Return structure names that have no matching FSL data element."""
    try:
        from fsl_seg_to_nidm.fslutils import cde_file
    except ImportError:
        return []

    with open(cde_file) as fp:
        cde = json.load(fp)

    unknown = []
    for name in stats:
        hemi = "Left" if "Left" in name else "Right" if "Right" in name else None
        key = (
            f"FSL(structure={name!r}, hemi={hemi!r}, "
            "measure='NVoxels', unit='voxel')"
        )
        if key not in cde:
            unknown.append(name)
    return unknown


def main():
    parser = argparse.ArgumentParser(
        description="Write segstats.json files in the format fslsegstats2nidm expects.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--derivatives-dir", "-d", required=True,
        help="FSL derivatives directory (contains sub-*/ses-*/)")
    parser.add_argument(
        "--subjects", "-s", nargs="*",
        help="Subject IDs to process (default: all sub-* directories)")
    parser.add_argument(
        "--session", default="ses-01", help="Session label (default: ses-01)")
    parser.add_argument(
        "--from-json", action="store_true",
        help="Convert the existing segstats.json instead of recomputing from NIfTI")
    parser.add_argument(
        "--dry-run", action="store_true", help="Report what would be written only")

    args = parser.parse_args()

    deriv = Path(args.derivatives_dir)
    if not deriv.is_dir():
        sys.exit(f"Error: derivatives directory not found: {deriv}")

    subjects = args.subjects or [
        p.name for p in sorted(deriv.iterdir())
        if p.is_dir() and p.name.startswith("sub-")
    ]
    if not subjects:
        sys.exit(f"No subjects found in {deriv}")

    n_ok = 0
    for sub in subjects:
        session_dir = deriv / sub / args.session
        out_path = session_dir / "segstats.json"
        try:
            if args.from_json:
                if not out_path.exists():
                    print(f"{sub}: skipping, {out_path} does not exist")
                    continue
                stats = convert_existing(out_path)
            else:
                stats = compute_segstats(session_dir)
        except Exception as exc:
            print(f"{sub}: FAILED - {exc}")
            continue

        unknown = validate(stats)
        if unknown:
            print(f"{sub}: dropping structures with no FSL data element: {unknown}")
            for name in unknown:
                stats.pop(name)

        if args.dry_run:
            print(f"{sub}: would write {len(stats)} structures to {out_path}")
        else:
            session_dir.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w") as fp:
                json.dump(stats, fp, indent=4)
                fp.write("\n")
            print(f"{sub}: wrote {len(stats)} structures to {out_path}")
        n_ok += 1

    print(f"\nDone: {n_ok}/{len(subjects)} subject(s)")


if __name__ == "__main__":
    main()
