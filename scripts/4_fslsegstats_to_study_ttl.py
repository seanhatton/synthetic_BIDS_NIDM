#!/usr/bin/env python3

import subprocess
import shutil
from pathlib import Path

bidsdir = Path("/mnt/c/Users/seanh/Documents/GitHub/synthetic_BIDS_NIDM")
session = "ses-01"

# Study-level NIDM graph that every subject gets appended to.
# Copy from bids_nidm.ttl if it does not exist yet.
study_nidm = bidsdir / "nidm" / "study_nidm_v2.ttl"
bids_nidm = bidsdir / "nidm" / "bids_nidm_v2.ttl"
if not study_nidm.exists():
    study_nidm.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(bids_nidm, study_nidm)
    print(f"Created Turtle file from bids_nidm.ttl: {study_nidm}")
else:
    print(f"Using existing Turtle file: {study_nidm}")


for i in range(1, 51):
    subject = f"sub-{i:02d}"

    d = bidsdir / "derivatives" / "fsl" / subject / session / "segstats.json"
    o = bidsdir / "derivatives" / "fsl" / subject / session / "fsl_nidm.ttl"
    n = study_nidm

    o.parent.mkdir(parents=True, exist_ok=True)

    # Use full path to fslsegstats2nidm in conda env
    fslsegstats2nidm = "/home/sehatton/miniconda3/bin/fslsegstats2nidm"

    cmd = [
        fslsegstats2nidm,
        "-add_de",
        "-d", str(d),
        "-subjid", subject,
        "-o", str(o),
        "-n", str(n),
    ]

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  FAILED ({subject}): {result.stderr.strip()}")
    else:
        print(f"  OK ({subject})")

