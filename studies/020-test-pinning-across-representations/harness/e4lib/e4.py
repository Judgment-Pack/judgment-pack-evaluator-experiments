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
1. **The registered exclusion filter, and the registered input domain.** §4
   registers an exclusion-class registry and a per-run excluded-case count.
   `REGISTERED_EXCLUSION_CLASSES` is that registry as data and is EMPTY since
   round-1 R1-2 retired X1 (the arm-A reference was repaired instead), so the
   published count is a measured zero rather than a filter nobody applied;
   `in_x1()` is kept as the retired predicate, gating nothing, so the repair
   stays re-measurable. What DOES filter is the registered INPUT DOMAIN, and it
   filters all three arms alike: `e4lib/domain.py` enumerates every arm's case
   inputs mechanically — arm A's from the matrix, arms B/C's from
   `opa parse --format json`'s own syntax tree — and validates each against the
   registered space before identity and before any mutation execution (round-1
   R1-3, which found that arms B and C received no case-level validation at all).
2. **The identity control as a first-class per-arm RATE**, not a gate that
   silently removes suites. The prototype reported identity failures per suite;
   section 5 reports the rate, and section 1a requires the exclusions to be
   "reported, never silently dropped".
3. **The tau cut as an integer derived at run time, PER LANGUAGE.** Section 5
   registers tau = 0.95 over the paired adequate subset and says the operative
   integer cut at the frozen paired count is stated. `stats.tau_cut()` derives
   it and the scorer prints it, so the number a run is judged against is in the
   published record rather than in an analyst's head. `high_kill_cuts()` derives
   ONE PER LANGUAGE from that language's own paired denominator (round-1 R1-1:
   a single JPS-derived cut applied to every arm made the primary endpoint
   unreachable for arms B and C), and `is_high_kill()` refuses a cut its run's
   denominator cannot reach instead of quietly answering False.
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

from . import domain
from . import engines
from . import stats

# The RETIRED X1 boundary, as the three numbers the prose used to state.
#
# ROUND-1 FINDING R1-2, and the arm-A reference repair that answered it
# (`design/reference/refA/PACK-CHANGE-001.md`): X1's inexpressibility claim did
# not survive review, the reference was repaired to answer the prose-correct
# `review` on all 72 cells, and the certificate's divergence count over the
# 236,196-cell registered space is now ZERO. `cert_offgold.py`'s own registry of
# exclusion classes is empty for that reason, and `REGISTERED_EXCLUSION_CLASSES`
# below is this module's copy of that fact.
#
# The predicate is KEPT and gates nothing, exactly as the certificate keeps its
# own: it is what makes "the repair moved exactly the cells the retired class
# named" a thing that can be re-measured rather than remembered.
X1_RISK_FLOOR = Decimal("40")      # inclusive
X1_RISK_CEILING = Decimal("70")    # exclusive
X1_SPEND_CAP = Decimal("100000.00")
X1_LOW_COUNTRY = "LOW"

# Section 4's registered exclusion classes, as data. EMPTY since 2026-08-18.
# A class is added by editing this dict with a written reason and nothing else,
# which is the only way one should ever be added; `partition_excluded()` reads
# it and excludes exactly what it names.
REGISTERED_EXCLUSION_CLASSES = {}

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


class MatrixError(E4Error):
    """The AUTHOR's matrix is not a matrixVersion-2 document.

    Distinguished from every other `E4Error` because it is the one refusal in
    this module that is about what the author emitted rather than about the
    apparatus: §1a keeps it in the denominator as a counted authoring outcome,
    and `harness/score.py` maps it onto the registered code. Round-1 finding
    R1-6 was that this class did not exist — `load_matrix()` assumed its way
    through the document and an `AttributeError` invalidated the whole attempt."""


