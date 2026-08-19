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
  registry leaves a record tied to the registry bytes it saw. ROUND-10 FINDING
  R10-1: that digest is now COMPARED as well as recorded — every admitted slot's
  `CALL.json.pinsSha256` must equal it, and a slot made under any other registry
  is §1a's `registry-mismatch`.
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

# THE ONLY STUDY-LOCAL IMPORT AT MODULE SCOPE, and it is deliberate (round-1
# R1-9). The finding was that "the scorer imports local modules before
# validation": `batch` and the whole of `e4lib` were bound at import, so the
# untracked-source and unreviewed-bytecode gate in `integrity.verify()` ran — if
# it ran at all — after the bytes it is about had already executed. `integrity`
# itself imports nothing study-local at module scope, so importing it costs
# nothing the gate could have caught, and `bind_study_modules()` below is what
# binds the rest — called from `main()` only after `integrity.verify()` has
# passed.
import integrity      # noqa: E402

PINS_PATH = os.path.join(HERE, "PINS.json")

STUDY_NAME = "019-authorship-across-representations"

# Which mutant language each arm's suite is scored against (section 3's arm
# table): arm A emits a pack and a matrix, arms B and C emit Rego and an
# `opa test` file. Written once here so the engine-supplied split, the kill
# machinery and the PER-LANGUAGE high-kill cut (round-1 R1-1) cannot disagree
# about which manifest an arm answers to.
LANGUAGE_OF_ARM = {"A": "jps", "B": "rego", "C": "rego"}

# Bound by `bind_study_modules()`, and DELIBERATELY NOT PREDEFINED: a module's
# `__getattr__` fires only for names that are not already in its globals, so a
# placeholder here would hand a reader an empty tuple instead of binding. Until
# something calls `bind_study_modules()` these names do not exist, which is the
# honest state of a module nobody has verified yet.
_LAZY_NAMES = ("batch", "admit_lib", "census_lib", "decision", "domain_lib",
               "e4lib", "engines", "extract", "reviewer_lib", "stats",
               "SHORTFALL_FILE", "ADMISSION_CODES", "APPARATUS_SIDE",
               "AUTHORING_SIDE")
_BOUND = False

# Set by `main()` the instant `integrity.verify()` returns, and read by the
# terminal path so that a pre-verification failure cannot bind the tree whose
# untrustworthiness is the reason it is failing (round-2 finding R2-8).
_VERIFIED = False


def bind_study_modules():
    """Import the study-local scoring modules and derive the constants from
    them. Idempotent.

    `main()` calls this AFTER `integrity.verify()` has established that no
    untracked source can shadow a reviewed one and that no compiled byte the
    reviewed sources did not produce sits in the tree. Everything below this
    line therefore runs on bytes something checked.

    Nothing is spelled twice: section 1a's partition is `batch.CODE_PARTITION`'s
    and the shortfall file's name is `batch.SHORTFALL_NAME`'s, because a second
    copy of a string is a second chance for the driver to declare a shortfall
    the scorer never looks for."""
    global batch, admit_lib, census_lib, decision, domain_lib, e4lib
    global engines, extract, reviewer_lib, stats
    global SHORTFALL_FILE, ADMISSION_CODES, APPARATUS_SIDE, AUTHORING_SIDE
    global _BOUND
    if _BOUND:
        return
    import batch as batch_module
    from e4lib import admit as admit_module
    from e4lib import census as census_module
    from e4lib import decision as decision_module
    from e4lib import domain as domain_module
    from e4lib import e4 as e4_module
    from e4lib import engines as engines_module
    from e4lib import extract as extract_module
    from e4lib import reviewer as reviewer_module
    from e4lib import stats as stats_module
    batch, admit_lib, census_lib = batch_module, admit_module, census_module
    decision, domain_lib, e4lib = decision_module, domain_module, e4_module
    engines, extract = engines_module, extract_module
    reviewer_lib, stats = reviewer_module, stats_module
    SHORTFALL_FILE = batch.SHORTFALL_NAME
    ADMISSION_CODES = tuple(sorted(batch.CODE_PARTITION))
    APPARATUS_SIDE = frozenset(code for code, (side, _phrase)
                               in batch.CODE_PARTITION.items()
                               if side == "apparatus")
    AUTHORING_SIDE = frozenset(code for code, (side, _phrase)
                               in batch.CODE_PARTITION.items()
                               if side == "authoring")
    _BOUND = True


def __getattr__(name):
    """PEP 562: reading one of the bound names binds them.

    A reader of this module — a test, a REPL — gets the same objects `main()`
    gets, and the PRODUCTION path still binds them explicitly after the
    integrity gate. The lazy hook is a convenience for readers, never the thing
    the attempt relies on."""
    if name in _LAZY_NAMES:
        bind_study_modules()
        return globals()[name]
    raise AttributeError("module %r has no attribute %r" % (__name__, name))

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
# The off-gold equivalence certificate — a freeze pin, a control artifact, and
# (round-1 R1-9) one of the scorer inputs the manifest did not cover.
OFFGOLD_RELATIVE = "controls/off-gold-equivalence.json"
# The sealed reviewer mutant directory (§1a, §4; round-1 R1-10).
REVIEWER_SET_RELATIVE = "controls/reviewer-mutants"

MANIFEST_RELATIVE = "harness/STUDY-MANIFEST.sha256"


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


def _manifest_digests() -> dict:
    """`{study-relative path: sha256}` from `harness/STUDY-MANIFEST.sha256`."""
    path = os.path.join(STUDY, MANIFEST_RELATIVE)
    covered = {}
    if not os.path.isfile(path):
        return covered
    with open(path, "rb") as handle:
        for line in handle.read().decode("utf-8").splitlines():
            if not line.strip():
                continue
            digest, _, name = line.partition("  ")
            covered[name] = digest
    return covered


