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

WHAT THIS FILE DELIBERATELY DOES NOT DO (PREREGISTRATION.md §7's deltas)
------------------------------------------------------------------------
* **It computes no threshold and reads none** (§7 delta 2, §5.1's "No cut, no τ,
  no dichotomy"). 019's E4 was a per-arm HIGH-KILL RUN RATE over an integer cut
  derived from tau = 0.95; `e4_endpoint()` now publishes coverage sets and
  per-language denominators and nothing a run is judged AGAINST.
* **It weights nothing.** §5.2's eighteen members, L2c's offset estimator, the
  two permutation schemes, the IU verdict, the drop-a-pole table and the BCa
  intervals are `e4lib/family.py`'s (§7 delta 5). This file evaluates that
  module behind `registered_family()` and REFUSES when it is absent, because
  §5.4's intersection-union logic makes a smaller family the anti-conservative
  direction — proceeding on the members that happen to import would make the
  claim easier.
* **It applies no author-side control gate** (§5.7, M-23 option (a)). There is
  no `E1_FLOOR`, no `floorHeld` member and no `e1-floor` row: §5.7 derives both
  the gate's 1.3–6.1 % spurious refusal of arm A at 019-scale N and the ~2,926
  degraded runs its certification would need, and an uncertified gate is not
  registered as if certified.
* **It never writes a run record whose schema cannot tell "nothing evaluated"
  from "everything killed"** (§7 delta 1). `e4lib.require_survivor_schema()`
  guards every write of a `kill` block.

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

STUDY_NAME = "020-test-pinning-across-representations"

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

# §5.7, ruled 2026-08-23 (M-23, option (a)): THERE IS NO AUTHOR-SIDE CONTROL
# GATE and no `E1_FLOOR` constant. 019's existence gate was a max statistic —
# it fires iff NO admitted run clears, so P(fire) = (1 − p)ⁿ and its stringency
# runs the wrong way in n, which differs by arm. It spuriously refused arm A
# with probability 1.3–6.1 % at 019-scale N even with a perfect stimulus, and
# certifying P(fire) ≥ 0.95 at N = 50 would need ~2,926 degraded runs (~162 h).
# An uncertified gate is not registered as if certified, so E1 is fully
# descriptive (§5.1), the `e1-floor` row leaves the decision table (§5.9), and
# the derived threshold survives only as C3's PRE-FREEZE go/no-go (§2a.4),
# which is `calibration/derive_floor.py`'s and is never read at attempt time.
#
# Section 2's registered timeout cap IS a control-gate row: breaching it
# adjudicates R1 in neither direction.
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

    **FULLY DESCRIPTIVE, WITH NO FLOOR** (§5.1, §5.7). 019 registered a floor
    and adjudicated its attempt `control-gate-failed: e1-floor` on it; §5.7
    rules that gate out, on two facts it derives rather than asserts — the gate
    spuriously refuses arm A at 1.3–6.1 % even with a perfect stimulus, and it
    cannot be empirically certified at any affordable n, because it is a max
    statistic over a stochastic authoring process. So 019's finding — *arm A
    never achieves perfect gold agreement* — is a REPORTED RESULT here rather
    than a study-killer, and this block carries no `floor` and no `floorHeld`:
    a reader cannot read a gate off a record that does not contain one.

    §5.1 registers the ITT denominator and the 117-row support, with the 110-row
    support published beside it; the common-mode threat the existence gate named
    is a BYTE threat and is caught deterministically by the prompt, prose,
    golden-context and reference digests, which fire with probability 1."""
    bind_study_modules()
    perfect = sum(1 for run in runs if run.get("goldPerfect"))
    block = stats.rate_block(perfect, len(runs), "admitted runs (ITT)")
    return {"arm": arm, "perfect": perfect, "runs": len(runs),
            "rate": block,
            "gates": "nothing (§5.7, M-23 option (a): there is no author-side "
                     "control gate and no e1-floor row in §5.9)"}


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
        for failure in run.get("referenceIdentityFailures") or []:
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
    paired-subset kill totals BOTH ways.

    §5.2 promotes the split from a description to a FAMILY AXIS: the exclusion
    drops 12 of 69 paired JPS mutants and 0 of 62 paired Rego, which is
    entirely one-sided and is an arm-blind reason it could matter, so BOTH
    columns are members and neither is "the" column. §7 delta 2 removes the
    reduced integer cut that used to sit on top of the excluded column."""
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
    # every run of an arm is scored against the same paired subset, so it is
    # passed in from the corpus rather than maximised over the runs (`max()`
    # over the runs was the same number whenever any run existed and was
    # undefined when none did, which is a second way to compute a constant).
    return {
        "arm": arm, "registered": True, "listedMutants": len(listed),
        "killsIncluded": {"killed": killed, "paired": paired},
        "killsExcluded": {"killed": killed_reduced, "paired": reduced},
        "reducedPairedDenominator": reduced_paired_count,
        "note": "§5.2's engine-supplied-kill AXIS: both columns are family "
                "members, so both are published and neither is the "
                "descriptive one. §7 delta 2: there is no reduced cut and "
                "no high-kill count under either column, because 020 registers "
                "no threshold at all.",
    }


def e4_endpoint(arm: str, runs: list, denominator: dict, engine_supplied=None,
                reduced_paired_count: int = 0, classes: list = ()) -> dict:
    """E4 (primary) — the per-arm record the eighteen-member family is computed
    FROM. §7 delta 2: no cut, no threshold, no dichotomy.

    §5.1 registers the primary endpoint as, per admitted run, "the run's
    coverage set S over the 33 shared classes", with "each of §5.2's eighteen
    members a weighted count over S". This function therefore publishes the
    per-run coverage sets and the per-arm denominators and computes NO member:
    the weighting, the offset, the permutation tests and the IU verdict are
    `e4lib/family.py`'s (§7 delta 5). Two things are kept apart on purpose —
    what was MEASURED (here) and how it is WEIGHTED (there) — because 019's
    single registered quantity fused them and the design phase then had to
    choose the weighting after seeing arm-labelled outcomes (§5.5's ledger).

    Section 5's denominator rule, in code and stated in the record: "Runs
    carrying authoring-outcome codes remain in the ITT members' denominators
    scoring 0; only apparatus codes leave." The identity control is a
    first-class per-arm RATE and identity-excluded runs are reported, never
    silently dropped: they define the per-protocol population and stay in the
    ITT one.

    ROUND-2 FINDING R2-2 of Study 019, carried: the denominator here is
    `len(runs)` — §1a's "attempted runs whose apparatus succeeded" — and not the
    identity-passing subset. Both populations are §5.2 family poles now, so the
    number that used to be one reading of one rule is two published members, and
    `perProtocolDenominator` names the other one explicitly rather than leaving
    a reader to subtract.

    `denominator` is this arm's LANGUAGE's entry from
    `e4lib.paired_denominators()`. It carries a count and a lattice and no
    threshold; `is_high_kill()` and its cut argument are gone, so there is no
    per-language number a run is judged AGAINST — only the language's own
    denominator the run is scored OVER (019's R1-1 defect, made structurally
    impossible rather than repaired)."""
    bind_study_modules()
    # ROUND-2 FINDING R2-1, the tri-state read explicitly at both poles. `is
    # True` and `is False` mean the relation was EVALUATED; `is None` means a
    # pinned engine never answered, which §6 registers as "neither a kill nor
    # an identity failure". The truthiness reads these two lines used to carry
    # put every engine-refused run in `identity_fail`, in `identityRate`'s
    # complement and in `identityFailedRuns` — a suite blamed for the
    # apparatus's silence.
    identity_pass = [run for run in runs
                     if run.get("referenceIdentityPass") is True]
    identity_fail = [run for run in runs if run.get("admitted")
                     and run.get("referenceIdentityPass") is False]
    identity_not_answered = [run for run in runs if run.get("admitted")
                             and run.get("referenceIdentityPass") is None]
    own_policy_pass = [run for run in runs
                       if (run.get("ownPolicyIdentity") or {}).get("pass")]
    # §5.2's coverage rule, per run, over the SHARED classes. A run that was
    # never executed has an empty coverage set and says so in
    # `coverage.unevaluatedClasses`; that is the same distinction the survivor
    # vector draws one level down, and it is drawn in both places because §5.2's
    # Fact 1 is that collapsing it moved 019's headline contrast by 0.0526.
    coverage_counts = []
    for run in runs:
        block = run.get("coverage")
        coverage_counts.append(0 if block is None else block["coveredCount"])
    out_of_domain = sum(len(run.get("outOfDomainCases") or []) for run in runs)
    return {
        "arm": arm,
        "language": denominator.get("language"),
        "denominator": len(runs),
        "denominatorRule": "§1a/§5.1: admitted runs (attempted runs whose "
                           "apparatus succeeded). Authoring outcomes stay in "
                           "the ITT members' denominators scoring 0 and "
                           "identity-control exclusions stay in and are "
                           "reported; only apparatus codes leave.",
        "perProtocolDenominator": len(identity_pass),
        "perProtocolRule": "§5.2: the per-protocol pole is the "
                           "referenceIdentity-passing runs. It is a family "
                           "member's population, not a filter applied before "
                           "the endpoint.",
        "referenceIdentityPass": len(identity_pass),
        "identityFail": len(identity_fail),
        # R2-1: the rate's denominator is the runs the relation was EVALUATED
        # for. A run the engine never answered about is counted beside the
        # rate under its own name, exactly as R1-14 did for E6's not-asked
        # runs — never diluted into it, and never counted against the author.
        "identityRate": stats.rate_block(
            len(identity_pass), len(runs) - len(identity_not_answered),
            "admitted runs the reference relation was evaluated for (R2-1: a "
            "run whose pinned engine never answered leaves this denominator "
            "and is published beside it as identityApparatusRefused)"),
        "identityApparatusRefused": len(identity_not_answered),
        "identityApparatusRefusedRuns": sorted(
            run["run"] for run in identity_not_answered),
        "identityFailedRuns": sorted(run["run"] for run in identity_fail),
        # E6 (§5.1, §7 delta 4). The SECOND named relation, published per arm
        # beside the first and gating nothing. The conjunction is §5.8's Tier D
        # population disposition: the population 020 did NOT register, made
        # visible beside the one it did. R1-14: the RATE's denominator is the
        # runs E6 actually answered for — a domain-failing run returns before
        # E6 and an E6 engine refusal is apparatus — and the not-asked count
        # is printed beside it rather than diluted into the rate.
        "ownPolicyIdentityPass": len(own_policy_pass),
        "ownPolicyIdentityAnswered": len(
            [run for run in runs if run.get("ownPolicyIdentity") is not None]),
        "ownPolicyIdentityNotAsked": len(
            [run for run in runs if run.get("ownPolicyIdentity") is None]),
        "ownPolicyIdentityRate": stats.rate_block(
            len(own_policy_pass),
            len([run for run in runs
                 if run.get("ownPolicyIdentity") is not None]),
            "runs E6 answered for (R1-14: not-asked runs are counted beside "
            "the rate, not inside it; rate_block publishes a null rate over "
            "an empty denominator rather than inventing one)"),
        "bothIdentitiesPass": len([run for run in runs
                                   if run.get("referenceIdentityPass") is True
                                   and (run.get("ownPolicyIdentity")
                                        or {}).get("pass")]),
        "coverageCounts": coverage_counts,
        "sharedClassCount": len(classes),
        "pairedDenominator": denominator,
        "outOfDomainCases": out_of_domain,
        "outOfDomainRuns": sorted(run["run"] for run in runs
                                  if run.get("outOfDomainCases")),
        "engineRefusedRuns": sorted(run["run"] for run in runs
                                    if run.get("engineRefused")),
        "mutantRefusals": sorted({mutant for run in runs
                                  for mutant in (run.get("kill") or {})
                                  .get("refusedAll", ())}),
        "engineSuppliedKill": engine_supplied_block(arm, runs, engine_supplied,
                                                    reduced_paired_count),
    }


def family_module():
    """`e4lib.family`, or None — §7 delta 5's module, imported by name at the
    one place the decision path needs it.

    It is a SEPARATE delta and a separate module on purpose: §5.2's eighteen
    members, L2c's offset estimator, the two permutation schemes and the IU
    verdict are the analysis, and this file is the publisher. The import is
    guarded rather than assumed so that the absence is a NAMED pipeline problem
    on §5.9 row 1 — never an attempt that quietly reaches row 5 and publishes
    INDETERMINATE-BY-DISAGREEMENT over a family that was never evaluated."""
    bind_study_modules()
    try:
        from e4lib import family as family_lib      # noqa: WPS433 (deferred)
    except ImportError:
        return None
    return family_lib


def registered_family(e4_by_arm: dict, per_arm_runs: dict, context: dict,
                      outcome: dict, refusals: dict, gate_causes: list) -> dict:
    """§5.9 row 4 and §5.4's intersection-union rule, in the registered fixed
    sequence: A−C, then A−B only because A−C claimed.

    THERE IS NO INTERVAL AND NO CUT HERE (§7 delta 2, §5.1 "No cut, no τ, no
    dichotomy"). 019's row 3 read a single binomial contrast's zero-exclusion
    over a high-kill run count; 020's row 4 reads eighteen members' signs and
    p-values and fires only on unanimity in both. The IU logic makes that a
    level-≤α test with no multiplicity correction (§5.4) and makes REMOVING a
    member the anti-conservative direction — which is why membership is
    append-only after registration and why an absent family scorer is a
    pipeline problem rather than a smaller family.

    Three outcomes, carried from 019's round-3 R3-8 because the failure mode is
    identical under the new row:

    * A gating row matched — nothing inferential is computed at all (§5.9's "No
      inferential quantity is computed, let alone published, at or above row
      3"), and the refusal says so.
    * The PRIMARY family could not be evaluated — a pipeline problem, because
      §5.9's last row is INDETERMINATE-BY-**DISAGREEMENT** and eighteen members
      that were never computed did not disagree. "An absent primary contrast is
      not a disagreeing one and never reaches row 5."
    * The SECONDARY could not be evaluated after the primary CLAIMED — published
      as the absent thing it is, WITH its cause, because `decision.decide()`
      refuses when that cause is missing."""
    bind_study_modules()
    if gate_causes:
        refusals["family"] = (
            "not computed: %d gating row(s) matched above the substantive "
            "rows (%s). §5.9 row 3 adjudicates R1 in neither direction, and "
            "a direction computed and then withheld is a direction "
            "published" % (len(gate_causes), "; ".join(gate_causes)))
        return {}
    family_lib = family_module()
    if family_lib is None:
        refusals["family"] = (
            "e4lib/family.py is absent: §5.2 registers eighteen members and "
            "§5.4's intersection-union rule makes a SMALLER family the "
            "anti-conservative direction, so an attempt does not proceed on "
            "the members that happen to be importable")
        outcome["pipelineProblems"] = [
            "the registered eighteen-member sensitivity family (§5.2, §7 delta "
            "5) could not be evaluated: e4lib/family.py is absent"]
        return {}
    verdicts, reports = {}, {}
    try:
        corpus = family_lib.build_corpus(context["pairing"],
                                         context["engineSupplied"])
        # ROUND-2 FINDING R2-1, at the one call site where the tri-state
        # decides the CLAIM. This read was `bool(run.get(...))`, and `bool(None)`
        # is False — so after the apparatus repair an engine-refused run would
        # still have entered all eighteen members as an identity-FAILING unit:
        # out of the per-protocol pole for the wrong reason and inside the ITT
        # pole scoring zero. §1a excludes apparatus failures from every
        # population, and this is the line where "every population" means the
        # family R1 is computed over. A run the relation was never evaluated
        # for is not a unit; it is already outside `per_arm_runs` when the
        # refusal was a scoring-time invocation, and this guard covers the
        # remaining path — an `ExecutionRefusal` at the identity step, which
        # keeps the run in the population for §6's gate to read.
        units = [family_lib.unit_from_kill_record(
                     run["run"], arm, run.get("referenceIdentityPass") is True,
                     run.get("caseCount"), run.get("kill"), corpus)
                 for arm in batch.ARMS for run in per_arm_runs[arm]
                 if run.get("referenceIdentityPass") is not None]
        not_answered = [run["run"] for arm in batch.ARMS
                        for run in per_arm_runs[arm]
                        if run.get("referenceIdentityPass") is None]
        if not_answered:
            # Stated, never silent: a family computed over fewer units than the
            # arm holds is a fact the reader is owed beside the verdict.
            outcome["familyUnitsExcluded"] = {
                "runs": sorted(not_answered),
                "why": "§1a/§6 (R2-1): the reference relation was never "
                       "evaluated for these runs because a pinned engine "
                       "produced no answer, so they are apparatus and enter "
                       "no member's population. §6's own engine gate reads "
                       "the same fact and adjudicates R1 in neither "
                       "direction.",
            }
    except Exception as error:                       # noqa: BLE001 (named below)
        refusals["family"] = "%s: %s" % (type(error).__name__, error)
        outcome["pipelineProblems"] = [
            "the registered family's units could not be built from the scored "
            "runs: %s" % error]
        return {}
    for left, right, key in (("A", "C", decision.CONTRAST_PRIMARY),
                             ("A", "B", decision.CONTRAST_SECONDARY)):
        if key == decision.CONTRAST_SECONDARY \
                and not verdicts[decision.CONTRAST_PRIMARY].get("claim"):
            break
        try:
            # R1-5: the permutation seed and the BCa pair come from the
            # registry, so the published intervals rest on registered numbers
            # rather than on bca_interval()'s refusal.
            family_pins = (context.get("pins") or {}).get("family") or {}
            kwargs = {"bca_resamples": family_pins.get("bcaResamples"),
                      "bca_seed": family_pins.get("bcaSeed")}
            if family_pins.get("permutationSeed") is not None:
                kwargs["seed"] = family_pins["permutationSeed"]
            report = family_lib.family_report(units, corpus, left, right,
                                              **kwargs)
        except Exception as error:                   # noqa: BLE001 (named below)
            where = ("family" if key == decision.CONTRAST_PRIMARY
                     else "familySecondary")
            refusals[where] = "%s: %s" % (type(error).__name__, error)
            if key == decision.CONTRAST_PRIMARY:
                outcome["pipelineProblems"] = [
                    "the registered primary family %s could not be evaluated: "
                    "%s" % (key, error)]
                return {}
            outcome["secondaryRefusal"] = (
                "the registered secondary family %s could not be evaluated: "
                "%s" % (key, error))
            break
        reports[key] = report
        # The DECISION reads the verdict block, whose shape `e4lib/decision.py`
        # owns; the member rows travel beside it so `results_markdown()` can
        # print §5.5's mandatory reprint. Both come from one call, so the table
        # a reader sees and the verdict the rule read cannot be two evaluations.
        verdict_block = dict(report["verdict"])
        verdict_block["members"] = report["members"]
        verdicts[key] = verdict_block
    outcome["familyReports"] = reports
    return verdicts


# --------------------------------------------------------------------------
# scoring one run
# --------------------------------------------------------------------------

def _empty_kill(context: dict, language: str) -> dict:
    """The kill block of a run that executed NO mutant, written through the same
    function every other run's block is written through.

    §7 delta 1, and this is the half that is easy to miss: 019 wrote
    `{"killedPaired": 0, "paired": N}` by hand on the no-suite and
    unparseable-suite paths, so those records carried neither a survivor list
    nor a vector — and a reader who assumed the survivor list was total read
    them as perfect. Building the block from `kill_rates()` with an EMPTY kill
    map makes every entry of the vector `not-evaluated`, which is exactly what
    happened, said in the record."""
    return e4lib.kill_rates({}, context["mutants"][language],
                            context["pairedIds"][language],
                            context["engineSupplied"][language])


def _run_record(arm: str, slot: dict) -> dict:
    """ROUND-2 FINDING R2-5: the TOTAL record every one of `score_run()`'s exits
    inherits, so the holdout's consumer can read a member without asking which
    branch produced the run.

    R2-5's mechanism: `reviewer.execute()` requires `suitePath` on every
    candidate, `score_run()` set it only after a suite was written, and three
    ORDINARY outcomes — a wrapper apparatus code, any of the six authoring
    codes, and a completion with no suite — omitted it. One such run in 180
    made the mandatory holdout execution fatal and ended the attempt.

    The two members added here are exactly the two the holdout reads and the
    two `main()` strips before publication, so no published byte moves.

    WHAT IS DELIBERATELY *NOT* TOTALISED, and why the constructor stops at two:
    `caseCount`'s ABSENCE is a registered state distinct from 0 (see the E4
    block below and `e4.require_survivor_schema()`'s third condition) — a
    `None` there would be a third spelling of a distinction §5.2 registers.
    Same for `kill`, `coverage`, `goldVector` and `policyBytes`: each is absent
    on some path because the state it describes did not happen."""
    return {
        "run": "run-%03d" % slot["slotIndex"], "arm": arm,
        "code": slot["code"], "admitted": False, "goldPerfect": False,
        # §7 delta 4: TWO NAMED RELATIONS, and ROUND-1 FINDING R1-13's rename
        # actually landed: `referenceIdentityPass` is `referenceIdentity` and
        # nothing else; E6's answer lives under its own name and is None until
        # the extra invocation has been made, so "not asked" and "asked and
        # failed" are different bytes.
        #
        # ROUND-2 FINDING R2-1 makes this member TRI-STATE: True, False, and
        # None for "the pinned engine never answered, so the relation was not
        # evaluated". False now means the relation was evaluated and did not
        # hold — which is what every consumer already believed it meant.
        "referenceIdentityPass": False,
        "identityRelation": e4lib.REFERENCE_IDENTITY,
        "ownPolicyIdentity": None,
        "suitePath": None, "scoredCases": None,
        "durationSeconds": slot["durationSeconds"],
    }


def score_run(tools, arm: str, slot: dict, context: dict, workdir: str) -> dict:
    """Extract, admit, evaluate — one slot, in the registered order.

    Never crashes the scoring: a row that makes an engine refuse is a ROW-ERROR
    with its class recorded, and an exception inside one run's evaluation is
    that run's problem and not the population's. ROUND-2 FINDING R2-1 made that
    sentence true: a pinned-engine no-answer inside the DETECTOR or the matrix
    parser used to leave this function as an untyped exception and end the
    attempt through `main()`'s last-resort handler."""
    bind_study_modules()
    run = _run_record(arm, slot)
    if slot["code"] is not None:
        return run
    pair = extract.extract_pair(slot["completion"] or "", arm)
    run["policyBytes"] = pair["policyBytes"]
    run["suiteBytes"] = pair["suiteBytes"]
    run["suitePresent"] = pair["suite"] is not None
    # §7 delta 3, and the scorer spells NO CODE: it reads §1a's partition from
    # `batch.CODE_PARTITION` and hands admission the registered state of §3.2's
    # kill switch. `presenceIdiomGuard` in the context OVERRIDES the registry
    # (the harness tests drive both sides of the switch that way); absent, it is
    # `None`, and `admit()` resolves the switch from `harness/PINS.json`'s
    # `presenceIdiomGuard.registered` — fail-shut toward NOT registered, so a
    # registry that never published the power analysis cannot emit the code.
    try:
        artifact, code, detail = admit_lib.admit(
            tools, arm, pair["policy"], workdir,
            context.get("presenceIdiomGuard"))
    except engines.EngineError as error:
        # R1-1: the pinned engine never answered about this artifact — an
        # APPARATUS event assigned at scoring time. The run leaves every
        # denominator (the caller partitions on this code) and §6's gate
        # reads it; no authoring code is invented for an answer that does
        # not exist.
        run["code"] = "engine-invocation-refused"
        run["invocationRefusal"] = str(error)
        return run
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
        # R1-1: a ROW-ERROR whose class says the engine NEVER ANSWERED (a
        # timeout, an invocation failure, an unreadable stream) is apparatus —
        # unlike an evaluator's own error document, which is an answer about
        # the authored artifact and stays an authored gold failure.
        if got[0] == "ROW-ERROR" and (
                got[1] in (engines.INVOCATION_TIMEOUT,
                           engines.UNREADABLE_INVOCATION,
                           "non-json-payload")
                or str(got[1]).startswith(engines.INVOCATION_FAILURE)):
            run["code"] = "engine-invocation-refused"
            run["invocationRefusal"] = ("E1 row %s: %s"
                                        % (row.get("id"), got[1]))
            return run
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
    if pair["suite"] is None:
        run["code"] = "no-marker-block"
        # §5.2's pinned definition 4 and §7 delta 1: `caseCount` is emitted for
        # every admitted run WITH A SUITE. This run has none, so the member is
        # deliberately absent rather than 0 — 0 is the registered value for a
        # suite that parses to no cases, and a run with no suite at all is a
        # different state. `require_survivor_schema()` reads `suitePresent`, so
        # the two are told apart by the schema and not by a convention.
        run["kill"] = _empty_kill(context, language)
        return e4lib.require_survivor_schema(run)
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
            # §5.2 definition 4: EVERY admitted run with a suite carries the
            # number, arm A included. 019 emitted it for arms B and C only,
            # which made the ANCOVA members undefined for exactly the arm whose
            # covariate mean the adjustment is evaluated at.
            run["caseCount"] = len(named)
            wire = "string"
        else:
            cases = None
            named = e4lib.rego_case_signatures(tools, suite_path, workdir,
                                               context["referenceB"])
            run["caseCount"] = len(named)
            wire = "number"
    except engines.EngineError as error:
        # ROUND-2 FINDING R2-1, and the ORDER matters: this handler precedes
        # `MatrixError` because a pinned-engine no-answer inside the matrix
        # parser used to arrive as `opa parse` exit 124 and leave as the
        # AUTHORING code `unparseable-artifact` — a statement about the author
        # made out of an invocation that produced nothing.
        run["code"] = "engine-invocation-refused"
        run["invocationRefusal"] = str(error)
        return run
    except e4lib.MatrixError as error:
        run["code"] = "unparseable-artifact"
        run["suiteRefusal"] = str(error)
        # The suite is present and did not parse to cases: §5.2 pins
        # `caseCount` = 0 for exactly that state, and 019's six runs that
        # carried a kill block with neither a survivor list nor a caseCount
        # (B run-026/027/032/036, C run-035/050) are the reason it is written
        # here rather than inferred later from an absence.
        run["caseCount"] = 0
        run["kill"] = _empty_kill(context, language)
        return e4lib.require_survivor_schema(run)

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
        run["referenceIdentityPass"] = False
        run["referenceIdentityFailures"] = domain_failures[:20]
        run["referenceIdentityFailureCount"] = len(domain_failures)
        run["kill"] = e4lib.kill_rates({}, context["mutants"][language],
                                       context["pairedIds"][language],
                                       context["engineSupplied"][language])
        run["coverage"] = e4lib.coverage_classes({}, context["classes"],
                                                 language)
        return e4lib.require_survivor_schema(run)

    try:
        return e4lib.require_survivor_schema(
            _identity_and_kill(tools, arm, run, artifact, suite_path, context,
                               workdir))
    except engines.EngineError as error:
        # ROUND-2 FINDING R2-1, ordered before `ExecutionRefusal` for the same
        # reason as above: an invocation that produced no answer is apparatus,
        # and it leaves by the one typed door §1a names.
        run["code"] = "engine-invocation-refused"
        run["invocationRefusal"] = str(error)
        return run
    except e4lib.ExecutionRefusal as error:
        # ROUND-1 R1-8. A pinned engine refused on a FROZEN artifact. That is
        # not a suite that failed to pin its reference down, so the run is not
        # scored zero and no number derived from it is published as if it were
        # valid: the refusal is recorded here and the `engine-execution-clean`
        # control gate reads it, which adjudicates R1 in neither direction.
        #
        # ROUND-2 FINDING R2-1 removed the last place this state still lied.
        # The run used to carry `referenceIdentityPass: False` and a FABRICATED
        # failure row reading `got: "engine-refused"`, so §6's own sentence —
        # "it is neither a kill nor an identity failure" — was contradicted by
        # the record it produced: the run entered `identityRate`'s complement,
        # `identityFailedRuns` and E3's taxonomy as a failing suite. The member
        # is now None, which is the third state the relation actually has: not
        # evaluated. Consumers that mean "evaluated and did not hold" test
        # `is False`.
        run["engineRefused"] = True
        run["engineRefusal"] = str(error)
        run["referenceIdentityPass"] = None
        run["referenceIdentityNotAnswered"] = True
        run["kill"] = e4lib.kill_rates({}, context["mutants"][language],
                                       context["pairedIds"][language],
                                       context["engineSupplied"][language])
        run["coverage"] = e4lib.coverage_classes({}, context["classes"],
                                                 language)
        return e4lib.require_survivor_schema(run)


def _identity_and_kill(tools, arm: str, run: dict, artifact: str,
                       suite_path: str, context: dict, workdir: str) -> dict:
    """The TWO identity relations and the kill vector for one run whose cases
    are enumerated, in-domain and filtered.

    §7 delta 4: `referenceIdentity` and `ownPolicyIdentity` are computed by two
    named functions into two named members. The kill vector is executed only
    when `referenceIdentity` holds — a suite that does not pin the frozen
    reference down is not asked about mutants — and E6 is computed for every
    admitted run regardless, because it gates nothing and its whole purpose is
    to describe the population 020 did not register (§5.1, §5.8)."""
    language = LANGUAGE_OF_ARM[arm]
    cases = run.get("scoredCases")
    if arm == "A":
        ok, identity_failures = e4lib.identity_arm_a(
            tools, context["referenceA"], cases, workdir)
        run["referenceIdentityPass"] = ok
        run["referenceIdentityFailures"] = identity_failures[:20]
        run["referenceIdentityFailureCount"] = len(identity_failures)
        kill_of = {}
        if ok:
            for mutant in context["mutants"]["jps"]:
                outcome, detail = e4lib.kill_arm_a(tools, mutant["path"],
                                                   cases, workdir)
                kill_of[mutant["id"]] = outcome
                if outcome == e4lib.KILLED:
                    run.setdefault("killingCase", {})[mutant["id"]] = \
                        detail.get("case")
    else:
        ok, detail = e4lib.identity_arm_rego(tools, context["referenceB"],
                                             suite_path, workdir)
        run["referenceIdentityPass"] = ok
        run["referenceIdentityFailures"] = [] if ok else [detail]
        run["referenceIdentityFailureCount"] = 0 if ok else 1
        kill_of = {}
        if ok:
            for mutant in context["mutants"]["rego"]:
                outcome, _detail = e4lib.kill_arm_rego(tools, mutant["path"],
                                                       suite_path, workdir)
                kill_of[mutant["id"]] = outcome
    run["kill"] = e4lib.kill_rates(kill_of, context["mutants"][language],
                                   context["pairedIds"][language],
                                   context["engineSupplied"][language])
    run["coverage"] = e4lib.coverage_classes(kill_of, context["classes"],
                                             language)
    # E6, LAST and unconditional on the reference relation, in ITS OWN refusal
    # scope (ROUND-1 FINDING R1-14): an engine refusal inside E6 must not
    # reach score_run()'s outer handler, which would overwrite the COMPLETED
    # reference-identity result and kill vector above with a generic refusal
    # record. E6's exposure is arm- and case-dependent — arm A evaluates the
    # own pack once per readable case, arms B/C run one `opa test` plus one
    # strict adjudication per reported failure — and §1.2 registers it as
    # measured rather than as the "one extra invocation" this comment once
    # claimed. Its refusal is still apparatus (`engine-execution-clean` reads
    # `e6EngineRefused`), and it is written under its own name, never merged
    # into `referenceIdentityPass`.
    try:
        run["ownPolicyIdentity"] = e4lib.own_policy_identity(
            tools, arm, artifact, cases, suite_path, workdir)
    except e4lib.ExecutionRefusal as error:
        run["ownPolicyIdentity"] = None
        run["e6EngineRefused"] = True
        run["e6Refusal"] = str(error)
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
    lines = ["# Study 020 — %s" % results["label"], "",
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
    lines += ["", "## E4 — witness-input coverage against the shared reference "
              "(primary)", "",
              "**No cut, no τ, no dichotomy** (§5.1). Each language scores over "
              "its OWN paired-adequate denominator: " + "; ".join(
                  "%s %d mutants (lattice %s)"
                  % (language, block["pairedAdequateMutants"],
                     _fmt(block["lattice"]))
                  for language, block in sorted(
                      (results.get("pairedDenominators") or {}).items())), "",
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
              # §5.8 makes the per-class imbalance a MANDATORY publication:
              # §5.2's Fact 2 derives L2's structural between-language bias
              # from it, so it is printed whatever the verdict.
              "Shared classes: %d, of which %d carry unequal per-language "
              "member counts (§5.2 Fact 2 — this imbalance is why the native "
              "mutant level enters the family de-biased, as L2c)."
              % ((results.get("sharedClasses") or {}).get("count", 0),
                 (results.get("sharedClasses") or {}).get("unequalCount", 0)),
              "",
              "| Arm | Language | Admitted (ITT) | Per-protocol | "
              "referenceIdentity | ownPolicyIdentity (E6) | Both | "
              "Out-of-domain cases |",
              "|---|---|---|---|---|---|---|---|"]
    for arm in batch.ARMS:
        entry = (results.get("e4") or {}).get(arm)
        if entry is None:
            lines.append("| %s | — | — | — | — | — | — | — |" % arm)
            continue
        lines.append("| %s | %s | %d | %d | %d | %d | %d | %d |"
                     % (arm, entry.get("language"), entry["denominator"],
                        entry["perProtocolDenominator"], entry["referenceIdentityPass"],
                        entry.get("ownPolicyIdentityPass", 0),
                        entry.get("bothIdentitiesPass", 0),
                        entry.get("outOfDomainCases", 0)))
    lines += ["", "## E1 — gold agreement (control, expected at ceiling)", "",
              "*Descriptive; published as an interpretation quantity that no "
              "decision reads (§5.1, §5.7).*", "",
              "| Arm | Perfect | Runs | Rate |", "|---|---|---|---|"]
    for arm in batch.ARMS:
        entry = (results.get("e1") or {}).get(arm)
        if entry is None:
            lines.append("| %s | — | — | — |" % arm)
            continue
        lines.append("| %s | %d | %d | %s |"
                     % (arm, entry["perfect"], entry["runs"],
                        _fmt(entry["rate"]["rate"])))
    lines += ["", "## The registered family (fixed-sequence: A−C, then A−B)",
              ""]
    gated_by = results.get("familyGatedBy") or []
    if gated_by:
        lines += ["**Not computed and not published.** %d gating row(s) matched "
                  "above §5.9's substantive rows, and each adjudicates R1 in "
                  "NEITHER direction — so no member, no p-value and no "
                  "direction exists for this attempt:" % len(gated_by), ""]
        lines += ["- %s" % cause for cause in gated_by]
    else:
        lines += ["§5.4's intersection–union rule: R1 = CLAIM iff **all "
                  "eighteen** members agree in the sign of the difference and "
                  "**all eighteen** reject at two-sided α = 0.05. Removing a "
                  "member is the anti-conservative direction, so every member "
                  "is published whatever the verdict (§5.2).", "",
                  "| Contrast | Members | Positive | Reject | Sign unanimous | "
                  "All reject | Verdict |", "|---|---|---|---|---|---|---|"]
        for name in (decision.CONTRAST_PRIMARY, decision.CONTRAST_SECONDARY):
            entry = (results.get("family") or {}).get(name)
            if entry is None:
                lines.append("| %s | — | — | — | — | — | — |" % name)
                continue
            members = entry.get("members") or []
            lines.append(
                "| %s | %d | %d | %d | %s | %s | %s |"
                % (name, len(members),
                   sum(1 for member in members
                       if (member.get("difference") or 0) > 0),
                   sum(1 for member in members if member.get("rejects")),
                   "**yes**" if entry.get("signUnanimous") else "no",
                   "**yes**" if entry.get("allReject") else "no",
                   "CLAIM" if entry.get("claim")
                   else "INDETERMINATE-BY-DISAGREEMENT"))
        for name in (decision.CONTRAST_PRIMARY, decision.CONTRAST_SECONDARY):
            entry = (results.get("family") or {}).get(name)
            if entry is None:
                continue
            lines += ["", "### %s — the eighteen members (§5.5's mandatory "
                      "reprint)" % name, "",
                      "| id | level | engine | population | adj | n (A/B/C) | "
                      "difference | p | rejects |",
                      "|---|---|---|---|---|---|---|---|---|"]
            for member in entry.get("members") or []:
                lines.append(
                    "| %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                    % (member.get("id"), member.get("level"),
                       member.get("engine"), member.get("population"),
                       member.get("adjustment") or "—",
                       member.get("n") or "—",
                       _fmt(member.get("difference")),
                       _fmt(member.get("p")),
                       "yes" if member.get("rejects") else "no"))
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

def _engine_execution_gate(per_arm_runs: dict,
                           scoring_apparatus: dict = None) -> dict:
    """Section 6's gate for round-1 R1-8: every scored invocation of this
    attempt returned an answer.

    Two kinds of refusal reach it, and both are about FROZEN bytes rather than
    about an author's: a reference the engine refused on during the identity
    control (`e4.ExecutionRefusal`, recorded on the run) and a manifest mutant
    the engine refused on during mutation execution (`kill_rates()`'s
    `refusedAll`). A gate that tolerated either would be a gate that let an
    apparatus failure decide a rate."""
    bind_study_modules()
    identity, mutant, e6, invocation = [], [], [], []
    # R1-1: the invocation-refused runs left `per_arm_runs` (they are in no
    # population), so the gate reads them from their own ledger — an exclusion
    # this gate did not see would be an apparatus event with no gate.
    for arm in sorted(scoring_apparatus or {}):
        for entry in scoring_apparatus[arm]:
            invocation.append("%s/%s: %s" % (arm, entry["run"],
                                             entry.get("refusal")))
    for arm in sorted(per_arm_runs):
        for run in per_arm_runs[arm]:
            if run.get("engineRefused"):
                identity.append("%s/%s: %s" % (arm, run["run"],
                                               run.get("engineRefusal")))
            # R1-14: E6's refusal has its own member so it cannot overwrite a
            # completed reference result — and its own list here so §6's
            # "covers E6's extra invocation too" is a scan, not a sentence.
            if run.get("e6EngineRefused"):
                e6.append("%s/%s: %s" % (arm, run["run"],
                                         run.get("e6Refusal")))
            for mutant_id in (run.get("kill") or {}).get("refusedAll", ()):
                mutant.append("%s/%s: %s" % (arm, run["run"], mutant_id))
    return {"held": not identity and not mutant and not e6 and not invocation,
            "invocationRefusals": sorted(invocation)[:20],
            "invocationRefusalCount": len(invocation),
            "identityRefusals": sorted(identity)[:20],
            "identityRefusalCount": len(identity),
            "mutantRefusals": sorted(mutant)[:20],
            "mutantRefusalCount": len(mutant),
            "e6Refusals": sorted(e6)[:20],
            "e6RefusalCount": len(e6),
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
        "controlGates": {}, "family": {}})
    results = {
        "study": STUDY_NAME,
        "attemptRoot": os.path.basename(os.path.normpath(attempt_root)),
        "label": label,
        "unfilledPins": unfilled,
        "pipelineInvalid": False,
        "pinsRawSha256": pins_raw_sha256,
        "batchShape": shape,
        "e1": None, "e2": None, "e3": None, "e4": None, "e5": None,
        "family": {},
        "familyGatedBy": verdict["causes"],
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
        workspace = tempfile.mkdtemp(prefix="study020-attempt-")
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
        # §7 delta 2. 019's round-1 R1-1 was ONE cut derived from the JPS
        # denominator and applied to every arm; 020 keeps the half that matters
        # — each language's denominator and lattice stay separate and are
        # published — and removes the threshold that sat on top of them. There
        # is no number here a run is judged AGAINST.
        denominators = e4lib.paired_denominators(paired_ids)
        for language in ("jps", "rego"):
            print("paired denominator (%s): %s"
                  % (language, denominators[language]["statement"]))
        # §5.1's units: the shared witness classes the coverage set is over.
        shared = e4lib.shared_classes(pairing)
        print("shared classes: %d (%d with unequal per-language membership)"
              % (shared["count"], shared["unequalCount"]))
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
                   "classes": shared["classes"],
                   "pairing": pairing,
                   "sharedClasses": shared,
                   "pairedDenominators": denominators,
                   # R1-5: the family's registered stream parameters travel
                   # with the context so `registered_family()` reads them from
                   # the registry rather than from a constant it trusts.
                   "pins": pins,
                   "referenceA": os.path.join(STUDY, REFERENCE_A_RELATIVE),
                   "referenceB": os.path.join(STUDY, REFERENCE_B_RELATIVE)}
        floor_gate = references_reproduce_gold(
            tools, gold, context["referenceA"], context["referenceB"],
            workspace)

        counted = population(slots)
        per_arm_runs, e1, e2, e3, e4_by_arm = {}, {}, {}, {}, {}
        scoring_apparatus = {}
        for arm in batch.ARMS:
            # ROUND-2 FINDING R2-5, the measured half. Every run used to be
            # scored in ONE shared directory, so `suite.<language>`,
            # `policy.rego` and `pack.json` were the same path for all 180
            # runs — and `reviewer.execute()` runs AFTER all scoring and reads
            # `run["suitePath"]` from disk. Two arm-A runs scored in one
            # workspace were measured sharing a path whose bytes held the LAST
            # run's suite: the holdout would have scored every eligible arm-B
            # and arm-C run against the last arm-C suite written and published
            # those outcomes under the wrong run ids. A per-run directory makes
            # every path expression inside `score_run()` per-run without
            # touching one of them; `reviewer.execute()` keeps the shared
            # workspace as its own scratch, which it only writes to.
            scored = []
            for slot in counted[arm]["slots"]:
                run_dir = os.path.join(workspace, arm,
                                       "run-%03d" % slot["slotIndex"])
                os.makedirs(run_dir, exist_ok=True)
                scored.append(score_run(tools, arm, slot, context, run_dir))
            # R1-1: a run the scorer coded `engine-invocation-refused` is
            # pipeline-invalid — the engine never answered about it — and
            # leaves every endpoint's population, published under its own
            # member with its refusal class so an absence is never silent.
            runs = [run for run in scored
                    if run.get("code") != "engine-invocation-refused"]
            scoring_apparatus[arm] = [
                {"run": run["run"],
                 "refusal": run.get("invocationRefusal")}
                for run in scored
                if run.get("code") == "engine-invocation-refused"]
            per_arm_runs[arm] = runs
            e1[arm] = e1_control(arm, runs)
            e2[arm] = e2_profile(arm, runs)
            e3[arm] = e3_taxonomy(runs)
            language = LANGUAGE_OF_ARM[arm]
            e4_by_arm[arm] = e4_endpoint(
                arm, runs, denominators[language], engine_supplied[language],
                reduced_paired[language], shared["classes"])

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
            # §5.7: NO `e1-floor` row. The gate is not registered, so it is
            # not evaluated and not published — `decision.CONTROL_GATES` does
            # not name it, and an unnamed gate cannot be silently satisfied.
            # ROUND-1 R1-8: every scored invocation of this attempt returned an
            # answer. A pinned engine refusing on a frozen reference or a frozen
            # mutant is an apparatus failure, and neither counting it as a kill
            # nor scoring the suite zero for it is honest — so it adjudicates R1
            # in neither direction, above every substantive row.
            "engine-execution-clean": _engine_execution_gate(
                per_arm_runs, scoring_apparatus),
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
                   "controlGates": gates, "family": {}}
        gate_causes = decision.gate_causes(outcome)
        family = registered_family(e4_by_arm, per_arm_runs, context, outcome,
                                   refusals, gate_causes)
        outcome["family"] = family
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
            # R1-1: scoring-time apparatus exclusions, published per arm with
            # their refusal classes — a run the engines never answered about
            # is in no population and in no silence either.
            "scoringApparatus": scoring_apparatus,
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
            "pairedDenominators": denominators,
            "sharedClasses": shared,
            "e1": e1, "e2": e2, "e3": e3, "e4": e4_by_arm, "e5": e5,
            "family": family,
            "familyGatedBy": gate_causes,
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
