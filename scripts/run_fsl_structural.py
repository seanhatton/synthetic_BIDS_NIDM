#!/usr/bin/env python3
"""
Batch processing script for FSL FIRST and FAST on BIDS directories.

Usage:
    python run_fsl_structural.py --help

    # Process all subjects in BIDS directory
    python run_fsl_structural.py -b /path/to/bids -o /path/to/derivatives

    # Process specific subjects
    python run_fsl_structural.py -b /path/to/bids -o /path/to/derivatives -s sub-01 sub-02

    # Run FIRST only
    python run_fsl_structural.py -b /path/to/bids -o /path/to/derivatives -f

    # Run FAST only
    python run_fsl_structural.py -b /path/to/bids -o /path/to/derivatives -a
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def find_bids_subjects(bids_dir: str) -> list:
    """Find all subject directories in a BIDS directory."""
    bids_path = Path(bids_dir)
    subjects = []
    for item in sorted(bids_path.iterdir()):
        if item.is_dir() and item.name.startswith("sub-"):
            subjects.append(item.name)
    return subjects


def find_t1w_image(bids_dir: str, subject_id: str) -> str:
    """Find the T1w image for a given subject in a BIDS directory.
    
    Looks for the standard BIDS structure:
    {bids_dir}/{subject_id}/ses-01/anat/{subject_id}_ses-01_T1w.nii.gz
    """
    subject_path = Path(bids_dir) / subject_id
    # Match: {bids_dir}/sub-13/ses-01/anat/sub-13_ses-01_T1w.nii.gz
    pattern = f"ses-01/anat/{subject_id}_ses-01_T1w.nii.gz"
    matches = list(subject_path.glob(pattern))
    if matches:
        return str(matches[0])
    raise FileNotFoundError(f"T1w image not found for {subject_id} in {bids_dir}")


def run_first(bids_dir: str, output_dir: str, subject_id: str, t1w_path: str) -> bool:
    """Run FSL FIRST for a single subject."""
    try:
        output_path = Path(output_dir) / subject_id / "ses-01"
        output_path.mkdir(parents=True, exist_ok=True)
        
        output_base = output_path / f"{subject_id}_FIRST"
        cmd = [
            "run_first_all",
            "-b",
            "-i", t1w_path,
            "-o", str(output_base),
        ]
        
        print(f"Running FIRST for {subject_id}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FIRST failed for {subject_id}: {result.stderr}")
            return False
        
        print(f"  Output: {output_base}")
        return True
    except Exception as e:
        print(f"Error running FIRST for {subject_id}: {e}")
        return False


def run_fast(bids_dir: str, output_dir: str, subject_id: str, t1w_path: str) -> bool:
    """Run FSL FAST for a single subject."""
    try:
        output_path = Path(output_dir) / subject_id / "ses-01"
        output_path.mkdir(parents=True, exist_ok=True)
        
        output_base = output_path / f"{subject_id}_FAST"
        cmd = [
            "fast",
            "-o", str(output_base),
            t1w_path,
        ]
        
        print(f"Running FAST for {subject_id}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FAST failed for {subject_id}: {result.stderr}")
            return False
        
        print(f"  Output: {output_base}")
        return True
    except Exception as e:
        print(f"Error running FAST for {subject_id}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Batch process FSL FIRST and FAST on BIDS directories.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("--bids-dir", "-b", required=True,
        help="Path to BIDS input directory")
    parser.add_argument("--output-dir", "-o", required=True,
        help="Path to derivatives output directory")
    parser.add_argument("--subjects", "-s", nargs="*",
        help="List of subject IDs to process (default: all subjects)")
    parser.add_argument("--first-only", "-f", action="store_true",
        help="Run only FIRST, skip FAST")
    parser.add_argument("--fast-only", "-a", action="store_true",
        help="Run only FAST, skip FIRST")
    
    args = parser.parse_args()
    
    # Validate directories
    if not os.path.isdir(args.bids_dir):
        print(f"Error: BIDS directory not found: {args.bids_dir}", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.isdir(args.output_dir):
        print(f"Creating output directory: {args.output_dir}")
        os.makedirs(args.output_dir, exist_ok=True)
    
    # Find subjects
    if args.subjects:
        subjects = args.subjects
    else:
        subjects = find_bids_subjects(args.bids_dir)
    
    if not subjects:
        print("No subjects found to process.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing {len(subjects)} subject(s)...")
    print(f"BIDS directory: {args.bids_dir}")
    print(f"Output directory: {args.output_dir}")
    print("-" * 50)
    
    first_count = 0
    fast_count = 0
    subject_count = 0
    
    for subject_id in subjects:
        print(f"\n=== Processing {subject_id} ===")
        subject_count += 1
        
        try:
            t1w_path = find_t1w_image(args.bids_dir, subject_id)
            print(f"  T1w image: {t1w_path}")
        except FileNotFoundError as e:
            print(f"  Skipping: {e}")
            continue
        
        if not args.fast_only:
            if run_first(args.bids_dir, args.output_dir, subject_id, t1w_path):
                first_count += 1
        
        if not args.first_only:
            if run_fast(args.bids_dir, args.output_dir, subject_id, t1w_path):
                fast_count += 1
    
    print("\n" + "=" * 50)
    print(f"Summary:")
    print(f"  Subjects processed: {subject_count}")
    if not args.fast_only:
        print(f"  FIRST completed: {first_count}")
    if not args.first_only:
        print(f"  FAST completed: {fast_count}")


if __name__ == "__main__":
    main()