def _registered_inputs_problems() -> list:
    """Every registered scorer input, required to be present AND covered by the
    exact-set manifest at the digest it hashes to.

    ROUND-1 FINDING R1-9. The scorer used to check five artifacts for EXISTENCE,
    and the manifest covered the two top-level mutant manifests and the reference
    Markdown but none of `mutants/jps/*.json`, `mutants/rego/*.rego`,
    `reference/refA/pack.json`, `reference/refB/policy.rego` or the off-gold
    certificate — which are the bytes this scorer actually executes. Both halves
    are closed here: the payload sets joined the manifest
    (`harness/make_manifest.py`), and an input outside the covered set is a
    pipeline problem naming itself rather than a file nobody checked.

    The mutant PAYLOAD paths are read from the two frozen manifests rather than
    globbed, so a manifest that names a mutant the directory does not carry
    refuses here rather than at a subprocess."""
    covered = _manifest_digests()
    named = [GOLD_RELATIVE, MUTANT_JPS_RELATIVE, MUTANT_REGO_RELATIVE,
             REFERENCE_A_RELATIVE, REFERENCE_B_RELATIVE, OFFGOLD_RELATIVE]
    problems = []
    for relative_path in named:
        if not os.path.isfile(os.path.join(STUDY, relative_path)):
            problems.append("registered artifact is absent: %s" % relative_path)
    for directory in (MUTANT_JPS_DIR, MUTANT_REGO_DIR):
        root = os.path.join(STUDY, directory)
        if not os.path.isdir(root):
            problems.append("registered mutant payload directory is absent: %s"
                            % directory)
            continue
        for name in sorted(os.listdir(root)):
            named.append("%s/%s" % (directory, name))
    for relative_path in named:
        absolute = os.path.join(STUDY, relative_path)
        if not os.path.isfile(absolute):
            continue
        if relative_path not in covered:
            problems.append(
                "%s is a scorer input and the exact-set study manifest does not "
                "cover it: an input nothing verified is an input this attempt "
                "cannot adjudicate against" % relative_path)
            continue
        with open(absolute, "rb") as handle:
            actual = hashlib.sha256(handle.read()).hexdigest()
        if actual != covered[relative_path]:
            problems.append("%s hashes to sha256:%s and the study manifest "
                            "records sha256:%s"
                            % (relative_path, actual, covered[relative_path]))
    return sorted(problems)


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
    bind_study_modules()
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
              golden_pin=None, pins: dict = None,
              pins_raw_sha256=None) -> dict:
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
    scorer's own reduced reader could never return.

    `pins_raw_sha256` IS THE ATTEMPT'S OWN REGISTRY DIGEST (round-10 finding
    R10-1), and the check it enables is the one `authoring_call.sh` claimed
    existed here and did not. The wrapper stamps the registry every call was made
    under into `CALL.json.pinsSha256`; `main()` hashes `harness/PINS.json`'s raw
    bytes before it parses them and records the digest in `ATTEMPT.json`; and
    until this round nothing compared the two, so a slot authored under a
    SUBSTITUTE registry — the round-10 reviewer's construction, an alternate
    complete mapping with every freeze pin filled and the real preregistration
    digest — was read as an ordinary registered run. It is `registry-mismatch`
    now: apparatus, excluded from every denominator, reported with its own count.

    The check is FAIL-CLOSED on the stamp's absence and on its type. A CALL.json
    with no `pinsSha256`, or one carrying a number or a null, is not a slot this
    wrapper wrote under this registry, and "the evidence is missing" is not
    "the evidence agrees". It runs BEFORE the golden comparison because the
    golden pin is read out of the very registry under dispute: a slot made under
    another registry would usually fail the golden check too, and filing it as a
    golden-context mismatch would name the wrong disagreement. Both codes are
    apparatus, so no denominator moves either way.

    Passing no `pins_raw_sha256` compares nothing and is for the readers that are
    not an attempt, exactly as passing no `golden_pin` is.

    THE TRANSCRIPT VERDICT IS RECOMPUTED HERE (round-2 finding R2-5), and `pins`
    is what it needs. R1-5's repair built the whole binding and sealed its
    verdict into every completed slot — and then nothing on the scoring side
    read it. This reader read the seal, the wrapper record, the golden stamp and
    the completion, and stopped; `batch.py`'s own note ("harness/score.py
    recomputes this verdict from the same retained bytes and does not trust this
    record") described a call that did not exist. In sealed-slot probes a
    transcript carrying an extra author turn, or a drifted pre-prompt context,
    left `code = None` and the slot stayed in its arm's denominator and was
    scored. §1a registers both outcomes and registers them DIFFERENTLY: an author
    protocol violation is an authoring outcome, retained and scoring zero, and a
    prompt/context/log failure is apparatus and leaves the denominator. So the
    binding runs on the sealed bytes, before the population is built, and its
    registered code is the slot's code. Passing no `pins` recomputes nothing and
    is for the readers that are not an attempt."""
    bind_study_modules()
    name = "run-%03d" % entry["slotIndex"]
    if present is None:
        present = slots_present(arms_root)
    path = (present.get(entry["arm"]) or {}).get(name)
    record = {"arm": entry["arm"], "slotIndex": entry["slotIndex"],
              "globalIndex": entry["globalIndex"], "round": entry["round"],
              "position": entry["position"], "present": path is not None,
              "code": None, "durationSeconds": None, "completion": None,
              "sessionId": None, "sealSha256": None, "wrapperExit": None,
              "transcript": None}
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
    if pins_raw_sha256 is not None:
        stamped = (call or {}).get("pinsSha256")
        if not isinstance(stamped, str) or \
                _bare(stamped) != _bare(pins_raw_sha256):
            record["code"] = "registry-mismatch"
            return record
    if golden_pin is not None:
        stamped = (call or {}).get("goldenSha256")
        if _bare(stamped) != _bare(golden_pin):
            record["code"] = "golden-context-mismatch"
            return record
    completion_path = os.path.join(path, "completion.txt")
    completion_present = os.path.isfile(completion_path)
    if completion_present:
        with open(completion_path, "rb") as handle:
            record["completion"] = handle.read().decode("utf-8", "replace")
    if pins is None:
        # A reader that is not an attempt. It gets the shape check and no
        # recomputed verdict, so it cannot quietly answer differently.
        if not completion_present:
            record["code"] = "slot-shape"
        return record
    verdict = bind_transcript_verdict(path, entry, pins)
    record["transcript"] = verdict
    # AN AUTHOR PROTOCOL VIOLATION OUTRANKS A MISSING COMPLETION, and the order
    # is not a preference — it is a fact about the apparatus. `authoring_call.sh`
    # writes NO `completion.txt` when the transcript shows the author using a
    # tool, deliberately and with its reason in the file: refusing there would
    # exit the wrapper non-zero, which is an apparatus code, "which would quietly
    # delete from every denominator exactly the runs §3's no-tools instruction
    # exists to catch". The scorer then read the missing file as `slot-shape` —
    # an APPARATUS code — and deleted them anyway, one layer up. Round-2 R2-5
    # made this visible: the tool-use branch of the driver's own binding tests
    # passes, and the run it is about was leaving the population.
    if verdict["side"] == "authoring":
        record["code"] = verdict["code"]
        return record
    if not completion_present:
        record["code"] = "slot-shape"
        return record
    if verdict["code"] is not None:
        record["code"] = verdict["code"]
    return record


def bind_transcript_verdict(slot_path: str, entry: dict, pins: dict) -> dict:
    """§1a's transcript binding, RECOMPUTED from the sealed bytes (round-2 R2-5).

    One binding, two callers: `batch.transcript_verdict()` is the driver's own
    entry point and the scorer runs the same function on the same retained
    bytes, so a verdict cannot be a driver record the scorer believes. The
    recomputed verdict is published per slot — reason, side and code — beside
    the driver's sealed one, because "the seal says admissible and the recompute
    does not" is a fact a reader should be able to see.

    An `UnclassifiedRefusal` is a defect in the gate, not an outcome for a run:
    §1a's rule is that a transcript this study cannot attribute does not get a
    denominator by default, so it refuses the whole scoring."""
    bind_study_modules()
    golden_path = batch.golden_path_for(pins)
    try:
        verdict = batch.transcript_verdict(slot_path, entry["arm"], pins,
                                           golden_path)
    except batch.transcript_check.UnclassifiedRefusal as error:
        raise ScoreError(
            "arm %s run-%03d: the transcript binding refused with a cause §1a "
            "does not name (%s): a transcript this study cannot attribute does "
            "not get a denominator by default"
            % (entry["arm"], entry["slotIndex"], error))
    except (OSError, ValueError) as error:
        raise ScoreError(
            "arm %s run-%03d: the transcript binding could not read the sealed "
            "bytes (%s: %s)" % (entry["arm"], entry["slotIndex"],
                                type(error).__name__, error))
    sealed = None
    sealed_path = os.path.join(slot_path, batch.TRANSCRIPT_NAME)
    if os.path.isfile(sealed_path):
        try:
            sealed = load_json(sealed_path)
        except (ValueError, OSError):
            sealed = None
    return {"admissible": verdict["admissible"], "reason": verdict["reason"],
            "side": verdict["side"], "code": verdict["code"],
            "sealedAdmissible": (sealed or {}).get("admissible"),
            "sealedReason": (sealed or {}).get("reason"),
            "agreesWithSeal": sealed is not None
                              and sealed.get("reason") == verdict["reason"]}


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


def shortfall_members() -> frozenset:
    """The exact member set `batch.declare_shortfall()` writes, DERIVED from the
    driver's own `SHORTFALL_SCHEMA`.

    It was transcribed here — eleven names, written while `declare_shortfall()`
    was growing four more (`declarationVersion`, `ledgerSha256`,
    `ledgerHeadSha256`, `slots`) for the same finding, in another lane's edit.
    Both halves passed their own tests and neither test crossed the seam, so the
    scorer refused every declaration the driver actually writes: fail-closed, but
    it made R1-7's whole point — an incomplete batch branching to the registered
    no-contrast outcome — unreachable. `harness/PORTS.md`'s batch row already
    registers the rule this restores: the scorer runs the driver's own functions
    on read "rather than spelling a member list of its own"."""
    bind_study_modules()
    return frozenset(batch.SHORTFALL_SCHEMA)


def validate_shortfall(declaration: dict, slots: list, arms_root: str) -> dict:
    """The declaration, the ledger and the slots on disk, checked against each
    other and against the registered order.

    ROUND-1 FINDING R1-7, whose whole force is that this function did not exist.
    Any JSON object made an arbitrary incomplete set terminal — `{}` included —
    and the scorer then computed ordinary endpoints and contrasts over whatever
    prefix happened to be on disk. That is outcome-selective deletion with a
    one-line file as its price, and it contradicts the driver's own registered
    rule and the scaffold's.

    Seven things are established here, and a failure of any of them refuses the
    whole scoring rather than downgrading it:

    0. the DRIVER's own `validate_shortfall()` passes on it — the schema, the
       declaration version, the slot inventory as a prefix of §2's order, every
       row's code inside §1a's partition, and every count derived from the
       inventory rather than asserted beside it. One definition, two callers:
       what follows is what the driver cannot check, because the driver validates
       what it is about to write and this reads slots that are on disk now;
    1. the declaration carries EXACTLY the members `declare_shortfall()` writes,
       READ FROM `batch.SHORTFALL_SCHEMA` (see `shortfall_members()`);
    2. its three `registered*` members are §2's registered constants;
    3. `completedSlots` is the number of slots actually present, and
       `completedThroughGlobalIndex` is that same number — a declared prefix is
       a PREFIX, so its length and its last global index are one number;
    4. `arms/BATCH.json` parses, its hash chain verifies, and its records are the
       registered order's prefix of their own length, position by position;
    5. the ledger's length equals the declared length equals the slots present,
       and the ledger's slot paths are exactly the slots present — the
       slot/seal bijection, computed rather than assumed;
    6. every present slot's recomputed seal equals the `manifestSha256` its
       ledger record carries.

    The scorer then branches to the registered no-contrast outcome. It does not
    score the prefix."""
    bind_study_modules()
    problems = []
    registered_members = shortfall_members()
    members = set(declaration)
    if members != registered_members:
        problems.append(
            "the declaration's members are %s and %s writes exactly %s"
            % (sorted(members) or "none", SHORTFALL_FILE,
               sorted(registered_members)))
        # Without the registered shape there is nothing to compare, and a
        # partial comparison would be a partial guarantee.
        raise ScoreError("; ".join(problems))
    # The driver's own validation, on the bytes it wrote. It is run BEFORE the
    # disk-side checks below because it is the one that establishes the
    # declaration is internally honest, and comparing a dishonest declaration
    # against the slots present would report the disagreement at the wrong end.
    try:
        batch.validate_shortfall(declaration)
    except batch.BatchError as error:
        raise ScoreError("%s does not validate against the driver that writes "
                         "it: %s" % (SHORTFALL_FILE, error))
    for member, registered in (("registeredSlots", batch.REGISTERED_SLOTS),
                               ("registeredRounds", batch.ROUNDS),
                               ("registeredRunsPerArm", batch.RUNS_PER_ARM)):
        if declaration[member] != registered:
            problems.append("%s declares %r and §2 registers %r"
                            % (member, declaration[member], registered))
    present = sorted((slot for slot in slots if slot["present"]),
                     key=lambda slot: slot["globalIndex"])
    count = len(present)
    if declaration["completedSlots"] != count:
        problems.append(
            "the declaration says %r slots completed and %d are present"
            % (declaration["completedSlots"], count))
    if declaration["completedThroughGlobalIndex"] != count:
        problems.append(
            "the declaration completes through global index %r over %d slots: a "
            "declared prefix is a prefix of §2's registered order, so those are "
            "one number" % (declaration["completedThroughGlobalIndex"], count))
    indices = [slot["globalIndex"] for slot in present]
    if indices != list(range(1, count + 1)):
        problems.append(
            "the slots present are not the registered order's prefix: their "
            "global indices are %s" % (indices[:10] + (["..."] if count > 10
                                                       else [])))
    ledger_path = os.path.join(arms_root, batch.LEDGER_NAME)
    # THE REGISTERED EMPTY PREFIX (round-2 finding R2-9). `SHORTFALL_SCHEMA`
    # registers `ledgerSha256`, `ledgerHeadSha256` and `lastSlot` as nullable
    # "only where a null is a fact (an empty prefix has no last slot)", and
    # `declare_shortfall()` emits exactly that when the batch died before slot 1:
    # no ledger file exists, so both digests are null and the inventory is empty.
    # This function demanded `BATCH.json` unconditionally, so the one declaration
    # the driver can write for the earliest failure was the one the scorer
    # refused — the registered representation did not round-trip, and R1-7's
    # branch to UNRESOLVED-BY-DESIGN was unreachable at zero. An empty prefix is
    # now validated as what it is: the driver's own two checks over an empty
    # ledger, plus the demand that no ledger file exist to contradict it.
    if count == 0:
        for member in ("ledgerSha256", "ledgerHeadSha256", "lastSlot"):
            if declaration[member] is not None:
                problems.append(
                    "the declaration completes 0 slots and names %s %r: an "
                    "empty prefix has no ledger, no chain head and no last slot"
                    % (member, declaration[member]))
        if declaration["slots"]:
            problems.append(
                "the declaration completes 0 slots and inventories %d"
                % len(declaration["slots"]))
        if os.path.isfile(ledger_path):
            problems.append(
                "the declaration declares an empty prefix with no ledger and %s "
                "exists: the declaration and the tree disagree about whether any "
                "slot ran" % batch.LEDGER_NAME)
        try:
            batch.verify_shortfall(declaration, [], None)
        except batch.BatchError as error:
            problems.append("the declaration against an empty ledger: %s"
                            % error)
        if problems:
            raise ScoreError(
                "%s does not declare this batch: %s"
                % (SHORTFALL_FILE, "; ".join(sorted(problems))))
        return {"declaredSlots": 0, "ledgerRecords": 0,
                "reason": declaration["reason"],
                "completedRounds": declaration["completedRounds"],
                "verified": ["member set (batch.SHORTFALL_SCHEMA)",
                             "batch.validate_shortfall",
                             "batch.verify_shortfall (empty ledger)",
                             "registered constants", "empty prefix",
                             "no ledger file"]}
    if not os.path.isfile(ledger_path):
        problems.append("%s carries no %s, so the declaration's prefix answers "
                        "to nothing" % (relative(arms_root), batch.LEDGER_NAME))
        raise ScoreError("; ".join(problems))
    try:
        ledger = load_json(ledger_path)
    except (ValueError, OSError) as error:
        raise ScoreError("%s cannot be read as duplicate-free JSON (%s)"
                         % (batch.LEDGER_NAME, error))
    records = ledger.get("records") if isinstance(ledger, dict) else None
    if not isinstance(records, list):
        raise ScoreError(
            "%s carries no records list: the declared prefix is the LEDGER's, "
            "verified against the registered order, and there is no ledger"
            % batch.LEDGER_NAME)
    entries = batch.schedule_entries()
    try:
        batch.verify_ledger_chain(records)
    except batch.BatchError as error:
        problems.append("the ledger's hash chain: %s" % error)
    # …and the driver's own comparison of the declaration against the ledger it
    # claims to describe: the slot inventory row for row, the chain head, and the
    # ledger FILE digest. The same "one definition, two callers" rule as above —
    # the driver runs this before it writes and the scorer runs it on read.
    try:
        with open(ledger_path, "rb") as handle:
            batch.verify_shortfall(
                declaration, records,
                "sha256:" + hashlib.sha256(handle.read()).hexdigest())
    except batch.BatchError as error:
        problems.append("the declaration against the ledger: %s" % error)
    if len(records) != count:
        problems.append(
            "%s records %d slots and %d are present: a declaration is a "
            "statement about the ledger AND about the slots present"
            % (batch.LEDGER_NAME, len(records), count))
    for offset, record in enumerate(records[:count]):
        expected = {key: entries[offset][key] for key in batch.SCHEDULE_KEYS}
        actual = {key: record.get(key) for key in batch.SCHEDULE_KEYS}
        if actual != expected:
            problems.append(
                "the ledger diverges from §2's registered call order at position "
                "%d: it records %r and the order assigns %r"
                % (offset + 1, actual, expected))
            break
    by_index = {slot["globalIndex"]: slot for slot in present}
    for record in records[:count]:
        slot = by_index.get(record.get("globalIndex"))
        if slot is None:
            problems.append(
                "the ledger records global index %r and no such slot is present: "
                "the slot/seal correspondence is a bijection or it is nothing"
                % record.get("globalIndex"))
            continue
        if _bare(record.get("manifestSha256")) != _bare(slot.get("sealSha256")):
            problems.append(
                "%s/run-%03d reseals to %s and its ledger record carries %s"
                % (slot["arm"], slot["slotIndex"], slot.get("sealSha256"),
                   record.get("manifestSha256")))
    if declaration["lastSlot"] != (records[count - 1].get("path")
                                   if count else None):
        problems.append(
            "the declaration names %r as its last slot and the ledger's prefix "
            "ends at %r" % (declaration["lastSlot"],
                            records[count - 1].get("path") if count else None))
    if problems:
        raise ScoreError(
            "%s does not declare this batch: %s"
            % (SHORTFALL_FILE, "; ".join(sorted(problems))))
    return {"declaredSlots": count, "ledgerRecords": len(records),
            "reason": declaration["reason"],
            "completedRounds": declaration["completedRounds"],
            "verified": ["member set (batch.SHORTFALL_SCHEMA)",
                         "batch.validate_shortfall", "batch.verify_shortfall",
                         "registered constants", "prefix length",
                         "ledger chain", "registered call order",
                         "slot/seal bijection", "last slot"]}


def terminality(slots: list, arms_root: str) -> dict:
    """Study 012's section 2.8 rule, ported: exactly the registered number of
    slots XOR a shortfall declaration whose prefix is the slots present.

    Both, or neither, refuses — a shortfall over a full batch is not a short
    batch, and an over-full batch is not a population this study contemplates.
    A declaration that cannot be read declares nothing and refuses the whole
    scoring, and a declaration that can be read is VALIDATED rather than
    believed (`validate_shortfall()`, round-1 R1-7)."""
    bind_study_modules()
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
    shape = {"present": present, "registered": batch.REGISTERED_SLOTS,
             "complete": complete, "declared": shortfall is not None,
             "declaration": None}
    if shortfall is not None:
        shape["declaration"] = validate_shortfall(shortfall, slots, arms_root)
    return shape


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
    bind_study_modules()
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
    bind_study_modules()
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
    bind_study_modules()
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
    bind_study_modules()
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
    bind_study_modules()
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
    bind_study_modules()
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


def engine_supplied_block(arm: str, runs: list, listed,
                          reduced_paired_count: int = 0) -> dict:
    """Section 4's "reported both included and excluded", per arm.

    The kills achievable only through the engine's structural conflict detection
    are a registered manifest member (SCAFFOLD item S9). This publishes the
    paired-subset kill totals BOTH ways and, descriptively, the high-kill count
    under the reduced denominator with its own derived integer cut — the reduced
    cut is R2's and the DECISION reads only the included one, because section 5
    registers the endpoint over the paired adequate subset entire."""
    bind_study_modules()
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
    # The reduced denominator is a property of the MUTANT SET, not of the runs:
    # every run of an arm is scored against the same paired subset, so the
    # reduced cut is derived once from that subset's size. (`max()` over the
    # runs was the same number whenever any run existed and was undefined when
    # none did, which is a second way to compute a constant.)
    reduced_paired = reduced_paired_count
    reduced_cut = None
    if reduced_paired > 0:
        try:
            reduced_cut = stats.tau_cut(reduced_paired)
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


def e4_endpoint(arm: str, runs: list, cut: dict, engine_supplied=None,
                reduced_paired_count: int = 0) -> dict:
    """E4 — the per-arm HIGH-KILL RUN RATE, the primary endpoint.

    Section 5's denominator rule, in code and stated in the record: "Runs
    carrying authoring-outcome codes remain in the E4 denominator as
    not-high-kill (no-marker included); only apparatus codes leave it, and
    identity-control exclusions are reported, never silently dropped."

    The identity control is a first-class per-arm RATE, and identity-excluded
    runs are reported. They leave the high-kill numerator by not being
    high-kill, and they stay in the denominator: an identity-failing suite is a
    suite that did not pin the reference down, which is an authoring outcome and
    not an apparatus failure.

    ROUND-2 FINDING R2-2, and it was a disagreement between two scorers about
    one registered rule. §5 registers the denominator here — "identity-control
    exclusions are reported, never silently dropped", over §1a's "attempted runs
    whose apparatus succeeded" — and this is that rule: `len(runs)`. The pilot
    scorer (`design/mutants/e4_score.py`) took the OTHER reading, dividing by the
    identity-PASSING runs only, and the round-1 disposition wrote that reading
    down; on a two-run arm with one identity-passing high-kill run the two rules
    answer 1/2 and 1/1. The registered rule is this one, the pilot has been
    changed to it, and the pilot's numbers moved (`design/mutants/E4-PILOT-v4.json`).

    The per-run marker is published as well as the count: an identity-failing run
    carries `highKill: null` — never `false` — because it was never asked, and it
    is in the denominator all the same. `highKillRuns` names the numerator and
    `identityFailedRuns` names the runs that are in the denominator without
    having been asked, so the two published lists reconstruct the rate."""
    bind_study_modules()
    identity_pass = [run for run in runs if run.get("identityPass")]
    identity_fail = [run for run in runs if run.get("admitted")
                     and not run.get("identityPass")]
    # ROUND-1 R1-1: `cut` is this arm's LANGUAGE's cut, and `is_high_kill()`
    # refuses one the run's own denominator cannot reach.
    high = [run for run in runs
            if run.get("identityPass")
            and e4lib.is_high_kill(run["kill"]["killedPaired"],
                                   run["kill"]["paired"], cut["integerCut"])]
    high_names = {run["run"] for run in high}
    for run in runs:
        run["highKill"] = (run["run"] in high_names
                           if run.get("identityPass") else None)
    # ROUND-3 FINDING R3-9. The per-run excluded-case list and its per-arm sum
    # are GONE, not zeroed. §4: "There is no exclusion class, no per-case X1
    # filter and no per-run excluded-case count." The scorer published
    # `x1Excluded` per run, `x1ExcludedCases` per arm and an excluded-case
    # column while the registration said the count did not exist and the smoke
    # record said the field did not exist — three surfaces, two of them false.
    # One surface is adopted: the registration's. What remains is
    # `outOfDomainCases`, which §4 does register, and `e4lib.in_x1()`, which is
    # a measurement helper that gates nothing and is asserted to gate nothing.
    out_of_domain = sum(len(run.get("outOfDomainCases") or []) for run in runs)
    return {
        "arm": arm,
        "language": cut.get("language"),
        "denominator": len(runs),
        "denominatorRule": "§1a/§5: admitted runs (attempted runs whose "
                           "apparatus succeeded). Authoring outcomes stay in as "
                           "not-high-kill and identity-control exclusions stay "
                           "in and are reported; only apparatus codes leave.",
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
        "outOfDomainCases": out_of_domain,
        "outOfDomainRuns": sorted(run["run"] for run in runs
                                  if run.get("outOfDomainCases")),
        "engineRefusedRuns": sorted(run["run"] for run in runs
                                    if run.get("engineRefused")),
        "mutantRefusals": sorted({mutant for run in runs
                                  for mutant in (run.get("kill") or {})
                                  .get("refusedAll", ())}),
        "cut": cut,
        "highKillRuns": sorted(run["run"] for run in high),
        "engineSuppliedKill": engine_supplied_block(arm, runs, engine_supplied,
                                                    reduced_paired_count),
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
    nothing else.

    THEY ARE NOT COMPUTED HERE (round-3 finding R3-8). `endpoints=True` marks the
    contrast's interval PENDING and `stats.fill_intervals()` settles it after
    the decision, for the same reason `stats.rate_block()` stopped computing its
    own Clopper-Pearson bounds in round 2: the sweep used to run the moment the
    contrast was built, which is before the run's final row is known. The
    reviewer's scenario is the proof — gates clear, A = 5/5, C = 0/5, B = 0/0,
    so A−C swept its endpoints, A−B then raised `FM-EMPTY-ARM`, and the attempt
    landed on row 1 with an inferential quantity already computed for it. §5
    prohibits the computation, not merely the printing.

    THE DENOMINATORS MUST BE POSITIVE (round-1 R1-14). An arm with zero admitted
    runs passes E1's floor by definition — `perfect / 0` is not evaluated and the
    gate reads `len(runs) == 0 or ...` — so the control rows let an empty arm
    through, the contrast then became a refusal, and the last row published a
    substantive `INDETERMINATE` over a comparison that could not be made. A
    denominator below the registered minimum is a PIPELINE problem here, which is
    row 1, which is above every substantive row."""
    bind_study_modules()
    left, right = e4_by_arm[left_arm], e4_by_arm[right_arm]
    for arm, entry in ((left_arm, left), (right_arm, right)):
        if entry["denominator"] < decision.REGISTERED_MINIMUM_DENOMINATOR:
            raise stats.StatsError(
                "FM-EMPTY-ARM arm %s has %d admitted runs and the registered "
                "minimum is %d: a contrast over an empty arm is not an interval "
                "that straddles zero, it is no interval at all"
                % (arm, entry["denominator"],
                   decision.REGISTERED_MINIMUM_DENOMINATOR))
    result = stats.excludes_zero(left["highKill"], right["highKill"],
                                 left["denominator"], right["denominator"])
    result["arms"] = [left_arm, right_arm]
    if endpoints:
        result["interval"] = None
        result["intervalState"] = stats.INTERVAL_PENDING
    return result


