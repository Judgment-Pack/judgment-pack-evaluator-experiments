"""The scorer — the only thing that publishes an attempt.

    <the CPython PINS.json pins> harness/score.py --attempt-root results/primary-attempt-001

PREREGISTRATION.md "The freeze and the primary attempt": the first invocation of
that command from the freeze commit is the primary attempt, crash and all. This
module never makes a model call. It consumes a batch directory that
`harness/batch.py` produced and publishes exactly one attempt from it.

ASSEMBLED, not written fresh. Every part is a design prototype that has been run
against the real engines, ported with a two-sided `harness/PORTS.md` row:

    e4lib/stats.py     Study 012 harness/score_rates.py
                       f4d4463f081439f147a341bb38d8a6b709b3860f73f6f4e524234a180ec23336
                       + design/mutants/oc_table.py
                       4707e50cee46a1a922f4202911efbfae311c6a20ddae0c96d1d0846c549cd131
    e4lib/extract.py   design/pilot/pilot_run.py
    e4lib/admit.py     09da06b334f6b3ae3224b03f6e49e2f0f3c5519401e94e72f23df7333cffd295
    e4lib/engines.py   (the same, plus design/gold/check_gold.py
                       a3aa62ea51491f370f4423f4945b79aa9bae06d03dd60489b9c8952ec6e9294b)
    e4lib/e4.py        design/mutants/e4_score.py
                       beb42b3903284dc2c33baff33000325814a1e53171d8268ca4d56820e4f995fb
    e4lib/census.py    Study 012 harness/census.py
                       911eb25773923789e5ddeae20f0bfa68032f932ae9c62fd7e9a21ad8aa8b73ea
    e4lib/decision.py  the 015-018 program shape, generalised to a table

THE REGIME (inherited from Studies 014-018, and each clause is enforced here)
-----------------------------------------------------------------------------
* `ATTEMPT.json` is written BEFORE `harness/PINS.json` is parsed, under every
  flag combination, and carries `pinsRawSha256` — the digest of the RAW registry
  bytes, computed before the parse, over the exact bytes that are then parsed
  (Study 016's round-1 R1-12 and its round-2 residual: one read, no
  hash/parse divergence window). Even an attempt that dies on a malformed
  registry leaves a record tied to the registry bytes it saw.
* Every later failure path persists a terminal pipeline-invalid `RESULTS.json`.
  `SystemExit`, `KeyboardInterrupt` and every other `BaseException` are
  RECORDED and then re-raised.
* The label is `integrity.study_label()`'s and is computed nowhere else:
  `REGISTERED` iff every freeze pin is non-null, `PILOT` otherwise, and it is
  stamped into every output. A PILOT supports no claim.
* The attempt root must not already exist. The scorer refuses rather than
  overwriting, because "the first invocation is the primary attempt" is only
  true if a second invocation cannot look like the first.
* TERMINALITY: a batch that did not complete is DECLARED, not scored. Exactly
  the registered 150 slots XOR a `SHORTFALL.json` whose prefix is the slots
  present; both or neither refuses (Study 012's section 2.8, ported).
* No output embeds a timestamp or an absolute path, so scoring the same batch
  twice is byte-identical. `tests/test_score.py` scores a fixture twice and
  diffs.
* `--include-reviewer-set` is refused mechanically while any pin is null
  (`harness/PINS.json`'s own rule).

WHAT IS NOT FINISHED, BY NAME (harness/SCAFFOLD.md; none of it fails silently)
------------------------------------------------------------------------------
`stats.interval_endpoints()` refuses with `FM-ENDPOINTS-UNPORTED` — the
zero-exclusion DECISION is exact and complete, the reported endpoints need the
Delta0 sweep. `census.registered_stimulus()` refuses with
`E5-STIMULUS-UNREGISTERED`. `e4.engine_supplied_ids()` refuses with
`E4-ENGINE-SUPPLIED-UNREGISTERED` until the mutant manifests carry the marking
as a member. Each refusal is caught at exactly one place below, published as a
named refusal in the R2 section, and never converted into a number.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile

# The ceremony's commands run with bytecode writing disabled (Study 012 section
# 2.10, carried through batch.py): set structurally, before anything imports.
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import batch          # noqa: E402  (this study's, imported the way the ceremony runs it)
import integrity      # noqa: E402
from e4lib import census as census_lib   # noqa: E402
from e4lib import decision               # noqa: E402
from e4lib import e4 as e4lib            # noqa: E402
from e4lib import engines                # noqa: E402
from e4lib import extract                # noqa: E402
from e4lib import stats                  # noqa: E402
from e4lib import admit as admit_lib     # noqa: E402

PINS_PATH = os.path.join(HERE, "PINS.json")
# Read from the driver rather than spelled again: the file whose presence makes
# a short batch terminal must have ONE name in the study, and a second copy of
# a string is a second chance for the driver to declare a shortfall the scorer
# never looks for. An `AttributeError` here is the loud failure that a renamed
# constant deserves.
SHORTFALL_FILE = batch.SHORTFALL_NAME

STUDY_NAME = "019-authorship-across-representations"

# Section 1a's partition, reached through `batch.py` so there is ONE copy of it
# in the study. `tests/test_partition.py`'s last test — written skipping since
# the scaffold, live the moment this module lands — asserts this equals
# `batch.CODE_PARTITION`'s keys.
ADMISSION_CODES = tuple(sorted(batch.CODE_PARTITION))
APPARATUS_SIDE = frozenset(code for code, (side, _phrase)
                           in batch.CODE_PARTITION.items() if side == "apparatus")
AUTHORING_SIDE = frozenset(code for code, (side, _phrase)
                           in batch.CODE_PARTITION.items() if side == "authoring")

# Section 5's registered E1 floor and section 2's registered timeout cap. Both
# are control-gate rows: breaching either adjudicates R1 in NEITHER direction.
E1_FLOOR = 0.60
TIMEOUT_RATE_CAP_PIN = ("batch", "timeoutRateCap")

# The frozen artifacts the scorer reads. Study-relative, never absolute: an
# absolute path in a published record is a path that cannot be reproduced.
GOLD_RELATIVE = "gold/GOLD.json"
MUTANT_JPS_RELATIVE = "mutants/MANIFEST-jps.json"
MUTANT_REGO_RELATIVE = "mutants/MANIFEST-rego.json"
MUTANT_JPS_DIR = "mutants/jps"
MUTANT_REGO_DIR = "mutants/rego"
REFERENCE_A_RELATIVE = "reference/refA/pack.json"
REFERENCE_B_RELATIVE = "reference/refB/policy.rego"


class ScoreError(Exception):
    """A population-level refusal: the scoring itself cannot be trusted, as
    distinct from a single run being invalid."""


# --------------------------------------------------------------------------
# bytes in, bytes out
# --------------------------------------------------------------------------

def sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _refuse_duplicate_keys(pairs):
    keys = [key for key, _value in pairs]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate object keys")
    return dict(pairs)


def load_json(path: str):
    """Duplicate-key-rejecting JSON: a shadowed member cannot mean one thing to
    this scorer and another to a reader."""
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"),
                          object_pairs_hook=_refuse_duplicate_keys)


# The absolute roots this process knows about, longest first, with the token
# each is published as. Sorting matters: the study tree lives under the
# temporary directory in a worktree, and a shorter prefix replaced first would
# leave the rest of the longer one behind.
_SCRUB_ROOTS = tuple(sorted(
    ((STUDY, "<study>"),
     (os.path.dirname(STUDY), "<studies>"),
     (os.path.dirname(os.path.dirname(STUDY)), "<repo>"),
     (tempfile.gettempdir(), "<tmp>")),
    key=lambda pair: -len(pair[0])))


def scrub(text: str) -> str:
    """Replace every absolute root this process knows about with a stable token.

    "Its outputs embed no timestamp and no absolute path" (PREREGISTRATION.md,
    "The freeze and the primary attempt") is a property of the BYTES, and the
    strings that most want to carry a path are the refusals — a digest mismatch
    naming the file it resolved, an integrity error naming the tree it walked.
    Scrubbing at the writer rather than at each message means a refusal added
    later cannot reintroduce the leak, and the tokens keep the message
    diagnosable."""
    replaced = str(text)
    for root, token in _SCRUB_ROOTS:
        if root:
            replaced = replaced.replace(root, token)
    return replaced


def scrub_document(value):
    """`scrub()` over every string in a document, recursively."""
    if isinstance(value, str):
        return scrub(value)
    if isinstance(value, dict):
        return {key: scrub_document(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [scrub_document(item) for item in value]
    return value


def write_json(path: str, document) -> None:
    """One writer, one encoding, sorted keys, trailing newline, scrubbed.

    Sorted keys are not cosmetic: byte-identical rescoring is a registered
    property and a dict iteration order is not a property of the data."""
    body = json.dumps(scrub_document(document), indent=2, sort_keys=True) + "\n"
    with open(path, "wb") as handle:
        handle.write(body.encode("utf-8"))


def write_text(path: str, body: str) -> None:
    with open(path, "wb") as handle:
        handle.write(scrub(body).encode("utf-8"))


def relative(path: str) -> str:
    """A study-relative POSIX path for publication. No output of this scorer
    embeds an absolute path."""
    return os.path.relpath(path, STUDY).replace(os.sep, "/")


# --------------------------------------------------------------------------
# the batch on disk
# --------------------------------------------------------------------------

def read_slot(entry: dict, arms_root: str) -> dict:
    """One registered slot, read into the record the population rule works on.

    A slot is TERMINAL when it carries `CALL.json` (the success path) or
    `REFUSAL.json` (the wrapper's pre-call refusal path). One that carries
    neither was started and never finished, and no section 1a code describes it
    honestly — that is a population-level refusal, not a per-run code."""
    path = os.path.join(arms_root, entry["arm"], "authoring",
                        "run-%03d" % entry["slotIndex"])
    record = {"arm": entry["arm"], "slotIndex": entry["slotIndex"],
              "globalIndex": entry["globalIndex"], "round": entry["round"],
              "position": entry["position"], "present": os.path.isdir(path),
              "code": None, "durationSeconds": None, "completion": None}
    if not record["present"]:
        return record
    call_path = os.path.join(path, "CALL.json")
    refusal_path = os.path.join(path, "REFUSAL.json")
    if os.path.isfile(refusal_path):
        record["code"] = "slot-shape"
        return record
    if not os.path.isfile(call_path):
        raise ScoreError(
            "arm %s's run-%03d carries neither CALL.json nor REFUSAL.json: it is "
            "not a terminal slot, and no rate is computed over a population "
            "holding one" % (entry["arm"], entry["slotIndex"]))
    call = load_json(call_path)
    record["durationSeconds"] = call.get("durationSeconds")
    status = call.get("exitCode")
    if call.get("timedOut") or status == 12:
        record["code"] = "call-timeout"
        return record
    if status not in (0, None):
        meaning = batch.WRAPPER_EXIT_MEANINGS.get(status)
        record["code"] = meaning[0] if meaning else "call-nonzero-exit"
        if record["code"] in ("complete", "preflight-refused"):
            record["code"] = "call-nonzero-exit"
        return record
    completion_path = os.path.join(path, "completion.txt")
    if not os.path.isfile(completion_path):
        record["code"] = "slot-shape"
        return record
    with open(completion_path, "rb") as handle:
        record["completion"] = handle.read().decode("utf-8", "replace")
    return record


def terminality(slots: list, arms_root: str) -> dict:
    """Study 012's section 2.8 rule, ported: exactly the registered number of
    slots XOR a shortfall declaration whose prefix is the slots present.

    Both, or neither, refuses — a shortfall over a full batch is not a short
    batch, and an over-full batch is not a population this study contemplates.
    A declaration that cannot be read declares nothing and refuses the whole
    scoring."""
    path = os.path.join(arms_root, SHORTFALL_FILE)
    try:
        shortfall = load_json(path) if os.path.isfile(path) else None
    except (ValueError, OSError) as error:
        raise ScoreError(
            "%s cannot be read as duplicate-free JSON (%s): the declaration is "
            "what makes a short batch terminal, and one that cannot be read "
            "declares nothing" % (relative(path), error))
    if shortfall is not None and not isinstance(shortfall, dict):
        raise ScoreError(
            "%s is not a declaration object: a declaration with no members to "
            "compare is not a declaration" % relative(path))
    present = sum(1 for slot in slots if slot["present"])
    complete = present == batch.REGISTERED_SLOTS
    if complete and shortfall is not None:
        raise ScoreError(
            "all %d registered slots are present and %s also declares a short "
            "batch: the batch cannot be both"
            % (batch.REGISTERED_SLOTS, SHORTFALL_FILE))
    if not complete and shortfall is None:
        raise ScoreError(
            "%d of %d registered slots are present and no %s declares why: the "
            "batch is not terminal"
            % (present, batch.REGISTERED_SLOTS, SHORTFALL_FILE))
    return {"present": present, "registered": batch.REGISTERED_SLOTS,
            "complete": complete, "declared": shortfall is not None}


# --------------------------------------------------------------------------
# the population (section 1a)
# --------------------------------------------------------------------------

def population(slots: list) -> dict:
    """Section 1a's rule, in code.

    The denominator of every per-arm rate is attempted runs whose APPARATUS
    succeeded. Apparatus failures are pipeline-invalid, excluded, and reported
    with their own rate and interval. Every failure attributable to what the
    author emitted is an authoring outcome: valid, COUNTED, and scoring zero on
    every endpoint it reaches. Section 1a records why this is in reviewed code
    rather than in the driver: the design-phase pilot driver mis-filed timeouts
    as an authoring code, which silently moves a run out of the excluded set and
    into the denominator of every rate."""
    per_arm = {}
    for arm in batch.ARMS:
        arm_slots = [slot for slot in slots if slot["arm"] == arm]
        apparatus = [slot for slot in arm_slots
                     if slot["code"] in APPARATUS_SIDE]
        admitted = [slot for slot in arm_slots
                    if slot["code"] not in APPARATUS_SIDE]
        timeouts = [slot for slot in arm_slots if slot["code"] == "call-timeout"]
        per_arm[arm] = {
            "attempted": len(arm_slots),
            "apparatusExcluded": len(apparatus),
            "denominator": len(admitted),
            "apparatusCodes": _code_counts(apparatus),
            "timeouts": len(timeouts),
            "timeoutRate": stats.rate_block(len(timeouts), len(arm_slots),
                                            "attempted runs"),
            "apparatusRate": stats.rate_block(len(apparatus), len(arm_slots),
                                              "attempted runs"),
            "slots": admitted,
        }
    return per_arm


def _code_counts(slots: list) -> dict:
    counts = {}
    for slot in slots:
        if slot["code"] is not None:
            counts[slot["code"]] = counts.get(slot["code"], 0) + 1
    return counts


# --------------------------------------------------------------------------
# the endpoints
# --------------------------------------------------------------------------

def e2_profile(arm: str, admitted: list) -> dict:
    """E2 — the authoring-validity profile, as the ORDERED code table section 1a
    registers, with the apparatus codes separated. Headline, not footnote
    (section 5)."""
    counts = _code_counts(admitted)
    ordered = [{"code": code, "side": batch.CODE_PARTITION[code][0],
                "phrase": batch.CODE_PARTITION[code][1],
                "count": counts.get(code, 0)}
               for code in admit_lib.DROP_ORDER]
    clean = sum(1 for slot in admitted if slot["code"] is None)
    return {"arm": arm, "denominator": len(admitted), "admitted": clean,
            "orderedCodes": ordered,
            "admittedRate": stats.rate_block(clean, len(admitted),
                                             "admitted runs (section 1a)")}


def e1_control(arm: str, runs: list) -> dict:
    """E1 — per-run perfect gold agreement on the policy artifact, ITT
    denominator.

    Section 5 expects this at ceiling in every arm and registers the CEILING
    ITSELF as a finding this study commits to publishing. A per-arm rate below
    the registered floor is a control-gate row, not a detection: it would mean
    the stimulus regressed, not that testing skill differs."""
    perfect = sum(1 for run in runs if run.get("goldPerfect"))
    block = stats.rate_block(perfect, len(runs), "admitted runs (ITT)")
    return {"arm": arm, "perfect": perfect, "runs": len(runs),
            "rate": block,
            "floor": E1_FLOOR,
            "floorHeld": len(runs) == 0 or (perfect / len(runs)) >= E1_FLOOR}


def e3_taxonomy(runs: list) -> dict:
    """E3 — the row-level failure taxonomy over E1 failures and identity
    failures.

    Categories are counted WITHIN ARM (section 5: "arm-structural categories
    within-arm-only, enforced in the scorer"), which is why this is called per
    arm and never over the pooled runs."""
    gold_failures, identity_failures = {}, {}
    for run in runs:
        for failure in run.get("goldFailures") or []:
            key = failure.get("category", "uncategorised")
            gold_failures[key] = gold_failures.get(key, 0) + 1
        for failure in run.get("identityFailures") or []:
            key = failure.get("got", "uncategorised")
            identity_failures[key] = identity_failures.get(key, 0) + 1
    return {"goldFailureCategories": gold_failures,
            "identityFailureCategories": identity_failures}


def e4_endpoint(arm: str, runs: list, cut: dict) -> dict:
    """E4 — the per-arm HIGH-KILL RUN RATE, the primary endpoint.

    Section 5's denominator rule, in code and stated in the record: "Runs
    carrying authoring-outcome codes remain in the E4 denominator as
    not-high-kill (no-marker included); only apparatus codes leave it, and
    identity-control exclusions are reported, never silently dropped."

    The identity control is a first-class per-arm RATE, and identity-excluded
    runs are reported. They leave the high-kill numerator by not being
    high-kill, and they stay in the denominator: an identity-failing suite is a
    suite that did not pin the reference down, which is an authoring outcome and
    not an apparatus failure."""
    identity_pass = [run for run in runs if run.get("identityPass")]
    identity_fail = [run for run in runs if run.get("admitted")
                     and not run.get("identityPass")]
    high = [run for run in runs
            if run.get("identityPass")
            and e4lib.is_high_kill(run["kill"]["killedPaired"],
                                   run["kill"]["paired"], cut["integerCut"])]
    excluded_cases = sum(len(run.get("x1Excluded") or []) for run in runs)
    return {
        "arm": arm,
        "denominator": len(runs),
        "highKill": len(high),
        "highKillRate": stats.rate_block(
            len(high), len(runs),
            "admitted runs (section 1a; authoring outcomes retained as "
            "not-high-kill)"),
        "identityPass": len(identity_pass),
        "identityFail": len(identity_fail),
        "identityRate": stats.rate_block(len(identity_pass), len(runs),
                                         "admitted runs"),
        "identityFailedRuns": sorted(run["run"] for run in identity_fail),
        "x1ExcludedCases": excluded_cases,
        "cut": cut,
        "highKillRuns": sorted(run["run"] for run in high),
    }


def contrast(left_arm: str, right_arm: str, e4_by_arm: dict) -> dict:
    """One registered contrast, on Reading 1 of the FM construction.

    Refuses on unequal denominators rather than approximating: the equal-N
    closed form is what `stats.z2_table()` implements, and a contrast computed
    at two different N with a formula for one N is a number nobody registered
    (`harness/SCAFFOLD.md` item S8)."""
    left, right = e4_by_arm[left_arm], e4_by_arm[right_arm]
    if left["denominator"] != right["denominator"]:
        raise stats.StatsError(
            "FM-UNEQUAL-N arm %s admitted %d runs and arm %s admitted %d; the "
            "registered contrast's closed form is the equal-size one and this "
            "attempt has no registered unequal-N inversion "
            "(harness/SCAFFOLD.md item S8)"
            % (left_arm, left["denominator"], right_arm, right["denominator"]))
    result = stats.excludes_zero(left["highKill"], right["highKill"],
                                 left["denominator"])
    result["arms"] = [left_arm, right_arm]
    return result


# --------------------------------------------------------------------------
# scoring one run
# --------------------------------------------------------------------------

def score_run(tools, arm: str, slot: dict, context: dict, workdir: str) -> dict:
    """Extract, admit, evaluate — one slot, in the registered order.

    Never crashes the scoring: a row that makes an engine refuse is a ROW-ERROR
    with its class recorded, and an exception inside one run's evaluation is
    that run's problem and not the population's."""
    run = {"run": "run-%03d" % slot["slotIndex"], "arm": arm,
           "code": slot["code"], "admitted": False, "goldPerfect": False,
           "identityPass": False, "durationSeconds": slot["durationSeconds"]}
    if slot["code"] is not None:
        return run
    pair = extract.extract_pair(slot["completion"] or "", arm)
    run["policyBytes"] = pair["policyBytes"]
    run["suiteBytes"] = pair["suiteBytes"]
    run["suitePresent"] = pair["suite"] is not None
    artifact, code, detail = admit_lib.admit(tools, arm, pair["policy"], workdir)
    run["admissionDetail"] = detail
    if code is not None:
        run["code"] = code
        return run
    run["admitted"] = True

    # E1: the policy artifact against every gold row.
    failures = []
    for row in context["gold"]:
        want = (("unresolved", None, tuple(sorted(row["expect"]["reasons"])))
                if row["expect"]["disposition"] == "unresolved"
                else ("outcome", row["expect"]["disposition"], ()))
        if arm == "A":
            facts, evidence = engines.facts_documents(row["inputs"])
            got = engines.eval_pack(tools, artifact, facts, evidence, workdir)
        else:
            got = engines.eval_rego(tools, artifact, row["inputs"], workdir)
        if got != want:
            failures.append({"id": row["id"], "cite": row.get("cite", []),
                             "category": got[0] if got[0] == "ROW-ERROR"
                             else "disagreement",
                             "expected": engines.scope_str(want),
                             "got": engines.scope_str(got)})
    run["goldFailures"] = failures
    run["goldPerfect"] = not failures

    # E4: the identity control, then the kill vector, over the X1-filtered
    # case set. The suite is the SECONDARY artifact; a run that emitted no
    # suite pins nothing and is not-high-kill, which section 5 makes an
    # authoring outcome rather than an exclusion.
    if pair["suite"] is None:
        run["code"] = "no-marker-block"
        run["kill"] = {"killedPaired": 0, "paired": context["pairedCount"]}
        return run
    suite_path = os.path.join(workdir, "suite.%s" % pair["suiteLanguage"])
    with open(suite_path, "w", encoding="utf-8") as handle:
        handle.write(pair["suite"])
    if arm == "A":
        try:
            cases, note = e4lib.load_matrix(suite_path)
        except ValueError:
            run["code"] = "unparseable-artifact"
            run["kill"] = {"killedPaired": 0, "paired": context["pairedCount"]}
            return run
        run.update(note)
        scored_cases, excluded = e4lib.partition_x1(cases)
        run["x1Excluded"] = excluded
        ok, identity_failures = e4lib.identity_arm_a(
            tools, context["referenceA"], scored_cases, workdir)
        run["identityPass"] = ok
        run["identityFailures"] = identity_failures[:20]
        run["identityFailureCount"] = len(identity_failures)
        kill_of = {}
        if ok:
            for mutant in context["mutants"]["jps"]:
                killed, case_id = e4lib.kill_arm_a(tools, mutant["path"],
                                                  scored_cases, workdir)
                kill_of[mutant["id"]] = killed
                if killed:
                    run.setdefault("killingCase", {})[mutant["id"]] = case_id
        run["kill"] = e4lib.kill_rates(kill_of, context["mutants"]["jps"],
                                       context["pairedIds"]["jps"])
    else:
        run["x1Excluded"] = []
        ok, detail = e4lib.identity_arm_rego(tools, context["referenceB"],
                                             suite_path, workdir)
        run["identityPass"] = ok
        run["identityFailures"] = [] if ok else [detail]
        run["identityFailureCount"] = 0 if ok else 1
        kill_of = {}
        if ok:
            for mutant in context["mutants"]["rego"]:
                killed, _detail = e4lib.kill_arm_rego(tools, mutant["path"],
                                                     suite_path, workdir)
                kill_of[mutant["id"]] = killed
        run["kill"] = e4lib.kill_rates(kill_of, context["mutants"]["rego"],
                                       context["pairedIds"]["rego"])
    return run


# --------------------------------------------------------------------------
# the report
# --------------------------------------------------------------------------

def results_markdown(results: dict) -> str:
    """The published table. Every rate with its denominator, every count that
    section 10 commits to, and the verdict last."""
    lines = ["# Study 019 — %s" % results["label"], "",
             "R1: %s" % results["decision"]["verdict"], ""]
    if results["label"] == "PILOT":
        lines += ["**PILOT — every freeze pin below is null and this attempt "
                  "supports no claim.** Unfilled: %s."
                  % ", ".join(results["unfilledPins"]), ""]
    lines += ["## Decision", "",
              "| Row | Registered text | Matched |", "|---|---|---|"]
    for index, row in enumerate(decision.ROWS, 1):
        matched = "**yes**" if results["decision"]["rowIndex"] == index else "no"
        lines.append("| %d %s | %s | %s |"
                     % (index, row.name, row.registered, matched))
    if results["decision"].get("causes"):
        lines += ["", "Causes: " + ", ".join(results["decision"]["causes"])]
    lines += ["", "## E4 — high-kill run rate (primary)", "",
              "| Arm | High-kill | Denominator | Rate | 95% CI | Identity pass | X1-excluded cases |",
              "|---|---|---|---|---|---|---|"]
    for arm in batch.ARMS:
        entry = (results.get("e4") or {}).get(arm)
        if entry is None:
            lines.append("| %s | — | — | — | — | — | — |" % arm)
            continue
        block = entry["highKillRate"]
        lines.append("| %s | %d | %d | %s | %s | %d | %d |"
                     % (arm, entry["highKill"], entry["denominator"],
                        _fmt(block["rate"]), _fmt_ci(block["ci95"]),
                        entry["identityPass"], entry["x1ExcludedCases"]))
    lines += ["", "## E1 — gold agreement (control, expected at ceiling)", "",
              "| Arm | Perfect | Runs | Rate | Floor held |", "|---|---|---|---|---|"]
    for arm in batch.ARMS:
        entry = (results.get("e1") or {}).get(arm)
        if entry is None:
            lines.append("| %s | — | — | — | — |" % arm)
            continue
        lines.append("| %s | %d | %d | %s | %s |"
                     % (arm, entry["perfect"], entry["runs"],
                        _fmt(entry["rate"]["rate"]),
                        "yes" if entry["floorHeld"] else "**no**"))
    lines += ["", "## E2 — authoring-validity profile", "",
              "| Arm | Code | Side | Count |", "|---|---|---|---|"]
    for arm in batch.ARMS:
        entry = (results.get("e2") or {}).get(arm)
        if entry is None:
            continue
        for row in entry["orderedCodes"]:
            lines.append("| %s | %s | %s | %d |"
                         % (arm, row["code"], row["side"], row["count"]))
    lines += ["", "## R2 — refusals published rather than estimated", ""]
    for name, refusal in sorted((results.get("refusals") or {}).items()):
        lines.append("- **%s** — %s" % (name, refusal))
    return "\n".join(lines) + "\n"


def _fmt(value):
    return "—" if value is None else "%.4f" % value


def _fmt_ci(bounds):
    return "—" if bounds is None else "[%.4f, %.4f]" % (bounds[0], bounds[1])


# --------------------------------------------------------------------------
# the attempt
# --------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--batch-root", default=os.path.join(STUDY, "arms"),
                        help="the batch directory to consume; the registered "
                             "default is this study's arms/ tree")
    parser.add_argument("--include-reviewer-set", action="store_true")
    arguments = parser.parse_args(argv)

    attempt_root = arguments.attempt_root
    if os.path.exists(attempt_root):
        print("the attempt root already exists; a new attempt needs a new root",
              file=sys.stderr)
        return 2
    os.makedirs(attempt_root)

    # The marker precedes the registry PARSE under every flag combination, and
    # carries the raw-byte digest of the registry it is about to trust. ONE
    # read: the bytes hashed are the bytes parsed.
    try:
        with open(PINS_PATH, "rb") as handle:
            pins_raw = handle.read()
        pins_raw_sha256 = sha256_bytes(pins_raw)
    except OSError:
        pins_raw, pins_raw_sha256 = None, None
    write_json(os.path.join(attempt_root, "ATTEMPT.json"), {
        "study": STUDY_NAME,
        "attemptRoot": os.path.basename(os.path.normpath(attempt_root)),
        "includeReviewerSet": bool(arguments.include_reviewer_set),
        "pinsRawSha256": pins_raw_sha256,
    })

    def terminal(problem, problems=None):
        write_json(os.path.join(attempt_root, "RESULTS.json"), {
            "study": STUDY_NAME,
            "attemptRoot": os.path.basename(os.path.normpath(attempt_root)),
            "pipelineInvalid": True,
            "pinsRawSha256": pins_raw_sha256,
            "problem": problem,
            "problems": sorted(problems or []),
            "decision": decision.decide({"pipelineProblems": [problem]}),
        })
        print("pipeline-invalid: %s" % problem, file=sys.stderr)
        return 2

    workspace = None
    try:
        if pins_raw is None:
            return terminal("the pin registry is unreadable")
        try:
            pins = json.loads(pins_raw.decode("utf-8"),
                              object_pairs_hook=_refuse_duplicate_keys)
        except ValueError as error:
            return terminal("the pin registry is not duplicate-free JSON: %s"
                            % error)
        label = integrity.study_label(pins)
        unfilled = integrity.unfilled_pins(pins)
        if arguments.include_reviewer_set and unfilled:
            return terminal(
                "--include-reviewer-set is refused while any freeze pin is null: "
                + ", ".join(unfilled))

        problems, refusals = [], {}
        try:
            integrity.verify_interpreter(pins)
        except integrity.IntegrityError as error:
            problems.append("interpreter: %s" % error)
        try:
            integrity.verify_chain()
        except integrity.IntegrityError as error:
            problems.append("port chain: %s" % error)

        tools = engines.Toolchain(pins)
        problems.extend(tools.problems)

        # The frozen artifacts. Absent ones are PIPELINE problems and never
        # substituted from design/: a scorer that fell back to the design tree
        # would adjudicate against unfrozen bytes.
        for relative_path in (GOLD_RELATIVE, MUTANT_JPS_RELATIVE,
                              MUTANT_REGO_RELATIVE, REFERENCE_A_RELATIVE,
                              REFERENCE_B_RELATIVE):
            if not os.path.isfile(os.path.join(STUDY, relative_path)):
                problems.append("registered artifact is absent: %s"
                                % relative_path)

        entries = batch.schedule_entries()
        try:
            slots = [read_slot(entry, arguments.batch_root) for entry in entries]
            shape = terminality(slots, arguments.batch_root)
        except ScoreError as error:
            problems.append("terminality: %s" % error)
            slots, shape = [], {"present": 0,
                               "registered": batch.REGISTERED_SLOTS,
                               "complete": False, "declared": False}

        if problems:
            return terminal("pipeline-invalid before any run was scored",
                            problems)

        tools.require()
        workspace = tempfile.mkdtemp(prefix="study019-attempt-")
        canary = engines.capabilities_canary(tools, workspace)
        gold = load_json(os.path.join(STUDY, GOLD_RELATIVE))["rows"]
        mutants = e4lib.load_mutants(
            os.path.join(STUDY, MUTANT_JPS_RELATIVE),
            os.path.join(STUDY, MUTANT_REGO_RELATIVE),
            os.path.join(STUDY, MUTANT_JPS_DIR),
            os.path.join(STUDY, MUTANT_REGO_DIR))
        pairing, paired_ids = e4lib.build_pairing(mutants)
        paired_count = len(paired_ids["jps"])
        cut = e4lib.high_kill_cut(paired_count)
        print("tau cut: %s" % cut["statement"])
        context = {"gold": gold, "mutants": mutants, "pairedIds": paired_ids,
                   "pairedCount": paired_count,
                   "referenceA": os.path.join(STUDY, REFERENCE_A_RELATIVE),
                   "referenceB": os.path.join(STUDY, REFERENCE_B_RELATIVE)}

        counted = population(slots)
        per_arm_runs, e1, e2, e3, e4_by_arm = {}, {}, {}, {}, {}
        for arm in batch.ARMS:
            runs = [score_run(tools, arm, slot, context, workspace)
                    for slot in counted[arm]["slots"]]
            per_arm_runs[arm] = runs
            e1[arm] = e1_control(arm, runs)
            e2[arm] = e2_profile(arm, counted[arm]["slots"])
            e3[arm] = e3_taxonomy(runs)
            e4_by_arm[arm] = e4_endpoint(arm, runs, cut)

        for name, thunk in (("E5", census_lib.registered_stimulus),
                            ("engineSuppliedKills",
                             lambda: e4lib.engine_supplied_ids(mutants, "jps"))):
            try:
                thunk()
            except (census_lib.CensusError, e4lib.E4Error) as error:
                refusals[name] = str(error)

        gates = {
            # NOT HELD, and deliberately: the floor gate — that BOTH references
            # reproduce every gold row at attempt time — is registered
            # (section 4, section 6) and is not wired yet
            # (`harness/SCAFFOLD.md` item S10). A gate that reported its own
            # success would be the failure section 6 exists to prevent, so this
            # fails closed and the attempt lands on section 5's row 2 until the
            # gate actually runs.
            "references-reproduce-gold": {
                "held": False,
                "code": "GATE-FLOOR-NOT-RUN",
                "note": "design/gold/check_gold.py's floor gate is not wired "
                        "into the scorer yet (harness/SCAFFOLD.md item S10); a "
                        "gate that reports its own success is not a gate"},
            "capabilities-canary-refused": {"held": canary["refused"],
                                            "detail": canary},
            "golden-context": {"held": (pins.get("golden") or {}).get("sha256")
                               is not None},
            "timeout-rate-within-cap": {
                "held": all(counted[arm]["timeoutRate"]["rate"] is None
                            or counted[arm]["timeoutRate"]["rate"]
                            <= (pins.get("batch") or {}).get("timeoutRateCap", 0)
                            for arm in batch.ARMS)},
            "e1-floor": {"held": all(e1[arm]["floorHeld"] for arm in batch.ARMS)},
        }
        contrasts = {}
        try:
            contrasts[decision.CONTRAST_PRIMARY] = contrast("A", "C", e4_by_arm)
            if contrasts[decision.CONTRAST_PRIMARY]["excludesZero"]:
                contrasts[decision.CONTRAST_SECONDARY] = contrast("A", "B",
                                                                  e4_by_arm)
        except stats.StatsError as error:
            refusals["contrast"] = str(error)

        verdict = decision.decide({"pipelineProblems": [],
                                   "controlGates": gates,
                                   "contrasts": contrasts})
        results = {
            "study": STUDY_NAME,
            "attemptRoot": os.path.basename(os.path.normpath(attempt_root)),
            "label": label,
            "unfilledPins": unfilled,
            "pipelineInvalid": False,
            "pinsRawSha256": pins_raw_sha256,
            "toolchain": tools.record(),
            "batchShape": shape,
            "population": {arm: {key: value
                                 for key, value in counted[arm].items()
                                 if key != "slots"}
                           for arm in batch.ARMS},
            "pairing": {"groups": len(pairing),
                        "pairedAdequateJps": len(paired_ids["jps"]),
                        "pairedAdequateRego": len(paired_ids["rego"]),
                        "unpairable": e4lib.unpairable(mutants, paired_ids)},
            "cut": cut,
            "e1": e1, "e2": e2, "e3": e3, "e4": e4_by_arm,
            "contrasts": contrasts,
            "controlGates": gates,
            "refusals": refusals,
            "perArmRuns": per_arm_runs,
            "decision": verdict,
        }
        write_json(os.path.join(attempt_root, "RESULTS.json"), results)
        write_text(os.path.join(attempt_root, "RESULTS.md"),
                   results_markdown(results))
        print("%s (%s)" % (verdict["verdict"], label))
        return 0
    except SystemExit as error:
        terminal("SystemExit: %r" % (error.code,))
        raise
    except KeyboardInterrupt:
        terminal("interrupted")
        raise
    except BaseException as error:
        terminal("%s: %s" % (type(error).__name__, error))
        raise
    finally:
        if workspace is not None:
            shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
