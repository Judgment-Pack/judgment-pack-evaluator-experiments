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

THE FIVE REFUSALS THE SCORER USED TO CARRY, AND WHAT CLOSED THEM
-----------------------------------------------------------------
Every one of `harness/SCAFFOLD.md`'s scorer items has landed, and each landed as
a computation rather than as the removal of a guard:

* **S6** — `census.registered_stimulus()` reads section 5's registered census
  stimulus (the gold-row input set) instead of raising
  `E5-STIMULUS-UNREGISTERED`. The vectors are the SAME evaluation E1 makes, so
  the two endpoints cannot disagree about what a run answered.
* **S7** — `stats.interval_endpoints()` sweeps Delta0 over the registered mesh
  and reports the acceptance set's convex hull; the zero-exclusion decision
  still reads the exact Delta0 = 0 inversion and nothing else.
* **S8** — `stats.excludes_zero()` takes BOTH arm sizes: the general unequal-N
  FM-score inversion section 5 registers, whose N_A = N_C slice reproduces the
  OC table's published constants exactly. `contrast()` no longer raises
  `FM-UNEQUAL-N`.
* **S9** — `e4.engine_supplied_ids()` reads the `engineSuppliedKill` member the
  frozen manifests now carry, and every arm publishes its paired kill totals
  both including and excluding that class (section 4). A language whose
  manifest omits the member still refuses by name.
* **S10** — `references_reproduce_gold()` RUNS the floor gate over both
  references at attempt time. It was stamped `held: true` with a note; a gate
  that reports its own success is not a gate.
* **S11** — the slot reader is the DRIVER's (`batch.collect_slots()`,
  `slot_outcome()`, `verify_seal_of()`, `session_identity()`, `C7_OUTCOMES`),
  the population is the declared PREFIX, and E2 counts the RUN records that
  carry section 1a's authoring codes.

A refusal that does survive — a manifest with no marking, an acceptance set
narrower than the Delta0 mesh — is caught at exactly one place below, published
as a named refusal in the R2 section, and never converted into a number.
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
# Which mutant language each arm's suite is scored against (section 3's arm
# table): arm A emits a pack and a matrix, arms B and C emit Rego and an
# `opa test` file. Written once here so the engine-supplied split and the kill
# machinery cannot disagree about which manifest an arm answers to.
LANGUAGE_OF_ARM = {"A": "jps", "B": "rego", "C": "rego"}
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
# Section 6 C7's retained verdict — the isolation negative control the
# golden-context gate reads. The driver writes it here
# (`batch.DEFAULT_NEGATIVE`); the scorer reads it as a study-relative path
# because no output of this scorer embeds an absolute one.
C7_VERDICT_RELATIVE = "controls/isolation-negative/VERDICT.json"


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

def _bare(digest):
    """A sha256 with or without the `sha256:` prefix, compared one way."""
    if not isinstance(digest, str):
        return digest
    return digest.split(":", 1)[1] if digest.startswith("sha256:") else digest


def slots_present(arms_root: str) -> dict:
    """`{arm: {slot name: path}}` for every slot ON DISK, through the DRIVER's
    own collector (`batch.collect_slots()`).

    SCAFFOLD item S11: the scorer was assembled while `harness/batch.py` was
    still the schedule core and grew its own reduced reader; the driver has since
    landed `collect_slots()`, `slot_outcome()`, `verify_seal_of()` and
    `session_identity()`, and those are the study's authority on what a slot is.
    Reading presence through `collect_slots()` rather than through `isdir()` is
    the first half of that reconciliation and is load-bearing twice: an entry
    named `run-NNN` claims the index WHATEVER its type — a symlink, a FIFO, a
    regular file — so a hole cannot be punched in the indices, and an entry the
    driver does not recognise is reported by name rather than ignored."""
    found, unexpected = {}, []
    for arm in batch.ARMS:
        root = os.path.join(arms_root, arm, "authoring")
        try:
            slots, extra = batch.collect_slots(root)
        except batch.BatchError as error:
            raise ScoreError("arm %s's authoring root refuses: %s" % (arm, error))
        found[arm] = {os.path.basename(path): path for path in slots}
        unexpected.extend("%s/%s" % (arm, name) for name in sorted(extra))
    if unexpected:
        raise ScoreError(
            "the batch tree holds %d entry/entries the registered order does not "
            "name (%s): a population is the registered slots and nothing else"
            % (len(unexpected), ", ".join(unexpected)))
    return found