class ExecutionRefusal(E4Error):
    """A pinned engine refused on a FROZEN study artifact.

    Round-1 finding R1-8: a mutant-phase timeout, compile failure or invocation
    failure used to count as a kill, and the same failure against the reference
    used to fail identity and score a correct suite zero. Neither is evidence
    about a suite, so neither is a rate; both raise here and reach the
    `engine-execution-clean` control gate."""


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
    enter an E4 number by accident.

    TOTAL over every JSON value (round-2 R2-6). `reasons` used to be iterated
    with only a falsy guard in front of it, so `"reasons": 1` raised an uncaught
    `TypeError` out of the scorer instead of landing on the registered authoring
    code. Every shape this cannot read now answers `None`, and `load_matrix()`
    refuses the document before this is ever reached with such a value."""
    if not isinstance(expected, dict):
        return None
    kind = expected.get("kind")
    raw_reasons = expected.get("reasons")
    if raw_reasons is None:
        raw_reasons = []
    if not isinstance(raw_reasons, list) \
            or not all(isinstance(reason, str) for reason in raw_reasons):
        return None
    reasons = tuple(sorted(raw_reasons))
    if kind == "outcome":
        outcome_id = expected.get("outcomeId")
        if not isinstance(outcome_id, str):
            return None
        return ("outcome", outcome_id, reasons)
    if kind == "unresolved":
        return ("unresolved", None, reasons)
    return None


# The REGISTERED spelling, and it is a STRING (round-2 finding R2-6).
# `design/prompts/ARM-A-INSTRUCTIONS.md`: "`matrixVersion`: the string `"2"`";
# the arm-A excerpt's own examples and every real pilot matrix
# (`design/pilots/.../arm-A/run-008/secondary.json`) emit `"matrixVersion": "2"`.
# This loader registered the INTEGER 2, so every prompt-conforming matrix was
# refused as `unparseable-artifact` and scored zero — the endpoint was
# unreachable for arm A in exactly the way R1-1's single cut made it unreachable
# for arms B and C, and the tests missed it because they were written against
# the loader rather than against the prompt.
MATRIX_VERSION = "2"
MATRIX_VERSION_MISREAD = 2

# §5's scored surface has no error-class axis, so `expectedErrorClass` is a
# registered expectation form this study cannot score: the case carries no
# readable expectation and fails the identity control, which is what §1a does
# with what the author emitted.
EXPECTATION_FORMS = ("expectedDisposition", "expectedErrorClass")


def _require(condition, message):
    if not condition:
        raise MatrixError("E4-MATRIX-SCHEMA " + message)


def load_matrix(path: str) -> tuple:
    """`(cases, note)`; a case is
    `(id, facts, evidence, expected, readable, signature)`.

    TOTAL matrixVersion-2 SCHEMA VALIDATION (round-1 R1-6). The reviewer's three
    payloads — `[]`, `{"cases": [null]}`, and a `facts.vendor` that is a string —
    are all valid JSON and all used to raise `AttributeError`/`TypeError` out of
    this function, past a caller that caught only `ValueError`, into the outer
    handler that publishes pipeline-invalid and re-raises. §1a registers the
    opposite outcome: unparseable or schema-invalid AUTHOR output is a counted
    authoring outcome that scores zero and stays in the denominator. Every
    author-controlled shape failure is therefore a `MatrixError` here, and the
    outer exception path is left for apparatus defects.

    The line between SCHEMA and READABILITY is drawn where the registration draws
    it. A member of the wrong TYPE is a schema failure and refuses the document.
    A member that is ABSENT, or an `expectedDisposition` whose `kind` is not one
    of the two registered kinds, leaves the case UNREADABLE — which fails the
    identity control, because it is what the author emitted and a suite whose
    cases cannot be read pins nothing."""
    with open(path, "rb") as handle:
        raw = handle.read()
    try:
        document = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as error:
        raise MatrixError("E4-MATRIX-SCHEMA the matrix block is not readable "
                          "JSON (%s)" % type(error).__name__)
    _require(isinstance(document, dict),
             "the matrix is a JSON %s and matrixVersion 2 is an object"
             % type(document).__name__)
    version = document.get("matrixVersion")
    _require(version == MATRIX_VERSION,
             "matrixVersion is %r and this study registers the string %r%s"
             % (version, MATRIX_VERSION,
                " (the JSON number 2 is not the registered spelling; the prompt "
                "and every example emit the string)"
                if version == MATRIX_VERSION_MISREAD else ""))
    raw_cases = document.get("cases")
    _require(isinstance(raw_cases, list),
             "the `cases` member is a JSON %s and matrixVersion 2 registers a "
             "list" % type(raw_cases).__name__)
    cases = []
    for index, case in enumerate(raw_cases):
        _require(isinstance(case, dict),
                 "case %d is a JSON %s and a case is an object"
                 % (index, type(case).__name__))
        case_id = case.get("id")
        _require(case_id is None or isinstance(case_id, str),
                 "case %d carries a non-string id" % index)
        case_id = case_id if isinstance(case_id, str) else "case[%d]" % index
        facts = case.get("facts")
        _require(facts is None or isinstance(facts, dict),
                 "%s carries a `facts` member that is a JSON %s"
                 % (case_id, type(facts).__name__))
        if isinstance(facts, dict):
            vendor = facts.get("vendor")
            _require(vendor is None or isinstance(vendor, dict),
                     "%s carries a `facts.vendor` member that is a JSON %s"
                     % (case_id, type(vendor).__name__))
        evidence = case.get("evidenceAvailability")
        _require(evidence is None or isinstance(evidence, dict),
                 "%s carries an `evidenceAvailability` member that is a JSON %s"
                 % (case_id, type(evidence).__name__))
        expectation = case.get("expectedDisposition")
        _require(expectation is None or isinstance(expectation, dict),
                 "%s carries an `expectedDisposition` member that is a JSON %s"
                 % (case_id, type(expectation).__name__))
        # ROUND-2 R2-6, second half: the enclosing-object check was the whole of
        # the validation, so a nested member of the wrong type walked past it
        # and raised out of `align_expected()`. Every nested member is typed
        # here, and the registered "exactly one of" is enforced: two expectation
        # forms in one case is a contradictory document and refuses, while
        # NEITHER form leaves the case unreadable, which is the line the
        # docstring above draws between a schema failure and an absence.
        _require(not all(form in case for form in EXPECTATION_FORMS),
                 "%s carries both `expectedDisposition` and "
                 "`expectedErrorClass` and the registered matrix row carries "
                 "exactly one of them" % case_id)
        for member in ("expectedErrorClass", "expectedErrorPhase"):
            value = case.get(member)
            _require(value is None or isinstance(value, str),
                     "%s carries a `%s` member that is a JSON %s"
                     % (case_id, member, type(value).__name__))
        if isinstance(expectation, dict):
            _require(isinstance(expectation.get("kind"), str)
                     or expectation.get("kind") is None,
                     "%s carries an `expectedDisposition.kind` that is a JSON %s"
                     % (case_id, type(expectation.get("kind")).__name__))
            reasons = expectation.get("reasons")
            _require(reasons is None
                     or (isinstance(reasons, list)
                         and all(isinstance(reason, str) for reason in reasons)),
                     "%s carries an `expectedDisposition.reasons` that is not a "
                     "list of strings (%r)" % (case_id, reasons))
            outcome_id = expectation.get("outcomeId")
            _require(outcome_id is None or isinstance(outcome_id, str),
                     "%s carries an `expectedDisposition.outcomeId` that is a "
                     "JSON %s" % (case_id, type(outcome_id).__name__))
            handoff = expectation.get("handoff")
            _require(handoff is None or isinstance(handoff, dict),
                     "%s carries an `expectedDisposition.handoff` that is a "
                     "JSON %s" % (case_id, type(handoff).__name__))
        target = case.get("expectedHandoffTarget")
        _require(target is None or isinstance(target, dict),
                 "%s carries an `expectedHandoffTarget` that is a JSON %s and "
                 "the registered member is an object or the literal null"
                 % (case_id, type(target).__name__))
        expected = align_expected(expectation)
        readable = isinstance(facts, dict) and expected is not None
        facts = facts if isinstance(facts, dict) else {}
        evidence = evidence if isinstance(evidence, dict) else {}
        cases.append((case_id, facts, evidence, expected, readable,
                      case_signature(facts, evidence)))
    return cases, {"matrixVersion": version, "caseCount": len(cases)}


def matrix_domain_signature(facts: dict, evidence: dict) -> dict:
    """One matrix case's input point in `domain.py`'s canonical shape, with
    every member the registered document does not carry recorded."""
    vendor = (facts or {}).get("vendor")
    extra = ["facts.%s" % name for name in (facts or {}) if name != "vendor"]
    return domain.signature_from_documents(vendor, evidence, extra)


def partition_excluded(cases: list) -> tuple:
    """`(scored cases, excluded case ids)` over `REGISTERED_EXCLUSION_CLASSES`.

    Applied ONCE and in one place, so identity and kill see the same case set by
    construction. The registry is EMPTY since X1's retirement (module head), so
    this excludes nothing today.

    ROUND-3 FINDING R3-9. This used to say the empty result was "published as
    the zero it is", and §4 says the opposite in terms: "There is no exclusion
    class, no per-case X1 filter and no per-run excluded-case count." The zero
    is no longer published anywhere — `harness/score.py` refuses outright if
    this ever returns a non-empty exclusion list, because a class the
    registration does not carry must not decide which cases are scored. The
    function survives as the single application point a future registered class
    would have to go through."""
    scored, excluded = [], []
    for case in cases:
        member = next((name for name, predicate
                       in sorted(REGISTERED_EXCLUSION_CLASSES.items())
                       if predicate(case[5])), None)
        if member is None:
            scored.append(case)
        else:
            excluded.append(case[0])
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
    satisfy section 4 in form only.

    ROUND-2 FINDING R2-10, and the refusal was not fail-closed. It fired only
    when EVERY record was unmarked, so a manifest marking one mutant and leaving
    the next silent was accepted and published a class computed from a partial
    census — the same "0 from an absence" this refusal exists to prevent, one
    record at a time. And the marking was read for TRUTHINESS, so the string
    `"false"` counted a mutant INTO the class. Every valid record must now carry
    a real Boolean: `type(...) is bool`, which admits neither `None`, nor `0`/`1`,
    nor `"false"`, and the refusal names the records that do not."""
    entries = mutants[language]
    unmarked = [record["id"] for record in entries
                if type(record.get("engineSuppliedKill")) is not bool]
    # SILENCE and WRONG TYPE are different refusals. A manifest where no record
    # carries the member at all has said nothing (the round-1 refusal); one that
    # carries values of the wrong type has said something unreadable, and naming
    # it "carries no member" would send a reader to the wrong file.
    if all(record.get("engineSuppliedKill") is None for record in entries):
        raise E4Error(
            "E4-ENGINE-SUPPLIED-UNREGISTERED the %s mutant manifest carries no "
            "engineSuppliedKill member, so section 4's 'reported both included "
            "and excluded' cannot be computed from frozen bytes; the marking is "
            "prose in design/mutants/ADEQUACY.md and must become a manifest "
            "member before the freeze (harness/SCAFFOLD.md item S9)" % language)
    if unmarked:
        raise E4Error(
            "E4-ENGINE-SUPPLIED-INCOMPLETE %d of the %d valid %s mutants carry "
            "no BOOLEAN engineSuppliedKill member (%s%s): section 4's class is "
            "a census over the whole set, and a class computed from a partial "
            "or mistyped census is the same '0 from an absence' the refusal "
            "above exists to prevent"
            % (len(unmarked), len(entries), language,
               ", ".join(unmarked[:5]), "…" if len(unmarked) > 5 else ""))
    return sorted(record["id"] for record in entries
                  if record["engineSuppliedKill"])


