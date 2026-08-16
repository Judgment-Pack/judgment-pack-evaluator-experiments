"""E4 — pairing, the X1 filter, the identity control, kill, and the tau cut.

ASSEMBLED FROM `design/mutants/e4_score.py`
(sha256 `beb42b3903284dc2c33baff33000325814a1e53171d8268ca4d56820e4f995fb`):
`load_mutants()` (152-194), `build_pairing()` (195-231), `align_expected()`
(232-245), `load_matrix()` (295-308), `identity_arm_a()` (310-322),
`kill_arm_a()` (323-336), `case_signature()` (375-384), and the per-arm
aggregation of `score_arm()` (556-654). `harness/PORTS.md` carries the two-sided
row and the enumerated change list.

WHAT THE PROTOTYPE DID NOT HAVE, and section 5 registers
--------------------------------------------------------
1. **The X1 filter.** Section 4 registers X1 as an exclusion class and a census
   row: the prose-correct outcome there is inexpressible in the JPS fragment (0
   of 2,048 `onUnknown` assignments), so an author cannot be right there in arm
   A and the other arms' being right is not a finding about testing skill.
   "Every authored test case whose inputs fall in X1 is excluded from identity
   and kill evaluation, with the per-run excluded-case count published."
   `in_x1()` is the predicate, as its own named function with its own test,
   because a filter that is a condition inside a loop is a filter nobody can
   check against the registration.
2. **The identity control as a first-class per-arm RATE**, not a gate that
   silently removes suites. The prototype reported identity failures per suite;
   section 5 reports the rate, and section 1a requires the exclusions to be
   "reported, never silently dropped".
3. **The tau cut as an integer derived at run time.** Section 5 registers
   tau = 0.95 over the paired adequate subset and says the operative integer cut
   at the frozen paired count is stated. `stats.tau_cut()` derives it and the
   scorer prints it, so the number a run is judged against is in the published
   record rather than in an analyst's head.
4. **The engine-supplied-kill split** (SCAFFOLD item S9, closed). Section 4
   registers 35 (now 41) arm-A mutants "listed in the registries" whose kills
   are achievable only through the engine's structural conflict detection,
   "reported both included and excluded". Both manifests now carry a
   machine-readable `engineSuppliedKill` member — arm A's derived from
   `design/mutants/refA/REGISTRY.json`'s `conflictOnlyMutants`, arm B's an
   EMPTY registered class, because the Rego ladder has no structural conflict
   detection and an empty class is a fact where a missing member would be a
   silence. `engine_supplied_ids()` reads the member and `kill_rates()` splits
   the paired subset on it; a manifest that carries no member at all still
   REFUSES by name, because the alternative is publishing "0 engine-supplied
   kills" from an absence.

Determinism: fixed orderings everywhere (manifest order for mutants, sorted run
ids, case order within a suite), no clock, no randomness, no environment lookup.
The prototype used a thread pool for wall-clock and reassembled results in the
fixed order; that is carried, and `E4_WORKERS` changes nothing but the wall
clock.
"""
from __future__ import annotations

import json
import os
from decimal import Decimal, InvalidOperation
from fractions import Fraction

from . import engines
from . import stats

# Section 4's registered X1 boundary, as the three numbers the prose states.
# Named constants rather than literals inside the predicate, because
# `design/gold/check_gold.py` asserts the same boundary against the gold suite
# and the two must be the same numbers or gold and the filter disagree about
# what is excluded.
X1_RISK_FLOOR = Decimal("40")      # inclusive
X1_RISK_CEILING = Decimal("70")    # exclusive
X1_SPEND_CAP = Decimal("100000.00")
X1_LOW_COUNTRY = "LOW"

# matrix facts member -> (canonical cell key, wire kind). The canonical keys are
# the gold suite's input keys, so one signature reads for gold rows, authored
# matrix cases and Rego input points alike.
VENDOR_MEMBERS = (("riskScore", "risk", "number"),
                  ("requestedSpend", "spend", "number"),
                  ("sanctionsStatus", "sanctions", "string"),
                  ("countryRisk", "country", "string"),
                  ("newVendor", "newVendor", "string"),
                  ("criticalSupplier", "critical", "string"),
                  ("priorEnforcement", "prior", "string"))
