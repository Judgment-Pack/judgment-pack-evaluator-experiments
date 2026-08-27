"""Section 2.1's per-arm perfect and identity rates over the sweep's slots.

WHY THIS FILE EXISTS, AND WHY IT IS NOT THE SWEEP DRIVER
--------------------------------------------------------
Section 2.1's fill obligation reads: "the sweep's full per-setting table
(per-arm durations, completion bytes, `reasoning_output_tokens`, per-arm
perfect and identity rates) is published". The sweep driver publishes the
first three and — by its own registered self-description ("It computes no rate,
chooses no setting and fills no pin... It publishes the table and stops",
`harness/batch.py`) — is forbidden the fourth. The rates are a SCORING output,
so they are computed here, by the same registered components the primary
attempt's scorer runs, and published beside the driver's ledger as
`SWEEP-RATES.json` plus a rates section appended to `SWEEP.md`. `sweeps/` is
outside the exact-set manifest by named constant, so this publication moves no
attested byte.

WHAT IS COMPUTED, AND — REGISTERED SCOPE — WHAT IS REFUSED
----------------------------------------------------------
Per slot, exactly the two quantities section 2.1 names, in `score_run()`'s own
order (`harness/score.py`): extract (`e4lib/extract.py`), admit
(`e4lib/admit.py`, the presence-idiom guard live), the E1 gold loop (the
authored policy against every row of `gold/GOLD.json` on its own engine, the
scored surface tuple), and `referenceIdentity` (the authored suite's cases
enumerated, domain-validated, then run against the arm's unmutated reference —
`e4lib/e4.py`'s `identity_arm_a` / `identity_arm_rego`, with the registered
pre-steps and the registered short-circuits: an out-of-domain case fails the
relation without invoking it; an engine refusal is REPORTED as engine-refused,
neither pass nor fail).

**No kill quantity is computed, by construction.** The obligation names
perfect and identity rates and nothing else; a mutant-kill number over three
runs per cell would be an endpoint-adjacent figure computed before the pilot,
outside every registered use, and inviting exactly the informal peek at the
outcome surface that the preregistration's sweep section exists to keep out of
the choice of condition. This module imports nothing from `e4lib.e4`'s kill
machinery and `harness/tests/test_sweep_rates.py` asserts the published block
carries no kill member.

ONE READING OF EVERY RULE
-------------------------
This module deliberately re-orchestrates four registered components rather
than calling `score.score_run()`, because `score_run` continues past identity
into the kill vector. The mirrored region is `score.py`'s extract→admit→gold
block and `_identity_and_kill()`'s pre-kill half, cited clause by clause at
the call sites below; the suite pins the shared semantics (a coded run scores
`goldPerfect` false and is never asked about identity; out-of-domain fails
identity; null completion is an extract failure) so a divergence between the
two orchestrations is a test failure, not a quiet second reading.

WHAT THIS SCRIPT REFUSES
------------------------
- a missing or unpinnable toolchain (`JPACK_BIN` / `OPA_BIN` / `OPA_CAPS`);
- a sweep label with no ledger (`SWEEP.json`) or a ledger whose call list
  names a slot that is not on disk;
- publishing over an existing `SWEEP-RATES.json`, or appending a second rates
  section to `SWEEP.md`, without `--force` — a stale rate surviving a
  recomputation is the defect the counterfactual script's gate exists for.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import integrity                      # noqa: E402
from e4lib import admit as admit_lib   # noqa: E402
from e4lib import e4                   # noqa: E402
from e4lib import engines              # noqa: E402
from e4lib import extract              # noqa: E402

HARNESS = HERE
STUDY = os.path.dirname(HARNESS)
SWEEP_ROOT = os.path.join(STUDY, "sweeps")
GOLD_PATH = os.path.join(STUDY, "gold", "GOLD.json")
REFERENCE_A = os.path.join(STUDY, "reference", "refA", "pack.json")
REFERENCE_B = os.path.join(STUDY, "reference", "refB", "policy.rego")
RATES_LEDGER_NAME = "SWEEP-RATES.json"
RATES_HEADING = "## Per-arm perfect and identity rates"

ARMS = ("A", "B", "C")
#: `score.py`'s own wire-form map for the domain validation step.
ARM_WIRE = {"A": "string", "B": "number", "C": "number"}


# VOCABULARY BOUNDARY (R1-13). This module's published records
# (SWEEP-RATES.json) carry `identityPass` — already-published sweep history —
# and are NOT renamed by 020's run-record move to `referenceIdentityPass`;
# a reader crossing from score.py's records to these is crossing studies'
# publication moments, not a drifted schema.


class RatesError(Exception):
    """A refusal. The message names the precondition that failed."""


def load_pins() -> dict:
    with open(os.path.join(HARNESS, "PINS.json"), "rb") as handle:
        return json.loads(handle.read().decode("utf-8"),
                          **integrity.LOAD_KWARGS)


def toolchain(pins: dict) -> engines.Toolchain:
    tools = engines.Toolchain(pins)
    if tools.problems:
        raise RatesError("RATES-TOOLCHAIN the pinned toolchain did not "
                         "resolve: %s" % "; ".join(tools.problems))
    return tools


def load_gold() -> list:
    with open(GOLD_PATH, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))["rows"]


def gold_perfect(tools, arm: str, artifact: str, gold: list,
                 workdir: str) -> tuple:
    """`score.py`'s E1 gold block, verbatim semantics: every row, the scored
    surface tuple, a failure list rather than an early exit."""
    failures = 0
    for row in gold:
        expect = row["expect"]
        want = (("unresolved", None, tuple(sorted(expect["reasons"])))
                if expect["disposition"] == "unresolved"
                else ("outcome", expect["disposition"], ()))
        if arm == "A":
            facts, evidence = engines.facts_documents(row["inputs"])
            got = engines.eval_pack(tools, artifact, facts, evidence, workdir)
        else:
            got = engines.eval_rego(tools, artifact, row["inputs"], workdir)
        if got[0] == "ROW-ERROR" and (
                got[1] in (engines.INVOCATION_TIMEOUT,
                           engines.UNREADABLE_INVOCATION,
                           "non-json-payload")
                or str(got[1]).startswith(engines.INVOCATION_FAILURE)):
            # R1-1: no answer at all — apparatus; the caller records it and
            # the slot leaves the rate.
            raise engines.EngineError(
                "ENGINE-INVOCATION-REFUSED gold row %s: %s"
                % (row.get("id"), got[1]))
        if got != want:
            failures += 1
    return failures == 0, failures


def reference_identity(tools, arm: str, suite_path: str,
                       workdir: str) -> dict:
    """`referenceIdentity` with `score._identity_and_kill()`'s pre-kill
    semantics: enumerate, validate the domain, and only then run the relation;
    an engine refusal is its own verdict, not a pass and not a fail."""
    try:
        if arm == "A":
            cases, _note = e4.load_matrix(suite_path)
            named = [(case[0],
                      e4.matrix_domain_signature(case[1], case[2]))
                     for case in cases]
        else:
            cases = None
            named = e4.rego_case_signatures(tools, suite_path, workdir,
                                            REFERENCE_B)
    except e4.MatrixError as refusal:
        # `score_run()`'s branch exactly: a present suite that does not parse
        # to cases is the registered authoring code, never an exception out of
        # the scorer — and the run's gold verdict, already computed, stands.
        return {"pass": False, "why": "suite-unparseable",
                "code": "unparseable-artifact", "refusal": str(refusal)[:200]}
    if arm == "A":
        # R3-9: the exclusion registry is EMPTY, so a non-empty partition is a
        # registration mismatch and refuses rather than quietly filtering.
        _scored, excluded = e4.partition_excluded(cases)
        if excluded:
            raise RatesError("RATES-EXCLUSION-REGISTRY %d case(s) partitioned "
                             "out under an empty registry" % len(excluded))
    out_of_domain = e4.domain_failures(named, ARM_WIRE[arm])
    if out_of_domain:
        return {"pass": False, "why": "out-of-domain-case",
                "outOfDomain": len(out_of_domain)}
    try:
        if arm == "A":
            ok, _failures = e4.identity_arm_a(tools, REFERENCE_A, cases,
                                              workdir)
        else:
            ok, _record = e4.identity_arm_rego(tools, REFERENCE_B, suite_path,
                                               workdir)
    except e4.ExecutionRefusal as refusal:
        # ROUND-2 FINDING R2-10: a pinned engine that refused on a FROZEN
        # artifact produced no verdict about this run's suite. It used to
        # return `pass: False`, which the caller wrote into `identityPass` and
        # the aggregator counted as a failing suite inside a fixed denominator
        # — §1a's population rule read backwards. It is APPARATUS, and it says
        # so in the vocabulary `score.population()` already uses.
        return {"pass": None, "why": "apparatus-refused",
                "apparatusCode": "engine-invocation-refused",
                "refusal": str(refusal)[:200]}
    return {"pass": bool(ok), "why": None if ok else "identity-failed"}


def score_slot(tools, arm: str, slot_dir: str, gold: list,
               guard_registered, workdir: str) -> dict:
    """One sweep slot -> the two registered quantities, `score_run()`'s order:
    extract, admit (a code ends the slot's scoring exactly as it does in the
    attempt path — counted, goldPerfect false, identity never asked), gold,
    identity."""
    record = {"slot": os.path.relpath(slot_dir, STUDY), "arm": arm,
              "code": None, "goldPerfect": False, "goldFailures": None,
              "identityPass": False, "identityWhy": "not-asked",
              # R2-10: §1a's apparatus side, per slot. None means the apparatus
              # succeeded and the slot is SCORED; a code means the slot leaves
              # the denominator and is published under it.
              "apparatusCode": None,
              "suitePresent": False}
    os.makedirs(workdir, exist_ok=True)
    completion_path = os.path.join(slot_dir, "completion.txt")
    if not os.path.isfile(completion_path):
        raise RatesError("RATES-NO-COMPLETION %s names no completion.txt"
                         % record["slot"])
    with open(completion_path, "r", encoding="utf-8") as handle:
        text = handle.read()
    # `score_run()`'s order, member by member: extraction's None reaches
    # admission unchanged (`admit()` spells `no-marker-block` itself), the
    # code ends the slot's scoring, the suite file takes the scorer's own
    # name (`suite.<language>`).
    pair = extract.extract_pair(text, arm)
    try:
        artifact, code, _detail = admit_lib.admit(tools, arm, pair["policy"],
                                                  workdir, guard_registered)
    except engines.EngineError as error:
        # R1-1/R2-10: the engine never answered — an apparatus event, filed in
        # §1a's own vocabulary, never as an authoring code or a rate input.
        record["apparatusCode"] = "engine-invocation-refused"
        record["apparatusDetail"] = str(error)[:200]
        record["identityPass"] = None
        return record
    if code is not None:
        record["code"] = code
        return record
    try:
        record["goldPerfect"], record["goldFailures"] = gold_perfect(
            tools, arm, artifact, gold, workdir)
    except engines.EngineError as error:
        record["apparatusCode"] = "engine-invocation-refused"
        record["apparatusDetail"] = str(error)[:200]
        record["identityPass"] = None
        return record
    if pair["suite"] is None:
        record["identityWhy"] = "no-suite"
        return record
    record["suitePresent"] = True
    suite_path = os.path.join(workdir, "suite.%s" % pair["suiteLanguage"])
    with open(suite_path, "w", encoding="utf-8") as handle:
        handle.write(pair["suite"])
    identity = reference_identity(tools, arm, suite_path, workdir)
    record["identityPass"] = identity["pass"]
    record["identityWhy"] = identity["why"]
    if identity.get("apparatusCode"):
        record["apparatusCode"] = identity["apparatusCode"]
        record["apparatusDetail"] = identity.get("refusal")
    if "code" in identity:
        record["code"] = identity["code"]
    if "outOfDomain" in identity:
        record["outOfDomainCases"] = identity["outOfDomain"]
    if "refusal" in identity:
        record["engineRefusal"] = identity["refusal"]
    return record


def per_arm_cell(rows: list) -> dict:
    """ROUND-2 FINDING R2-10: ONE per-arm population cell, in the member names
    `score.population()` already uses, so a pilot record and the attempt's own
    population are diffable rather than two dialects of one rule.

    §1a: "The denominator of every per-arm rate is attempted runs whose
    apparatus succeeded. Apparatus failures ... are pipeline-invalid, excluded,
    and reported with their own rate and interval." `attempted` is every slot,
    `calls` is the scored denominator, `apparatusExcluded` is the difference —
    three numbers that are ONE partition, published together so a rate can
    never quietly acquire a different denominator than its numerator."""
    scored = [row for row in rows if not row.get("apparatusCode")]
    apparatus = [row for row in rows if row.get("apparatusCode")]
    counts = {}
    for row in apparatus:
        counts[row["apparatusCode"]] = counts.get(row["apparatusCode"], 0) + 1
    return {
        "attempted": len(rows),
        "calls": len(scored),
        "apparatusExcluded": len(apparatus),
        "apparatusCodes": counts,
        "perfect": sum(1 for row in scored if row["goldPerfect"]),
        "identityPass": sum(1 for row in scored
                            if row["identityPass"] is True),
        "codes": sorted(row["code"] for row in scored if row["code"]),
    }


def sweep_rates(tools, label: str, gold: list, scratch: str) -> dict:
    ledger_path = os.path.join(SWEEP_ROOT, label, "SWEEP.json")
    if not os.path.isfile(ledger_path):
        raise RatesError("RATES-NO-SWEEP no ledger at sweeps/%s/SWEEP.json"
                         % label)
    with open(ledger_path, "rb") as handle:
        ledger = json.loads(handle.read().decode("utf-8"))
    guard_registered = admit_lib.guard_is_registered()
    settings = []
    for setting in ledger["settings"]:
        rows = []
        for call in setting["calls"]:
            slot_dir = os.path.join(STUDY, call["slot"])
            if not os.path.isdir(slot_dir):
                raise RatesError("RATES-NO-SLOT the ledger names %s and it is "
                                 "not on disk" % call["slot"])
            workdir = os.path.join(scratch, setting["setting"], call["arm"],
                                   "run-%03d" % call["runIndex"])
            os.makedirs(workdir, exist_ok=True)
            rows.append(score_slot(tools, call["arm"], slot_dir, gold,
                                   guard_registered, workdir))
        per_arm = {}
        for arm in ARMS:
            mine = [row for row in rows if row["arm"] == arm]
            per_arm[arm] = per_arm_cell(mine)
        settings.append({"setting": setting["setting"], "perArm": per_arm,
                         "slots": rows})
    return {
        "label": label,
        "obligation": "PREREGISTRATION.md section 2.1 — the fill's per-arm "
                      "perfect and identity rates; computed by "
                      "harness/sweep_rates.py through the registered scoring "
                      "components, no kill quantity computed by construction",
        "citable": False,
        "goldRows": len(gold),
        "guardRegistered": guard_registered,
        "settings": settings,
    }


def render_rates(body: dict) -> str:
    lines = [
        "",
        RATES_HEADING,
        "",
        "Scored post-sweep by `harness/sweep_rates.py` (the driver registers "
        "that it computes no rate), through the registered scoring components: "
        "extract, admit with the presence-idiom guard live, the gold loop over "
        "%d rows, and `referenceIdentity` with its registered pre-steps. "
        "**No kill quantity is computed**, by registered scope. "
        "`citable: false`, like everything in this file." % body["goldRows"],
        "",
        "| setting | arm | perfect | identity | authoring codes |",
        "|---|---|---|---|---|",
    ]
    for setting in body["settings"]:
        for arm in ARMS:
            cell = setting["perArm"][arm]
            codes = ", ".join("`%s`" % code for code in cell["codes"]) or "—"
            lines.append("| %s | %s | %d/%d | %d/%d | %s |" % (
                setting["setting"], arm, cell["perfect"], cell["calls"],
                cell["identityPass"], cell["calls"], codes))
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Section 2.1's per-arm perfect and identity rates.")
    parser.add_argument("--label", required=True,
                        help="the sweep's dated label under sweeps/")
    parser.add_argument("--scratch", default=None)
    parser.add_argument("--write", action="store_true",
                        help="write SWEEP-RATES.json and append the rates "
                             "section to SWEEP.md")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    ledger_out = os.path.join(SWEEP_ROOT, args.label, RATES_LEDGER_NAME)
    table_path = os.path.join(SWEEP_ROOT, args.label, "SWEEP.md")
    if args.write and not args.force:
        if os.path.exists(ledger_out):
            raise RatesError("RATES-EXISTS %s exists; recomputation replaces "
                             "it only under --force"
                             % os.path.relpath(ledger_out, STUDY))
        if os.path.isfile(table_path):
            with open(table_path, "r", encoding="utf-8") as handle:
                if RATES_HEADING in handle.read():
                    raise RatesError("RATES-EXISTS SWEEP.md already carries a "
                                     "rates section; --force replaces nothing "
                                     "here — remove it deliberately first")

    pins = load_pins()
    tools = toolchain(pins)
    gold = load_gold()
    if args.scratch:
        os.makedirs(args.scratch, exist_ok=True)
        body = sweep_rates(tools, args.label, gold, args.scratch)
    else:
        with tempfile.TemporaryDirectory() as scratch:
            body = sweep_rates(tools, args.label, gold, scratch)
    sys.stdout.write(render_rates(body))
    if args.write:
        with open(ledger_out, "w", encoding="utf-8") as handle:
            json.dump(body, handle, indent=2, sort_keys=True)
            handle.write("\n")
        with open(table_path, "a", encoding="utf-8") as handle:
            handle.write(render_rates(body))
        sys.stdout.write("\nwrote %s and appended the section to SWEEP.md\n"
                         % os.path.relpath(ledger_out, STUDY))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RatesError as refusal:
        sys.stderr.write("%s\n" % refusal)
        sys.exit(1)