# --- the identity control and kill ------------------------------------------


KILLED = "killed"
SURVIVED = "survived"
REFUSED = "refused"
# NEW IN 020, AND IT IS THE WHOLE OF §7's DELTA 1. Study 019 had three outcome
# tokens and a fourth STATE it had no token for: a mutant that was never
# evaluated at all, because the run failed the identity control before the kill
# loop ran. `kill_rates({}, …)` then produced `killedPaired: 0` with
# `survivorsPaired: []`, which is BYTE-IDENTICAL to the record of a suite that
# killed every paired mutant — the empty survivor list encodes "nothing
# evaluated" and "everything killed" with the same token.
#
# On 019's own batch that single collision moves the group-level ITT A−C
# contrast from +0.19112 (naive) to +0.13849 (corrected): two arm-A runs
# (`run-025`, `run-046`, both identity-failing) score a perfect 33/33 having
# killed nothing. §5.2 registers the repair as a DAY-ONE requirement and this
# constant is it — every paired-adequate mutant of every admitted run now
# carries an explicit token, and `NOT_EVALUATED` is the one the collision
# needed.
NOT_EVALUATED = "not-evaluated"
MUTANT_OUTCOMES = (KILLED, SURVIVED, REFUSED, NOT_EVALUATED)

# The identity-failure category §5's E3 taxonomy publishes for a case that left
# the registered input domain. Named once so the scorer, the taxonomy and the
# tests cannot hold three spellings of it.
OUT_OF_DOMAIN = "out-of-domain-case"


