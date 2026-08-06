#!/usr/bin/env python3
"""The truth-region validator (PREREGISTRATION.md §2): pack C, evaluated by
the pinned runtime on one probe per truth region, must produce exactly the
policy mirror's outcome in all 24 regions — S x E x P x {r<40, 40<=r<70,
r>=70}. It runs inside the protocol-lock gate, before authoring, and touches
only pack C: never D, never a record.

Usage: JPACK_BIN=<pinned binary> regions_check.py
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import policy_mirror  # noqa: E402

PACK_C = os.path.join(STUDY, "packs", "vendor-screening-correct.pack.json")
SCORES = {"low": "20", "mid": "55", "high": "88"}


class RegionError(Exception):
    pass


BOUNDARY_SCORES = ("39", "39.5", "40", "41", "69.9", "70", "70.5", "71")


def probes() -> list[dict]:
    result = []
    for sanctions in (True, False):
        for country in ("KP", "DE"):
            for personal in (True, False):
                for band, score in sorted(SCORES.items()):
                    result.append({
                        "sanctionsHit": sanctions,
                        "registeredCountry": country,
                        "handlesPersonalData": personal,
                        "riskScore": score,
                        "band": band,
                    })
    # The locked boundary battery (PREREGISTRATION.md §2): every stated and
    # unstated threshold from both sides, both personal-data values, plus
    # each embargo literal and SY's high band.
    for personal in (True, False):
        for score in BOUNDARY_SCORES:
            result.append({"sanctionsHit": False, "registeredCountry": "DE",
                           "handlesPersonalData": personal, "riskScore": score,
                           "band": "boundary"})
    for country in ("KP", "IR", "SY"):
        result.append({"sanctionsHit": False, "registeredCountry": country,
                       "handlesPersonalData": False, "riskScore": "5",
                       "band": "embargo"})
    result.append({"sanctionsHit": False, "registeredCountry": "SY",
                   "handlesPersonalData": False, "riskScore": "85",
                   "band": "embargo"})
    return result


def evaluate(jpack: str, vendor: dict) -> dict:
    facts = {"vendor": {key: vendor[key] for key in
                        ("sanctionsHit", "registeredCountry", "handlesPersonalData", "riskScore")}}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(facts, handle)
        facts_path = handle.name
    try:
        completed = subprocess.run(
            [jpack, "experimental", "evaluate", PACK_C, "--facts", facts_path,
             "--format", "json"],
            capture_output=True, text=True, timeout=60)
        return json.loads(completed.stdout)["disposition"]
    finally:
        os.unlink(facts_path)


def check(jpack: str) -> int:
    checked = 0
    for probe in probes():
        vendor = {key: probe[key] for key in
                  ("sanctionsHit", "registeredCountry", "handlesPersonalData", "riskScore")}
        expected = policy_mirror.verdict(vendor)
        disposition = evaluate(jpack, vendor)
        if disposition.get("kind") != "outcome" or disposition.get("outcomeId") != expected:
            raise RegionError(
                "region %r: POLICY.md says %s, pack C disposed %s"
                % (probe, expected, json.dumps(disposition)))
        checked += 1
    if checked != 44:
        raise RegionError("expected 44 probes, ran %d" % checked)
    return checked


def main() -> int:
    jpack = os.environ.get("JPACK_BIN", "")
    if not jpack or not os.path.exists(jpack):
        print("refused: JPACK_BIN must name the pinned binary", file=sys.stderr)
        return 2
    try:
        checked = check(jpack)
    except RegionError as error:
        print("refused: %s" % error, file=sys.stderr)
        return 1
    print("regions: ok (%d regions agree with POLICY.md)" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