def registered_contrasts(e4_by_arm: dict, outcome: dict, refusals: dict,
                         gate_causes: list) -> dict:
    """§5's fixed sequence — A−C, then A−B only because A−C decided — with the
    two failure modes kept apart.

    EXTRACTED FROM `main()` FOR ROUND-3 FINDING R3-8, and the extraction is part
    of the fix: the sequence lived inline in a 300-line function, which is why
    the one thing it got wrong could only be found by running an attempt. It is
    driven directly by `tests/test_score_publication.py` now.

    Three outcomes, and the finding is the third:

    * A gating row matched — nothing is computed at all, and the refusal says
      so (round-1 R1-14).
    * The PRIMARY could not be computed — a pipeline problem, because the last
      row's INDETERMINATE is the statement that an interval straddles zero and
      there is no interval (round-1 R1-14's second scenario).
    * The SECONDARY could not be computed after the primary DECIDED — the
      finding. Both contrasts shared one `except`, so `FM-EMPTY-ARM` on A−B
      deleted a primary that had already decided, filed itself under the
      primary's name and landed the attempt on row 1 — over an A−C comparison
      that was made and is sound. §5's decided row registers "A−C interval
      excludes zero -> R1 decided, direction as observed; THEN A−B likewise":
      the sequence is conditional, so the decided row stands and the secondary
      is published as the absent thing it is, WITH its cause.
      `decision.decide()` refuses when that cause is missing, so silence is not
      one of the answers available here."""
    bind_study_modules()
    if gate_causes:
        refusals["contrast"] = (
            "not computed: %d gating row(s) matched above the substantive "
            "rows (%s). §5's row 2 adjudicates R1 in neither direction, and "
            "a direction computed and then withheld is a direction "
            "published" % (len(gate_causes), "; ".join(gate_causes)))
        return {}
    try:
        primary = contrast("A", "C", e4_by_arm)
    except stats.StatsError as error:
        refusals["contrast"] = str(error)
        outcome["pipelineProblems"] = [
            "the registered primary contrast could not be computed: %s" % error]
        return {}
    contrasts = {decision.CONTRAST_PRIMARY: primary}
    if primary["excludesZero"]:
        try:
            contrasts[decision.CONTRAST_SECONDARY] = contrast("A", "B",
                                                              e4_by_arm)
        except stats.StatsError as error:
            refusals["contrastSecondary"] = str(error)
            outcome["secondaryRefusal"] = (
                "the registered secondary contrast %s could not be computed: "
                "%s" % (decision.CONTRAST_SECONDARY, error))
    return contrasts