def rego_case_signatures(tools: engines.Toolchain, suite_path: str,
                         workdir: str, policy_path: str = None) -> list:
    """`[(case name, signature)]` for an `opa test` file — the B/C half of
    round-1 R1-3's symmetric enumeration.

    Arms B and C used to hand the scorer an opaque file and receive no
    case-level validation of any kind, while arm A's matrix was parsed and
    filtered. The suite's own SYNTAX TREE closes that: `opa parse --format json`
    is the pinned binary's reading of the file, and every `with input as
    <literal>` term in it is a case input this study can check against the same
    registered domain arm A's cases are checked against.

    TWO MODES, because real suites use both. Literal `with input as {…}` terms
    are read straight off the tree; a table-driven suite — which is what the
    pilot's own arm-B and arm-C runs wrote, with named evidence constants and a
    `make_input()` helper over `object.union` — carries a ref there instead, and
    that ref is resolved against the suite's own package document, EVALUATED with
    the pinned binary, plus the rule body's own `:=` and `some … in` bindings.
    Both readings are the pinned toolchain's; neither is a re-implementation of
    Rego and neither is a guess.

    ROUND-2 FINDING R2-4. The refusal used to be "no input-shaped literal exists
    ANYWHERE in the file", which is a statement about the file and not about the
    terms: the reviewer's probe carried one unrelated valid `decoy` literal,
    built its real input inside a rule body, and had the decoy satisfy the check
    while the tested point — `newVendor: 7` — was never enumerated and never
    domain-validated. The enumeration is per term now, so EVERY `with input as`
    term must resolve; one that does not is this refusal by name, whatever else
    the file contains.

    A file the pinned parser refuses, or a suite with a `with input as` term that
    cannot be resolved either way, is a `MatrixError` — the registered authoring
    outcome — and never a silent pass."""
    code, raw = engines.opa_parse(tools, suite_path, workdir)
    if code != 0:
        raise MatrixError(
            "E4-MATRIX-SCHEMA the pinned parser refuses the suite file "
            "(`opa parse` exit %d), so its cases cannot be enumerated and its "
            "input points cannot be validated against the registered domain"
            % code)
    try:
        document = domain.parse_tree(raw)
        unresolved, cases = domain.cases_from_tree(document)
        if unresolved:
            # The table-driven mode. Evaluate the suite's own package with the
            # pinned binary: that resolves the named constants and helper
            # functions real suites build their input points out of, and gives
            # the NAME MAP the per-term resolution needs.
            data_paths = [suite_path] + ([policy_path] if policy_path else [])
            eval_code, eval_raw = engines.opa_eval_document(
                tools, data_paths, domain.package_path(document), workdir)
            if eval_code == 0:
                resolved = domain.package_document(eval_raw)
                names = resolved if isinstance(resolved, dict) else None
                unresolved, cases = domain.cases_from_tree(document, names)
    except domain.DomainError as error:
        raise MatrixError("E4-MATRIX-SCHEMA %s" % error)
    except ValueError as error:
        raise MatrixError("E4-MATRIX-SCHEMA the resolved suite document is not "
                          "readable JSON (%s)" % type(error).__name__)
    if unresolved:
        raise MatrixError(
            "E4-MATRIX-SCHEMA %d `with input as` term(s) name an input point "
            "that neither the suite's syntax tree nor its resolved package "
            "document holds (%s): those case inputs cannot be validated against "
            "the registered domain, and an unrelated literal elsewhere in the "
            "file does not stand in for them"
            % (len(unresolved), "; ".join(sorted(set(unresolved))[:3])))
    return [("case[%d]" % order, signature)
            for order, (_index, signature) in enumerate(cases)]


