#!/usr/bin/env python3
"""
type_string_literals.py

The inverse companion to `dedupe_string_literals.py`.

`dedupe_string_literals.py --keep untyped` leaves subject identifiers as
*plain* literals::

    niiri:e3c6334a... a prov:Agent, prov:Person ;
        ndar:src_subject_id "sub-01" .

Per RDF 1.1 that is the same value as ``"sub-01"^^xsd:string``, but rdflib
treats the two terms as distinct, so SPARQL queries that ask for the typed
form return nothing. Several pynidm-based tools hard-code the typed form,
e.g. `fslsegstats2nidm` / `segstats2nidm`::

    ?agent rdf:type prov:Agent ;
           ndar:src_subject_id "sub-01"^^xsd:string .

which silently fails ("Subject ID (sub-01) was not found in existing NIDM
file...") and then crashes with
``UnboundLocalError: ... 'participant_agent' ...``.

This script re-adds the explicit xsd:string datatype so those queries match.
By default only identifier predicates are touched; use --all-predicates to
convert every plain string literal in the graph.

Usage:
    python type_string_literals.py study_nidm.ttl study_nidm.ttl
    python type_string_literals.py in.ttl out.ttl --dry-run
    python type_string_literals.py in.ttl out.ttl --all-predicates
    python type_string_literals.py in.ttl out.ttl -p https://example.org/myPred
"""

import argparse
from collections import defaultdict

from rdflib import Graph, Literal, URIRef, XSD, util

# Predicates whose objects are looked up as "..."^^xsd:string by pynidm tools
DEFAULT_PREDICATES = [
    "https://ndar.nih.gov/api/datadictionary/v2/dataelement/src_subject_id",
    "https://ndar.nih.gov/api/datadictionary/v2/dataelement/subjectkey",
    "http://purl.org/nidash/nidm#subjectID",
    "http://purl.org/nidash/nidm#sessionLabel",
]


def find_plain_literals(graph, predicates=None):
    """Return plain (datatype-less, language-less) string literal triples."""
    found = []
    for s, p, o in graph:
        if predicates is not None and p not in predicates:
            continue
        if isinstance(o, Literal) and o.language is None and o.datatype is None:
            found.append((s, p, o))
    return found


def retype(graph, predicates=None):
    """Replace plain string literals with xsd:string-typed ones, in-place."""
    triples = find_plain_literals(graph, predicates)
    for s, p, o in triples:
        graph.remove((s, p, o))
        graph.add((s, p, Literal(str(o), datatype=XSD.string)))
    return triples


def main():
    parser = argparse.ArgumentParser(
        description="Add explicit xsd:string datatypes to plain string literals "
                    "so pynidm SPARQL lookups match."
    )
    parser.add_argument("input", help="Input Turtle (.ttl) file")
    parser.add_argument("output", help="Output Turtle (.ttl) file")
    parser.add_argument(
        "--predicate", "-p", action="append", default=None,
        help="Predicate URI to convert (repeatable). Defaults to the "
             "subject/session identifier predicates.")
    parser.add_argument(
        "--all-predicates", action="store_true",
        help="Convert every plain string literal, regardless of predicate")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report what would change without writing an output file")
    args = parser.parse_args()

    if args.all_predicates:
        predicates = None
    else:
        predicates = {URIRef(u) for u in (args.predicate or DEFAULT_PREDICATES)}

    g = Graph()
    g.parse(args.input, format=util.guess_format(args.input) or "turtle")
    before = len(g)

    triples = find_plain_literals(g, predicates)
    print(f"Parsed {args.input}: {before} triples")

    if not triples:
        print("No plain string literals to convert.")
        if not args.dry_run and args.output != args.input:
            g.serialize(destination=args.output, format="turtle")
            print(f"Wrote {args.output}: {before} triples (unchanged).")
        return

    by_pred = defaultdict(int)
    for _, p, _ in triples:
        by_pred[str(p)] += 1
    print(f"Found {len(triples)} plain string literal(s):")
    for pred, count in sorted(by_pred.items(), key=lambda x: -x[1]):
        print(f"  {count:>5}  {pred}")

    if args.dry_run:
        print("\nDry run: nothing written.")
        return

    retype(g, predicates)
    g.serialize(destination=args.output, format="turtle")
    print(f"\nRetyped {len(triples)} literal(s) as xsd:string")
    print(f"Wrote {args.output}: {len(g)} triples")


if __name__ == "__main__":
    main()
