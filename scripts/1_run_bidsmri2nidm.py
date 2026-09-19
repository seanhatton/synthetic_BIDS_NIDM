#!/usr/bin/env python3
import os
import subprocess

BIDSDIR = "/mnt/c/Users/seanh/Documents/GitHub/synthetic_BIDS_NIDM"

subprocess.run(
    [
        "bidsmri2nidm",
        "-d", BIDSDIR,
        "-bidsignore",
        "-o", os.path.join(BIDSDIR, "./nidm/bids_nidm.ttl")
    ]
)