def domain_failures(named_signatures, wire: str) -> list:
    """Every case whose input point leaves the registered domain, as identity
    failures in the shape `identity_arm_a()` returns.

    THE SAME CHECK IN ALL THREE ARMS, applied BEFORE identity and before any
    mutation execution (round-1 R1-3). A case outside the registered space is
    one on which the off-gold certificate establishes nothing — the labelled
    supplementary stratum measured 18,954 reference divergences out there — so a
    suite that asserts about it is asserting about behaviour this study's oracle
    does not fix. It is what the author emitted, so §5's identity control is
    where it lands: the run stays in the E4 denominator as not-high-kill, the
    failure is reported per arm as a first-class rate, and E3 counts it under
    `out-of-domain-case`. It is never silently dropped and never silently
    scored."""
    failures = []
    for name, signature in named_signatures:
        problems = domain.domain_problems(signature, wire)
        if problems:
            failures.append({"case": name, "expected": "<in registered domain>",
                             "got": OUT_OF_DOMAIN, "problems": problems})
    return failures


def identity_arm_a(tools: engines.Toolchain, reference_pack: str, cases: list,
                   workdir: str) -> tuple:
    """Section 5's identity control for arm A: every scored case must agree with
    the arm's own UNMUTATED reference on the scored surface.

    A case with no readable facts or expectation is a failure, not a skip: it is
    what the author emitted, and a suite whose cases cannot be read pins nothing.

    A REFERENCE that refuses is not a suite failure at all (round-1 R1-8). Every
    case reaching here has already been validated against the registered input
    domain (`domain.py`), and the off-gold certificate establishes that the
    reference answers every point of that domain — so a `ROW-ERROR` here is the
    apparatus, and zero-scoring a correct suite on it is the attribution error
    the finding names. It raises."""
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
        if observed[0] == "ROW-ERROR":
            raise ExecutionRefusal(
                "E4-IDENTITY-ENGINE-REFUSED the arm-A reference refused on the "
                "in-domain case %s with %s: the identity control cannot be "
                "decided and a suite is not scored zero for an engine refusal"
                % (case_id, engines.scope_str(observed)))
        if observed != expected:
            failures.append({"case": case_id,
                             "expected": engines.scope_str(expected),
                             "got": engines.scope_str(observed)})
    return not failures, failures


def kill_arm_a(tools: engines.Toolchain, mutant_path: str, cases: list,
               workdir: str) -> tuple:
    """`(outcome, detail)` — `killed`/`survived`/`refused`.

    Kill is "at least one scored case disagrees on the mutant" (section 5), so
    the scan short-circuits at the first disagreement and records which case it
    was — the diagnostic E3 reads.

    A REFUSAL IS NOT A KILL (round-1 R1-8). The prototype counted any
    disagreement, `ROW-ERROR` included, so an engine timeout or a non-JSON
    payload on the mutant side made the suite look as if it had distinguished the
    mutant. Every mutant in the frozen manifests validated (`load_mutants()`
    keeps only `validates: true`), so a `ROW-ERROR` here is evidence about the
    apparatus and the mutant is scored neither way; the run's refusal list and
    the `engine-execution-clean` control gate carry it."""
    for case_id, facts, evidence, expected, readable, _signature in cases:
        if not readable:
            continue
        observed = engines.eval_pack(tools, mutant_path, facts, evidence,
                                     workdir)
        if observed[0] == "ROW-ERROR":
            return REFUSED, {"case": case_id,
                             "got": engines.scope_str(observed)}
        if observed != expected:
            return KILLED, {"case": case_id}
    return SURVIVED, {}


def identity_arm_rego(tools: engines.Toolchain, reference_policy: str,
                      suite_path: str, workdir: str) -> tuple:
    """Section 5's identity control for arms B/C, from the RESULT DOCUMENT.

    `pass` is the control held; `failed` is a real identity failure — the suite
    asserts something the reference does not do. Every other status is the
    apparatus (`engines.TEST_SUITE_STATUSES` is the two that are not) and
    raises, because `opa test` exiting nonzero because it could not compile is
    not a suite that failed to pin its reference down."""
    record = engines.opa_test(tools, reference_policy, suite_path, workdir)
    if record["status"] not in engines.TEST_SUITE_STATUSES:
        raise ExecutionRefusal(
            "E4-IDENTITY-ENGINE-REFUSED `opa test` against the arm's reference "
            "returned %s (exit %s): the identity control cannot be decided and "
            "a suite is not scored zero for an invocation failure"
            % (record["status"], record["exitCode"]))
    return record["status"] == engines.TEST_PASS, record