# --------------------------------------------------------------------------
# scoring one run
# --------------------------------------------------------------------------

def score_run(tools, arm: str, slot: dict, context: dict, workdir: str) -> dict:
    """Extract, admit, evaluate — one slot, in the registered order.

    Never crashes the scoring: a row that makes an engine refuse is a ROW-ERROR
    with its class recorded, and an exception inside one run's evaluation is
    that run's problem and not the population's."""
    bind_study_modules()
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

    # E4: the case enumeration, the registered-domain validation, the registered
    # exclusion filter, the identity control, then the kill vector. The suite is
    # the SECONDARY artifact; a run that emitted no suite pins nothing and is
    # not-high-kill, which section 5 makes an authoring outcome rather than an
    # exclusion.
    language = LANGUAGE_OF_ARM[arm]
    paired_count = len(context["pairedIds"][language])
    if pair["suite"] is None:
        run["code"] = "no-marker-block"
        run["kill"] = {"killedPaired": 0, "paired": paired_count}
        return run
    suite_path = os.path.join(workdir, "suite.%s" % pair["suiteLanguage"])
    with open(suite_path, "w", encoding="utf-8") as handle:
        handle.write(pair["suite"])
    run["suitePath"] = suite_path

    # ROUND-1 R1-3 AND R1-6, and the order is the registration's: enumerate,
    # validate the domain, exclude, and only then run identity or a mutant. Arm
    # A's cases come from the matrix and arms B/C's from the suite's own syntax
    # tree, so the same check reaches all three; a document neither can be read
    # out of is the registered authoring code and never an exception out of the
    # scorer.
    try:
        if arm == "A":
            cases, note = e4lib.load_matrix(suite_path)
            run.update(note)
            named = [(case[0], e4lib.matrix_domain_signature(case[1], case[2]))
                     for case in cases]
            wire = "string"
        else:
            cases = None
            named = e4lib.rego_case_signatures(tools, suite_path, workdir,
                                               context["referenceB"])
            run["caseCount"] = len(named)
            wire = "number"
    except e4lib.MatrixError as error:
        run["code"] = "unparseable-artifact"
        run["suiteRefusal"] = str(error)
        run["kill"] = {"killedPaired": 0, "paired": paired_count}
        return run

    domain_failures = e4lib.domain_failures(named, wire)
    run["outOfDomainCases"] = [failure["case"] for failure in domain_failures]

    if arm == "A":
        # ROUND-3 FINDING R3-9. `partition_excluded()` stays — it is the ONE
        # place a registered exclusion class would ever be applied, and a class
        # applied in two places is two filters — but nothing about it is
        # PUBLISHED any more. The registry is empty (X1 retired, R1-2) and §4
        # registers no per-case filter and no per-run excluded-case count, so
        # `excludedCases`/`x1Excluded` were publishing a measured zero for a
        # thing the registration says does not exist. A non-empty partition is
        # therefore impossible under the registered surface and is refused as
        # the registration mismatch it would be, rather than quietly reported.
        scored_cases, excluded = e4lib.partition_excluded(cases)
        if excluded:
            raise e4lib.MatrixError(
                "E4-EXCLUSION-REGISTRY §4 registers no exclusion class and no "
                "per-case filter, and %d case(s) were partitioned out (%s): a "
                "filter this registration does not carry must not decide which "
                "cases are scored" % (len(excluded), ", ".join(excluded[:3])))
        run["scoredCases"] = scored_cases

    if domain_failures:
        # Identical treatment in all three arms: the run stays in the E4
        # denominator, the identity control records why, and nothing is
        # executed against a point on which the two references are not known to
        # agree.
        run["identityPass"] = False
        run["identityFailures"] = domain_failures[:20]
        run["identityFailureCount"] = len(domain_failures)
        run["kill"] = e4lib.kill_rates({}, context["mutants"][language],
                                       context["pairedIds"][language],
                                       context["engineSupplied"][language])
        return run

    try:
        return _identity_and_kill(tools, arm, run, suite_path, context, workdir)
    except e4lib.ExecutionRefusal as error:
        # ROUND-1 R1-8. A pinned engine refused on a FROZEN artifact. That is
        # not a suite that failed to pin its reference down, so the run is not
        # scored zero and no number derived from it is published as if it were
        # valid: the refusal is recorded here and the `engine-execution-clean`
        # control gate reads it, which adjudicates R1 in neither direction.
        run["engineRefused"] = True
        run["engineRefusal"] = str(error)
        run["identityPass"] = False
        run["identityFailures"] = [{"case": "<engine>",
                                    "expected": "<an answer from the pinned "
                                                "engine>",
                                    "got": "engine-refused"}]
        run["identityFailureCount"] = 1
        run["kill"] = e4lib.kill_rates({}, context["mutants"][language],
                                       context["pairedIds"][language],
                                       context["engineSupplied"][language])
        return run


