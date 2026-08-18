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


MATRIX_VERSION = 2


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
             "matrixVersion is %r and this study registers %d"
             % (version, MATRIX_VERSION))
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
    this excludes nothing today and the per-run excluded count §4 requires is
    published as the zero it is — which is a measured fact about the repaired
    reference rather than a filter nobody applied."""
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


KILLED = "killed"
SURVIVED = "survived"
REFUSED = "refused"

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
    the points are recovered by EVALUATING the suite's own package with the
    pinned binary. Both readings are the pinned toolchain's; neither is a
    re-implementation of Rego and neither is a guess.

    A file the pinned parser refuses, or a suite whose input points cannot be
    read either way, is a `MatrixError` — the registered authoring outcome — and
    never a silent pass."""
    code, raw = engines.opa_parse(tools, suite_path, workdir)
    if code != 0:
        raise MatrixError(
            "E4-MATRIX-SCHEMA the pinned parser refuses the suite file "
            "(`opa parse` exit %d), so its cases cannot be enumerated and its "
            "input points cannot be validated against the registered domain"
            % code)
    try:
        document = domain.parse_tree(raw)
        indirect, cases = domain.cases_from_tree(document)
        if indirect:
            # The table-driven mode. Evaluate the suite's own package with the
            # pinned binary: that resolves the named constants and helper
            # functions real suites build their input points out of, and gives
            # both a NAME MAP for the syntactic scan (a table written inside a
            # rule body never reaches the package document) and a set of
            # resolved points (a table written AS a rule does).
            data_paths = [suite_path] + ([policy_path] if policy_path else [])
            eval_code, eval_raw = engines.opa_eval_document(
                tools, data_paths, domain.package_path(document), workdir)
            if eval_code == 0:
                resolved = domain.package_document(eval_raw)
                names = resolved if isinstance(resolved, dict) else None
                _indirect, cases = domain.cases_from_tree(document, names)
                seen = {domain.canonical(signature)
                        for _index, signature in cases}
                merged = list(cases)
                for _index, signature in domain.resolved_input_points(eval_raw):
                    key = domain.canonical(signature)
                    if key not in seen:
                        seen.add(key)
                        merged.append((len(merged), signature))
                cases = merged
    except domain.DomainError as error:
        raise MatrixError("E4-MATRIX-SCHEMA %s" % error)
    except ValueError as error:
        raise MatrixError("E4-MATRIX-SCHEMA the resolved suite document is not "
                          "readable JSON (%s)" % type(error).__name__)
    if indirect and not cases:
        raise MatrixError(
            "E4-MATRIX-SCHEMA %d `with input as` term(s) name an input point "
            "rather than carrying one, and neither the suite's syntax tree nor "
            "its resolved document holds one: its case inputs cannot be "
            "validated against the registered domain" % indirect)
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
        # Round-1 R1-8: a mutant the engine refused on is scored NEITHER way.
        # It is not a kill (an apparatus failure is not a suite distinguishing a
        # mutant) and not a survivor (nothing was asked), it stays in the
        # denominator so no refusal can inflate a rate by shrinking it, and the
        # `engine-execution-clean` control gate reads the list.
        "refusedPaired": refused(paired_adequate),
        "refusedAll": refused(mutants),
    }


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