# --- E6: `ownPolicyIdentity` (M-13, §1.2, §5.1) -----------------------------
#
# TWO RELATIONS, NAMED SEPARATELY, AND ONLY ONE GATES.
#
# `referenceIdentity` above is Study 019's control, unchanged. `ownPolicyIdentity`
# is the SAME suite evaluated against the run's OWN authored policy — one extra
# engine invocation per admitted run — and it is a REPORTED quantity that gates
# nothing. R1's construct statement is conditioned on it: the endpoint measures
# pinning against the SHARED REFERENCE, not against the policy each suite
# accompanies, and this score is what makes that severance visible instead of
# merely disclosed.
#
# **Why it cannot raise where `referenceIdentity` does.** The two relations
# evaluate the same suite against two very different artifacts. The reference is
# FROZEN and certified — the off-gold certificate establishes that it answers
# every point of the registered domain — so a `ROW-ERROR` from it is the
# apparatus and `identity_arm_a()` raises. The run's own policy is neither: a
# `ROW-ERROR` from an authored artifact is an ANSWER about that artifact, and
# raising on it would turn a reported quantity into a control-gate failure and
# would let E6 do exactly the gating §1.2 says it must not do.
#
# What DOES stay apparatus is an invocation that never returned an answer at
# all: §6's `engine-execution-clean` gate "now covers E6's extra invocation
# too", so the record carries `evaluated: false` with the engine's own status
# and the gate reads it.
OWN_POLICY_RELATION = "ownPolicyIdentity"
REFERENCE_RELATION = "referenceIdentity"
IDENTITY_RELATIONS = (REFERENCE_RELATION, OWN_POLICY_RELATION)
# The one that gates, named once, so "which relation is the gate" is a constant
# a test can read rather than a sentence a reader has to trust (§1.2).
GATING_IDENTITY_RELATION = REFERENCE_RELATION


def _own_policy_record(evaluated, passed, failures, note=None) -> dict:
    return {"relation": OWN_POLICY_RELATION, "gates": False,
            "evaluated": bool(evaluated),
            "pass": None if not evaluated else bool(passed),
            "failures": list(failures)[:20],
            "failureCount": len(failures),
            "note": note}


def own_policy_identity_arm_a(tools: engines.Toolchain, pack_path,
                              cases: list, workdir: str) -> dict:
    """E6 for arm A: the authored suite against the run's OWN authored pack."""
    if not pack_path:
        return _own_policy_record(
            False, None, [], "no admitted artifact: E6 has nothing to evaluate")
    failures = []
    for case_id, facts, evidence, expected, readable, _signature in cases:
        if not readable:
            failures.append({"case": case_id, "expected": "<unreadable>",
                             "got": "<not-run>"})
            continue
        observed = engines.eval_pack(tools, pack_path, facts, evidence, workdir)
        if observed != expected:
            failures.append({"case": case_id,
                             "expected": engines.scope_str(expected),
                             "got": engines.scope_str(observed)})
    return _own_policy_record(True, not failures, failures)


def own_policy_identity_arm_rego(tools: engines.Toolchain, policy_path,
                                 suite_path: str, workdir: str) -> dict:
    """E6 for arms B/C: the authored suite against the run's OWN policy."""
    if not policy_path:
        return _own_policy_record(
            False, None, [], "no admitted artifact: E6 has nothing to evaluate")
    record = engines.opa_test(tools, policy_path, suite_path, workdir)
    if record["status"] not in engines.TEST_SUITE_STATUSES:
        return _own_policy_record(
            False, None, [],
            "`opa test` against the run's own policy returned %s (exit %s): the "
            "invocation returned no answer, which §6's engine-execution-clean "
            "gate reads and which E6 records rather than adjudicates"
            % (record["status"], record["exitCode"]))
    passed = record["status"] == engines.TEST_PASS
    return _own_policy_record(True, passed, [] if passed else [record])


def kill_arm_rego(tools: engines.Toolchain, mutant_path: str, suite_path: str,
                  workdir: str) -> tuple:
    """`(outcome, record)` — `killed`/`survived`/`refused`, from the RESULT
    DOCUMENT rather than from the exit status (round-1 R1-8).

    Section 5 registers the kill as "`opa test` nonzero with class recorded",
    and nonzero was the defect: at v1.19.0 a compile failure, a load failure and
    the harness's own timeout are all nonzero, so every one of them killed every
    mutant it touched. An ASSERTION FAILURE is the kill; a test that ERRORED
    never decided; an invocation that never ran the tests is not evidence about
    the suite at all."""
    record = engines.opa_test(tools, mutant_path, suite_path, workdir)
    if record["status"] == engines.TEST_FAILED:
        return KILLED, record
    if record["status"] == engines.TEST_PASS:
        return SURVIVED, record
    return REFUSED, record


# --- the run-level endpoint -------------------------------------------------