def read_slot(entry: dict, arms_root: str, present: dict = None,
              golden_pin=None) -> dict:
    """One registered slot, read into the record the population rule works on —
    through the DRIVER's readers and no second reading of its own.

    `batch.verify_seal_of()` recomputes section 2.9's per-slot manifest, so a
    slot whose bytes MOVED after sealing refuses the whole scoring rather than
    being counted; `batch.slot_outcome()` reads the wrapper's own retained
    record, so the driver's `call-timeout` cannot become the scorer's
    `slot-shape` (the undercount the registered status 12 exists to prevent);
    and `batch.session_identity()` names the call, so two slots that are one call
    are visible to `require_distinct_sessions()`.

    A slot that carries neither `CALL.json` nor `REFUSAL.json` was started and
    never finished, and no section 1a code describes it honestly — that is a
    population-level refusal, not a per-run code, and `slot_outcome()` raises it.

    `golden_pin` is the registry's `golden.sha256`. The wrapper stamps the
    golden capture it ran behind into every `CALL.json` (section 3.2), so a run
    made against another capture is the apparatus code
    `golden-context-mismatch` — which the partition has always named and the
    scorer's own reduced reader could never return."""
    name = "run-%03d" % entry["slotIndex"]
    if present is None:
        present = slots_present(arms_root)
    path = (present.get(entry["arm"]) or {}).get(name)
    record = {"arm": entry["arm"], "slotIndex": entry["slotIndex"],
              "globalIndex": entry["globalIndex"], "round": entry["round"],
              "position": entry["position"], "present": path is not None,
              "code": None, "durationSeconds": None, "completion": None,
              "sessionId": None, "sealSha256": None, "wrapperExit": None}
    if path is None:
        return record
    try:
        record["sealSha256"] = batch.verify_seal_of(path, entry)
        status, code = batch.slot_outcome(path)
    except batch.BatchError as error:
        raise ScoreError("arm %s %s: %s" % (entry["arm"], name, error))
    record["wrapperExit"] = status
    record["code"] = code
    call_path = os.path.join(path, "CALL.json")
    call = load_json(call_path) if os.path.isfile(call_path) else None
    if isinstance(call, dict):
        record["durationSeconds"] = call.get("durationSeconds")
    session_path = os.path.join(path, "session.jsonl")
    if os.path.isfile(session_path):
        try:
            record["sessionId"] = batch.session_identity(session_path)
        except (ValueError, OSError):
            record["sessionId"] = None
    if code is not None:
        return record
    if golden_pin is not None:
        stamped = (call or {}).get("goldenSha256")
        if _bare(stamped) != _bare(golden_pin):
            record["code"] = "golden-context-mismatch"
            return record
    completion_path = os.path.join(path, "completion.txt")
    if not os.path.isfile(completion_path):
        record["code"] = "slot-shape"
        return record
    with open(completion_path, "rb") as handle:
        record["completion"] = handle.read().decode("utf-8", "replace")
    return record