def _identity_and_kill(tools, arm: str, run: dict, suite_path: str,
                       context: dict, workdir: str) -> dict:
    """The identity control and the kill vector for one run whose cases are
    enumerated, in-domain and filtered."""
    if arm == "A":
        ok, identity_failures = e4lib.identity_arm_a(
            tools, context["referenceA"], run["scoredCases"], workdir)
        run["identityPass"] = ok
        run["identityFailures"] = identity_failures[:20]
        run["identityFailureCount"] = len(identity_failures)
        kill_of = {}
        if ok:
            for mutant in context["mutants"]["jps"]:
                outcome, detail = e4lib.kill_arm_a(tools, mutant["path"],
                                                   run["scoredCases"], workdir)
                kill_of[mutant["id"]] = outcome
                if outcome == e4lib.KILLED:
                    run.setdefault("killingCase", {})[mutant["id"]] = \
                        detail.get("case")
        run["kill"] = e4lib.kill_rates(kill_of, context["mutants"]["jps"],
                                       context["pairedIds"]["jps"],
                                       context["engineSupplied"]["jps"])
    else:
        ok, detail = e4lib.identity_arm_rego(tools, context["referenceB"],
                                             suite_path, workdir)
        run["identityPass"] = ok
        run["identityFailures"] = [] if ok else [detail]
        run["identityFailureCount"] = 0 if ok else 1
        kill_of = {}
        if ok:
            for mutant in context["mutants"]["rego"]:
                outcome, _detail = e4lib.kill_arm_rego(tools, mutant["path"],
                                                       suite_path, workdir)
                kill_of[mutant["id"]] = outcome
        run["kill"] = e4lib.kill_rates(kill_of, context["mutants"]["rego"],
                                       context["pairedIds"]["rego"],
                                       context["engineSupplied"]["rego"])
    return run