def kill_rates(kill_of: dict, mutants: list, paired_ids: set,
               engine_supplied=(), evaluated: bool = True) -> dict:
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
        return sum(1 for record in subset if kill_of.get(record["id"]) == KILLED)
    def refused(subset):
        return [record["id"] for record in subset
                if kill_of.get(record["id"]) == REFUSED]
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
                            if kill_of.get(record["id"]) == SURVIVED],
        # §7 delta 1, and it is the member the collision needed.
        # `survivorVector` carries EVERY paired-adequate mutant with its own
        # token, in the manifest's order, so "nothing evaluated" and "everything
        # killed" are two different documents rather than two readings of one.
        # It is emitted for every admitted run, whatever the run's identity
        # outcome, and `validate_kill_block()` refuses the ambiguous shape at
        # write time.
        #
        # A mutant missing from `kill_of` is `NOT_EVALUATED` and never
        # `SURVIVED`: reading an absent answer as "the suite did not kill it" is
        # the collision one level down, and it is exactly what
        # `kill_rates({}, …)` did in 019.
        "survivorVector": [[record["id"],
                            kill_of.get(record["id"], NOT_EVALUATED)]
                           for record in paired_adequate],
        "notEvaluatedPaired": [record["id"] for record in paired_adequate
                               if record["id"] not in kill_of],
        "evaluatedPaired": sum(1 for record in paired_adequate
                               if record["id"] in kill_of),
        # The one member that says WHICH state an all-empty survivor list is in.
        # `False` means the kill loop never ran for this run at all.
        "killsEvaluated": bool(evaluated),
        # Round-1 R1-8: a mutant the engine refused on is scored NEITHER way.
        # It is not a kill (an apparatus failure is not a suite distinguishing a
        # mutant) and not a survivor (nothing was asked), it stays in the
        # denominator so no refusal can inflate a rate by shrinking it, and the
        # `engine-execution-clean` control gate reads the list.
        "refusedPaired": refused(paired_adequate),
        "refusedAll": refused(mutants),
    }


# §7 delta 1's write-time gate. Every member a kill block must carry for the
# collision to be unrepresentable, named once.
KILL_BLOCK_REQUIRED = ("killedPaired", "paired", "survivorsPaired",
                       "survivorVector", "notEvaluatedPaired",
                       "evaluatedPaired", "killsEvaluated")


def unevaluated_kill_block(mutants: list, paired_ids: set,
                           engine_supplied=(), reason: str = None) -> dict:
    """The kill block of an admitted run whose kill loop NEVER RAN.

    Study 019 wrote three different shapes for this state and all three were
    ambiguous. Two of them were the literal dict `{"killedPaired": 0, "paired":
    n}` — a block with no survivor member and no `caseCount` at all, which is
    the defect §5.2's definition 4 names and which produced exactly six runs (B
    `run-026/027/032/036`, C `run-035/050`; arm A zero) carrying a `kill` block
    with neither. The third was `kill_rates({}, …)`, whose empty `survivorsPaired`
    reads as a perfect score.

    There is one shape now, it is the SAME shape a scored run gets, and every
    paired-adequate mutant in it carries `NOT_EVALUATED`. `reason` travels with
    it so a reader of one run's record can see WHY nothing was evaluated without
    joining it to another member."""
    block = kill_rates({}, mutants, paired_ids, engine_supplied,
                       evaluated=False)
    block["notEvaluatedReason"] = reason
    return block


def validate_kill_block(block: dict, where: str = "a kill block") -> dict:
    """REFUSE the token collision at write time (§5.2, §7 delta 1).

    Four refusals, and the second is the registered one:

    1. a member of `KILL_BLOCK_REQUIRED` is absent — a partial block is what
       019's six `caseCount`-less runs had, and a reader cannot tell a missing
       member from a measured zero;
    2. **`survivorsPaired == []` with `killedPaired == 0` over a non-empty
       paired denominator and nothing recorded as not-evaluated** — the exact
       shape §5.2 registers as refused rather than read as 33/33;
    3. the per-mutant census does not add up to `paired` — a vector that has
       lost a mutant is a coverage set computed over the wrong denominator;
    4. `killsEvaluated` disagrees with the vector — a block claiming the loop
       ran while carrying `NOT_EVALUATED` tokens, or claiming it did not while
       carrying answers.

    Returns the block, so a caller can write `run["kill"] =
    validate_kill_block(...)` and cannot forget to check."""
    missing = [name for name in KILL_BLOCK_REQUIRED if name not in block]
    if missing:
        raise E4Error(
            "E4-KILL-BLOCK-INCOMPLETE %s is missing %s: §7's delta 1 requires "
            "an explicit per-mutant survivor vector for EVERY admitted run, and "
            "a block a reader has to interpret is the defect it repairs"
            % (where, ", ".join(missing)))
    paired = block["paired"]
    vector = block["survivorVector"]
    if len(vector) != paired:
        raise E4Error(
            "E4-KILL-VECTOR-SHORT %s carries %d per-mutant tokens over a paired "
            "adequate denominator of %d: the vector IS the denominator"
            % (where, len(vector), paired))
    tokens = [token for _identifier, token in vector]
    unknown = sorted(set(tokens) - set(MUTANT_OUTCOMES))
    if unknown:
        raise E4Error(
            "E4-KILL-VECTOR-TOKEN %s carries the outcome token(s) %s, and the "
            "registered set is %s" % (where, ", ".join(unknown),
                                      ", ".join(MUTANT_OUTCOMES)))
    not_evaluated = tokens.count(NOT_EVALUATED)
    if tokens.count(KILLED) != block["killedPaired"]:
        raise E4Error(
            "E4-KILL-VECTOR-DISAGREES %s reports %d paired kills and its vector "
            "carries %d: the count and the vector are one measurement"
            % (where, block["killedPaired"], tokens.count(KILLED)))
    if tokens.count(SURVIVED) != len(block["survivorsPaired"]):
        raise E4Error(
            "E4-KILL-VECTOR-DISAGREES %s lists %d survivors and its vector "
            "carries %d" % (where, len(block["survivorsPaired"]),
                            tokens.count(SURVIVED)))
    if not_evaluated != len(block["notEvaluatedPaired"]):
        raise E4Error(
            "E4-KILL-VECTOR-DISAGREES %s lists %d not-evaluated mutants and its "
            "vector carries %d" % (where, len(block["notEvaluatedPaired"]),
                                   not_evaluated))
    if block["evaluatedPaired"] + not_evaluated != paired:
        raise E4Error(
            "E4-KILL-CENSUS %s says %d of %d paired mutants were evaluated and "
            "%d were not: the two must partition the denominator"
            % (where, block["evaluatedPaired"], paired, not_evaluated))
    if block["killsEvaluated"] and not_evaluated:
        raise E4Error(
            "E4-KILL-EVALUATED-CONTRADICTION %s claims the kill loop ran and "
            "carries %d not-evaluated mutant(s)" % (where, not_evaluated))
    if not block["killsEvaluated"] and block["evaluatedPaired"]:
        raise E4Error(
            "E4-KILL-EVALUATED-CONTRADICTION %s claims the kill loop did not "
            "run and carries %d evaluated mutant(s)"
            % (where, block["evaluatedPaired"]))
    if (paired and not block["survivorsPaired"] and not block["killedPaired"]
            and not block["notEvaluatedPaired"]):
        raise E4Error(
            "E4-KILL-VECTOR-AMBIGUOUS %s has no survivors, no kills and nothing "
            "recorded as not-evaluated over %d paired adequate mutants: "
            "\"nothing evaluated\" and \"everything killed\" would be the same "
            "document, which §5.2 registers as refused at write time rather "
            "than read as a perfect score" % (where, paired))
    return block


