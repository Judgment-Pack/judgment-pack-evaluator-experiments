#!/usr/bin/env python3
"""The transcriber under study (PREREGISTRATION.md §7): verified artifact
references in, one matrix document out.

It has no pack input, no policy input, and no evaluator call — its command
line takes a store, a key file, a reference list, a rule path, and an output
path, nothing else. It is deliberately a separate implementation from the
gate that afterwards re-derives every row from the same artifacts: the gate
exists to catch a transcriber that did anything else, and the harness's
tamper tests prove it does.
"""
from __future__ import annotations
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
LINE = os.path.dirname(os.path.dirname(STUDY))
sys.path.insert(0, os.path.join(LINE, "fabrication-gate"))
sys.path.insert(0, os.path.join(LINE, "derivation-rule"))
sys.path.insert(0, os.path.join(LINE, "acquisition-proxy"))

import importlib.util as _importlib_util

def _load_fabrication():
    spec = _importlib_util.spec_from_file_location(
        "fabrication_gate", os.path.join(LINE, "fabrication-gate", "gate.py"))
    module = _importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

fabrication = _load_fabrication()


def transcribe(store_root: str, key: bytes, refs: list[dict], rule: dict,
               authority: str) -> dict:
    cases = []
    for ref in sorted(refs, key=lambda r: r["caseId"]):
        admitted = fabrication.admit(
            store_root, key, ref["sessionId"], ref["callIndex"], rule, {},
            expected_authority=authority)
        digest = admitted["lineage"]["resultDigest"]
        artifact = json.loads(open(os.path.join(
            store_root, "artifacts", digest.split(":", 1)[1]), "rb").read())
        outcome = artifact["decision"]["outcome"]
        cases.append({
            "id": artifact["caseId"],
            "origin": "transcribed:%s@%s" % (artifact["caseId"], digest),
            "facts": admitted["facts"],
            "evidenceAvailability": {},
            "expectedDisposition": {
                "kind": "outcome",
                "outcomeId": outcome,
                "reasons": [],
                "handoff": {"state": "none"},
            },
        })
    return {"matrixVersion": "1", "cases": cases}


def main() -> None:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--store", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--refs", required=True)
    parser.add_argument("--rule", required=True)
    parser.add_argument("--authority", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    key = open(args.key, "rb").read()
    refs = json.load(open(args.refs))
    rule = json.load(open(args.rule))
    matrix = transcribe(args.store, key, refs, rule, args.authority)
    with open(args.out, "w") as handle:
        json.dump(matrix, handle, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    main()
