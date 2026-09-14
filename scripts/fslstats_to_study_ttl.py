#!/usr/bin/env python3

import subprocess
from pathlib import Path

bidsdir = Path("/mnt/c/Users/sehatton/Documents/GitHub/synthetic_BIDS_NIDM")
session = "ses-01"

for i in range(1, 51):
    subject = f"sub-{i:02d}"

    d = bidsdir / subject / session / "segstats.json"
    o = bidsdir / "derivatives" / "fsl" / subject / session / "fsl_nidm.ttl"
    n = bidsdir / "nidm" / "study_nidm.ttl"

    o.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "fslsegstats2nidm",
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