def is_high_kill(killed_paired: int, paired: int, cut: int) -> bool:
    """Section 5's high-kill predicate, at the INTEGER cut.

    Stated as an integer comparison and not as `rate >= 0.95`, because at
    paired = 65 the rate 61/65 is 0.9384… and 62/65 is 0.9538… — the float
    comparison and the integer cut agree there, and the point of deriving the
    cut is that whether they agree is checkable rather than hoped for.

    `paired` IS READ (round-1 R1-1). It was an ignored argument, which is how one
    cut derived from the JPS denominator came to be applied to a Rego run whose
    denominator was smaller: a cut above the denominator makes the predicate
    unsatisfiable, so a PERFECT suite would have been not-high-kill and the
    primary endpoint would have been impossible for two of the three arms. A cut
    that cannot be reached is refused here rather than silently returning
    False."""
    if cut > paired:
        raise E4Error(
            "E4-CUT-UNREACHABLE the high-kill cut is %d and this run's paired "
            "adequate denominator is %d: no suite could ever be high-kill, so "
            "the endpoint is not computed from a cut that does not belong to "
            "this arm's language" % (cut, paired))
    return killed_paired >= cut


def high_kill_cut(paired: int) -> dict:
    """The cut at ONE paired-mutant count, with the arithmetic that produced it.

    Section 5 registers that "the operative integer cut at the frozen paired-
    mutant count is stated"; the scorer prints this block per language."""
    cut = stats.tau_cut(paired)
    if cut > paired:
        raise E4Error(
            "E4-CUT-UNREACHABLE tau = %s over %d paired adequate mutants gives "
            "the cut %d, which exceeds the denominator: no suite could ever be "
            "high-kill" % (stats.TAU, paired, cut))
    return {"tau": str(stats.TAU), "pairedAdequateMutants": paired,
            "integerCut": cut,
            "cutRate": float(Fraction(cut, paired)),
            "cutReachable": cut <= paired,
            "statement": "a run is high-kill iff it kills at least %d of the %d "
                         "paired adequate mutants (tau = %s)"
                         % (cut, paired, stats.TAU)}


def high_kill_cuts(paired_ids: dict) -> dict:
    """The cut PER LANGUAGE, each from its own paired-adequate denominator.

    ROUND-1 FINDING R1-1, and it was a blocker for the reason the reviewer
    states: the scorer derived ONE cut from the JPS count and passed it to every
    arm while each arm's kill denominator stayed language-specific, so a perfect
    Rego suite could not reach a cut computed over the (larger) JPS subset and
    the primary endpoint was impossible for arms B and C. The cut belongs to a
    LANGUAGE, and this returns one per language with the denominator it came
    from beside it, each asserted reachable.

    `harness/score.py` selects by `LANGUAGE_OF_ARM` and publishes both."""
    cuts = {}
    for language in ("jps", "rego"):
        cuts[language] = high_kill_cut(len(paired_ids[language]))
        cuts[language]["language"] = language
    return cuts