# --------------------------------------------------------------------------
# the report
# --------------------------------------------------------------------------

def results_markdown(results: dict) -> str:
    """The published table. Every rate with its denominator, every count that
    section 10 commits to, and the verdict last.

    NOTHING INFERENTIAL IS PRINTED BELOW A FAILED GATE (round-1 R1-14). The
    contrast section used to print "Decided **yes**" and a direction out of a
    contrast the decision rule had already discarded on row 2. It now prints the
    gate causes in that section's place, because a direction a reader can see is
    a direction the study published whatever the verdict line says."""
    bind_study_modules()
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
              "The high-kill cut is PER LANGUAGE, each from its own paired "
              "adequate denominator: " + "; ".join(
                  "%s %s" % (language, block["statement"])
                  for language, block in sorted(
                      (results.get("cuts") or {}).items())), "",
              # R1-19: both group counts, in one sentence, so neither can be
              # read as the other.
              "Pairing: %d witness groups in total, of which %d are shared and "
              "non-degenerate (%d degenerate), covering %d paired adequate JPS "
              "and %d paired adequate Rego mutants."
              % ((results.get("pairing") or {}).get("groups", 0),
                 (results.get("pairing") or {}).get("sharedGroups", 0),
                 (results.get("pairing") or {}).get("degenerateGroups", 0),
                 (results.get("pairing") or {}).get("pairedAdequateJps", 0),
                 (results.get("pairing") or {}).get("pairedAdequateRego", 0)),
              "",
              # ROUND-3 R3-9: the excluded-case column is gone. §4 registers
              # no per-run excluded-case count, so a column of zeros for it
              # taught every reader of RESULTS.md that a filter was applied.
              "| Arm | Language | Cut | High-kill | Denominator | Rate | "
              "95% CI | Identity pass | Out-of-domain cases |",
              "|---|---|---|---|---|---|---|---|---|"]
    for arm in batch.ARMS:
        entry = (results.get("e4") or {}).get(arm)
        if entry is None:
            lines.append("| %s | — | — | — | — | — | — | — | — |" % arm)
            continue
        block = entry["highKillRate"]
        lines.append("| %s | %s | %d | %d | %d | %s | %s | %d | %d |"
                     % (arm, entry.get("language"), entry["cut"]["integerCut"],
                        entry["highKill"], entry["denominator"],
                        _fmt(block["rate"]), _fmt_ci(block["ci95"]),
                        entry["identityPass"],
                        entry.get("outOfDomainCases", 0)))
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
              ""]
    gated_by = results.get("contrastsGatedBy") or []
    if gated_by:
        lines += ["**Not computed and not published.** %d gating row(s) matched "
                  "above §5's substantive rows, and each adjudicates R1 in "
                  "NEITHER direction — so no contrast, no interval and no "
                  "direction exists for this attempt:" % len(gated_by), ""]
        lines += ["- %s" % cause for cause in gated_by]
    else:
        lines += ["| Contrast | Counts | Denominators | Decided | Direction | "
                  "Interval | Construction |", "|---|---|---|---|---|---|---|"]
        for name in (decision.CONTRAST_PRIMARY, decision.CONTRAST_SECONDARY):
            entry = (results.get("contrasts") or {}).get(name)
            if entry is None:
                lines.append("| %s | — | — | — | — | — | — |" % name)
                continue
            interval = entry.get("interval")
            lines.append(
                "| %s | %d vs %d | %d, %d | %s | %s | %s | %s |"
                % (name, entry["left"], entry["right"], entry["nLeft"],
                   entry["nRight"],
                   "**yes**" if entry["excludesZero"] else "no",
                   decision.direction(entry),
                   "—" if interval is None
                   else "[%s, %s]" % (interval["lower"], interval["upper"]),
                   entry.get("constructionName", "—")))
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
    reviewer = results.get("reviewerSet")
    if reviewer:
        lines += ["", "## The sealed reviewer mutant set (§1a, reported "
                  "separately)", "",
                  "Manifest %s; %d reviewer mutants. %s"
                  % (reviewer["manifestSha256"], reviewer["reviewerMutants"],
                     reviewer["movesNothing"]), "",
                  "| Arm | Language | Reviewer mutants | Scored runs |",
                  "|---|---|---|---|"]
        for arm in batch.ARMS:
            entry = (reviewer.get("perArm") or {}).get(arm)
            if entry is None:
                continue
            lines.append("| %s | %s | %d | %d |"
                         % (arm, entry["language"], entry["reviewerMutants"],
                            entry["scoredRuns"]))
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

