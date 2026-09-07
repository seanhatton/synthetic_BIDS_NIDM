#!/usr/bin/env python3
import json
import re
import sys

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else None
    if not input_file:
        print("Usage: python fsl2json_Sep2026.py <input.ttl>")
        sys.exit(1)
    with open(input_file) as f:
        content = f.read()
    # Split into subject blocks
    # Each subject block starts with "a nidm:FSLStatsCollection," and ends with "prov:wasGeneratedBy"
    blocks = re.split(r'\n(?=\n?niiri:)', content)
    results = {}
    for block in blocks:
        # Find subject ID
        subj_match = re.search(r'ndar:src_subject_id "sub-(\d+)"', block)
        if not subj_match:
            continue
        subj = f"sub-{subj_match.group(1)}"
        # Find FSL values
        vals = []
        fsl_pattern = re.compile(r'(fsl:fsl_\d+)\s+(\S+)')
        for match in fsl_pattern.finditer(block):
            fsl_id = match.group(1)
            val = match.group(2).strip('"')
            try:
                val = float(val)
            except ValueError:
                pass
            vals.append((fsl_id, val))
        if vals:
            results[subj] = vals
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