def require_distinct_sessions(slots: list) -> None:
    """Two slots naming one session are one call.

    `batch.session_identity()` reads the id the transcript records for itself,
    and the driver's own capture gate (`require_distinct_sessions()` there) makes
    the same demand of the two golden probes for the same reason. A duplicate is
    a POPULATION-level refusal and not a per-run code: section 1a's partition
    names no code for it, and every interval in this study is computed over runs
    assumed to be distinct trials (section 8)."""
    seen = {}
    for slot in slots:
        session = slot.get("sessionId")
        if not session:
            continue
        key = "%s/run-%03d" % (slot["arm"], slot["slotIndex"])
        if session in seen:
            raise ScoreError(
                "%s and %s retain one session id: two slots naming one session "
                "are one call, and no rate is computed over a population holding "
                "one twice" % (seen[session], key))
        seen[session] = key


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
    into the denominator of every rate.

    THE POPULATION IS THE DECLARED PREFIX (SCAFFOLD item S11; the end-to-end
    smoke's D-1). Section 1a's denominator is "attempted runs", and a registered
    slot that is not on disk was never attempted. `terminality()` establishes
    that a short batch is DECLARED rather than scored as a full one, section
    2.8's rule is that a declared short batch is scored over the PREFIX, and
    `slot["present"]` is what says which slots that is. Partitioning on the code
    alone put every ABSENT slot into its arm's denominator wearing
    `no-marker-block` — a phantom run scored zero on every endpoint it reached,
    over a completion that does not exist."""
    per_arm = {}
    for arm in batch.ARMS:
        registered = [slot for slot in slots if slot["arm"] == arm]
        arm_slots = [slot for slot in registered if slot["present"]]
        apparatus = [slot for slot in arm_slots
                     if slot["code"] in APPARATUS_SIDE]
        admitted = [slot for slot in arm_slots
                    if slot["code"] not in APPARATUS_SIDE]
        timeouts = [slot for slot in arm_slots if slot["code"] == "call-timeout"]
        per_arm[arm] = {
            "registered": len(registered),
            "absent": len(registered) - len(arm_slots),
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

def e2_profile(arm: str, runs: list) -> dict:
    """E2 — the authoring-validity profile, as the ORDERED code table section 1a
    registers, with the apparatus codes separated. Headline, not footnote
    (section 5).

    OVER THE RUN RECORDS, not over the slot records (SCAFFOLD item S11; the
    end-to-end smoke's D-3). A slot's code is the WRAPPER's exit status, and
    every code the wrapper can produce is on section 1a's apparatus side; the
    six AUTHORING codes are assigned later, by `score_run()`, onto the run
    record. Counting slots made the six-code table section 5 publishes as a
    headline structurally always zero, and made `admitted` the number of clean
    EXITS rather than the number of admitted ARTIFACTS.

    The apparatus side is separated by construction rather than by filtering: an
    apparatus code on a run record would mean a run the population rule should
    have excluded reached an endpoint, so it refuses here."""
    counts = {}
    for run in runs:
        code = run.get("code")
        if code is None:
            continue
        if code in APPARATUS_SIDE:
            raise ScoreError(
                "arm %s's %s carries the apparatus code %r and is in the E2 "
                "denominator: section 1a excludes apparatus failures from every "
                "per-arm rate, so a run record cannot carry one"
                % (arm, run.get("run"), code))
        counts[code] = counts.get(code, 0) + 1
    ordered = [{"code": code, "side": batch.CODE_PARTITION[code][0],
                "phrase": batch.CODE_PARTITION[code][1],
                "count": counts.get(code, 0)}
               for code in admit_lib.DROP_ORDER]
    clean = sum(1 for run in runs if run.get("code") is None)
    return {"arm": arm, "denominator": len(runs), "admitted": clean,
            # The artifact-level count, published beside the run-level one so
            # neither has to stand in for the other: a run whose POLICY was
            # admitted and whose suite block was missing is `admitted: true` and
            # carries `no-marker-block`.
            "artifactAdmitted": sum(1 for run in runs if run.get("admitted")),
            "orderedCodes": ordered,
            "admittedRate": stats.rate_block(clean, len(runs),
                                             "admitted runs (section 1a)")}


def golden_context_gate(pins: dict) -> dict:
    """Section 6's golden-context gate: the capture is pinned AND the isolation
    negative control is on record with the assent it needed.

    Section 6 lists them together — "the golden-context gate holds with the
    isolation negative control on record" — because the allowlist's POWER is
    what the control demonstrates: a golden capture nothing has ever failed
    against is an allowlist with no shown discrimination. The registered
    outcome set is `batch.C7_OUTCOMES`, read from the driver, which is where it
    is defined and where the driver's own preflight reads it; the shape of the
    record is checked by `batch.c7_record_shape_problems()`, the one function
    both gates read, so the scorer and the driver cannot hold two readings of a
    verdict either."""
    detail = {"registeredOutcomes": list(batch.C7_OUTCOMES),
              "goldenPinned": (pins.get("golden") or {}).get("sha256") is not None,
              "assent": (pins.get("isolationNegative") or {}).get("assent"),
              "outcome": None}
    problems = []
    if not detail["goldenPinned"]:
        problems.append("harness/PINS.json records no golden.sha256")
    if detail["assent"] is None:
        problems.append("harness/PINS.json records no isolationNegative.assent")
    path = os.path.join(STUDY, C7_VERDICT_RELATIVE)
    if not os.path.isfile(path):
        problems.append("no isolation negative control record at %s"
                        % C7_VERDICT_RELATIVE)
    else:
        try:
            verdict = load_json(path)
        except (ValueError, OSError) as error:
            verdict = None
            problems.append("%s cannot be read as duplicate-free JSON: %s"
                            % (C7_VERDICT_RELATIVE, error))
        if verdict is not None and not isinstance(verdict, dict):
            problems.append("%s is not a verdict object" % C7_VERDICT_RELATIVE)
        elif isinstance(verdict, dict):
            problems.extend(batch.c7_record_shape_problems(verdict))
            detail["outcome"] = verdict.get("outcome")
            if detail["outcome"] not in batch.C7_OUTCOMES:
                problems.append(
                    "the control records outcome %r and section 6 C7 registers "
                    "%r" % (detail["outcome"], list(batch.C7_OUTCOMES)))
            elif detail["outcome"] != "refused":
                problems.append(
                    "the control records outcome %r: its registered expectation "
                    "is that the golden match FAILS, and only a refusal shows "
                    "the gate has power" % detail["outcome"])
    return {"held": not problems, "problems": sorted(problems), "detail": detail}


def references_reproduce_gold(tools, gold: list, reference_a: str,
                              reference_b: str, workdir: str) -> dict:
    """Section 4's FLOOR GATE and section 6's first control row, RUN — both
    references reproduce every gold row, at attempt time (SCAFFOLD item S10).

    This is `design/gold/check_gold.py`'s clause (5), through the same two
    invocations the scorer uses everywhere else (`engines.eval_pack()` and
    `engines.eval_rego()` carry that file's flags verbatim — `harness/PORTS.md`
    records it as one of the three sources of `e4lib/engines.py`). It was stamped
    `held: true` with a note while it was unwired, and a gate that reports its
    own success is the failure section 6 exists to prevent; it is a real
    evaluation now, and `held` is true only when both references reproduced all
    of gold."""
    failures = []
    for row in gold:
        want = (("unresolved", None, tuple(sorted(row["expect"]["reasons"])))
                if row["expect"]["disposition"] == "unresolved"
                else ("outcome", row["expect"]["disposition"], ()))
        facts, evidence = engines.facts_documents(row["inputs"])
        for reference, got in (
                ("A", engines.eval_pack(tools, reference_a, facts, evidence,
                                        workdir)),
                ("B", engines.eval_rego(tools, reference_b, row["inputs"],
                                        workdir))):
            if got != want:
                failures.append({"reference": reference, "id": row["id"],
                                 "expected": engines.scope_str(want),
                                 "got": engines.scope_str(got)})
    return {"held": not failures, "rows": len(gold),
            "references": [REFERENCE_A_RELATIVE, REFERENCE_B_RELATIVE],
            "failures": failures[:20], "failureCount": len(failures),
            "gate": "both references reproduce every gold row at attempt time "
                    "(section 4's floor gate; section 6's first control row)"}


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


def census_vectors(runs: list, stimulus: dict) -> dict:
    """`{run id: answer vector}` over the registered census stimulus.

    The vector is the run's OWN artifact's answer on each of the stimulus's
    cells, in the stimulus's order — which is exactly what `score_run()` already
    computed for E1, kept rather than reduced to a pass/fail. A run with no
    admitted artifact answered nothing and is not a census member; the census is
    over readings that exist.

    Refuses a vector of the wrong length rather than censusing it: the two
    registered E5 rows compare runs cell by cell, and a vector that is not the
    stimulus's length is an answer to a different question."""
    vectors = {}
    for run in runs:
        vector = run.get("goldVector")
        if vector is None:
            continue
        if len(vector) != stimulus["count"]:
            raise census_lib.CensusError(
                "E5-VECTOR-LENGTH %s answered %d cells and the registered "
                "stimulus has %d" % (run["run"], len(vector),
                                     stimulus["count"]))
        vectors[run["run"]] = vector
    return vectors


def engine_supplied_block(arm: str, runs: list, listed) -> dict:
    """Section 4's "reported both included and excluded", per arm.

    The kills achievable only through the engine's structural conflict detection
    are a registered manifest member (SCAFFOLD item S9). This publishes the
    paired-subset kill totals BOTH ways and, descriptively, the high-kill count
    under the reduced denominator with its own derived integer cut — the reduced
    cut is R2's and the DECISION reads only the included one, because section 5
    registers the endpoint over the paired adequate subset entire."""
    if listed is None:
        return {"arm": arm, "registered": False,
                "note": "the manifest carries no engineSuppliedKill member; the "
                        "refusal is published in the R2 section and no number is "
                        "computed from an absence"}
    paired = sum(run["kill"]["paired"] for run in runs if run.get("kill"))
    reduced = sum(run["kill"].get("pairedExcludingEngineSupplied", 0)
                  for run in runs if run.get("kill"))
    killed = sum(run["kill"]["killedPaired"] for run in runs if run.get("kill"))
    killed_reduced = sum(
        run["kill"].get("killedPairedExcludingEngineSupplied", 0)
        for run in runs if run.get("kill"))
    per_run_paired = [run["kill"].get("pairedExcludingEngineSupplied", 0)
                      for run in runs if run.get("kill")]
    reduced_cut = None
    if per_run_paired and max(per_run_paired) > 0:
        try:
            reduced_cut = stats.tau_cut(max(per_run_paired))
        except stats.StatsError:
            reduced_cut = None
    high_reduced = 0
    if reduced_cut is not None:
        high_reduced = sum(
            1 for run in runs
            if run.get("identityPass") and run.get("kill")
            and e4lib.is_high_kill(
                run["kill"].get("killedPairedExcludingEngineSupplied", 0),
                run["kill"].get("pairedExcludingEngineSupplied", 0),
                reduced_cut))
    return {
        "arm": arm, "registered": True, "listedMutants": len(listed),
        "killsIncluded": {"killed": killed, "paired": paired},
        "killsExcluded": {"killed": killed_reduced, "paired": reduced},
        "reducedIntegerCut": reduced_cut,
        "highKillExcludingEngineSupplied": high_reduced,
        "note": "section 4: kills achievable only through the engine's "
                "structural conflict detection are reported both included and "
                "excluded. The DECISION reads the included column; the excluded "
                "column and its reduced cut are R2, descriptive.",
    }


def e4_endpoint(arm: str, runs: list, cut: dict, engine_supplied=None) -> dict:
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
        "engineSuppliedKill": engine_supplied_block(arm, runs, engine_supplied),
    }


def contrast(left_arm: str, right_arm: str, e4_by_arm: dict,
             endpoints: bool = True) -> dict:
    """One registered contrast, on the general FM inversion.

    UNEQUAL DENOMINATORS ARE THE REGISTERED CASE (SCAFFOLD item S8, closed).
    Section 1a excludes apparatus failures from the denominator, so unequal
    admitted counts are a real possibility, and section 5 registers "the general
    unequal-N FM-score inversion (the OC table's equal-N closed form is its
    N_A = N_C slice)". The scorer no longer refuses on it and no longer
    approximates it: `stats.excludes_zero()` takes both arm sizes.

    The reported ENDPOINTS come from `stats.interval_endpoints()` — "the
    reported interval endpoints come from the full Delta0 sweep of the same
    construction" (section 5) — and are a report, never the decision: an
    endpoint that failed to compute leaves the zero-exclusion verdict intact and
    publishes its own refusal, because section 5's rule reads `excludesZero` and
    nothing else."""
    left, right = e4_by_arm[left_arm], e4_by_arm[right_arm]
    result = stats.excludes_zero(left["highKill"], right["highKill"],
                                 left["denominator"], right["denominator"])
    result["arms"] = [left_arm, right_arm]
    if endpoints:
        try:
            result["interval"] = stats.interval_endpoints(
                left["highKill"], right["highKill"],
                left["denominator"], right["denominator"])
        except stats.StatsError as error:
            result["interval"] = None
            result["intervalRefusal"] = str(error)
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

    # E1: the policy artifact against every gold row — and, in the same pass,
    # the run's answer VECTOR over the registered E5 census stimulus, which
    # section 5 registers as this same gold-row input set. One evaluation, two
    # endpoints: computing the census on a second pass over the same cells would
    # be a second chance for the two to disagree about what the run answered.
    failures, vector = [], []
    for row in context["gold"]:
        want = (("unresolved", None, tuple(sorted(row["expect"]["reasons"])))
                if row["expect"]["disposition"] == "unresolved"
                else ("outcome", row["expect"]["disposition"], ()))
        if arm == "A":
            facts, evidence = engines.facts_documents(row["inputs"])
            got = engines.eval_pack(tools, artifact, facts, evidence, workdir)
        else:
            got = engines.eval_rego(tools, artifact, row["inputs"], workdir)
        vector.append(engines.scope_str(got))
        if got != want:
            failures.append({"id": row["id"], "cite": row.get("cite", []),
                             "category": got[0] if got[0] == "ROW-ERROR"
                             else "disagreement",
                             "expected": engines.scope_str(want),
                             "got": engines.scope_str(got)})
    run["goldFailures"] = failures
    run["goldPerfect"] = not failures
    run["goldVector"] = vector

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
                                       context["pairedIds"]["jps"],
                                       context["engineSupplied"]["jps"])
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
                                       context["pairedIds"]["rego"],
                                       context["engineSupplied"]["rego"])
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
    lines += ["", "## The registered contrasts (fixed-sequence: A−C, then A−B)",
              "", "| Contrast | Counts | Denominators | Decided | Direction | "
              "Interval |", "|---|---|---|---|---|---|"]
    for name in (decision.CONTRAST_PRIMARY, decision.CONTRAST_SECONDARY):
        entry = (results.get("contrasts") or {}).get(name)
        if entry is None:
            lines.append("| %s | — | — | — | — | — |" % name)
            continue
        interval = entry.get("interval")
        lines.append(
            "| %s | %d vs %d | %d, %d | %s | %s | %s |"
            % (name, entry["left"], entry["right"], entry["nLeft"],
               entry["nRight"], "**yes**" if entry["excludesZero"] else "no",
               decision.direction(entry),
               "—" if interval is None
               else "[%s, %s]" % (interval["lower"], interval["upper"])))
    lines += ["", "## E2 — authoring-validity profile", "",
              "| Arm | Code | Side | Count |", "|---|---|---|---|"]
    for arm in batch.ARMS:
        entry = (results.get("e2") or {}).get(arm)
        if entry is None:
            continue
        for row in entry["orderedCodes"]:
            lines.append("| %s | %s | %s | %d |"
                         % (arm, row["code"], row["side"], row["count"]))
    census_block = results.get("e5")
    if census_block:
        lines += ["", "## E5 — interpretive-spread census (descriptive)", "",
                  "Stimulus: %s. No tradeoff statement combining these rows "
                  "with the E4 rates is licensed (section 9)."
                  % census_block["stimulus"]["label"], "",
                  "| Arm | Runs | Distinct encodings | Minimal covering set |",
                  "|---|---|---|---|"]
        for entry in census_block["perArm"]:
            lines.append("| %s | %d | %d | %d |"
                         % (entry["arm"], entry["runs"],
                            entry["distinctEncodings"],
                            entry["minimalCoveringSet"]))
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
            present = slots_present(arguments.batch_root)
            golden_pin = (pins.get("golden") or {}).get("sha256")
            slots = [read_slot(entry, arguments.batch_root, present, golden_pin)
                     for entry in entries]
            require_distinct_sessions(slots)
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
        gold_path = os.path.join(STUDY, GOLD_RELATIVE)
        with open(gold_path, "rb") as handle:
            gold_sha256 = sha256_bytes(handle.read())
        gold = load_json(gold_path)["rows"]
        mutants = e4lib.load_mutants(
            os.path.join(STUDY, MUTANT_JPS_RELATIVE),
            os.path.join(STUDY, MUTANT_REGO_RELATIVE),
            os.path.join(STUDY, MUTANT_JPS_DIR),
            os.path.join(STUDY, MUTANT_REGO_DIR))
        pairing, paired_ids = e4lib.build_pairing(mutants)
        paired_count = len(paired_ids["jps"])
        cut = e4lib.high_kill_cut(paired_count)
        print("tau cut: %s" % cut["statement"])
        # Section 4's engine-supplied-kill list, from the FROZEN manifests
        # (SCAFFOLD item S9). A language whose manifest carries no
        # `engineSuppliedKill` member refuses by name and its arm reports the
        # refusal instead of a number; a manifest that carries the member and
        # marks nothing true is the registered statement that the arm has NO
        # engine-supplied class, which is arm B's case and is a fact rather than
        # an absence.
        engine_supplied = {}
        for language in ("jps", "rego"):
            try:
                engine_supplied[language] = e4lib.engine_supplied_ids(mutants,
                                                                      language)
            except e4lib.E4Error as error:
                engine_supplied[language] = None
                refusals["engineSuppliedKills.%s" % language] = str(error)
        context = {"gold": gold, "mutants": mutants, "pairedIds": paired_ids,
                   "pairedCount": paired_count,
                   "engineSupplied": {language: (ids or ())
                                      for language, ids
                                      in engine_supplied.items()},
                   "referenceA": os.path.join(STUDY, REFERENCE_A_RELATIVE),
                   "referenceB": os.path.join(STUDY, REFERENCE_B_RELATIVE)}
        floor_gate = references_reproduce_gold(
            tools, gold, context["referenceA"], context["referenceB"],
            workspace)

        counted = population(slots)
        per_arm_runs, e1, e2, e3, e4_by_arm = {}, {}, {}, {}, {}
        for arm in batch.ARMS:
            runs = [score_run(tools, arm, slot, context, workspace)
                    for slot in counted[arm]["slots"]]
            per_arm_runs[arm] = runs
            e1[arm] = e1_control(arm, runs)
            e2[arm] = e2_profile(arm, runs)
            e3[arm] = e3_taxonomy(runs)
            e4_by_arm[arm] = e4_endpoint(
                arm, runs, cut,
                engine_supplied[LANGUAGE_OF_ARM[arm]])

        try:
            stimulus = census_lib.registered_stimulus(gold, gold_sha256)
            e5 = {"stimulus": stimulus,
                  "perArm": [census_lib.census(arm,
                                               census_vectors(per_arm_runs[arm],
                                                              stimulus),
                                               stimulus["label"])
                             for arm in batch.ARMS]}
        except census_lib.CensusError as error:
            e5 = None
            refusals["E5"] = str(error)

        gates = {
            # RUN, not asserted (SCAFFOLD item S10): both references are
            # evaluated against every gold row here, at attempt time, through
            # the same two invocations every other number in this attempt is
            # produced by.
            "references-reproduce-gold": floor_gate,
            "capabilities-canary-refused": {"held": canary["refused"],
                                            "detail": canary},
            "golden-context": golden_context_gate(pins),
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
            "e1": e1, "e2": e2, "e3": e3, "e4": e4_by_arm, "e5": e5,
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