def _engine_execution_gate(per_arm_runs: dict) -> dict:
    """Section 6's gate for round-1 R1-8: every scored invocation of this
    attempt returned an answer.

    Two kinds of refusal reach it, and both are about FROZEN bytes rather than
    about an author's: a reference the engine refused on during the identity
    control (`e4.ExecutionRefusal`, recorded on the run) and a manifest mutant
    the engine refused on during mutation execution (`kill_rates()`'s
    `refusedAll`). A gate that tolerated either would be a gate that let an
    apparatus failure decide a rate."""
    bind_study_modules()
    identity, mutant = [], []
    for arm in sorted(per_arm_runs):
        for run in per_arm_runs[arm]:
            if run.get("engineRefused"):
                identity.append("%s/%s: %s" % (arm, run["run"],
                                               run.get("engineRefusal")))
            for mutant_id in (run.get("kill") or {}).get("refusedAll", ()):
                mutant.append("%s/%s: %s" % (arm, run["run"], mutant_id))
    return {"held": not identity and not mutant,
            "identityRefusals": sorted(identity)[:20],
            "identityRefusalCount": len(identity),
            "mutantRefusals": sorted(mutant)[:20],
            "mutantRefusalCount": len(mutant),
            "gate": "every scored invocation of the pinned engines on a frozen "
                    "artifact returned an answer; a refusal is an apparatus "
                    "failure and is never a kill and never a suite scoring zero"}


