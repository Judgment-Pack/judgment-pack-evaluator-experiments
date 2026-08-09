"""Judgment-semantic pack mutations M1-M6 + M15a — deterministic, from pinned bytes.

Each mutated pack is a clearly labeled defective study fixture derived from
packs/ (never from the runtime tree). The mutations mirror realistic encoding
defects; M1 is family index 0 of the 009/010 transcription defect family,
reused here as an integration probe, not as a re-run of the authorship studies.

Stdlib only. Run: python3 harness/mutate_packs.py
"""

import argparse
import copy
import json
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
OUT = STUDY / "scenarios" / "mutations" / "packs"


def load(name):
    return json.loads((STUDY / "packs" / name).read_text())


def dump(name, pack, note):
    OUT.mkdir(parents=True, exist_ok=True)
    pack = copy.deepcopy(pack)
    pack["description"] = "[STUDY 013 MUTATED FIXTURE — DEFECTIVE ON PURPOSE: " + note + "] " + pack.get("description", "")
    (OUT / name).write_text(json.dumps(pack, indent=2) + "\n")


def rule(pack, rule_id):
    return next(r for r in pack["rules"] if r["id"] == rule_id)


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(OUT),
                        help="output directory (integrity.py re-derives into a temp dir)")
    OUT = Path(parser.parse_args().out)

    fee = load("decimal-threshold-fee.json")
    triage = load("data-request-intake-triage.json")

    m01 = copy.deepcopy(fee)
    rule(m01, "standard-fee-at-or-above-threshold")["when"]["operator"] = "greater-than"
    dump("m01-decimal-threshold-fee.json", m01, "greater-than-or-equal weakened to greater-than")

    m02 = copy.deepcopy(fee)
    rule(m02, "standard-fee-at-or-above-threshold")["when"]["value"] = "1001"
    rule(m02, "reduced-fee-below-threshold")["when"]["value"] = "1001"
    dump("m02-decimal-threshold-fee.json", m02,
         "threshold moved 1000 -> 1001 in the ordered rules; the exempt equality rule was not moved")

    m03 = copy.deepcopy(triage)
    m03["exceptions"] = []
    dump("m03-data-request-intake-triage.json", m03, "embargo exception removed")

    m04 = copy.deepcopy(triage)
    exc = m04["exceptions"][0]
    exc["effect"] = "suppress-rule"
    exc["targetRule"] = "decline-hard-appropriateness-failure"
    del exc["outcome"]
    dump("m04-data-request-intake-triage.json", m04,
         "embargo exception effect force-outcome -> suppress-rule (adaptation of the "
         "requested precedence mutation: JPS Core has no authorable exception order)")

    m05 = copy.deepcopy(triage)
    req = next(r for r in m05["evidenceRequirements"] if r["id"] == "sponsor-endorsement")
    req["required"] = False
    dump("m05-data-request-intake-triage.json", m05,
         "sponsor-endorsement requirement demoted required true -> false")

    m06 = copy.deepcopy(fee)
    rule(m06, "standard-fee-at-or-above-threshold")["onUnknown"] = "ignore"
    rule(m06, "reduced-fee-below-threshold")["onUnknown"] = "ignore"
    dump("m06-decimal-threshold-fee.json", m06,
         "onUnknown escalate -> ignore on both ordered rules")

    m15a = copy.deepcopy(fee)
    m15a["specVersion"] = "0.1.0-draft"
    dump("m15a-decimal-threshold-fee.json", m15a,
         "byte-frozen pack re-declared under 0.1.0-draft; the pinned evaluator must "
         "refuse it at preflight (spec-version exactness)")

    print("wrote 7 mutated packs to", OUT)


if __name__ == "__main__":
    main()
