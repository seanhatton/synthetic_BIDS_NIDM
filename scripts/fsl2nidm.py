#!/usr/bin/env python3
"""
Add FSL FIRST/FAST segmentation statistics to a NIDM study file.

Runs `fslsegstats2nidm` once per subject. Note that when `-n` is used,
fslsegstats2nidm merges the new triples into the *NIDM file* and rewrites it
in place; the `-o` argument is only used to locate an output directory. So
this script processes subjects serially and keeps a backup of the study file.

Prerequisites for each subject:
  derivatives/fsl/<sub>/<ses>/segstats.json  in the format read_fsl_stats()
  expects, i.e. {"Left-Caudate": [n_voxels, volume_mm3], ...}
  (generate it with make_segstats.py -- a dict such as
  {"voxels": N, "volume_ml": V} causes `KeyError: 0`)

The subject must also exist in the NIDM file as
  ?agent a prov:Agent ; ndar:src_subject_id "<sub>"^^xsd:string
Plain (untyped) literals do not match that query; fix with
nidm/type_string_literals.py, or pass --force-nidm to create a new agent.

Usage:
    python fsl2nidm.py                       # all subjects found on disk
    python fsl2nidm.py -s sub-01 sub-02
    python fsl2nidm.py --dry-run
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_BASE = Path("/mnt/c/Users/seanh/Documents/GitHub/synthetic_BIDS_NIDM")


def check_segstats(path: Path) -> str | None:
    """Return an error string if segstats.json is unusable, else None."""
    if not path.exists():
        return f"missing {path}"
    try:
        with open(path) as fp:
            data = json.load(fp)
    except json.JSONDecodeError as exc:
        return f"invalid JSON ({exc})"
    if not data:
        return "empty file"
    for name, value in data.items():
        if not isinstance(value, (list, tuple)) or len(value) < 2:
            return (f"{name!r} is {type(value).__name__}, expected "
                    "[n_voxels, volume_mm3] -- rerun make_segstats.py")
    return None


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base-dir", "-b", type=Path, default=DEFAULT_BASE,
                        help=f"Project root (default: {DEFAULT_BASE})")
    parser.add_argument("--nidm-file", "-n", type=Path, default=None,
                        help="NIDM study file (default: <base>/nidm/study_nidm.ttl)")
    parser.add_argument("--subjects", "-s", nargs="*",
                        help="Subject IDs (default: all sub-* in derivatives/fsl)")
    parser.add_argument("--session", default="ses-01", help="Session label")
    parser.add_argument("--exe", default="fslsegstats2nidm",
                        help="Path to the fslsegstats2nidm executable")
    parser.add_argument("--force-nidm", action="store_true",
                        help="Pass -forcenidm: create the agent if the subject "
                             "is not found in the NIDM file")
    parser.add_argument("--no-backup", action="store_true",
                        help="Do not copy the NIDM file before modifying it")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate inputs and print commands only")
    args = parser.parse_args()

    base_dir = args.base_dir
    fsl_dir = base_dir / "derivatives" / "fsl"
    study_nidm = args.nidm_file or (base_dir / "nidm" / "study_nidm.ttl")

    exe = shutil.which(args.exe) or args.exe
    if not args.dry_run and shutil.which(args.exe) is None:
        sys.exit(f"Error: '{args.exe}' not found on PATH. Activate the conda/venv "
                 "environment where fsl_seg_to_nidm is installed, or pass "
                 "--exe /full/path/to/fslsegstats2nidm")

    if not fsl_dir.is_dir():
        sys.exit(f"Error: FSL derivatives directory not found: {fsl_dir}")
    if not study_nidm.is_file():
        sys.exit(f"Error: NIDM file not found: {study_nidm}")

    subjects = args.subjects or [
        p.name for p in sorted(fsl_dir.iterdir())
        if p.is_dir() and p.name.startswith("sub-")
    ]
    if not subjects:
        sys.exit(f"No subjects found in {fsl_dir}")

    # Validate all inputs up front: fslsegstats2nidm rewrites the study file on
    # every call, so it is better to know about bad inputs before we start.
    problems = {}
    for sub in subjects:
        err = check_segstats(fsl_dir / sub / args.session / "segstats.json")
        if err:
            problems[sub] = err
    if problems:
        print("Skipping subjects with unusable segstats.json:")
        for sub, err in problems.items():
            print(f"  {sub}: {err}")
        subjects = [s for s in subjects if s not in problems]
        if not subjects:
            sys.exit("Nothing to do.")

    if not args.dry_run and not args.no_backup:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = study_nidm.with_suffix(f".{stamp}.bak.ttl")
        shutil.copy2(study_nidm, backup)
        print(f"Backup: {backup}")

    failed = []
    for i, sub in enumerate(subjects, 1):
        cmd = [
            exe,
            "-add_de",
            "-d", str(fsl_dir / sub / args.session / "segstats.json"),
            "-subjid", sub,
            # -o is required by the CLI but unused when -n is given
            "-o", str(fsl_dir / sub / "fsl_nidm.ttl"),
            "-n", str(study_nidm),
        ]
        if args.force_nidm:
            cmd.append("-forcenidm")

        print(f"[{i}/{len(subjects)}] {sub}...")
        if args.dry_run:
            print("  " + " ".join(cmd))
            continue

        result = subprocess.run(cmd, capture_output=True, text=True)
        out = (result.stdout or "") + (result.stderr or "")
        if result.returncode != 0:
            failed.append(sub)
            print(f"  FAILED (exit {result.returncode})")
            print("  " + out.strip().replace("\n", "\n  "))
            continue
        if "was not found in existing NIDM file" in out:
            print("  warning: subject not found in NIDM file "
                  "(check src_subject_id literals / use --force-nidm)")
        print(f"  ok -> {study_nidm}")

    print(f"\nDone: {len(subjects) - len(failed)}/{len(subjects)} subject(s) added")
    if failed:
        print("Failed: " + ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