def _declare_unresolved(attempt_root: str, label: str, unfilled: list,
                        pins_raw_sha256, shape: dict) -> int:
    """Publish the registered no-contrast outcome for a DECLARED short batch.

    Round-1 R1-7. Nothing here computes an endpoint, a rate or a contrast: the
    registered price of a shortfall is UNRESOLVED-BY-DESIGN on every level
    verdict and no contrast at all, and the declaration has already been
    validated against the ledger, the registered order and the seals."""
    bind_study_modules()
    declaration = shape["declaration"] or {}
    verdict = decision.decide({
        "pipelineProblems": [],
        "shortfallDeclared": ["%d of %d registered slots, declared: %s"
                              % (shape["present"], shape["registered"],
                                 declaration.get("reason"))],
        "controlGates": {}, "contrasts": {}})
    results = {
        "study": STUDY_NAME,
        "attemptRoot": os.path.basename(os.path.normpath(attempt_root)),
        "label": label,
        "unfilledPins": unfilled,
        "pipelineInvalid": False,
        "pinsRawSha256": pins_raw_sha256,
        "batchShape": shape,
        "e1": None, "e2": None, "e3": None, "e4": None, "e5": None,
        "contrasts": {},
        "contrastsGatedBy": verdict["causes"],
        "controlGates": {},
        "refusals": {"scoring": "the batch was declared short and is DECLARED "
                                "rather than scored; no endpoint, no rate and no "
                                "contrast is computed from a prefix"},
        "decision": verdict,
    }
    write_json(os.path.join(attempt_root, "RESULTS.json"), results)
    write_text(os.path.join(attempt_root, "RESULTS.md"),
               results_markdown(results))
    print("%s (%s)" % (verdict["verdict"], label))
    return 0


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

    # Nothing an earlier invocation established carries into this one: the
    # production path is one attempt per process, and a flag that survived would
    # let a verified run license an unverified one (round-2 R2-8).
    global _VERIFIED
    _VERIFIED = False

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
        # `decision` may still be unbound: this path is reachable before the
        # integrity gate has let anything study-local be imported, which is the
        # whole point of the restructure. The verdict is the registered row-1
        # text either way, and it is spelled from the table when the table is
        # available and from the registration's own words when it is not.
        #
        # ROUND-2 R2-8: the guard is `_VERIFIED`, not a `try`. This block used to
        # call `bind_study_modules()` unconditionally, so the EARLY terminal
        # paths — an unreadable registry, a refused integrity gate — imported
        # `batch` and the whole of `e4lib` in order to print a row-1 verdict
        # whose text is a constant. The one path that exists because the tree
        # cannot be trusted was the path that bound the untrusted tree.
        if _VERIFIED:
            bind_study_modules()
            verdict = decision.decide({"pipelineProblems": [problem]})
        else:
            verdict = {"row": "pipeline-invalid", "rowIndex": 1,
                       "verdict": "R1 inconclusive - pipeline-invalid",
                       "causes": [problem],
                       "note": "the decision table could not be imported; the "
                               "verdict is §5 row 1's registered text"}
        write_json(os.path.join(attempt_root, "RESULTS.json"), {
            "study": STUDY_NAME,
            "attemptRoot": os.path.basename(os.path.normpath(attempt_root)),
            "pipelineInvalid": True,
            "pinsRawSha256": pins_raw_sha256,
            "problem": problem,
            "problems": sorted(problems or []),
            "decision": verdict,
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
        # ROUND-2 FINDING R2-8, and the ORDER is the whole of it. This block used
        # to call `integrity.study_label()` and `integrity.unfilled_pins()` —
        # study-local code — before `integrity.verify()` had established anything
        # about the tree those functions live in, so the label rule and the
        # null-pin guard both ran on unverified bytes. Verification is now the
        # FIRST thing that happens after the registry is parsed, and nothing
        # study-local is invoked above it.
        #
        # What this does NOT establish, stated rather than implied: `score.py`
        # and `integrity.py` are themselves read and executed by the interpreter
        # before either can check anything, so this is a gate against a tree that
        # drifted under an honest operator and not a root of trust against a
        # hostile one. `integrity.py` says the same about `-P`. Closing that gap
        # needs an externally pinned bootstrap that authenticates these two files
        # first, which this study does not have; the honest claim is the narrow
        # one. (Owed to the registration lane: §7's stronger sentence.)
        try:
            integrity.verify(STUDY)
        except integrity.IntegrityError as error:
            return terminal("integrity: %s" % error)
        _VERIFIED = True
        bind_study_modules()

        label = integrity.study_label(pins)
        unfilled = integrity.unfilled_pins(pins)
        if arguments.include_reviewer_set and unfilled:
            return terminal(
                "--include-reviewer-set is refused while any freeze pin is null: "
                + ", ".join(unfilled))
        # ROUND-1 R1-10, the other half of the same rule. The flag was optional
        # and the governing invocation omitted it, so the promised "first
        # executed at the primary attempt" could not happen at all. A REGISTERED
        # attempt executes the sealed set; a PILOT may not, because
        # `reviewerMutantSet` is a freeze pin and the flag refuses above while it
        # is null. OWED TO THE PROSE LANE: the §"freeze and the primary attempt"
        # invocation must carry the flag.
        if label == "REGISTERED" and not arguments.include_reviewer_set:
            return terminal(
                "a REGISTERED attempt runs the sealed reviewer mutant set: "
                "--include-reviewer-set is required, because §1a registers the "
                "set as first executed at the primary attempt and there is only "
                "one primary attempt")

        problems, refusals = [], {}

        # ROUND-2 FINDING R2-7: the sealed set is LOADED AND VALIDATED HERE, and
        # a failure terminates. §1a registers it as "loaded and schema-checked
        # before the attempt without any engine being invoked on it"; the load
        # sat instead at the end of the run, after every endpoint, every gate,
        # every contrast and the decision itself, with its failure caught into
        # `refusals` and the attempt still exiting 0 with `pipelineInvalid:
        # false`. A missing, malformed or digest-invalid mandatory holdout could
        # therefore coexist with a published substantive verdict. It cannot now:
        # nothing below this line runs if the set does not load.
        sealed_set = None
        if arguments.include_reviewer_set:
            try:
                sealed_set = reviewer_lib.load(
                    os.path.join(STUDY, REVIEWER_SET_RELATIVE),
                    (pins.get("reviewerMutantSet") or {}).get("sha256"))
            except reviewer_lib.ReviewerSetError as error:
                return terminal("the sealed reviewer mutant set is mandatory "
                                "for this attempt and does not load: %s" % error)

        tools = engines.Toolchain(pins)
        problems.extend(tools.problems)

        # The frozen artifacts, VERIFIED and not merely counted (round-1 R1-9:
        # "it then checks five artifacts only for existence"). `verify()` above
        # has already established that `harness/STUDY-MANIFEST.sha256` describes
        # the tree it covers exactly and — once the freeze fills the pin — that
        # the manifest is the one the registry pins. Every scorer input is inside
        # that covered set now (`harness/make_manifest.py`: the mutant payloads,
        # both reference implementations and the off-gold certificate joined the
        # registered documents), so what remains here is to require each one to
        # be PRESENT and to be a member of the covered set — an input the
        # manifest does not name is an input nothing verified.
        problems.extend(_registered_inputs_problems())

        entries = batch.schedule_entries()
        try:
            present = slots_present(arguments.batch_root)
            golden_pin = (pins.get("golden") or {}).get("sha256")
            slots = [read_slot(entry, arguments.batch_root, present, golden_pin,
                               pins, pins_raw_sha256)
                     for entry in entries]
            require_distinct_sessions(slots)
            shape = terminality(slots, arguments.batch_root)
        except ScoreError as error:
            problems.append("terminality: %s" % error)
            slots, shape = [], {"present": 0,
                               "registered": batch.REGISTERED_SLOTS,
                               "complete": False, "declared": False,
                               "declaration": None}

        if problems:
            return terminal("pipeline-invalid before any run was scored",
                            problems)

        # ROUND-1 R1-7: a DECLARED short batch is not scored. `terminality()`
        # has just established that the declaration describes this batch — its
        # exact member set, §2's registered constants, the prefix's length and
        # last index, the ledger's chain and its agreement with the registered
        # call order, the slot/seal bijection and the last slot. Having
        # established it, the scorer stops: the registered price of a shortfall
        # is UNRESOLVED-BY-DESIGN on every level verdict and no contrast at all,
        # and computing the endpoints anyway is how an incomplete batch becomes
        # a result with a caveat.
        if shape["declared"]:
            return _declare_unresolved(attempt_root, label, unfilled,
                                       pins_raw_sha256, shape)

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
        # ROUND-1 R1-1: ONE CUT PER LANGUAGE, each from its own paired-adequate
        # denominator, each asserted reachable. The single JPS-derived cut this
        # replaces was handed to every arm while each arm's kill denominator
        # stayed language-specific, so a PERFECT Rego suite could not reach it
        # and the primary endpoint was impossible for arms B and C.
        cuts = e4lib.high_kill_cuts(paired_ids)
        for language in ("jps", "rego"):
            print("tau cut (%s): %s" % (language, cuts[language]["statement"]))
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
        reduced_paired = {
            language: len([record for record in mutants[language]
                           if not record["notAdequate"]
                           and record["id"] in paired_ids[language]
                           and record["id"] not in set(engine_supplied[language]
                                                       or ())])
            for language in ("jps", "rego")}
        context = {"gold": gold, "mutants": mutants, "pairedIds": paired_ids,
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
            language = LANGUAGE_OF_ARM[arm]
            e4_by_arm[arm] = e4_endpoint(
                arm, runs, cuts[language], engine_supplied[language],
                reduced_paired[language])

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
            # ROUND-1 R1-8: every scored invocation of this attempt returned an
            # answer. A pinned engine refusing on a frozen reference or a frozen
            # mutant is an apparatus failure, and neither counting it as a kill
            # nor scoring the suite zero for it is honest — so it adjudicates R1
            # in neither direction, above every substantive row.
            "engine-execution-clean": _engine_execution_gate(per_arm_runs),
        }

        # ROUND-1 R1-14: NOTHING INFERENTIAL IS COMPUTED BELOW A FAILED GATE.
        # The abstract table is ordered and its rows are exhaustive, but the
        # publisher used to compute A-C and A-B, print "Decided yes" and print a
        # direction while `decide()` correctly selected the control-gate row —
        # which is not what "adjudicates R1 in neither direction" means. The
        # gating predicate is derived from the table itself
        # (`decision.gate_causes()`), so a row added there cannot be a row this
        # forgets.
        outcome = {"pipelineProblems": [], "shortfallDeclared": [],
                   "controlGates": gates, "contrasts": {}}
        gate_causes = decision.gate_causes(outcome)
        contrasts = registered_contrasts(e4_by_arm, outcome, refusals,
                                         gate_causes)
        outcome["contrasts"] = contrasts
        verdict = decision.decide(outcome)

        # ROUND-2 R2-12, and this is the only place any interval is computed.
        # §5: "No inferential quantity is computed, let alone published, at or
        # above row 3." The marginal Clopper-Pearson bounds used to be computed
        # inside each endpoint — before a single gate had been read — and printed
        # whatever the row. The gate rows are evaluated above; the bounds are
        # settled here, once, for every pending rate block in the whole result,
        # and only when the outcome reached the substantive rows.
        interval_licence = not gate_causes and not outcome["pipelineProblems"]
        suppression = None
        if not interval_licence:
            suppression = (
                "§5: no inferential quantity is computed at or above row 3; "
                "%d gating row(s) matched (%s)"
                % (len(gate_causes) + len(outcome["pipelineProblems"]),
                   "; ".join(gate_causes + outcome["pipelineProblems"])))
            refusals["intervals"] = suppression

        # ROUND-1 R1-10. Executed exactly once, here, at the primary attempt —
        # after every registered number is already fixed, so nothing it produces
        # can reach one. `outcome` above is the whole of the decision's input and
        # carries no member this block writes.
        reviewer_set = None
        if sealed_set is not None:
            try:
                reviewer_set = reviewer_lib.execute(
                    tools, sealed_set, per_arm_runs, context, batch.ARMS,
                    LANGUAGE_OF_ARM, workspace)
            except reviewer_lib.ReviewerSetError as error:
                # R2-7: two-sided. The load is fatal above and the execution is
                # fatal here, because "first executed at the primary attempt" is
                # a promise about this attempt and an attempt that published
                # without it is an attempt that did not keep it.
                return terminal("the sealed reviewer mutant set did not execute "
                                "at this attempt: %s" % error)
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
            # ROUND-1 R1-19. `groups` is EVERY witness-key group, shared or not;
            # section 4 registers the SHARED, non-degenerate groups as the thing
            # the paired subset comes from, and one number published under one
            # name was read as either. Both are published, with the degenerate
            # group counted out loud rather than subtracted silently.
            "pairing": {"groups": len(pairing),
                        "sharedGroups": sum(1 for row in pairing
                                            if row["countedInPairedSubset"]),
                        "degenerateGroups": sum(1 for row in pairing
                                                if row["degenerate"]),
                        "pairedAdequateJps": len(paired_ids["jps"]),
                        "pairedAdequateRego": len(paired_ids["rego"]),
                        "unpairable": e4lib.unpairable(mutants, paired_ids)},
            "cuts": cuts,
            "e1": e1, "e2": e2, "e3": e3, "e4": e4_by_arm, "e5": e5,
            "contrasts": contrasts,
            "contrastsGatedBy": gate_causes,
            "controlGates": gates,
            "refusals": refusals,
            "perArmRuns": [
                {key: value for key, value in run.items()
                 # Two members are working state, not published bytes: a
                 # workspace path is an absolute path and a scored case list is
                 # the author's own input document repeated per mutant.
                 if key not in ("suitePath", "scoredCases")}
                for arm in batch.ARMS for run in per_arm_runs[arm]],
            "reviewerSet": reviewer_set,
            "decision": verdict,
        }
        results["intervalsPublished"] = {
            "licensed": interval_licence,
            "settled": stats.fill_intervals(results, interval_licence,
                                            suppression),
            "reason": suppression,
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