EVIDENCE_MEMBERS = (("financial-evidence", "finEvidence"),
                    ("insurance-certificate", "insurance"))


class E4Error(Exception):
    """A refusal in the E4 machinery, with a named code as its first word."""


def _decimal(value):
    """A canonical decimal from a wire value, or None when it is unreadable.

    Every numeric input in this study travels as a DECIMAL STRING (section 2's
    naming appendix), and `Decimal(str(v))` reads an authored JSON number
    without a float round-trip. An unreadable value is None — the same state as
    an omitted member, which is what section 4's input-domain closure requires."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, ArithmeticError):
        return None


def in_x1(signature: dict) -> bool:
    """Section 4's registered X1 exclusion class, as one predicate.

        {new vendor yes; risk in [40, 70); LOW country with spend unreadable,
         or country unreadable with spend <= 100,000.00}

    An unreadable risk is NOT in X1: the class is defined over a risk band, and
    a point with no readable risk is not in a band. That reading is the same one
    `design/gold/check_gold.py` enforces over the gold suite (`i["risk"] is not
    None and 40 <= int(i["risk"]) < 70`), and the two must agree or gold
    contains a row the filter would have excluded."""
    if signature.get("newVendor") != "yes":
        return False
    risk = _decimal(signature.get("risk"))
    if risk is None or not (X1_RISK_FLOOR <= risk < X1_RISK_CEILING):
        return False
    country = signature.get("country")
    spend = _decimal(signature.get("spend"))
    low_country_unreadable_spend = (country == X1_LOW_COUNTRY
                                    and signature.get("spend") is None)
    unreadable_country_small_spend = (country is None and spend is not None
                                      and spend <= X1_SPEND_CAP)
    return low_country_unreadable_spend or unreadable_country_small_spend


def case_signature(facts: dict, evidence: dict) -> dict:
    """The canonical input signature of one authored matrix case."""
    vendor = (facts or {}).get("vendor") or {}
    signature = {}
    for member, cell, _kind in VENDOR_MEMBERS:
        signature[cell] = vendor.get(member)
    for member, cell in EVIDENCE_MEMBERS:
        signature[cell] = (evidence or {}).get(member)
    return signature


def align_expected(expected):
    """`(kind, outcomeId, sorted reasons)` from a matrix case's
    `expectedDisposition`, or None when the case does not carry a readable one.

    This IS the alignment map on the expectation side, and it drops exactly what
    section 5 puts outside every endpoint: `handoff` (state, triggeredBy,
    target) and `trace[]` are never read, so ADR-0025's handoff assertion cannot
    enter an E4 number by accident."""
    if not isinstance(expected, dict):
        return None
    kind = expected.get("kind")
    reasons = tuple(sorted(str(reason)
                           for reason in (expected.get("reasons") or [])))
    if kind == "outcome":
        return ("outcome", expected.get("outcomeId"), reasons)
    if kind == "unresolved":
        return ("unresolved", None, reasons)
    return None


def load_matrix(path: str) -> tuple:
    """`(cases, note)`; a case is
    `(id, facts, evidence, expected, readable, signature)`.

    A case is UNREADABLE rather than absent when it carries no facts object or
    no readable expectation. Unreadable cases fail identity (they are what the
    author emitted) and can kill nothing."""
    with open(path, "rb") as handle:
        document = json.loads(handle.read().decode("utf-8"))
    cases = []
    for index, case in enumerate(document.get("cases") or []):
        case_id = case.get("id") if isinstance(case.get("id"), str) \
            else "case[%d]" % index
        facts = case.get("facts")
        evidence = case.get("evidenceAvailability") or {}
        expected = align_expected(case.get("expectedDisposition"))
        readable = isinstance(facts, dict) and expected is not None
        facts = facts if isinstance(facts, dict) else {}
        evidence = evidence if isinstance(evidence, dict) else {}
        cases.append((case_id, facts, evidence, expected, readable,
                      case_signature(facts, evidence)))
    return cases, {"matrixVersion": document.get("matrixVersion"),
                   "caseCount": len(cases)}


def partition_x1(cases: list) -> tuple:
    """`(scored cases, excluded case ids)` — the X1 filter, applied once.

    Applied ONCE and in one place, so identity and kill see the same case set
    by construction. Section 4 requires the excluded count to be published per
    run, so the ids come back rather than a count."""
    scored, excluded = [], []
    for case in cases:
        if in_x1(case[5]):
            excluded.append(case[0])
        else:
            scored.append(case)
    return scored, excluded


# --- the mutant sets and the pairing ---------------------------------------


def load_mutants(jps_manifest_path: str, rego_manifest_path: str,
                 jps_dir: str, rego_dir: str) -> dict:
    """`{'jps': [record...], 'rego': [record...]}` in MANIFEST order, valid only.

    Changed from the prototype: the manifest paths and the mutant directories
    are ARGUMENTS rather than module constants pointing into `design/`. The
    frozen manifests are `mutants/MANIFEST-jps.json` and
    `mutants/MANIFEST-rego.json` (the registry's `mutantManifests` pin), and a
    scorer that reads its mutants from the design tree would score the study
    against unfrozen bytes."""
    records = {}
    with open(jps_manifest_path, "rb") as handle:
        jps_manifest = json.loads(handle.read().decode("utf-8"))
    jps = []
    for mutant in jps_manifest:
        if mutant.get("validates") is not True:
            continue
        witnesses = sorted(mutant.get("witnessSet") or [])
        jps.append({"id": mutant["id"],
                    "path": os.path.join(jps_dir, mutant["id"] + ".json"),
                    "witnessSet": witnesses,
                    "witnessKey": tuple(witnesses),
                    "notAdequate": bool(mutant.get("notAdequate")),
                    "class": mutant.get("class"),
                    "engineSuppliedKill": mutant.get("engineSuppliedKill")})
    with open(rego_manifest_path, "rb") as handle:
        rego_manifest = json.loads(handle.read().decode("utf-8"))
    rego = []
    for mutant in rego_manifest["mutants"]:
        if mutant.get("status") != "valid":
            continue
        witnesses = sorted(mutant.get("witnessSet") or [])
        rego.append({"id": mutant["id"],
                     "path": os.path.join(rego_dir, mutant["file"]),
                     "witnessSet": witnesses,
                     "witnessKey": tuple(witnesses),
                     "notAdequate": bool(mutant.get("notAdequate")),
                     "class": mutant.get("mutationClass"),
                     "engineSuppliedKill": mutant.get("engineSuppliedKill")})
    records["jps"], records["rego"] = jps, rego
    for language, entries in records.items():
        for entry in entries:
            if not os.path.exists(entry["path"]):
                raise E4Error("E4-MISSING-MUTANT %s %s has no file"
                              % (language, entry["id"]))
            # The empty-witness <-> notAdequate identity the pairing rule leans
            # on. Asserted rather than assumed: if it ever fails, the degenerate
            # group stops being the notAdequate set and the paired subset
            # silently changes size.
            if entry["notAdequate"] != (len(entry["witnessSet"]) == 0):
                raise E4Error(
                    "E4-WITNESS-DISAGREEMENT %s %s: notAdequate=%s but witness "
                    "set size %d" % (language, entry["id"], entry["notAdequate"],
                                     len(entry["witnessSet"])))
    return records


def build_pairing(mutants: dict) -> tuple:
    """Section 4's registered pairing rule: IDENTICAL SORTED WITNESS SETS.

    Pairing is a grouping by witness-set key and is therefore many-to-many; the
    whole grouping is the published pairing table. The empty witness set is a
    key like any other, and pairing all empty-witness JPS mutants with all
    empty-witness Rego mutants would pair on the ABSENCE of a discriminating
    gold row rather than on a shared one — so that group is emitted flagged and
    excluded from the paired subsets ("the empty witness set is degenerate and
    never pairs")."""
    groups = {}
    for language in ("jps", "rego"):
        for record in mutants[language]:
            group = groups.setdefault(record["witnessKey"],
                                      {"jps": [], "rego": []})
            group[language].append(record["id"])
    table = []
    for key in sorted(groups, key=lambda k: (len(k), k)):
        group = groups[key]
        paired = bool(group["jps"]) and bool(group["rego"])
        degenerate = paired and len(key) == 0
        table.append({
            "witnessSet": list(key),
            "witnessCount": len(key),
            "jpsMutants": group["jps"],
            "regoMutants": group["rego"],
            "jpsCount": len(group["jps"]),
            "regoCount": len(group["rego"]),
            "paired": paired,
            "notAdequate": len(key) == 0,
            "degenerate": degenerate,
            "countedInPairedSubset": paired and not degenerate,
        })
    paired_ids = {"jps": set(), "rego": set()}
    for row in table:
        if row["countedInPairedSubset"]:
            paired_ids["jps"].update(row["jpsMutants"])
            paired_ids["rego"].update(row["regoMutants"])
    return table, paired_ids


def unpairable(mutants: dict, paired_ids: dict) -> dict:
    """The counts section 4 publishes as "a finding about the defect spaces"."""
    return {language: sorted(record["id"] for record in mutants[language]
                             if not record["notAdequate"]
                             and record["id"] not in paired_ids[language])
            for language in ("jps", "rego")}


def engine_supplied_ids(mutants: dict, language: str) -> list:
    """Section 4's engine-supplied-kill list, from the manifest.

    Section 4 says those mutants are "listed in the registries", and the
    registered report is "both included and excluded". The marking used to exist
    only as a `conflict-only` glyph in `design/mutants/ADEQUACY.md`'s prose
    table; both manifests carry it as a member now (SCAFFOLD item S9), so this
    reads frozen bytes rather than parsing a registered number out of prose.

    A language whose manifest carries the member on NO mutant still refuses by
    name. The distinction is the point: a manifest where every mutant records
    `engineSuppliedKill: false` is the registered statement that the arm has an
    EMPTY engine-supplied class — which is arm B's, and which
    `design/mutants/refB/MANIFEST.json`'s `engineSuppliedKillClass` states with
    its reason — while a manifest with no member at all says nothing, and
    returning an empty list from it would publish "0 engine-supplied kills" and
    satisfy section 4 in form only."""
    entries = mutants[language]
    marked = [record for record in entries
              if record.get("engineSuppliedKill") is not None]
    if not marked:
        raise E4Error(
            "E4-ENGINE-SUPPLIED-UNREGISTERED the %s mutant manifest carries no "
            "engineSuppliedKill member, so section 4's 'reported both included "
            "and excluded' cannot be computed from frozen bytes; the marking is "
            "prose in design/mutants/ADEQUACY.md and must become a manifest "
            "member before the freeze (harness/SCAFFOLD.md item S9)" % language)
    return sorted(record["id"] for record in marked
                  if record["engineSuppliedKill"])


# --- the identity control and kill ------------------------------------------


def identity_arm_a(tools: engines.Toolchain, reference_pack: str, cases: list,
                   workdir: str) -> tuple:
    """Section 5's identity control for arm A: every non-X1 case must agree with
    the arm's own UNMUTATED reference on the scored surface.

    A case with no readable facts or expectation is a failure, not a skip: it is
    what the author emitted, and a suite whose cases cannot be read pins
    nothing."""
    failures = []
    for case_id, facts, evidence, expected, readable, _signature in cases:
        if not readable:
            failures.append({"case": case_id, "expected": "<unreadable>",
                             "got": "<not-run>",
                             "reason": "case carries no facts object or no "
                                       "readable expectedDisposition"})
            continue
        observed = engines.eval_pack(tools, reference_pack, facts, evidence,
                                     workdir)
        if observed != expected:
            failures.append({"case": case_id,
                             "expected": engines.scope_str(expected),
                             "got": engines.scope_str(observed)})
    return not failures, failures


def kill_arm_a(tools: engines.Toolchain, mutant_path: str, cases: list,
               workdir: str) -> tuple:
    """`(killed, first disagreeing case id or None)`.

    Kill is "at least one non-X1 case disagrees on the mutant" (section 5), so
    the scan short-circuits at the first disagreement and records which case it
    was — the diagnostic E3 reads. A refusal on a mutant counts as
    disagreement: the suite distinguished the mutant from the reference, which
    is what a kill is."""
    for case_id, facts, evidence, expected, readable, _signature in cases:
        if not readable:
            continue
        observed = engines.eval_pack(tools, mutant_path, facts, evidence,
                                     workdir)
        if observed != expected:
            return True, case_id
    return False, None


def identity_arm_rego(tools: engines.Toolchain, reference_policy: str,
                      suite_path: str, workdir: str) -> tuple:
    """Section 5's identity control for arms B/C: `opa test` against the arm's
    reference must exit 0."""
    code, label = engines.opa_test(tools, reference_policy, suite_path, workdir)
    return code == 0, {"exitCode": code, "class": label}


def kill_arm_rego(tools: engines.Toolchain, mutant_path: str, suite_path: str,
                  workdir: str) -> tuple:
    """`(killed, {exitCode, class})` — nonzero `opa test` kills, with the class
    recorded (section 5: "for B/C, `opa test` nonzero with class recorded")."""
    code, label = engines.opa_test(tools, mutant_path, suite_path, workdir)
    return code != 0, {"exitCode": code, "class": label}


# --- the run-level endpoint -------------------------------------------------


def kill_rates(kill_of: dict, mutants: list, paired_ids: set,
               engine_supplied=()) -> dict:
    """The kill counts one suite produces, over named denominators.

    `killedPaired`/`paired` is the ONLY pair the endpoint reads (section 5: "the
    suite's paired-subset kill rate = killed / paired adequate mutants"); the
    others are R2's failure map. Each carries its denominator's name, so no
    reader can mistake the own-language rate for the cross-arm one.

    `engine_supplied` is section 4's registered list of mutants whose kills are
    achievable only through the engine's structural conflict detection. Section 4
    registers them "reported both included and excluded", so the paired subset is
    split here — once, at the only place that knows which mutant each kill came
    from — rather than reconstructed later from an aggregate."""
    supplied = set(engine_supplied or ())
    adequate = [record for record in mutants if not record["notAdequate"]]
    not_adequate = [record for record in mutants if record["notAdequate"]]
    paired_adequate = [record for record in adequate
                       if record["id"] in paired_ids]
    excluded = [record for record in paired_adequate
                if record["id"] not in supplied]
    listed = [record for record in paired_adequate
              if record["id"] in supplied]
    def killed(subset):
        return sum(1 for record in subset if kill_of.get(record["id"]))
    return {
        "killedAdequate": killed(adequate),
        "adequate": len(adequate),
        "killedPaired": killed(paired_adequate),
        "paired": len(paired_adequate),
        # Section 4, "reported both included and excluded": the same paired
        # subset with the registered engine-supplied mutants taken out, and the
        # engine-supplied members on their own.
        "killedPairedExcludingEngineSupplied": killed(excluded),
        "pairedExcludingEngineSupplied": len(excluded),
        "killedEngineSupplied": killed(listed),
        "engineSupplied": len(listed),
        "killedNotAdequate": killed(not_adequate),
        "notAdequate": len(not_adequate),
        "survivorsPaired": [record["id"] for record in paired_adequate
                            if not kill_of.get(record["id"])],
    }


def is_high_kill(killed_paired: int, paired: int, cut: int) -> bool:
    """Section 5's high-kill predicate, at the INTEGER cut.

    Stated as an integer comparison and not as `rate >= 0.95`, because at
    paired = 39 the rate 37/39 is 0.9487… and 38/39 is 0.9743… — the float
    comparison and the integer cut agree there, and the point of deriving the
    cut is that whether they agree is checkable rather than hoped for."""
    return killed_paired >= cut


def high_kill_cut(paired: int) -> dict:
    """The cut, with the arithmetic that produced it, for publication.

    Section 5 registers that "the operative integer cut at the frozen paired-
    mutant count is stated"; the scorer prints this block."""
    cut = stats.tau_cut(paired)
    return {"tau": str(stats.TAU), "pairedAdequateMutants": paired,
            "integerCut": cut,
            "cutRate": float(Fraction(cut, paired)),
            "statement": "a run is high-kill iff it kills at least %d of the %d "
                         "paired adequate mutants (tau = %s)"
                         % (cut, paired, stats.TAU)}
