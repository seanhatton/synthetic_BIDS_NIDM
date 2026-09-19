#!/usr/bin/env python3
"""
dedupe_string_literals.py

Fixes a common artifact of merging NIDM/RDF files from different export
tools: two literals that represent the SAME string value but differ only
in whether they carry an explicit xsd:string datatype, e.g.:

    ex:agent1 ndar:src_subject_id "sub-01" .
    ex:agent1 ndar:src_subject_id "sub-01"^^xsd:string .

Per RDF 1.1 these denote the same value, but rdflib treats them as
distinct triples (different hash), so a naive graph union (like
`pynidm merge`) keeps both. This script finds every (subject, predicate)
pair where that exact plain/typed duplication occurs and drops one of
the two triples, for every predicate in the graph -- not just one.

It will NOT touch:
  - literals with a language tag
  - literals of any other datatype (int, float, dateTime, etc.)
  - a plain/typed pair whose lexical values actually differ
  - any literal that doesn't have both a plain AND a typed duplicate

Usage:
    python dedupe_string_literals.py input.ttl output.ttl
    python dedupe_string_literals.py input.ttl output.ttl --keep typed
    python dedupe_string_literals.py input.ttl output.ttl --dry-run
"""

import argparse
from collections import defaultdict

from rdflib import Graph, Literal, XSD, util


def find_duplicate_pairs(graph):
    """
    Group literal triples by (subject, predicate, lexical value) for
    language-less literals that are either untyped or xsd:string typed.
    Return only the groups that contain BOTH forms.
    """
    groups = defaultdict(list)
    for s, p, o in graph:
        if isinstance(o, Literal) and o.language is None:
            if o.datatype is None or o.datatype == XSD.string:
                groups[(s, p, str(o))].append(o)

    dupes = {}
    for key, literals in groups.items():
        untyped = next((l for l in literals if l.datatype is None), None)
        typed = next((l for l in literals if l.datatype == XSD.string), None)
        if untyped is not None and typed is not None:
            dupes[key] = (untyped, typed)
    return dupes


def dedupe(graph, keep="untyped"):
    """Remove one literal from each plain/typed duplicate pair in-place."""
    dupes = find_duplicate_pairs(graph)

    for (s, p, value), (untyped, typed) in dupes.items():
        drop = typed if keep == "untyped" else untyped
        graph.remove((s, p, drop))

    return dupes


def main():
    parser = argparse.ArgumentParser(
        description="Deduplicate plain-vs-xsd:string literal pairs in an RDF Turtle file."
    )
    parser.add_argument("input", help="Input Turtle (.ttl) file")
    parser.add_argument("output", help="Output Turtle (.ttl) file")
    parser.add_argument(
        "--keep",
        choices=["untyped", "typed"],
        default="untyped",
        help="Which literal form to keep for each duplicate pair (default: untyped)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without writing an output file",
    )
    args = parser.parse_args()

    g = Graph()
    g.parse(args.input, format=util.guess_format(args.input) or "turtle")
    before = len(g)

    dupes = find_duplicate_pairs(g)

    if not dupes:
        print(f"Parsed {args.input}: {before} triples. No plain/xsd:string duplicate pairs found.")
        if not args.dry_run:
            g.serialize(destination=args.output, format="turtle")
            print(f"Wrote {args.output}: {before} triples (unchanged).")
        return

    print(f"Parsed {args.input}: {before} triples")
    print(f"Found {len(dupes)} plain/xsd:string duplicate pair(s):")
    by_pred = defaultdict(int)
    for (s, p, value) in dupes:
        by_pred[str(p)] += 1
    for pred, count in sorted(by_pred.items(), key=lambda x: -x[1]):
        print(f"  {count:>4}  {pred}")

    if args.dry_run:
        print(f"\nDry run: would remove {len(dupes)} triple(s), keeping the '{args.keep}' form. Nothing written.")
        return

    dedupe(g, keep=args.keep)
    after = len(g)
    g.serialize(destination=args.output, format="turtle")

    print(f"\nRemoved {before - after} duplicate triple(s) (kept '{args.keep}' form)")
    print(f"Wrote {args.output}: {after} triples")


if __name__ == "__main__":
    main()
