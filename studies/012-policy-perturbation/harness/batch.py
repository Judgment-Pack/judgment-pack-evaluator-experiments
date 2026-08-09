#!/usr/bin/env python3
"""The batch driver: the 150 slots of §2.8's registered call order, one
authoring call each, the pre-batch golden recapture that admission depends on,
and the §6 C7 isolation negative control.

PORTED from Study 011's `harness/batch.py`
(sha256 `fb513e9f30cc28dcb3748b502e679fea6ec9270d15b730334ac01936f0b1deb7`, at
commit `3b93d3e7917e917516bd55cf4c7f5285c91fbc13` — the commit `harness/PORTS.md`
and `harness/PINS.json` bind the port to; round 3 finding 20 found this header
naming `e52925ec…` instead, a later commit at which the source blob is
identical, so the digest was right and the provenance named two commits).
Study 011 pins none of its own harness files, so that commit and that digest
are the whole source-side binding — §2.2's port table says so in its own
authority column, §6 C1 puts this file in no tier, and `harness/PORTS.md`
carries the diff. The registered changes are exactly these:

1. **§2.8's registered call order and its global index.** The batch is no
   longer N runs of one cell; it is the 150-slot first-order carryover-balanced
   order built from the Williams table for five treatments and the three
   registered block orders. It is expanded here, in code, from the two facts
   §2.8 states about that table, and every slot carries
   `(globalIndex, round, position, arm, slotIndex)`.
2. **Per-arm slot roots.** Slots live at `arms/<ARM>/authoring/run-NNN`, where
   NNN is that ARM's own slot index, contiguous `1…count_X` per arm.
3. **The arm and the arm's prompt reach the wrapper as arguments**, and the
   stamps the wrapper writes back are verified against the schedule (§2.7,
   §3.1 gate 9).
4. **The schedule stamps in `CALL.json` are written here**, and §2.2's port
   table puts them here in those words ("the arm and schedule stamps in
   `CALL.json`"). §2.7 registers the wrapper's permitted differences as
   *exactly three*, and reading a round and a position from the environment is
   not among them; §2.9 nevertheless registers the round index, the
   within-round position and the global schedule index as retained in
   `CALL.json`. The driver adds them after the wrapper returns and before the
   slot is sealed, so they are inside the seal.
5. **§2.9's per-slot terminal manifest**, written for every outcome, refusals
   included.
6. **§2.9's chained ledger.** `BATCH.json` is one append-only record per slot
   in schedule order, each carrying its slot's manifest digest and the previous
   record's digest.
7. **Resume by global schedule index [D-22].** `run --resume` continues at the
   ledger's next index; `--start` and `--start-round` are removed, and a
   command line still carrying one refuses rather than doing something else.
8. **`shortfall` takes no `--slots` [D-23]** and names the completed prefix,
   the last completed round, and the UTC wall clock of the last completed slot.
9. **The population root is derived** from this file's own location, so no
   invocation can point the batch at a tree the scorer will not read.
10. **Preflight reads the registry members that exist** (`batch.n`,
   `batch.slots`, `batch.order.firstRow`, `batch.order.blocks`) and requires
   the order the REGISTRY carries to expand to the order this file derives.
   Round 3 finding 3: the preflight read `batch.runs` and a top-level
   `schedule.williams`/`schedule.blocks`, none of which `harness/PINS.json`
   registers, so every real batch would have refused once the stage-null pins
   were filled — while `score_rates.py` read the registered spelling and agreed
   with nobody. Driver, scorer and registry now name one set of members, and
   `harness/tests/test_batch.py` runs this check against the COMMITTED registry
   so a member-name split cannot survive a green suite again.
11. **§6 C7's assent member is `isolationNegative.assent`**, the name the
   registry registers. Round 3 finding 4: the driver read
   `isolationNegative.operatorAssent`, so filling the registered member could
   never authorize the control and filling the one the code read would have
   authorized it without the registry recording anything.
12. **The shortfall's `completedRounds` counts COMPLETED rounds** and its
   `lastSlotEndedAt` names the slot it was read from. Round 3 finding 15: the
   count was the LAST SLOT's round, so a prefix ending inside round 1 declared
   one round completed when none was; and a tail whose wrapper refused before
   writing `CALL.json` produced a bare `null` timestamp with nothing saying
   why. The count is now derived from the prefix (zero when no round is whole),
   the clock falls back to the last slot that HAS a `CALL.json`, and the
   declaration's own note states the fallback.
13. **`load_ledger()` refuses a physically reordered ledger** instead of
   normalizing it. Round 3 finding 16: it sorted the records by `globalIndex`
   before anything looked at them, so a file whose records had been moved
   passed the prefix check and was rewritten in the order the driver preferred
   — while `score_rates.py` reads the same file in file order and would refuse
   it. File order IS schedule order (§2.9's chain is over the file), and it is
   verified before the records are used for anything.
14. **The crash window between the seal and the ledger is closed** (round 6,
   finding 6). §2.9 has the driver seal a slot and then append its record, so a
   kill in between leaves a sealed slot the ledger does not name — and that
   batch could neither be resumed (the resume planned the orphan's index again
   and refused its existing path) nor declared short (the two counts disagreed
   and the scorer refused the declaration under C5). Three changes:
   `write_ledger()` writes through a same-directory temporary and `os.replace`,
   so a kill during the rewrite cannot truncate the ledger;
   `reconcile_ledger()` completes that ONE interrupted append from the slot's
   own verified seal — the slot ran, only the bookkeeping stopped — and refuses
   every other disagreement by name; and `shortfall` reconciles through the same
   function before it declares, because a batch killed in that window is exactly
   the batch that needs a declaration.
15. **§6 C7 is a precondition of the BATCH, not only of its own command**
   (round 9, finding 3). The registration orders the isolation negative control
   before the batch and the registry's assent gated the control's command —
   and nothing on the batch path read either, so all 150 calls could run with
   the assent still null and no control record on disk. `preflight()` now
   requires the registry's assent and the canonical
   `controls/isolation-negative/VERDICT.json`, at one of the three registered
   outcomes, under that same assent, and against the golden capture this batch
   runs behind. `--dry-run` refuses too, because preflight precedes the dry-run
   branch — as it already did for the golden gate.

Everything else is 011's, including every refusal it registered.

Each run is an independent invocation of `transcription/authoring_call.sh` with
its own scratch directory, its own fresh HOME, its own fresh CODEX_HOME, and
its own slot under its arm's authoring tree. Runs are sequential, never
parallel (§2.8: parallel calls would share provider-side backpressure and
correlate in ways nothing here could measure), and share no state. The pinned
binary digest, model, arm prompt digests and golden digest come from a registry
file (`harness/PINS.json` by default), not from anything this driver computes.

**Study 011's registered difference from Study 010, retained** (§2.5): a run
that fails or is refused terminates its own slot with a REFUSAL.json and the
batch CONTINUES. Study 010 had one slot and a zero-retry rule because a
retained transcript from a killed call would let an operator read the answer
and try again for a single unrepeatable draw. This study makes no draw: every
invocation leaves its own slot, no slot is ever written twice, and the
pipeline-invalid rate is one of the endpoints (§4.4) — so stopping at the first
failure would destroy data the study exists to collect. What that does NOT
license is re-running a slot: the wrapper refuses an existing slot, and the
driver refuses a batch whose target slots are already on disk, whose global
indices the ledger already records, or whose results have already been
published.

Preflight refuses, before a single call is spent, when: the ported bytes are
not the registered ones and the interpreter is not the registered one
(harness/integrity.py, §6 C1, §2.2); the preregistration's freeze digest is
unregistered or does not match this file (§2.10); an arm's prompt is not that
arm's pinned prompt; a named CLI is not the pinned binary; the registry's N is
not the N the registered order encodes; a plan would reach past global index
150; `RESULTS.json` exists; a planned slot exists; or — for the registered
prompt — the golden capture is absent or its digest is not the one
`harness/PINS.json` registers (§3.2), or §6 C7's control has not run and left
its verdict. The golden one is why the recapture cannot be skipped: no slot is
created until the capture is taken, registered and committed. That digest is
then stamped into every slot's `CALL.json`, so a capture substituted after the
batch does not change which runs were admissible — the scorer scores those
slots `golden-mismatch` instead (§3.2 step 3).

Commands:

  run                        the registered call order, sequentially, into
                             arms/<ARM>/authoring/run-NNN. `--resume` continues
                             at the ledger's next global index [D-22], first
                             completing the one ledger record a crash between a
                             slot's seal and the append can leave unwritten
  capture                    the §3.2 golden recapture: two probe calls into a
                             numbered attempt directory, whose pre-prompt
                             contexts must agree, then the golden derivation.
                             ONE recapture serves all five arms [D-8]
  capture-golden             derive a golden capture from retained capture
                             slots (the second half of `capture`, for the case
                             where the calls were made and the derivation was
                             not). At least two agreeing captures, always:
                             --min-slots cannot ask for fewer, and the captures
                             must come from distinct sessions — a copied slot
                             or a transcript retained twice agrees with itself
                             and refuses
  capture-isolation-negative §6 C7: ONE probe call with the operator's real
                             HOME, expected to FAIL the golden match. Retains
                             the verdict and a stripped call record always, and
                             the context digests when the call produced them;
                             never the transcript, whose deletion it verifies.
                             Exits non-zero if it reached neither comparison.
                             It runs once for the whole batch, not per arm
  shortfall                  declare a short batch before anything is scored

What this file deliberately does NOT do: **compute coverage or any rate**
(§2.8's mechanical prohibition; score_rates.py is the only publisher), score
anything, judge a completion, decide admissibility (score_rates.py recomputes
all of that from the retained bytes and never trusts a REFUSAL.json), retry a
run, re-run a slot, choose N after seeing results, drop or re-author an arm, or
delete a slot.

Wrapper exit status → refusal code:

  0   the run completed and the slot is admissible-shaped (scoring decides)
  1   preflight-refused    nothing was called
  10  call-nonzero-exit    the process exited non-zero; slot retained
  11  session-count        the call produced other than one new session
  *   wrapper-error        any other status, retained with the stderr tail

Usage:
  batch.py run --scratch-parent DIR [--resume] [--runs N] [--pins PATH]
               [--golden PATH] [--cli-override PATH] [--dry-run]
  batch.py capture --scratch-parent DIR [--captures DIR] [--out PATH]
               [--runs N] [--pins PATH] [--cli-override PATH]
  batch.py capture-golden --slots DIR --out PATH [--min-slots N]
  batch.py capture-isolation-negative --scratch-parent DIR [--out DIR]
               [--pins PATH] [--golden PATH] [--cli-override PATH]
  batch.py shortfall --reason TEXT [--pins PATH]
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)

# The ceremony's commands run with bytecode writing disabled (§2.10,
# round 5 finding 3): set structurally, not left to the operator's
# environment, before any harness module is imported — which means before
# the `import integrity` below, not after it. Round 9, finding 1: the
# assignment sat one import too late, so the gate module's own cache was
# written by the command whose comment said none was.
sys.dont_write_bytecode = True


def _refuse_untracked_python_sources():
    """Round 8, finding 2: an untracked package can shadow a reviewed module
    at import time — including the module carrying the untracked-source scan
    itself, which is why THIS tripwire lives in the entry file the ceremony
    names by path, before any harness import. Import resolution cannot shadow
    a script invoked as a file. Round 9, finding 1: "before any harness
    import" includes `import integrity` — the gate module was imported above
    this scan, so the one module a shadow package would replace was the one
    module the scan could not precede."""
    import subprocess as _subprocess
    study = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tracked = set(_subprocess.run(
        ["git", "ls-files", "-z", "--", "."],
        cwd=study, capture_output=True, check=True
    ).stdout.decode("utf-8").split("\0"))
    for base, _dirs, files in os.walk(study):
        for name in files:
            if not name.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(base, name), study)
            if rel.replace(os.sep, "/") not in tracked:
                print("refused: untracked Python source %s sits in the study "
                      "tree; the reviewed bytes are the bytes that run "
                      "(§2.10, round 8 finding 2)" % rel, file=sys.stderr)
                raise SystemExit(2)


def _refuse_unsafe_import_path():
    """Round 10, finding 1: the scan above cannot precede the head imports of
    the file it lives in. Running a script BY PATH puts that script's own
    directory first on `sys.path`, and every module the head imports resolves
    from it before a single byte of this file runs — `subprocess` included,
    which is the module the tripwire asks git what is tracked with. The scan's
    own instrument is therefore resolvable from the directory the scan exists
    to police, and no assignment inside the file can close that: `sys.path[0]`
    is populated before the file is read, unlike `sys.dont_write_bytecode`,
    which is consulted later.

    `-P` / `PYTHONSAFEPATH=1` is the closure, and README step 0 exports it.
    What this refusal establishes is that the operator applied it — a discipline
    check against operator error, NOT a gate against a hostile tree, because it
    executes after the head imports it is about. The only fully structural form
    would be a re-exec guard written above every shadowable import; it is larger
    than this residual warrants and is declined here by name rather than left
    unmentioned."""
    if not sys.flags.safe_path:
        print("refused: run this file with -P, or with PYTHONSAFEPATH=1 in the "
              "environment as README step 0 exports it; invoking a script by "
              "path puts its own directory first on sys.path, so this file's "
              "head imports — `subprocess`, which the untracked-source scan "
              "above runs on, among them — resolve from the very directory the "
              "scan exists to police (§2.10, round 10 finding 1)",
              file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    _refuse_unsafe_import_path()
    _refuse_untracked_python_sources()

# Nothing is put on the import path until the tree has been scanned — and,
# under the safe path the refusal above requires, nothing was on it before
# either, which is what makes this comment true of the whole file.
sys.path.insert(0, HERE)
import integrity  # noqa: E402
import score_rates  # noqa: E402  (one slot-naming rule and one JSON loader, not two)
import transcript_check  # noqa: E402

SCRIPT = os.path.join(STUDY, "transcription", "authoring_call.sh")
DEFAULT_PINS = os.path.join(HERE, "PINS.json")
# §2.10 [D-23]: the population root is DERIVED from this file's own location
# and there is no `--slots`. An earlier draft left the root an argument, so the
# batch could be written into — and the population read from — any directory of
# the right shape: a copy with a slot removed, a duplicated arm, a renamed
# tree, every per-slot check still passing. The canonical root is
# `harness/../arms` and nothing else names it.
ARMS_ROOT = os.path.join(STUDY, "arms")
DEFAULT_CAPTURES = os.path.join(STUDY, "controls", "recapture")
DEFAULT_NEGATIVE = os.path.join(STUDY, "controls", "isolation-negative")
# §6 C7's three registered outcomes. The command that WRITES a verdict, the
# preflight that READS one and `score_rates.verify_preconditions()` take the
# list from ONE place, so a fourth outcome cannot be written by one and refused
# by another; it is defined there and named here because this module imports
# that one and not the reverse (round 9, finding 3).
C7_OUTCOMES = score_rates.C7_OUTCOMES
DEFAULT_GOLDEN = os.path.join(STUDY, "transcription", "GOLDEN-CONTEXT.json")
PROBE_PROMPT = os.path.join(STUDY, "transcription", "PROBE-PROMPT.txt")
RESULTS = os.path.join(STUDY, "RESULTS.json")
LEDGER_NAME = "BATCH.json"
SHORTFALL_NAME = "SHORTFALL.json"
MANIFEST_NAME = "SLOT-MANIFEST.json"

# §2.9 as amended (round 7, finding 3): the seal records EVERY entry in the
# slot tree. A regular file is recorded as `[path, byte length, sha256]`; every
# other entry — a symlink, a directory, a FIFO, a socket, a device — is
# recorded as `[path, NON_FILE_LENGTH, "type:<marker>"]`, by path and type
# alone, because it is not a byte range to hash. The two row shapes cannot
# collide: no file has a negative length and no sha256 hex string begins with
# `type:`. `score_rates.py` writes the same two shapes and the same markers.
NON_FILE_LENGTH = -1
# Round 8, finding 4: the slot ROOT is an entry of its own list, at the one
# relative path no entry beneath it can take. `os.path.relpath(child, slot)` is
# never `.`, so the root's row cannot be forged by planting a file in the tree.
SLOT_ROOT_ENTRY = "."
TYPE_MARKERS = (
    (stat.S_ISLNK, "symlink"),
    (stat.S_ISDIR, "directory"),
    (stat.S_ISFIFO, "fifo"),
    (stat.S_ISSOCK, "socket"),
    (stat.S_ISCHR, "char-device"),
    (stat.S_ISBLK, "block-device"),
    (stat.S_ISDOOR if hasattr(stat, "S_ISDOOR") else (lambda mode: False), "door"),
)

WRAPPER_CODES = {0: None, 1: "preflight-refused", 10: "call-nonzero-exit",
                 11: "session-count"}
STDERR_TAIL = 4000

# §2.8's registered call order, as the two facts the preregistration states
# about its own table rather than as a transcription of it. W1…W5 are the
# cyclic rows of the Williams first row for five treatments; W6…W10 are those
# five reversed; the batch is three blocks of the ten, each block in its own
# registered order. A transcribed table is ten chances to mistype a letter and
# no way to notice — a derived one either reproduces §2.8's published
# transition matrix or it does not, and the harness test checks it against that
# matrix and not against this code.
ARMS = ("A", "B", "C", "D", "E")
WILLIAMS_FIRST_ROW = ("A", "B", "E", "C", "D")
BLOCK_ORDERS = (("W2", "W4", "W7", "W10", "W1", "W9", "W8", "W6", "W3", "W5"),
                ("W4", "W3", "W2", "W10", "W9", "W8", "W5", "W1", "W7", "W6"),
                ("W4", "W6", "W5", "W7", "W1", "W2", "W10", "W8", "W9", "W3"))
POSITIONS = len(ARMS)
SEQUENCES = 2 * POSITIONS  # ten: the five cyclic rows and those five reversed
ROUNDS = len(BLOCK_ORDERS) * SEQUENCES  # 30: three blocks of the ten sequences
# N = 30 slots per arm [D-1], 150 in total. Both are properties of the
# registered order above, derived here so that no invocation can plan against
# one number while the schedule expands to another.
RUNS_PER_ARM = ROUNDS
REGISTERED_SLOTS = ROUNDS * POSITIONS
# The members that make a slot a slot of the registered order (§2.8 [D-22],
# §3.3 `schedule-mismatch`, §6 C5 clause 3). The ledger carries them per record
# and the driver compares them position by position against the expansion.
SCHEDULE_KEYS = ("globalIndex", "round", "position", "arm", "slotIndex")

# §2.7 gives the wrapper five required positional arguments, and the probe
# calls of §3.2 and §6 C7 are made under no arm: they answer the registered
# probe prompt, which is arm-independent by construction and is why ONE
# recapture serves all five arms [D-8]. The wrapper's registered interface
# spells that case `none`, refuses `PROMPT_KIND=probe` under any other arm id,
# and stamps `arm: null`; the prompt argument is the probe prompt's own path,
# whose digest the wrapper checks against the registry's `probePrompt` member.
# Capture slots are never batch slots and enter no denominator.
PROBE_ARM = "none"

# §3.2: a golden capture is derived from at least TWO independent captures whose
# normalized pre-prompt contexts agree. One capture cannot show that a context
# reproduces, and an allowlist built from a context that might vary is not an
# allowlist. This is the floor, not a default: a smaller --min-slots refuses.
MIN_CAPTURE_SLOTS = 2
# …and the two must be two CALLS. The rule's meaning is that two independent
# probe invocations reproduced the same context; a copied slot, or one call's
# transcript retained twice, satisfies "two agreeing captures" and shows
# nothing at all. Each member below is a piece of RAW retained evidence that
# says WHICH call produced a capture, and two capture slots that share any of
# them are one call — the normalized digests are deliberately not among them,
# because two genuinely independent calls SHOULD agree there and that agreement
# is the point of the derivation, not a defect in it. §3.3 applies the same
# rule to the 150 batch slots, where the scorer reads it as `session-reused`.
CAPTURE_IDENTITY = (
    ("sessionSha256", "the retained transcript bytes"),
    ("sessionId", "the session id the transcript records"),
    ("callIdentity", "the call record's own start, end, working directory and "
                     "isolated home"),
)
# §6 C7: what a retained negative-control CALL.json may not carry. The control
# runs against the operator's real environment, so every member that names or
# enumerates it is dropped before the file is written into the study.
C7_REDACTED = ("environment", "environmentValues", "home", "codexHome", "cwd",
               "isolatedHomeInventory", "operatorHomeSkillsPresent")


class BatchError(Exception):
    """A refusal that stops the batch before any call is made."""


def _load_json(path: str):
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"),
                          object_pairs_hook=score_rates._refuse_duplicate_keys)


def _digest(path: str) -> str:
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


def _matches(actual: str, pinned) -> bool:
    """One computed digest against one registry pin.

    `harness/integrity.py`'s `bare()` is this study's single rule for reading a
    digest written with or without its `sha256:` prefix, and this file calls it
    rather than adding a second rule that could disagree with the module every
    other artifact is checked by."""
    return integrity.bare(actual) == integrity.bare(pinned)


def _canonical(body) -> bytes:
    """The serialization the ledger's hash chain is taken over: JSON with
    sorted keys and no insignificant whitespace.

    §2.9 registers a chain over ledger records, and a record is a structure and
    not a file — so the bytes being digested have to be defined somewhere,
    once, in a form the scorer can reproduce exactly. (The slot manifest's list
    has its own encoding, `files_digest()`, which is the one
    `harness/integrity.py` already uses for §2.10's tree manifest.)"""
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _write_json(path: str, body: dict) -> None:
    with open(path, "wb") as handle:
        handle.write((json.dumps(body, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def _write_json_atomic(path: str, body: dict) -> None:
    """The same bytes, written so that no reader ever sees half of them: a
    temporary file in the SAME directory, flushed and fsynced, then `os.replace`,
    then the directory entry fsynced too.

    Round 6, finding 6. `BATCH.json` is rewritten in full after every slot, and
    `_write_json()` truncates the file and then writes it — so a kill between
    those two leaves a truncated ledger, and the batch's only record of every
    slot that came before is gone. `os.replace` is atomic within a filesystem,
    so the ledger on disk is always one of the two whole versions. The
    same-directory temporary is what makes that true: a rename across
    filesystems is a copy. The two fsyncs are what make it survive the other
    half of a crash — the file's bytes before the rename, and the rename itself
    — because a rename that reaches the directory before the data does can
    leave an empty file where a whole one used to be.

    The manifests and `CALL.json` do not need this: each is written once, into a
    slot the ledger does not yet name, and a slot whose seal is half-written is
    refused rather than merged. The ledger is the one file this driver rewrites.

    What a crash can still leave is a `BATCH.json.…partial` beside the ledger,
    if it lands between the temporary file and the rename. That file is inert —
    nothing reads it, and the ledger itself is whole either way — and removing
    it is a housekeeping note in `DEVIATIONS.md`, not a recovery.
    """
    directory = os.path.dirname(path) or "."
    handle_fd, temporary = tempfile.mkstemp(
        dir=directory, prefix=os.path.basename(path) + ".", suffix=".partial")
    try:
        with os.fdopen(handle_fd, "wb") as handle:
            handle.write((json.dumps(body, indent=2, sort_keys=True)
                          + "\n").encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        # `mkstemp` creates at 0600; the committed ledger is a published
        # artifact and is readable like every other file in the tree.
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    except BaseException:
        if os.path.lexists(temporary):
            os.unlink(temporary)
        raise
    directory_fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def williams(first_row=WILLIAMS_FIRST_ROW) -> dict:
    """§2.8's ten registered sequences W1…W10, derived.

    W1…W5 are the cyclic rows of the Williams first row `A, B, E, C, D` — each
    row the one before it with every arm advanced one step through A→B→C→D→E→A
    — and W6…W10 are those five rows reversed. Over the ten, each arm holds
    each of the five positions exactly twice and each of the twenty ordered
    pairs X→Y is adjacent exactly twice.

    `first_row` is an argument only so that the REGISTRY's own first row can be
    expanded by this same construction and compared with the expansion this
    file derives (`check_registry()`); every other caller takes the registered
    default and the two are the same table or nothing runs."""
    if sorted(first_row) != sorted(ARMS):
        raise BatchError("§2.8's Williams first row is a permutation of %r; %r is not"
                         % (list(ARMS), list(first_row)))
    rows = {}
    for step in range(POSITIONS):
        rows["W%d" % (step + 1)] = tuple(
            ARMS[(ARMS.index(arm) + step) % POSITIONS] for arm in first_row)
        rows["W%d" % (step + 1 + POSITIONS)] = tuple(
            reversed(rows["W%d" % (step + 1)]))
    return rows


def schedule(first_row=WILLIAMS_FIRST_ROW, blocks=BLOCK_ORDERS) -> list:
    """The 150 slots of §2.8's registered call order, expanded deterministically
    from the table above: `[(globalIndex, round, position, arm)]`, global index
    1…150, round 1…30, within-round position 1…5.

    The arms are interleaved, not blocked, because blocked execution would
    confound the arm with the drift across the batch; the order is
    carryover-balanced rather than merely position-balanced, because a schedule
    that balances position alone leaves an arm following one particular
    predecessor almost always, and provider-side state carried from one call to
    the next is exactly what §7 admits this design cannot exclude.

    The harness test re-derives the same expansion from §2.8's table and
    asserts this function equals it, so the driver cannot drift from the
    registration while the published balance properties still pass.

    `first_row` and `blocks` default to the registered table and are arguments
    for one caller only: `check_registry()` expands `harness/PINS.json`'s own
    `batch.order` through this same function and requires the result to equal
    the default expansion, so the registry and the driver are one order rather
    than two spellings that happen to agree."""
    rows = williams(first_row)
    # Each registered block is the ten sequences in its own order — a
    # permutation of W1…W10 and not a selection from them. Checked here because
    # the per-arm counts below cannot see it: every sequence holds every arm
    # once, so a block that ran W4 twice and W3 never still gives 30 slots per
    # arm and destroys the transition balance §2.8 registers.
    for number, block in enumerate(blocks, 1):
        if not all(isinstance(name, str) for name in block) \
                or sorted(block) != sorted(rows):
            raise BatchError("block %d of §2.8's registered order is %r, which is not "
                             "a permutation of W1…W%d" % (number, block, SEQUENCES))
    slots, seen, index, round_index = [], {arm: 0 for arm in ARMS}, 0, 0
    for block in blocks:
        for sequence in block:
            round_index += 1
            for position, arm in enumerate(rows[sequence], 1):
                index += 1
                seen[arm] += 1
                slots.append((index, round_index, position, arm))
    # Not a formality: this is the one place the expansion's shape is asserted
    # against the registered numbers, and a mistyped block order would be
    # caught here rather than at slot 150.
    if len(slots) != REGISTERED_SLOTS or round_index != ROUNDS \
            or sorted(seen.values()) != [RUNS_PER_ARM] * POSITIONS:
        raise BatchError(
            "the expanded call order is %d slots over %d rounds with per-arm counts "
            "%r: §2.8 registers %d slots over %d rounds, %d per arm"
            % (len(slots), round_index, seen, REGISTERED_SLOTS, ROUNDS,
               RUNS_PER_ARM))
    return slots


def schedule_entries() -> list:
    """`schedule()` with each slot's per-arm slot index attached: the five
    members §2.8 [D-22] registers per ledger record and §2.9 registers per
    `CALL.json`.

    `slotIndex` is derived from the order and not stored in it — it is the
    count of that arm's slots so far — which is what makes §6 C5 clause 4's
    "exactly the contiguous range 1…count_X, derived from that prefix" true of
    any prefix, complete or not, without reference to a round number."""
    entries, seen = [], {arm: 0 for arm in ARMS}
    for global_index, round_index, position, arm in schedule():
        seen[arm] += 1
        entries.append({"globalIndex": global_index, "round": round_index,
                        "position": position, "arm": arm,
                        "slotIndex": seen[arm]})
    return entries


def slot_path(entry: dict) -> str:
    """`arms/<ARM>/authoring/run-NNN` — the slot root is the ARM's, and NNN is
    that arm's own slot index zero-padded to three digits, so within an arm the
    run order IS the on-disk order and a drift read is a sort, not a join."""
    return os.path.join(ARMS_ROOT, entry["arm"], "authoring",
                        "run-%03d" % entry["slotIndex"])


def arm_prompt(pins: dict, arm: str) -> tuple:
    """(path, pinned sha256) of one arm's registered `PROMPT.txt`.

    The path is structural and the digest is pinned, which is how this study
    treats every arm artifact: `harness/integrity.py` reads
    `arms/<X>/PROMPT.txt` at `arms.<X>.promptSha256`, and the wrapper's own
    prompt gate reads that same member (`pin arms "$ARM" promptSha256`). A
    registry that pins no digest for an arm refuses before anything is spent:
    an arm whose prompt bytes are not registered before the batch is not a
    registered arm, and an arm may not be added, dropped or re-authored once a
    call has been made (§2.8)."""
    pinned = ((pins.get("arms") or {}).get(arm) or {}).get("promptSha256")
    if not pinned:
        raise BatchError(
            "harness/PINS.json registers no arms.%s.promptSha256: every arm's "
            "PROMPT.txt is pinned before any call (§2.10)" % arm)
    return os.path.join(STUDY, "arms", arm, "PROMPT.txt"), pinned


def check_registry(pins: dict) -> None:
    """§2.10's `batch` member and the five arm prompts, against §2.8's
    expansion — every registry check the preflight makes that does not depend
    on a stage-null pin, in one function so the harness can run the REAL ones
    against the COMMITTED registry.

    Round 3 finding 3 is why this exists as a function rather than as a block
    of `preflight()`. The driver required `batch.runs` and a top-level
    `schedule.williams`/`schedule.blocks`; the registry carries `batch.n`,
    `batch.slots` and `batch.order.firstRow`/`.blocks`; and `score_rates.py`
    read the registry's spelling. Nothing failed, because the only preflight
    the suite ran was against stand-in registries built for the tests, and the
    committed one is not reachable from a batch that cannot start until its
    stage-null members are filled. So the checks are here, and
    `harness/tests/test_batch.py` calls this with the committed file.

    `batch.order.construction` is prose — a sentence naming the construction
    for a reader — and is deliberately not checked as data: the construction
    that governs is `williams()`, and `test_schedule.py` holds that against
    §2.8's published table.
    """
    batch_pin = pins.get("batch")
    if not isinstance(batch_pin, dict):
        raise BatchError(
            "harness/PINS.json registers no batch member: §2.8's call order, its N "
            "and its slot count are registry members, and a batch is not run "
            "against an order the registry does not carry")
    order = batch_pin.get("order")
    if not isinstance(order, dict):
        raise BatchError(
            "harness/PINS.json registers no batch.order: §2.8's call order is a "
            "registry member (its first row and its three block orders), and this "
            "batch will not run against an order the registry does not carry")
    first_row = order.get("firstRow")
    blocks = order.get("blocks")
    if not isinstance(first_row, list) or not isinstance(blocks, list) \
            or not all(isinstance(block, list) for block in blocks):
        raise BatchError(
            "harness/PINS.json's batch.order is %r: §2.8 registers firstRow as a "
            "list of arms and blocks as a list of lists of sequence names"
            % ({"firstRow": first_row, "blocks": blocks},))
    # The registry's OWN order, expanded by the same construction this file
    # runs the batch from. Comparing the two members elementwise would say the
    # registry holds the same letters; expanding them says it holds the same
    # ORDER, which is what the ledger, the resume and §6 C5 are checked against.
    registered = schedule(tuple(first_row), tuple(tuple(block) for block in blocks))
    derived = schedule()
    if registered != derived:
        first = next(offset for offset, (left, right)
                     in enumerate(zip(registered, derived)) if left != right)
        raise BatchError(
            "harness/PINS.json's batch.order expands to a different call order than "
            "§2.8's: at global index %d the registry's order gives %r and this "
            "file's gives %r. The registry and the driver are one order, not two"
            % (first + 1, registered[first], derived[first]))
    # The registry states N and the slot count (§2.10) and the code expands the
    # order; they agree or nothing runs. A registry naming a different N —
    # [D-1]'s registered alternative of 25, say — is a different study, and it
    # must not be possible to run the 30-round order under it. `score_rates.py`
    # reads these same two members before it reads a slot.
    if batch_pin.get("n") != RUNS_PER_ARM:
        raise BatchError(
            "harness/PINS.json registers batch.n = %r per arm and §2.8's order is %d "
            "rounds of %d arms — N = %d slots per arm, %d in total [D-1]. The batch "
            "size and the call order are fixed together before the batch, so a "
            "registry that names another N refuses before a call is spent"
            % (batch_pin.get("n"), ROUNDS, POSITIONS, RUNS_PER_ARM, REGISTERED_SLOTS))
    if batch_pin.get("slots") != REGISTERED_SLOTS:
        raise BatchError(
            "harness/PINS.json registers batch.slots = %r and §2.8's call order "
            "expands to %d" % (batch_pin.get("slots"), REGISTERED_SLOTS))
    # Every arm's prompt, not one prompt: all five arms exist from round 1 under
    # the interleaved order, so all five are checked before slot 1.
    for arm in ARMS:
        path, pinned = arm_prompt(pins, arm)
        actual = _digest(path)
        if not _matches(actual, pinned):
            raise BatchError("arm %s's %s is %s, not the pinned %s"
                             % (arm, os.path.relpath(path, STUDY), actual, pinned))


def plan(runs: int, start: int, slots_dir: str, stem: str = "run") -> list:
    """The slot paths a CAPTURE attempt will create, in order. Named
    capture-NNN with a three-digit index, in one flat attempt directory.

    The batch's own slots do not come from here any more: they come from
    `schedule_entries()` and `slot_path()`, because a slot's index is its
    arm's and its order is the registered order's (§2.8)."""
    return [os.path.join(slots_dir, "%s-%03d" % (stem, index))
            for index in range(start, start + runs)]


def verify_ported_bytes() -> dict:
    """§6 C1 as a precondition of the batch, not only of CI. A drifted mirror
    or compiler changes every count, and from round 3 onward the tree manifest
    binds the reviewed bytes to the running ones (§2.10 [D-20]); the digest
    table is checked before a call is spent, because afterwards it is too late
    for the batch."""
    try:
        return integrity.verify()
    except integrity.IntegrityError as error:
        raise BatchError("the ported bytes are not the registered ones: %s" % error)


def preflight(entries: list, slots: list, scratch_parent: str, pins_path: str,
              cli_override: str, prompt_kind: str,
              golden_path: str = None) -> dict:
    """The pins, or BatchError. Everything checkable before the first call is
    checked before the first call: a batch that would run drifted bytes,
    collide with retained slots, publish after results exist, run a prompt that
    is not the arm's pinned one, reach past the registered global index, or run
    without the registered golden capture must not spend a single invocation.

    `entries` are the schedule entries this invocation plans, empty for the
    probe calls (the recapture and §6 C7), which are not slots of the order."""
    verify_ported_bytes()
    if not slots:
        raise BatchError("a batch needs at least one run")
    if not os.path.isfile(SCRIPT):
        raise BatchError("no authoring wrapper at %s" % SCRIPT)
    if not os.path.isdir(scratch_parent):
        raise BatchError("scratch parent %s is not a directory" % scratch_parent)
    pins = _load_json(pins_path)
    require_freeze(pins)
    if prompt_kind == "registered":
        if not entries:
            raise BatchError("a batch of the registered order is planned from the "
                             "order: no schedule entries were given for %d slots"
                             % len(slots))
        # §2.8: the whole call order is registered before the batch, so the
        # LAST slot this invocation would create is bounded by its end —
        # unconditionally, whether or not --runs was given. Study 011's round-4
        # finding was the same rule against a count rather than an index: with
        # --runs omitted the driver used the registered N as a COUNT and
        # planned a batch past it, which no scoring could ever publish. Here
        # the entries are a slice of the expansion and cannot exceed it by
        # construction; the bound is checked anyway, because "cannot happen by
        # construction" is a claim about today's code and this is a claim about
        # the study.
        if entries[-1]["globalIndex"] > REGISTERED_SLOTS:
            raise BatchError(
                "this invocation plans global indices %d…%d and §2.8 registers %d "
                "slots: no invocation may plan a slot past the registered order"
                % (entries[0]["globalIndex"], entries[-1]["globalIndex"],
                   REGISTERED_SLOTS))
        # §2.10: N, the slot count, the call order and every arm's prompt, read
        # at the member names the registry actually carries and compared with
        # this file's expansion. `score_rates.py` makes the same comparison over
        # the same members before it reads a slot; made here as well, because
        # the driver is what spends the calls and an order the registry does not
        # agree with is one no scoring will accept.
        check_registry(pins)
    else:
        pinned = pins.get("probePrompt", {}).get("sha256")
        if not pinned:
            raise BatchError("harness/PINS.json registers no probePrompt.sha256")
        actual = _digest(PROBE_PROMPT)
        if not _matches(actual, pinned):
            raise BatchError("%s is %s, not the pinned %s"
                             % (os.path.relpath(PROBE_PROMPT, STUDY), actual, pinned))
    if cli_override is not None:
        if not os.path.isfile(cli_override):
            raise BatchError("no CLI at %s" % cli_override)
        override_digest = _digest(cli_override)
        if not _matches(override_digest, pins["codex"]["binarySha256"]):
            raise BatchError("the CLI at %s is %s, not the pinned %s"
                             % (cli_override, override_digest, pins["codex"]["binarySha256"]))
    if prompt_kind == "registered":
        if os.path.exists(RESULTS):
            # §2.8: no slot in ANY arm after a rate has been computed. Adding
            # runs once the numbers are visible is the one thing a rate study
            # must never do, and here the operator also holds a directional
            # prediction about one of the arms.
            raise BatchError("%s exists: no slot may be created in any arm after a "
                             "rate has been computed" % RESULTS)
        golden = require_golden(pins, golden_path)
        # LAST in the registered branch, and after the golden gate: §6 C7's
        # record is bound to the capture, so the capture is verified before the
        # binding is compared, and every earlier refusal still fails for its own
        # reason. Probe calls — the recapture and C7 itself — take the other
        # branch, because the recapture precedes the control and the control
        # precedes the batch.
        require_isolation_negative(pins, golden)
    # `lexists`, not `exists`: a DANGLING symlink at a planned slot path is
    # absent to `exists()` and present to `mkdir`, so the batch used to pass
    # preflight and then die of an uncaught FileExistsError in refuse_slot() —
    # no call spent, no refusal recorded, and BATCH.json left behind. A link
    # at a planned slot path is a slot that already exists, whatever it points
    # at, and it refuses here through the registered path.
    existing = [os.path.relpath(slot, STUDY) for slot in slots if os.path.lexists(slot)]
    if existing:
        raise BatchError("these slots already exist and are never rewritten: %s"
                         % ", ".join(existing))
    return pins


def require_freeze(pins: dict) -> str:
    """§2.10: the preregistration's freeze digest, before anything is called.

    The freeze precedes the recapture, which precedes the batch, so the pin is
    already fillable at every point this runs. Registering it as a precondition
    of the CALLS as well as of the scoring is what makes it more than an
    intention: a registry merged with its null intact spends no quota."""
    pinned = (pins.get("freeze") or {}).get("preregistrationSha256")
    if not pinned:
        raise BatchError(
            "harness/PINS.json registers no freeze.preregistrationSha256: the frozen "
            "PREREGISTRATION.md's digest replaces the null at the freeze, before any "
            "call is made, so that a post-freeze edit is detectable (§2.10)")
    path = os.path.join(STUDY, "PREREGISTRATION.md")
    if not os.path.isfile(path):
        raise BatchError("the preregistration is missing from %s" % STUDY)
    actual = _digest(path)
    if not _matches(actual, pinned):
        raise BatchError("PREREGISTRATION.md is %s, not the %s registered at the "
                         "freeze: it was edited after the freeze" % (actual, pinned))
    return actual


def golden_path_for(pins: dict, override: str = None) -> str:
    """The capture's path is structural — `transcription/GOLDEN-CONTEXT.json`,
    as §3.2 step 2 names it — and the registry pins its digest, which is how
    this study treats every registered artifact. `--golden` serves the harness
    tests; the pin still has to match whatever it names."""
    return override or DEFAULT_GOLDEN


def require_golden(pins: dict, golden_path: str = None) -> str:
    """§3.2 step 3, as much of it as a driver can check: the capture is on disk
    and the registry's `golden.sha256` is non-null and equal to its digest,
    before any slot is created. A skipped recapture therefore costs nothing
    instead of costing a hundred and fifty calls, and the digest verified here
    is stamped into every slot's CALL.json so the binding is per run and not
    per batch. ONE capture serves all five arms [D-8]: the pre-prompt context
    precedes the prompt and does not depend on it, and that does not become
    five properties because there are five prompts.

    What this does NOT check, stated here so no caller can read more into it:
    that either file was COMMITTED. Nothing in this study compares a worktree
    file to a HEAD blob (§7, "deliberately not claimed"); committing the
    capture and the registry before slot 1 is ledger discipline the study
    records, not an ordering the driver enforces."""
    path = golden_path_for(pins, golden_path)
    pinned = pins.get("golden", {}).get("sha256")
    if not os.path.isfile(path):
        raise BatchError(
            "no golden context at %s: run the §3.2 recapture (batch.py capture "
            "--scratch-parent DIR) and commit it before the first slot" % path)
    if not pinned:
        raise BatchError(
            "harness/PINS.json registers no golden.sha256: the capture's digest must "
            "replace the null and be committed before the first slot (§3.2 step 3)")
    actual = _digest(path)
    if not _matches(actual, pinned):
        raise BatchError("the golden capture at %s is %s, not the registered %s"
                         % (path, actual, pinned))
    return path


def require_isolation_negative(pins: dict, golden_path: str) -> dict:
    """§6 C7's retained verdict, before any slot is created. The control runs
    ONCE and BEFORE the batch (README step 5, §6 C7), and round 9 finding 3 is
    that the ordering was ceremony only: the registry's assent gated the
    control's own command and nothing else, so a hundred and fifty calls could
    be spent on a study whose §7 publication list promises a control record
    that was never made — and a post-hoc run would be a departure from "before
    the batch" rather than the registered step.

    Checked here: the registry records the assent; the verdict is at the
    CANONICAL path and readable as duplicate-free JSON; its outcome is one of
    §6 C7's THREE registered outcomes; it names the same assent the registry
    now records; and it was compared against the golden capture THIS batch runs
    behind, which is the capture whose gate C7 demonstrates the power of (§3.2,
    §6 C7). Round 10, finding 5 adds the last of it: the record has the SHAPE
    the writer produces, in `score_rates.c7_record_shape_problems()`, which
    names what is checked and what is deliberately not. All three outcomes
    admit the batch — a `no-context` verdict already exits non-zero and is
    reported as undemonstrated, and refusing it here would make that registered
    sentence unreachable, because the command refuses to rewrite a record that
    exists. What is refused is a control that never ran.

    The path is structural, `controls/isolation-negative/`, and `--out` is not
    consulted: [D-23]'s rule that a derived canonical location is not an
    argument applies to the record a precondition reads as much as to the
    population root.

    What this does NOT establish, stated so no caller reads more into it: that
    the control's own calls were the registered ones — the wrapper checks the
    probe prompt and the pinned binary at the moment C7 runs — nor that the
    record was COMMITTED, which is ledger discipline the study records and not
    an ordering this driver enforces (§7, "deliberately not claimed")."""
    assent = pins.get("isolationNegative", {}).get("assent")
    if assent != "granted":
        raise BatchError(
            "harness/PINS.json records isolationNegative.assent %r: §6 C7 runs "
            "before the batch and the registry records the assent it ran under "
            "(README step 5)" % (assent,))
    path = os.path.join(DEFAULT_NEGATIVE, "VERDICT.json")
    relative = os.path.relpath(path, STUDY)
    if not os.path.isfile(path):
        raise BatchError(
            "no §6 C7 record at %s: the isolation negative control runs ONCE, "
            "BEFORE the batch (batch.py capture-isolation-negative "
            "--scratch-parent DIR), and no slot is created until its verdict is "
            "on disk" % relative)
    try:
        verdict = _load_json(path)
    except (ValueError, OSError) as error:
        raise BatchError("%s cannot be read as duplicate-free JSON (%s): the "
                         "control's verdict is the record the batch runs behind"
                         % (relative, error))
    if not isinstance(verdict, dict):
        raise BatchError("%s is a %s and §6 C7's verdict is an object"
                         % (relative, type(verdict).__name__))
    if verdict.get("outcome") not in C7_OUTCOMES:
        raise BatchError("%s records outcome %r and §6 C7 registers %r: a record "
                         "carrying none of them is not a control that ran"
                         % (relative, verdict.get("outcome"), list(C7_OUTCOMES)))
    if verdict.get("assent") != assent:
        raise BatchError("%s: the control was authorized by %r and the registry "
                         "now records %r: the record is not this batch's"
                         % (relative, verdict.get("assent"), assent))
    recorded = verdict.get("goldenSha256")
    actual = _digest(golden_path)
    if not isinstance(recorded, str) or not _matches(actual, recorded):
        raise BatchError("%s: the control was compared against golden capture %r "
                         "and this batch runs against %s: C7 demonstrates the "
                         "power of the gate THIS batch runs behind (§3.2, §6 C7)"
                         % (relative, recorded, actual))
    shape = score_rates.c7_record_shape_problems(verdict)
    if shape:
        raise BatchError("%s: %s — the record is not one this driver wrote"
                         % (relative, "; ".join(shape)))
    return verdict


def invoke(slot: str, scratch_parent: str, pins_path: str, cli_override: str,
           prompt_kind: str, arm: str, arm_prompt_path: str,
           isolation: str = "isolated", golden_sha256: str = None) -> tuple:
    """(wrapper exit status, refusal code or None, stderr) for one call.

    `arm` and `arm_prompt_path` are §2.7's two new wrapper arguments, inserted
    before the optional binary: the wrapper writes into the arm's slot tree —
    and refuses a slot path that is not `arms/<ARM>/authoring/` — and stamps
    `arm` and `armPromptSha256` into CALL.json, so §3.3's `arm-mismatch` is a
    per-slot check against retained bytes rather than a claim about this
    driver's bookkeeping. The probe calls pass the wrapper's registered
    no-arm literal and the probe prompt's own path.

    `golden_sha256` is the digest `require_golden()` verified at preflight; the
    wrapper stamps it into the slot's CALL.json, so the scorer can check the
    golden-before-slots ordering per slot instead of taking it on trust (§3.2).
    The probe calls — the recapture and §6 C7 — precede the golden and pass
    none.

    The environment contract is 011's, unchanged and not extended: PYTHON_BIN,
    PROMPT_KIND, ISOLATION, GOLDEN_SHA256. §2.9's schedule stamps do NOT travel
    this way, because §2.7 registers the wrapper's permitted differences as
    exactly three and reading a round index from the environment is not among
    them; `stamp_slot()` writes them after this returns.
    """
    argv = ["bash", SCRIPT, scratch_parent, slot, pins_path, arm, arm_prompt_path]
    if cli_override is not None:
        argv.append(cli_override)
    environment = dict(os.environ)
    environment["PYTHON_BIN"] = sys.executable
    environment["PROMPT_KIND"] = prompt_kind
    environment["ISOLATION"] = isolation
    environment["GOLDEN_SHA256"] = golden_sha256 or ""
    # The helper interpreters the wrapper runs must not write bytecode
    # beside the reviewed sources: an existing cache loads even under -B,
    # and the verification gate refuses on one (§2.10, round 5 finding 3).
    environment = dict(environment)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(argv, env=environment, capture_output=True, text=True)
    return (completed.returncode, WRAPPER_CODES.get(completed.returncode, "wrapper-error"),
            completed.stderr)


def stamp_slot(slot: str, entry: dict, pins: dict) -> None:
    """§2.9's schedule stamps into `CALL.json`, after checking §2.7's.

    Two things happen here, in this order, and both before the slot is sealed.

    First the wrapper's own stamps are checked against the schedule this driver
    planned: the `arm` must be the slot's SCHEDULED arm, the `armPromptSha256`
    must be that arm's pinned prompt (§3.1 gate 9), and the `slotIndex` the
    wrapper read out of the slot name must be the arm's own index. The scorer
    re-derives all of it from the retained bytes and assigns `arm-mismatch` and
    `schedule-mismatch` itself (§3.3) — nothing here is that judgment. What
    this catches is a driver/wrapper disagreement, at a cost of one call rather
    than a hundred and fifty, and it refuses the batch because every remaining
    slot would carry the same defect.

    Then the three members §2.9 registers and the wrapper does not write —
    `round`, `position`, `globalIndex` — are added. **They are written here and
    not by the wrapper**, and §2.2's port table says so in its own words: the
    arm and schedule stamps in `CALL.json` are this file's registered scope,
    while §2.7 registers the wrapper's permitted differences as exactly three,
    none of which is reading a schedule from its environment. The stamps go in
    before `seal_slot()` runs, so they are inside the seal and an edit to them
    afterwards is exactly what §2.9's manifest and chain refuse.

    A slot with no CALL.json — the wrapper refused before it wrote one — has
    nothing to stamp and nothing to check, and is left to the scorer, which
    reads the absence itself (`call-unreadable`).

    A refusal here leaves the slot on disk, unsealed and unrecorded, which the
    scorer refuses as a slot with no ledger record (§3.3): the disagreement is
    adjudicated in `DEVIATIONS.md` and not by this driver, whose alternative
    would be to seal bookkeeping it has just found to be wrong.
    """
    call_path = os.path.join(slot, "CALL.json")
    if not os.path.isfile(call_path):
        return
    call = _load_json(call_path)
    _, pinned = arm_prompt(pins, entry["arm"])
    if call.get("arm") != entry["arm"]:
        raise BatchError(
            "%s is scheduled as arm %s at global index %d and its CALL.json records "
            "arm %r: the batch stops here rather than spending the remaining slots "
            "under a wrapper that names the wrong arm (§2.7, §3.1 gate 9)"
            % (os.path.relpath(slot, STUDY), entry["arm"], entry["globalIndex"],
               call.get("arm")))
    stamped = call.get("armPromptSha256")
    if not isinstance(stamped, str) or not _matches(stamped, pinned):
        raise BatchError(
            "%s records armPromptSha256 %r and arm %s's registered prompt is %s: the "
            "run was made with bytes that are not the arm's (§3.1 gate 9)"
            % (os.path.relpath(slot, STUDY), stamped, entry["arm"], pinned))
    if call.get("slotIndex") != entry["slotIndex"]:
        raise BatchError(
            "%s records slotIndex %r and the registered order assigns arm %s's slot "
            "%d at global index %d: the slot's name and its place in the order "
            "disagree (§2.9)"
            % (os.path.relpath(slot, STUDY), call.get("slotIndex"), entry["arm"],
               entry["slotIndex"], entry["globalIndex"]))
    for member in ("globalIndex", "round", "position"):
        if member in call:
            raise BatchError(
                "%s already carries a %s stamp (%r): the schedule stamps are written "
                "once, by the driver, into the slot it just made"
                % (os.path.relpath(slot, STUDY), member, call[member]))
        call[member] = entry[member]
    _write_json(call_path, call)


def refuse_slot(slot: str, code: str, status: int, stderr: str) -> None:
    """Terminate one slot with its refusal record. A pre-flight refusal may
    leave no slot at all; the record still gets one, so every attempted run is
    on disk and the population has no invisible members.

    `exist_ok=True` covers the ordinary case of a slot the wrapper created. It
    does not cover a path that exists and is not a directory — a link, a file,
    a FIFO — where `makedirs` raises `FileExistsError` and the batch would end
    in a bare traceback. Preflight already refuses those, so reaching this is a
    bug; it refuses as a BatchError rather than as a traceback so that the
    driver's failure is one of its own registered refusals either way."""
    if os.path.lexists(slot) and not os.path.isdir(slot):
        raise BatchError(
            "%s exists and is not a directory, so no refusal record can be written "
            "into it: remove it by hand and record the cause in DEVIATIONS.md" % slot)
    os.makedirs(slot, exist_ok=True)
    _write_json(os.path.join(slot, "REFUSAL.json"), {
        "run": os.path.basename(slot),
        "code": code,
        "wrapperExit": status,
        "wrapperStderrTail": stderr[-STDERR_TAIL:],
        "note": "Recorded by batch.py. score_rates.py recomputes admission from the "
                "retained bytes and does not trust this record.",
    })


def _entry_type(mode: int) -> str:
    """The type marker a non-regular entry is sealed by. Every marker is a
    fixed string, so the seal a driver writes and the list a scorer recomputes
    name a FIFO the same way on both sides (round 7, finding 3)."""
    for predicate, marker in TYPE_MARKERS:
        if predicate(mode):
            return marker
    return "other"


def slot_files(slot: str) -> list:
    """§2.9's sorted list, over the slot ROOT and EVERY entry beneath it, in
    path order — the shape `score_rates.py` recomputes and compares entry for
    entry.

    A regular file is `[relative path, byte length, bare sha256 hex]`. Every
    other entry — a symlink, a directory, a FIFO, a socket, a device — is
    `[relative path, NON_FILE_LENGTH, "type:<marker>"]`: named and typed, since
    it is not a byte range to hash.

    **Round 8, finding 4: the root is an entry too, at path `.`.** Round 7's
    fix walked only what lay BENEATH the slot and never `lstat`ed `run-NNN`
    itself, so the whole of round 7 could be evaded one level up: rename the
    sealed directory and plant a symlink at its old path, and every entry the
    list covers is byte-identical through the link — `verify_seal()` returned
    None while §3.3's lstat-first rule scored the slot `slot-symlink` and moved
    it out of `V_X` into `I_X` with `sealed` still true. That is the same
    denominator change round 7 closed, bought at the one path round 7 did not
    seal. The root's own `lstat` type is now the row `. -1 type:directory`, so
    a root replaced by a link to itself is a manifest discrepancy and §2.9's
    consequence is the WHOLE batch's — every level verdict
    `UNRESOLVED-BY-DESIGN`, no contrast — rather than one slot's. No entry
    beneath the root can collide with it: `os.path.relpath` of a child is never
    `.`.

    **Round 7, finding 3: every entry, not every regular file.** This listed
    regular files only, so an entry ADDED after the seal — a symlink, most
    of all — left the manifest recomputing exactly as written and
    `verify_seal()` succeeding. §3.3's lstat-first rule then scored that slot
    `slot-symlink`, which moves it out of `V_X` and into `I_X`: a post-seal
    alteration buying precisely the denominator change §2.9 registers that it
    must never buy. Recording every entry makes any post-seal addition a seal
    discrepancy instead, which §2.9 makes the WHOLE batch's — every level
    verdict `UNRESOLVED-BY-DESIGN`, no contrast — rather than one slot's.
    §2.9's sentence was amended to say "every entry" for the same reason.

    `SLOT-MANIFEST.json` is excluded from its own list — a file cannot carry
    its own digest — and is sealed instead by the ledger, which records the
    digest of the manifest file itself. `os.walk` does not descend into
    symlinked directories, so a link cannot smuggle a subtree into the seal:
    the link itself is one typed row, and the tree it points at is not the
    slot's. Every type is decided by `lstat`, and only regular files are
    opened, so a FIFO in a slot tree is sealed rather than read (an `open()`
    on one blocks forever)."""
    rows = [[SLOT_ROOT_ENTRY, NON_FILE_LENGTH,
             "type:%s" % _entry_type(os.lstat(slot).st_mode)]]
    for base, directories, names in os.walk(slot):
        directories.sort()
        for name in sorted(directories + names):
            path = os.path.join(base, name)
            relative = os.path.relpath(path, slot)
            if relative == MANIFEST_NAME:
                continue
            mode = os.lstat(path).st_mode
            if stat.S_ISREG(mode):
                with open(path, "rb") as handle:
                    body = handle.read()
                rows.append([relative, len(body),
                             hashlib.sha256(body).hexdigest()])
            else:
                rows.append([relative, NON_FILE_LENGTH,
                             "type:%s" % _entry_type(mode)])
    return sorted(rows)


def files_digest(files: list) -> str:
    """§2.9's "sha256 of that sorted list", made byte-exact: one
    `<path> <bytes> <sha256>` line per file, sorted, newline-terminated.

    §2.9 registers the CONTENT of the list and not its serialization, so the
    serialization has to be fixed somewhere — and this is `harness/integrity.py`'s
    tree-manifest encoding line for line (§2.10), which `score_rates.py`'s
    `manifest_digest()` recomputes. One manifest convention for the study, and
    the harness test that seals a fixture and re-verifies it is what holds the
    driver and the scorer together.

    A non-regular entry's row encodes in the same three fields (round 7,
    finding 3): `<path> -1 type:<marker>`. §2.10's whole-tree manifest is over
    git-tracked regular files and never produces one, so the encoding is
    unchanged there; a slot tree can hold anything, and the seal has to be able
    to say so."""
    listing = "\n".join("%s %d %s" % tuple(row) for row in sorted(files)) + "\n"
    return "sha256:" + hashlib.sha256(listing.encode("utf-8")).hexdigest()


def seal_slot(slot: str, entry: dict) -> str:
    """§2.9's terminal manifest, and the digest of the FILE it writes — the
    value the ledger record carries, which binds the list and its digest into
    the chain and is what `score_rates.py`'s `verify_seal()` recomputes.

    **The sealer is the driver, by the amended registration.** §2.9 as
    amended under round 3's dispositioned finding 5 names the driver as the
    sealer; the seal is written HERE, one statement after the wrapper
    returns.
    The reason is that the same section requires the seal to cover *the slot*
    and the wrapper is not the last writer into it: `REFUSAL.json` is this
    driver's (§2.5, Study 011's registered difference from Study 010, ported
    unchanged), so a manifest written inside the wrapper would seal every slot
    except the refused ones — leaving exactly the slots whose retained bytes
    explain a failure unsealed, and the pipeline-invalid rate is an endpoint
    (§4.4). The seal is therefore taken after the refusal record and the
    schedule stamps are written and before the ledger record is appended, for
    every outcome including refusals; the wrapper's own header states the same
    division ("it does not seal the slot — SLOT-MANIFEST.json and the ledger
    chain of §2.9 are the driver's"), so the two artifacts agree rather than
    each assuming the other did it. `harness/PORTS.md` carries the
    adjudication record.

    What the seal establishes and what it does not is §2.9's own statement,
    repeated here so no caller reads more into it: the operator can recompute
    the whole chain. It shows that a slot was not altered in isolation or after
    the ledger was published; it does not show that the ledger was written
    honestly, and this study has no transparency log (§7)."""
    if not os.path.isdir(slot):
        raise BatchError(
            "%s is not a directory after the wrapper returned, so it cannot be "
            "sealed: record the cause in DEVIATIONS.md" % slot)
    path = os.path.join(slot, MANIFEST_NAME)
    if os.path.lexists(path):
        raise BatchError("%s already exists: a slot is sealed once, and a slot that "
                         "carries a seal was not created by this invocation" % path)
    files = slot_files(slot)
    _write_json(path, {
        "slot": os.path.basename(slot),
        "arm": entry["arm"],
        "globalIndex": entry["globalIndex"],
        "files": files,
        "filesSha256": files_digest(files),
        "note": "The terminal seal of this slot (§2.9): the slot ROOT itself, at the "
                "relative path `.`, and EVERY entry beneath it by relative path — "
                "regular files by byte length and sha256, everything "
                "else (symlinks, directories, FIFOs, sockets, devices) by a -1 length "
                "and a type: marker — sorted by path, and the sha256 of that sorted "
                "list. Every entry, so that an entry ADDED after the seal breaks it "
                "rather than passing it and then buying that slot a pipeline-invalid "
                "code and the denominator change it carries; and the root, so that "
                "renaming this directory and planting a symlink at its old path "
                "breaks it for the same reason. "
                "This file is not a member of its own "
                "list — a file cannot carry its own digest — and is sealed instead by "
                "the ledger, whose record for this slot carries the digest of THIS "
                "FILE and the previous record's digest, so BATCH.json is a hash chain "
                "in schedule order. A slot whose recomputed manifest differs from the "
                "ledger's, or a chain that does not verify, invalidates confirmatory "
                "scoring for the WHOLE batch rather than moving this slot out of a "
                "denominator (§2.9).",
    })
    return _digest(path)


def record_digest(record: dict) -> str:
    """One ledger record's digest, over the same canonical serialization the
    manifest's list uses. The record being digested carries its own
    `previousSha256`, which is what makes the sequence a chain rather than a
    list of independently digested lines."""
    return "sha256:" + hashlib.sha256(_canonical(record)).hexdigest()


def ledger_record(entry: dict, slot: str, status: int, code: str,
                  manifest_sha256: str, previous: str) -> dict:
    """§2.8 [D-22] and §2.9's per-slot record: where the slot sits in the
    registered order, where it sits on disk, what the wrapper's exit status
    was, its seal, and the digest of the record before it."""
    record = {key: entry[key] for key in SCHEDULE_KEYS}
    record.update({
        "slot": os.path.basename(slot),
        # §6 C5 clause 2 puts the ledger and the slot set in bijection "at the
        # path the record names", so the record names one — study-relative, so
        # the ledger is portable and the population is not addressed by an
        # absolute path this machine happens to have.
        "path": os.path.relpath(slot, STUDY),
        "wrapperExit": status,
        "code": code,
        "manifestSha256": manifest_sha256,
        "previousSha256": previous,
    })
    return record


def load_ledger() -> list:
    """The per-slot records BATCH.json already holds, IN FILE ORDER. A resumed
    batch MERGES into these rather than replacing them: §2.9 registers the
    wrapper's exit status as retained per slot, and a slot that exited 0 carries
    it nowhere else, so overwriting the ledger would delete the only record of
    runs the resume did not make.

    File order is schedule order, and that is verified here before the records
    are used for anything. Round 3 finding 16: this function sorted the records
    by `globalIndex` first, so a ledger whose records had been physically
    reordered was silently normalized — the prefix check then passed over the
    sorted list, the resume continued, and `write_ledger()` rewrote the file in
    the order the driver preferred. `score_rates.py` reads the same file in file
    order and refuses it, so the two modules disagreed about the same bytes. A
    reordered ledger is a ledger someone edited; §2.9's chain is over the file,
    and the driver refuses rather than repairing it.

    Round 8, finding 9: the decoded top level and the `records` member are both
    TYPE-CHECKED here. `BATCH.json` holding `[]` used to reach `.get` on a list
    and raise an `AttributeError`, which is not one of `main()`'s registered
    refusals — the operator got a traceback where §2.8's resume rule promises a
    refusal naming the file."""
    path = os.path.join(ARMS_ROOT, LEDGER_NAME)
    if not os.path.isfile(path):
        return []
    ledger = _load_json(path)
    if not isinstance(ledger, dict):
        # Round 8, finding 9: `[]` decodes fine and then `.get` raised an
        # AttributeError outside `main()`'s catch — a traceback where §2.8's
        # resume rule promises malformed population state refuses through the
        # driver's own registered path.
        raise BatchError(
            "%s decodes to a JSON %s and a ledger is an object carrying a records "
            "list: a file that is not one is not this batch's ledger, whatever it "
            "holds. Move it aside and record why in DEVIATIONS.md"
            % (path, type(ledger).__name__))
    records = ledger.get("records")
    if records is None:
        raise BatchError(
            "%s is a pre-merge ledger (batchVersion %r) and cannot be resumed into: "
            "move it aside and record why in DEVIATIONS.md"
            % (path, ledger.get("batchVersion")))
    if not isinstance(records, list):
        raise BatchError(
            "%s's records member is a JSON %s and §2.9 registers it as the list of "
            "per-slot records in schedule order: a ledger whose records are not a "
            "list has no prefix to check and no chain to verify. Move it aside and "
            "record why in DEVIATIONS.md" % (path, type(records).__name__))
    previous = None
    for offset, record in enumerate(records):
        index = record.get("globalIndex") if isinstance(record, dict) else None
        if not isinstance(index, int) or isinstance(index, bool):
            raise BatchError(
                "%s's record %d carries globalIndex %r: every ledger record names its "
                "place in §2.8's registered order, and a record that does not cannot "
                "be checked against it" % (path, offset + 1, index))
        if previous is not None and index <= previous:
            raise BatchError(
                "%s records global index %d after %d: the ledger is append-only in "
                "§2.8's registered order and its FILE order is that order. A file "
                "whose records have been moved is refused, not re-sorted — the driver "
                "would otherwise rewrite it in an order the scorer never saw. Record "
                "the cause in DEVIATIONS.md" % (path, index, previous))
        previous = index
    return records


def verify_chain(records: list) -> None:
    """§2.9's hash chain, verified over the ledger in schedule order.

    Verified by the DRIVER and not only by the scorer, because a batch whose
    chain does not verify can never be scored confirmatorily (§2.9 registers
    that consequence in advance), and continuing to spend calls into it would
    be spending them on a batch that already has no verdict to give."""
    previous = None
    for record in records:
        if record.get("previousSha256") != previous:
            raise BatchError(
                "the ledger's hash chain breaks at global index %r: the record names "
                "%r as its predecessor's digest and the record before it digests to "
                "%r. A batch whose chain does not verify is not scored "
                "confirmatorily at all (§2.9); record the cause in DEVIATIONS.md"
                % (record.get("globalIndex"), record.get("previousSha256"), previous))
        previous = record_digest(record)


def verify_prefix(records: list, entries: list) -> None:
    """The ledger IS the registered order's prefix of its own length, position
    by position, or BatchError naming the first divergence ([D-22], §6 C5
    clause 3).

    This is what makes resumption by global index safe where `--start-round`
    was not: a round number cannot say whether the rest of its round ran, and
    an overlap or an omission inside a round is undetectable after the fact
    from one. A prefix of the registered order is checkable against the order
    itself, at every position, before a call is spent.

    **Round 8, finding 5: the record's `path` is one of the compared members,
    and it is DERIVED.** Nothing here read it, and `reconcile_ledger()` asked
    only that it be a nonempty string naming something that exists — so a first
    record carrying §2.8's schedule keys for global index 1 and the path
    `README.md` verified as the registered prefix, reconciled against a study
    tree in which `run-001` was absent, and let `--resume` continue at index 2.
    The slot at index 1 was never made and nothing said so. §6 C5 clause 2 puts
    the ledger and the slot set in bijection "at the path the record names", so
    the path a record names has to be the path §2.8 assigns its (arm, slot
    index) — recomputed here from `slot_path()`, the same function the driver
    plans and seals with, rather than compared against a shape."""
    if len(records) > len(entries):
        raise BatchError(
            "%s records %d slots and §2.8 registers %d: a ledger longer than the "
            "registered order is not a prefix of it"
            % (os.path.join(ARMS_ROOT, LEDGER_NAME), len(records), len(entries)))
    for offset, record in enumerate(records):
        expected = {key: entries[offset][key] for key in SCHEDULE_KEYS}
        # The canonical slot path for THIS position, derived from the schedule
        # entry by the function that plans it, exactly as `ledger_record()`
        # writes it (round 8, finding 5).
        expected["path"] = os.path.relpath(slot_path(entries[offset]), STUDY)
        actual = {key: record.get(key) for key in SCHEDULE_KEYS}
        actual["path"] = record.get("path")
        if actual != expected:
            raise BatchError(
                "the ledger diverges from §2.8's registered call order at position "
                "%d: it records %r and the order assigns %r. No slot is re-run and "
                "no batch continues from a ledger that is not a prefix of the "
                "registered order [D-22]" % (offset + 1, actual, expected))
    verify_chain(records)


def ledger_header(member: str, default=None):
    """One member of the ledger FILE's own header, or `default` when there is no
    ledger yet. `declare_shortfall()` reads `cliOverride` through this when it
    completes a crash-interrupted record: the header describes the batch that
    ran, and the declaration is not the place to restate it from a fresh
    command line."""
    path = os.path.join(ARMS_ROOT, LEDGER_NAME)
    if not os.path.isfile(path):
        return default
    ledger = _load_json(path)
    return ledger.get(member, default) if isinstance(ledger, dict) else default


def write_ledger(records: list, pins: dict, cli_override: str) -> None:
    # Atomically (round 6, finding 6): this file is rewritten in full after
    # every slot, and a kill during the rewrite used to be able to leave a
    # truncated one — losing the only record of every slot that ran before it.
    _write_json_atomic(os.path.join(ARMS_ROOT, LEDGER_NAME), {
        "batchVersion": "3",
        "registeredRunsPerArm": RUNS_PER_ARM,
        "registeredSlots": REGISTERED_SLOTS,
        "model": pins["codex"]["model"],
        "binarySha256": pins["codex"]["binarySha256"],
        "armPromptSha256": {arm: arm_prompt(pins, arm)[1] for arm in ARMS},
        "goldenSha256": pins.get("golden", {}).get("sha256"),
        "cliOverride": cli_override,
        # Schedule order IS chain order: each record's previousSha256 is the
        # digest of the record before it in this list, so sorting by global
        # index is the same list the chain was built in.
        "records": sorted(records, key=lambda row: row["globalIndex"]),
        "note": "One append-only record per slot in §2.8's registered order, written "
                "after every run and MERGED by a resumed invocation (batch.py run "
                "--resume), which continues at the next global index, refuses to "
                "overlap a recorded one, and refuses if the recorded prefix diverges "
                "from the registered order at any position [D-22]. Each record "
                "carries its slot's SLOT-MANIFEST.json digest and the previous "
                "record's digest, so this file is a hash chain over the batch (§2.9) "
                "— which the operator can recompute in full, and which therefore "
                "shows that no slot was altered in isolation, not that this ledger "
                "was written honestly (§7). No clock is recorded here; each slot's "
                "CALL.json carries its own start and end.",
    })


def verify_seal_of(slot: str, entry: dict) -> str:
    """The digest of a slot's `SLOT-MANIFEST.json` when that manifest is this
    slot's — the slot root and every entry beneath it at the length, digest or
    type marker it records (round 8, finding 4), the sorted-list digest over
    them, and the slot, arm and global index it names — or BatchError saying
    which of those failed.

    This is `seal_slot()` read backwards, over a slot the driver did not just
    make. It exists for the one case that needs it (`reconcile_ledger()` below)
    and it recomputes rather than trusts: a manifest that does not verify is
    exactly the evidence that a slot was interrupted mid-write or edited, and
    neither may be admitted to the ledger on the strength of the file that
    claims to seal it.

    Round 7, finding 4: a manifest that is not readable JSON, or whose keys are
    duplicated, is that same evidence and refuses through this registered path
    rather than escaping `reconcile_ledger()` as a bare `ValueError` — the
    operator gets a refusal naming the slot where the registration promises
    one, and the batch is left exactly as it was found.
    """
    path = os.path.join(slot, MANIFEST_NAME)
    if os.path.islink(path) or not os.path.isfile(path):
        raise BatchError(
            "%s is not sealed: %s is missing or is not a regular file. The driver "
            "seals a slot BEFORE it records it, so an unsealed slot is one whose "
            "wrapper never returned — it did not run to a terminal outcome, and no "
            "ledger record can be completed for it. Remove it by hand and record "
            "the cause in DEVIATIONS.md"
            % (os.path.relpath(slot, STUDY), MANIFEST_NAME))
    try:
        manifest = _load_json(path)
    except (ValueError, OSError) as error:
        raise BatchError(
            "%s cannot be read as duplicate-free JSON (%s): a seal that cannot be "
            "read is not a seal that verifies, and no ledger record is completed "
            "from one. Remove the slot by hand and record the cause in "
            "DEVIATIONS.md" % (os.path.relpath(path, STUDY), error))
    if not isinstance(manifest, dict):
        raise BatchError("%s is not a JSON object" % os.path.relpath(path, STUDY))
    named = (manifest.get("slot"), manifest.get("arm"), manifest.get("globalIndex"))
    expected = (os.path.basename(slot), entry["arm"], entry["globalIndex"])
    if named != expected:
        raise BatchError(
            "%s seals %r and §2.8's registered order puts %r at that path: the "
            "manifest is not this slot's" % (os.path.relpath(path, STUDY),
                                             named, expected))
    files = slot_files(slot)
    if manifest.get("files") != files or manifest.get("filesSha256") != files_digest(files):
        raise BatchError(
            "%s does not verify against the slot it seals: the tree on disk is not "
            "the one the manifest lists. A slot whose seal does not recompute is "
            "not admitted to the ledger — §2.9 makes that discrepancy the whole "
            "batch's, and completing a record from a broken seal would put it "
            "inside the chain instead" % os.path.relpath(path, STUDY))
    return _digest(path)


def slot_outcome(slot: str) -> tuple:
    """(wrapper exit status, refusal code) as the SLOT's own retained bytes
    record them: `REFUSAL.json` when the driver terminated it, and exit 0 with
    no code when the wrapper wrote a `CALL.json` and no refusal.

    Those are the only two shapes `run_batch()` produces, and the pair is
    checked against `WRAPPER_CODES` rather than taken from the file: a refusal
    record naming a code no exit status of this wrapper yields is not this
    driver's, and a slot carrying neither artifact never reached a terminal
    outcome at all (§6 C5 rule 1).
    """
    refusal_path = os.path.join(slot, "REFUSAL.json")
    call_path = os.path.join(slot, "CALL.json")
    relative = os.path.relpath(slot, STUDY)
    if not os.path.islink(refusal_path) and os.path.isfile(refusal_path):
        refusal = _load_json(refusal_path)
        if not isinstance(refusal, dict):
            raise BatchError("%s/REFUSAL.json is not a JSON object" % relative)
        status, code = refusal.get("wrapperExit"), refusal.get("code")
        if not isinstance(status, int) or isinstance(status, bool):
            raise BatchError("%s/REFUSAL.json records wrapperExit %r, and §2.9 "
                             "registers an integer exit status" % (relative, status))
        if code != WRAPPER_CODES.get(status, "wrapper-error"):
            raise BatchError(
                "%s/REFUSAL.json records code %r for wrapper exit %d, and this "
                "driver writes %r for that status: the refusal record is not one "
                "this batch produced"
                % (relative, code, status, WRAPPER_CODES.get(status, "wrapper-error")))
        return status, code
    if not os.path.islink(call_path) and os.path.isfile(call_path):
        return 0, None
    raise BatchError(
        "%s carries neither CALL.json nor REFUSAL.json: it is not a terminal slot, "
        "and no ledger record describes it honestly (§6 C5 rule 1). Record the "
        "cause in DEVIATIONS.md" % relative)


def slots_on_disk() -> list:
    """Every slot present under every arm's `authoring/`, as sorted
    study-relative paths, counted by the SCORER's own rule (round 7,
    finding 4).

    `score_rates.collect_slots()` names an entry `run-NNN` a slot whatever it
    holds — a directory, a symlink, a FIFO, a regular file — because the NAME is
    what claims the index. The driver counts the population the same way the
    scoring will, so a reconciliation cannot pass over a slot the scorer will
    then refuse to score.
    """
    present = []
    for arm in ARMS:
        root = os.path.join(ARMS_ROOT, arm, "authoring")
        if not os.path.isdir(root):
            continue
        slots, _unexpected = score_rates.collect_slots(root)
        present.extend(os.path.relpath(path, STUDY) for path in slots)
    return sorted(present)


def reconcile_ledger(records: list, entries: list) -> dict:
    """The ONE ledger record a crash between the seal and the ledger write can
    leave unwritten, completed from that slot's own seal — or None when the
    ledger and the slots on disk already agree. Any other disagreement is a
    BatchError naming it exactly.

    Round 6, finding 6. §2.9 has the driver seal a slot and then append its
    ledger record, so there is a window in which a slot is sealed and the ledger
    does not name it. A kill inside that window used to leave a batch that could
    not be resumed and could not be declared short either: `--resume` planned
    the orphan's index again and refused its existing path, while `shortfall`
    counted the slots on disk and the ledger's records separately and wrote a
    declaration whose two numbers disagreed — which the scorer then refused
    under C5. The batch was stuck with no registered way forward.

    **The slot RAN.** That is the whole of the reasoning, and it is why
    completing the record is not the same as inventing one: the wrapper
    returned, the driver wrote the refusal record and the schedule stamps, and
    the driver sealed the tree — every one of those precedes the ledger append,
    and the seal is the evidence that all of them happened. Only the bookkeeping
    was interrupted. Nothing is re-run, no call is spent, and every member of
    the completed record is READ from the slot: its place in §2.8's registered
    order, the seal's digest, the wrapper's exit status and refusal code from
    the slot's own `REFUSAL.json`, and the previous record's digest from the
    ledger.

    The conditions are narrow on purpose, and each refuses rather than guesses:

      * the orphan is the NEXT scheduled slot and nothing further ahead — the
        driver runs the order one slot at a time, so a slot beyond the next
        index was not left by this driver;
      * there is exactly ONE — two orphans mean two slots ran with no record
        between them, which this window cannot produce and which no seal can
        put back in order;
      * its manifest VERIFIES — an unsealed or unverifiable slot is one whose
        wrapper never returned or whose tree was edited, and §2.9 makes that the
        whole batch's problem rather than something a driver quietly repairs;
      * every recorded slot is still on disk — a ledger record whose slot is
        gone is the disagreement in the other direction, and the scorer refuses
        the whole scoring for it (C5 rule 2).

    **Round 7, finding 4: the reconciliation is over every slot PRESENT, not
    over the canonical paths §2.8 would name next.** This used to look only at
    the future schedule's own paths, so a slot at an index the registered order
    never assigns — `run-099` — was invisible to it: `--resume` planned the
    remaining order and spent calls over a population the scoring would then
    refuse under C5 rule 4, and the operator learned it after the calls. Every
    slot on disk is now either recorded in the ledger at the path the record
    names, or the single orphan at the next registered index, or the batch
    refuses before any call is made.
    """
    for offset, record in enumerate(records):
        path = record.get("path")
        if not isinstance(path, str) or not path:
            # An absent or empty `path` used to join to the study root itself,
            # which exists, so a record naming no slot passed the check below
            # as a slot that is present (round 7, finding 4).
            raise BatchError(
                "ledger record %d names no slot path (%r): §6 C5 clause 2 puts the "
                "ledger and the slot set in bijection at the path the record names, "
                "and a record that names none cannot be reconciled with anything. "
                "Record the cause in DEVIATIONS.md" % (offset + 1, path))
    recorded = [os.path.normpath(record["path"]) for record in records]
    missing = [path for path in recorded
               if not os.path.lexists(os.path.join(STUDY, path))]
    if missing:
        raise BatchError(
            "the ledger records %d slot(s) that are not on disk (%s): a ledger "
            "record with no slot is not a crash this driver can have caused, and "
            "the scorer refuses the whole scoring over it (§6 C5 rule 2). Record "
            "the cause in DEVIATIONS.md"
            % (len(missing), ", ".join(missing)))
    orphans = [entry for entry in entries[len(records):]
               if os.path.lexists(slot_path(entry))]
    if len(orphans) > 1:
        raise BatchError(
            "%d slots past the ledger's last record exist on disk (global indices "
            "%s) and the ledger records none of them. The seal-then-record window "
            "can leave at most ONE, so this is not an interrupted append: no slot "
            "is admitted to the ledger from it, and the cause goes in DEVIATIONS.md"
            % (len(orphans), ", ".join(str(entry["globalIndex"]) for entry in orphans)))
    permitted = set(recorded)
    if orphans:
        permitted.add(os.path.relpath(slot_path(orphans[0]), STUDY))
    unaccounted = [path for path in slots_on_disk() if path not in permitted]
    if unaccounted:
        raise BatchError(
            "%d slot(s) are on disk that the ledger does not record and §2.8's "
            "registered order does not put next (%s): the seal-then-record window "
            "leaves exactly ONE slot, at the next registered index, so this is not "
            "that window. No call is made and no record is completed from it — the "
            "slots go, or the cause goes in DEVIATIONS.md"
            % (len(unaccounted), ", ".join(unaccounted)))
    if not orphans:
        return None
    entry = orphans[0]
    if entry["globalIndex"] != entries[len(records)]["globalIndex"]:
        raise BatchError(
            "a slot exists at global index %d and the ledger ends at %d: the driver "
            "runs the registered order one slot at a time, so a slot past the next "
            "index was not left by an interrupted append. Record the cause in "
            "DEVIATIONS.md"
            % (entry["globalIndex"], records[-1]["globalIndex"] if records else 0))
    slot = slot_path(entry)
    if os.path.islink(slot) or not os.path.isdir(slot):
        raise BatchError(
            "%s exists and is not a directory, so it is not a sealed slot this "
            "driver left: slots already on disk are never rewritten, and this one "
            "must be removed by hand with the cause recorded in DEVIATIONS.md"
            % os.path.relpath(slot, STUDY))
    manifest = verify_seal_of(slot, entry)
    status, code = slot_outcome(slot)
    previous = record_digest(records[-1]) if records else None
    return ledger_record(entry, slot, status, code, manifest, previous)


def run_batch(runs: int, resume: bool, scratch_parent: str, pins_path: str,
              cli_override: str, dry_run: bool,
              golden_override: str = None) -> int:
    entries = schedule_entries()
    records = load_ledger()
    verify_prefix(records, entries)
    done = len(records)
    if records and not resume:
        raise BatchError(
            "%s already records %d slots: a batch is continued with `run --resume`, "
            "which resumes at global index %d, and never restarted [D-22]"
            % (os.path.join(ARMS_ROOT, LEDGER_NAME), done, done + 1))
    # The crash window §2.9 leaves open, closed on the resume that follows it
    # (round 6, finding 6): a slot sealed and not yet recorded is completed from
    # its seal, and any other disagreement between the ledger and the slots on
    # disk refuses here rather than being planned over. `--resume` only: a plain
    # `run` over retained slots is a restart, and no slot is ever rewritten.
    recovered = reconcile_ledger(records, entries) if resume else None
    if recovered is not None:
        records.append(recovered)
        verify_prefix(records, entries)
        done = len(records)
        if not dry_run:
            # The completed record enters the ledger under the same
            # preconditions a call does: the ported bytes, the freeze, and the
            # no-slots-after-a-rate rule. It is written BEFORE anything else so
            # that a resume with nothing left to run still leaves the ledger
            # whole.
            if os.path.exists(RESULTS):
                raise BatchError(
                    "%s exists: no ledger record may be completed after a rate has "
                    "been computed, any more than a slot may be created (§2.8)"
                    % RESULTS)
            verify_ported_bytes()
            recovery_pins = _load_json(pins_path)
            require_freeze(recovery_pins)
            write_ledger(records, recovery_pins, cli_override)
        print("%s the ledger record for global index %d from its seal: the slot "
              "ran and only the append was interrupted"
              % ("dry run: would complete" if dry_run else "completed",
                 recovered["globalIndex"]))
    if resume and not records:
        raise BatchError(
            "--resume was given and the ledger records no slot: there is nothing to "
            "resume at, and the first invocation of a batch is `run` without it")
    remaining = entries[done:]
    if not remaining:
        raise BatchError(
            "the registered order is complete: all %d slots are in the ledger, and "
            "no batch may be extended (§2.8)" % REGISTERED_SLOTS)
    if runs is not None:
        if runs < 1:
            raise BatchError("a batch needs at least one run")
        if runs > len(remaining):
            raise BatchError(
                "--runs %d asks for more slots than the registered order has left: "
                "%d of %d are in the ledger and %d remain. The order is fixed before "
                "the batch (§2.8), so an invocation that would reach past global "
                "index %d is refused before a call is spent"
                % (runs, done, REGISTERED_SLOTS, len(remaining), REGISTERED_SLOTS))
        remaining = remaining[:runs]
    slots = [slot_path(entry) for entry in remaining]
    pins = preflight(remaining, slots, scratch_parent, pins_path, cli_override,
                     "registered", golden_override)
    if dry_run:
        print("dry run: %d slots, none created" % len(slots))
        print("  model      %s" % pins["codex"]["model"])
        print("  binary     %s" % pins["codex"]["binarySha256"])
        for arm in ARMS:
            print("  prompt %s   %s" % (arm, arm_prompt(pins, arm)[1]))
        print("  golden     %s" % pins.get("golden", {}).get("sha256"))
        print("  wrapper    %s" % SCRIPT)
        print("  cli        %s" % (cli_override or "codex on PATH"))
        for entry, slot in zip(remaining, slots):
            print("  would create %s (global %d, round %d, position %d, arm %s)"
                  % (os.path.relpath(slot, STUDY), entry["globalIndex"],
                     entry["round"], entry["position"], entry["arm"]))
        return 0
    os.makedirs(ARMS_ROOT, exist_ok=True)
    # The digest preflight verified, stamped into every slot this invocation
    # makes: a golden swapped after the batch changes the pin, and every slot
    # then names a digest that is not the pin it is being scored under.
    golden_pin = pins.get("golden", {}).get("sha256")
    previous = record_digest(records[-1]) if records else None
    for entry, slot in zip(remaining, slots):
        status, code, stderr = invoke(slot, scratch_parent, pins_path, cli_override,
                                      "registered", entry["arm"],
                                      arm_prompt(pins, entry["arm"])[0],
                                      golden_sha256=golden_pin)
        # Refusal record, then the schedule stamps, then the seal, then the
        # ledger. The order is the registered one and each step is a reason for
        # the next: the refusal record is part of the slot (§2.5) and the
        # schedule stamps are part of CALL.json (§2.9), so both must be written
        # before the manifest that seals them; and the ledger record carries
        # the manifest's digest, so it is appended after the seal exists.
        if code is not None:
            refuse_slot(slot, code, status, stderr)
        stamp_slot(slot, entry, pins)
        manifest = seal_slot(slot, entry)
        records.append(ledger_record(entry, slot, status, code, manifest, previous))
        previous = record_digest(records[-1])
        write_ledger(records, pins, cli_override)
        print("%03d %s %s: exit %d%s"
              % (entry["globalIndex"], entry["arm"], os.path.basename(slot), status,
                 "" if code is None else " (%s)" % code))
    made = records[done:]
    refused = [row for row in made if row["code"] is not None]
    print("batch: %d slots this invocation (%d refused), %d of %d in the ledger"
          % (len(made), len(refused), len(records), REGISTERED_SLOTS))
    return 0


def capture_slots(directory: str) -> list:
    """Every retained slot beneath a directory that has a session and a call
    record, in name order. Used by the recapture: capture slots are not batch
    slots, are not named run-NNN, and never enter any denominator — a
    directory named run-<digits> refuses outright, so a golden capture can
    never be derived from the batch's own runs."""
    if not os.path.isdir(directory):
        raise BatchError("%s is not a directory" % directory)
    found = []
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        parts = name.split("-", 1)
        if os.path.isdir(path) and len(parts) == 2 and parts[0] == "run" \
                and parts[1].isdigit():
            raise BatchError(
                "%s holds the batch slot %s: a golden capture is derived from probe "
                "captures taken before the batch, never from the batch's own runs"
                % (directory, name))
        if os.path.isdir(path) and not os.path.islink(path) \
                and os.path.isfile(os.path.join(path, "session.jsonl")) \
                and os.path.isfile(os.path.join(path, "CALL.json")):
            found.append(path)
    return found


def capture_identity(slot: str) -> dict:
    """The raw retained evidence of WHICH call produced this capture (§3.2).

    Raw, deliberately: the session file's bytes, the session id, and the call
    record's own wall clock, working directory and isolated home. Not the
    normalized context digests — those are what two independent calls are
    SUPPOSED to share.
    """
    call = _load_json(os.path.join(slot, "CALL.json"))
    return {
        "slot": os.path.basename(slot),
        "sessionSha256": _digest(os.path.join(slot, "session.jsonl")),
        "sessionId": score_rates.session_identity(os.path.join(slot, "session.jsonl")),
        "callIdentity": (call.get("startedAt"), call.get("endedAt"),
                         call.get("cwd"), call.get("home")),
    }


def require_distinct_sessions(identities: list) -> None:
    """Every capture slot is a different call, or BatchError naming the pair.

    The hole this closes: `capture-golden` counted slots and compared
    normalized contexts, so two slots holding one call's evidence — a copied
    directory, or one transcript retained twice — agreed perfectly and derived
    an allowlist from a context that had never been shown to reproduce. The
    floor of two is a floor of two INDEPENDENT calls.
    """
    for index, first in enumerate(identities):
        for second in identities[index + 1:]:
            for member, prose in CAPTURE_IDENTITY:
                if first[member] is None or second[member] is None:
                    continue
                if first[member] != second[member]:
                    continue
                raise BatchError(
                    "capture %s and capture %s share %s (%r): a golden capture is "
                    "derived from at least two INDEPENDENT calls that reproduced "
                    "the same context, and two slots holding one call's evidence "
                    "agree by construction rather than by reproduction (§3.2)"
                    % (first["slot"], second["slot"], prose, first[member]))


def capture_golden(slots_dir: str, out_path: str, min_slots: int,
                   pins_path: str = DEFAULT_PINS) -> int:
    """Derive this study's golden pre-prompt context from retained capture
    slots (PREREGISTRATION.md §3.2).

    Study 010 locked a capture taken from two independent real runs that
    reproduced identically, and Study 011 repeated that procedure in its own
    environment; this repeats it again here, because a golden capture pins one
    machine's codex boilerplate and an inherited one would refuse every honest
    run. The captures must AGREE — a context that varies run to run cannot be
    an allowlist — and none of them may carry a leak token before the prompt,
    or the capture would bless a planted turn. ONE capture serves all five arms
    [D-8]: the pre-prompt context precedes the prompt and does not depend on
    it, which is the property that made the probe-prompt capture legitimate in
    the first place and does not become five properties because there are five
    prompts.

    The two-capture rule is enforced HERE, where the derivation happens, and
    not only in the command that makes the calls: `MIN_CAPTURE_SLOTS` is a
    floor, so `--min-slots 1` refuses rather than deriving an allowlist from a
    single unreproduced context — and the two must be two independent CALLS,
    which `require_distinct_sessions()` checks on the raw retained evidence
    rather than on the normalized digests two honest calls are supposed to
    share.

    It runs the same preflight the command that makes the calls runs — the
    ported bytes, the registered interpreter, and the preregistration's freeze
    digest — because this half derives the artifact every later admission is
    checked against. Without it a golden capture could be derived under an
    unregistered interpreter from an unfrozen study. And it requires every
    capture slot to be a PROBE call at the pinned probe-prompt digest:
    `capture_slots()` refuses batch-shaped names, but a name is not evidence of
    which prompt was answered, and a golden derived from an arm's own runs
    would pin a context the operator had already seen coverage profiles from
    (§3.2 step 2).
    """
    if not out_path:
        raise BatchError("--out is required: a golden capture is written where the "
                         "operator names it, never into the study tree by default")
    if os.path.exists(out_path):
        raise BatchError("%s already exists; a registered capture is never rewritten"
                         % out_path)
    if min_slots < MIN_CAPTURE_SLOTS:
        raise BatchError(
            "a golden capture is derived from at least %d agreeing captures and "
            "--min-slots %d asks for fewer: one capture cannot show that a "
            "pre-prompt context reproduces, and a context that might vary is not "
            "an allowlist (§3.2)" % (MIN_CAPTURE_SLOTS, min_slots))
    verify_ported_bytes()
    pins = _load_json(pins_path)
    require_freeze(pins)
    probe_pin = pins.get("probePrompt", {}).get("sha256")
    if not probe_pin:
        raise BatchError("%s pins no probePrompt.sha256: a capture is derived only "
                         "from runs of the registered probe prompt (§3.2)" % pins_path)
    usable, contexts, identities = [], [], []
    for slot in capture_slots(slots_dir):
        session = os.path.join(slot, "session.jsonl")
        call = _load_json(os.path.join(slot, "CALL.json"))
        if call.get("promptKind") != "probe" or call.get("promptSha256") != probe_pin:
            raise BatchError(
                "capture %s records promptKind %r and prompt %r: a golden capture is "
                "derived only from calls that answered the registered PROBE prompt "
                "(%s). Running an arm's prompt before the batch would show the "
                "operator coverage profiles first, which is the cost Study 010's "
                "DEVIATIONS §1 records (§3.2 step 2)"
                % (os.path.basename(slot), call.get("promptKind"),
                   call.get("promptSha256"), probe_pin))
        events, turn_contexts = transcript_check._events(session)
        positions = [index for index, (role, _) in enumerate(events) if role == "user"]
        position = positions[-1] if positions else len(events)
        transcript_check.screen_prior_context(
            events, position, transcript_check.environment_paths(turn_contexts, call))
        usable.append(os.path.basename(slot))
        contexts.append(transcript_check.context_digests(session, call))
        identities.append(capture_identity(slot))
    required = max(min_slots, MIN_CAPTURE_SLOTS)
    if len(usable) < required:
        raise BatchError("a capture needs at least %d capture slots with a session; found %d"
                         % (required, len(usable)))
    # …and they are that many CALLS: agreement between two copies of one
    # transcript is not reproduction (§3.2). Checked before the contexts are
    # compared, because a duplicate agrees by construction and the comparison
    # below would report success.
    require_distinct_sessions(identities)
    first = contexts[0]
    for name, context in zip(usable[1:], contexts[1:]):
        if context != first:
            raise BatchError("capture %s does not reproduce %s's pre-prompt context; "
                             "a varying context cannot be an allowlist" % (name, usable[0]))
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    _write_json(out_path, {
        "contextVersion": first["contextVersion"],
        "entries": first["entries"],
        "capturedFrom": usable,
        "capturedIn": os.path.basename(os.path.abspath(slots_dir)),
        "note": "The pre-prompt context of this study's registered invocations, captured "
                "from independent probe-prompt runs that reproduced identically after "
                "normalization. One capture serves all five arms (§3.2 [D-8]). Any "
                "deviation in a batch run's context refuses that run (score_rates.py, "
                "code transcript-refused). Its digest goes into harness/PINS.json "
                "golden.sha256 and both are committed before round 1.",
    })
    print("captured: %d entries from %d agreeing captures" % (len(first["entries"]), len(usable)))
    print("next: put %s into harness/PINS.json golden.sha256 and commit both before "
          "the first slot" % _digest(out_path))
    return 0


def next_attempt(captures_dir: str) -> str:
    """`controls/recapture/attempt-N/`, the next unused N.

    §3.2 step 2 registers that a disagreeing recapture may be repeated after
    the environmental cause is fixed. A repeat needs somewhere to go: slots are
    never rewritten, so attempt 2 is its own directory and every attempt stays
    published (§8)."""
    used = []
    if os.path.isdir(captures_dir):
        for name in os.listdir(captures_dir):
            parts = name.split("-", 1)
            if len(parts) == 2 and parts[0] == "attempt" and parts[1].isdigit():
                used.append(int(parts[1]))
    return os.path.join(captures_dir, "attempt-%d" % ((max(used) + 1) if used else 1))


def run_capture(runs: int, captures_dir: str, out_path: str, scratch_parent: str,
                pins_path: str, cli_override: str) -> int:
    """The §3.2 recapture, end to end: N probe calls into a numbered attempt
    directory, then the derivation.

    The probe prompt — not any arm's — is deliberate. The pre-prompt context
    precedes the prompt and does not depend on it, and running an arm's prompt
    here would show the operator coverage profiles before the batch, which is
    exactly the cost Study 010's DEVIATIONS §1 records. It is also what makes
    ONE recapture serve five arms [D-8]: the probe's bytes are
    arm-independent by construction.
    """
    if os.path.exists(out_path):
        raise BatchError("%s already exists; a registered capture is never rewritten"
                         % out_path)
    if runs < MIN_CAPTURE_SLOTS:
        # Before a single call is spent: a recapture that could only produce one
        # context could never derive a capture from it.
        raise BatchError(
            "the recapture makes at least %d probe calls and --runs %d asks for "
            "fewer: the capture is derived only from contexts that agree, so one "
            "call could never produce one (§3.2)" % (MIN_CAPTURE_SLOTS, runs))
    attempt = next_attempt(captures_dir)
    slots = plan(runs, 1, attempt, stem="capture")
    preflight([], slots, scratch_parent, pins_path, cli_override, "probe")
    os.makedirs(attempt, exist_ok=True)
    print("capture attempt: %s" % attempt)
    for slot in slots:
        status, code, stderr = invoke(slot, scratch_parent, pins_path, cli_override,
                                      "probe", PROBE_ARM, PROBE_PROMPT)
        if code is not None:
            refuse_slot(slot, code, status, stderr)
            raise BatchError("capture %s failed (%s); the batch does not start until two "
                             "captures agree. Fix the cause and run capture again: the "
                             "next attempt gets its own directory."
                             % (os.path.basename(slot), code))
        print("%s: exit %d" % (os.path.basename(slot), status))
    return capture_golden(attempt, out_path, runs, pins_path)


def capture_isolation_negative(out_dir: str, scratch_parent: str, pins_path: str,
                               cli_override: str, golden_override: str) -> int:
    """§6 C7: the isolation gate's power, demonstrated rather than assumed.

    ONE probe call with the operator's REAL home — everything else exactly as
    registered — whose registered expectation is that it FAILS the golden
    match. If it matches instead, the gate has no demonstrated power against
    home leakage in this environment; that is recorded and the batch proceeds
    unchanged. Registering both outcomes before the batch is what keeps this a
    control rather than a decision. It runs ONCE for the whole batch, not per
    arm [D-8]: it uses the probe prompt and tests home leakage, neither of
    which depends on which policy text an arm carries.

    THREE outcomes are registered, not two (§6 C7): `refused` (the expectation),
    `matched` (the limitation), and `no-context` — the call produced nothing
    comparable, so neither comparison happened. `no-context` returns NON-ZERO:
    it is a control that did not run, and returning 0 for it would report a
    step as done that reached neither registered comparison. Its verdict is
    still retained, so the failure is on disk rather than only in a shell's
    exit status.

    Retention is done by code, not by the operator's care: the call is made
    into a scratch slot, and the only bytes that reach the study are the
    comparison verdict, a CALL.json stripped of every member that names or
    enumerates the operator's environment, and — when the call produced one —
    the context digests. session.jsonl, stdout.raw and stderr.raw are digested
    and deleted here — publishing the transcript of a non-isolated run would
    publish an inventory of the operator's own machine, which is the thing the
    control exists to detect. The deletion is VERIFIED, not attempted: if the
    scratch slot survives the removal this refuses and names it, because
    "deleted by the driver" is a claim about the disk and `ignore_errors` would
    make it a claim about the call that was made.

    The control's slot is not a slot of the registered order, so it carries no
    schedule stamps and is not sealed into the ledger: it is a control, it
    enters no denominator, and §2.9's chain is over the batch.
    """
    verify_ported_bytes()
    pins = _load_json(pins_path)
    require_freeze(pins)
    # §6 C7's assent is `isolationNegative.assent` — the member the registry
    # registers and the only one that can authorize this call. The driver read
    # `isolationNegative.operatorAssent` until round 3 finding 4, so granting
    # assent where the registry records it left the control refusing, and
    # granting it where the code looked would have run the control with the
    # registry recording nothing.
    assent = pins.get("isolationNegative", {}).get("assent")
    if assent != "granted":
        raise BatchError(
            "harness/PINS.json records isolationNegative.assent %r: C7 is the one "
            "registered step that exposes the operator's real environment to the "
            "pinned CLI and it runs only with recorded assent (§6 C7)" % (assent,))
    if not os.path.isdir(scratch_parent):
        raise BatchError("scratch parent %s is not a directory" % scratch_parent)
    golden = require_golden(pins, golden_override)
    if os.path.exists(out_dir):
        raise BatchError("%s already exists; a registered control is never rewritten"
                         % out_dir)
    raw = os.path.join(scratch_parent, "s012-c7-raw-%d" % os.getpid())
    if os.path.exists(raw):
        raise BatchError("%s already exists" % raw)
    status, code, stderr = invoke(raw, scratch_parent, pins_path, cli_override,
                                  "probe", PROBE_ARM, PROBE_PROMPT,
                                  isolation="operator-home")
    try:
        call_path = os.path.join(raw, "CALL.json")
        if not os.path.isfile(call_path):
            raise BatchError("the control left no CALL.json (wrapper exit %d): %s"
                             % (status, stderr[-STDERR_TAIL:]))
        call = _load_json(call_path)
        session = os.path.join(raw, "session.jsonl")
        context_path = os.path.join(raw, "context.json")
        if os.path.isfile(session) and os.path.isfile(context_path):
            try:
                transcript_check.check_golden(session, call, golden)
                outcome, message = "matched", (
                    "the non-isolated call reproduced the golden pre-prompt context: "
                    "the golden gate has no demonstrated power against home leakage "
                    "in this environment (§6 C7, recorded as a limitation)")
            except transcript_check.TranscriptError as error:
                outcome, message = "refused", str(error)
        else:
            # Round 10, finding 5: "neither registered outcome occurred" was
            # plainly false — `no-context` IS one of §6 C7's three registered
            # outcomes, and this string is the one that reports it. What did
            # not happen is a COMPARISON, which is the word §6 C7 itself,
            # README step 5 and both neighbours below already use.
            outcome, message = "no-context", (
                "the control produced no comparable context (wrapper exit %d, code %r): "
                "neither registered comparison happened and the gate's power is "
                "undemonstrated" % (status, code))
        digests = {}
        for name in ("session.jsonl", "stdout.raw", "stderr.raw", "completion.txt"):
            path = os.path.join(raw, name)
            if os.path.isfile(path):
                digests[name] = _digest(path)
        os.makedirs(out_dir)
        if os.path.isfile(context_path):
            shutil.copyfile(context_path, os.path.join(out_dir, "context.json"))
        stripped = {key: value for key, value in call.items() if key not in C7_REDACTED}
        stripped["redacted"] = sorted(key for key in C7_REDACTED if key in call)
        stripped["note"] = ("§6 C7's CALL.json, stripped by batch.py of every member "
                            "that names or enumerates the operator's real environment. "
                            "The transcript was digested and deleted, not retained.")
        _write_json(os.path.join(out_dir, "CALL.json"), stripped)
        _write_json(os.path.join(out_dir, "VERDICT.json"), {
            "control": "C7 — the isolation gate's power",
            "registeredExpectation": "the golden match FAILS",
            "registeredOutcomes": list(C7_OUTCOMES),
            "outcome": outcome,
            "message": message,
            "wrapperExit": status,
            "wrapperCode": code,
            "goldenSha256": _digest(golden),
            "deletedByCode": digests,
            # The registry member this call was authorized by, under the
            # registry's own name for it (§6 C7, `isolationNegative.assent`):
            # one member name in the registry, in the driver and in the
            # retained verdict.
            "assent": assent,
            "retention": "This file and a stripped CALL.json are always retained, and "
                         "context.json whenever the call produced a comparable "
                         "context (outcome 'no-context' is the case where it did "
                         "not). session.jsonl, stdout.raw, stderr.raw and any "
                         "completion were digested above and deleted by batch.py, and "
                         "the deletion is verified: publishing the transcript of a "
                         "deliberately non-isolated run would publish an inventory of "
                         "the operator's environment.",
        })
    finally:
        # Every exit from the block above passes here, including the ones that
        # are already carrying an exception — so the warning is printed on all
        # of them and the refusal is raised on the one that would otherwise
        # have reported success.
        shutil.rmtree(raw, ignore_errors=True)
        if os.path.exists(raw):
            print("WARNING: the control's scratch slot %s survived removal" % raw,
                  file=sys.stderr)
    if os.path.exists(raw):
        raise BatchError(
            "the control's scratch slot %s survived removal: its transcript is an "
            "inventory of the operator's environment and is still on disk. Remove it "
            "by hand and record the cause in DEVIATIONS.md before publishing anything "
            "from %s" % (raw, out_dir))
    print("C7: %s — %s" % (outcome, message))
    print("retained under %s: %s" % (out_dir, ", ".join(sorted(os.listdir(out_dir)))))
    if outcome == "no-context":
        print("refused: the control reached neither registered comparison; its verdict "
              "is retained and the gate's power is undemonstrated", file=sys.stderr)
        return 1
    return 0


def completed_rounds(records: list) -> int:
    """§2.8's "last completed round *R*": the last round every one of whose
    five slots the ledger holds, and **zero** when no round is whole.

    Round 3 finding 15: the declaration used the LAST SLOT's round, so a batch
    that died three slots into round 1 declared one round completed — and the
    headline §2.8 registers ("R of 30 rounds completed") would have reported a
    round that never finished. The count is derived from the prefix here, which
    `verify_prefix()` has already checked against the registered order, so
    "completed" means every slot of that round is on disk and in the chain.
    """
    counted = {}
    for record in records:
        counted[record.get("round")] = counted.get(record.get("round"), 0) + 1
    whole = 0
    while counted.get(whole + 1) == POSITIONS:
        whole += 1
    return whole


def last_slot_clock(records: list) -> tuple:
    """(§2.8's UTC wall clock of the last completed slot, the record it was read
    from) — falling back through the prefix to the last slot that HAS a
    `CALL.json`.

    Round 3 finding 15's other half: the wrapper writes `CALL.json` after the
    call returns, so a tail whose wrapper refused at preflight has no clock at
    all, and the declaration recorded a bare `null` with nothing saying why. The
    driver reads no clock of its own (§2.8 registers the timestamp as the
    wrapper's stamp, not the declaration's), so the honest fallback is the last
    slot that carries one — named in the declaration beside the value, so a
    reader can see the timestamp is that slot's and not the tail's.
    """
    for record in reversed(records):
        call_path = os.path.join(STUDY, record.get("path") or "", "CALL.json")
        if not os.path.isfile(call_path):
            continue
        ended = _load_json(call_path).get("endedAt")
        if ended:
            return ended, record
    return None, None


def declare_shortfall(reason: str, pins_path: str) -> int:
    """§2.8: a batch that cannot finish declares the shortfall BEFORE anything
    is scored. The scorer refuses an incomplete batch without this file, so the
    declaration cannot be written after the rates are seen — and it refuses a
    declaration over a batch that is not short, so this file cannot be used to
    unblock scoring of a full or over-full one.

    What it declares is §2.8's own list: the reason, the last completed round
    R, the exact completed prefix of the registered order — the global index of
    the last completed slot — and the UTC wall clock of that slot. The prefix
    is the ledger's, verified against the registered order first, because §6 C5
    clause 5 requires the declared prefix to equal the ledger's slot for slot,
    and per-arm counts follow from a prefix where they do not follow from a
    round number (clause 4).

    The clock is READ, not taken: the driver holds no clock, and the timestamp
    is the one the wrapper stamped into that slot's CALL.json when it ran. §2.8
    says plainly what it is worth — it does not make a stop involuntary, it
    timestamps the stop against the append-only ledger. `completed_rounds()` and
    `last_slot_clock()` above are the two edge cases round 3 finding 15 found:
    a prefix that ends mid-round completed the round BEFORE it, and a tail whose
    wrapper refused before writing a CALL.json has no clock of its own, so the
    declaration names the slot the clock it publishes came from.

    Declaring one costs the study its whole confirmatory surface: under §2.8's
    stopping rule [D-21] an incomplete batch, at any round and for any reason,
    yields `UNRESOLVED-BY-DESIGN` on every level verdict and no contrast at
    all. That price is registered in advance and is not this file's to reduce.

    It runs the same ported-bytes, interpreter and freeze preflight the calls
    and the scoring run: this file enters the published population arithmetic,
    so it is not a step that may be taken under an unregistered interpreter or
    against an unfrozen preregistration."""
    verify_ported_bytes()
    if os.path.exists(RESULTS):
        raise BatchError("%s exists: a shortfall may not be declared after a rate has "
                         "been computed" % RESULTS)
    out_path = os.path.join(ARMS_ROOT, SHORTFALL_NAME)
    if os.path.exists(out_path):
        raise BatchError("%s already exists" % out_path)
    if not reason:
        raise BatchError("--reason is required: a shortfall without a reason is a gap")
    pins = _load_json(pins_path)
    require_freeze(pins)
    entries = schedule_entries()
    records = load_ledger()
    verify_prefix(records, entries)
    # The slots actually on disk, counted by the SCORER's own rule, so the
    # driver's count is not a second definition of the population — and by the
    # same function the reconciliation below enumerates them with (round 7,
    # finding 4), so the declaration and the reconciliation cannot be looking at
    # two different populations.
    present = len(slots_on_disk())
    if present >= REGISTERED_SLOTS:
        raise BatchError(
            "%d slots are present and %d were registered: a shortfall declares a SHORT "
            "batch, and this one is not short" % (present, REGISTERED_SLOTS))
    # The declaration is a statement about the ledger AND about the slots on
    # disk — §6 C5 rule 5 requires the declared prefix to equal the ledger's,
    # and the scorer requires the slots present to be exactly that prefix — so
    # the two are reconciled before either is written down (round 6, finding 6).
    # A batch killed in the seal-then-record window is exactly the batch that
    # then needs a shortfall, and it used to be the one batch that could not
    # have one: the counts were taken separately and the declaration they
    # produced was refused by the scorer. The single interrupted append is
    # completed from the slot's own seal, here as on the resume and by the same
    # function; anything else refuses with the disagreement named.
    recovered = reconcile_ledger(records, entries)
    if recovered is not None:
        records.append(recovered)
        verify_prefix(records, entries)
        write_ledger(records, pins, ledger_header("cliOverride"))
        print("completed the ledger record for global index %d from its seal: the "
              "slot ran and only the append was interrupted"
              % recovered["globalIndex"])
    if present != len(records):
        raise BatchError(
            "%d slots are on disk and the ledger records %d: a declaration is a "
            "statement about the ledger AND about the slots present, and the "
            "scorer requires the two to agree slot for slot (§6 C5 rules 2 and "
            "5). The disagreement is not the seal-then-record window — that "
            "leaves exactly one slot, and it is completed above — so it goes in "
            "DEVIATIONS.md rather than into a declaration the scoring will refuse"
            % (present, len(records)))
    last = records[-1] if records else None
    whole_rounds = completed_rounds(records)
    stopped_at, clock_record = last_slot_clock(records)
    _write_json(out_path, {
        "registeredRounds": ROUNDS,
        "registeredRunsPerArm": RUNS_PER_ARM,
        "registeredSlots": REGISTERED_SLOTS,
        # §2.8's "last completed round R", counted over WHOLE rounds: a prefix
        # that ends inside a round declares the round before it, and zero when
        # none is whole (the headline reports "R of 30 rounds completed").
        "completedRounds": whole_rounds,
        # §2.8's "exact completed prefix of the registered schedule" is the
        # global index of the last completed slot. `score_rates.py`'s
        # check_population() reads exactly this member to check C5 rule 5 —
        # the declared prefix against the ledger's, slot for slot — and the
        # registered parity test asserts the two spellings agree (a first
        # draft wrote it as `globalIndex` and every honest short batch would
        # have refused).
        "completedThroughGlobalIndex": last["globalIndex"] if last else 0,
        "completedSlots": present,
        "lastSlot": last["path"] if last else None,
        "lastSlotEndedAt": stopped_at,
        # Which slot that clock is the clock OF. It is the last slot of the
        # prefix whenever that slot has a CALL.json, and an earlier one when the
        # tail's wrapper refused before writing one; a reader can tell the two
        # apart by comparing it with lastSlot instead of guessing.
        "lastSlotEndedAtFrom": clock_record["path"] if clock_record else None,
        "reason": reason,
        "note": "Declared before scoring. The completed prefix is the ledger's, "
                "verified against §2.8's registered call order position by position; "
                "the scorer requires it to equal the ledger's prefix slot for slot "
                "and the slots actually present to be exactly that prefix (§6 C5). "
                "completedRounds counts WHOLE rounds — a prefix ending inside a round "
                "declares the round before it, and 0 when none is whole. "
                "lastSlotEndedAt is read from a slot's own CALL.json — the driver "
                "reads no clock — and falls back through the prefix to the last slot "
                "that HAS one, because a wrapper that refused at preflight wrote no "
                "CALL.json and therefore stamped no clock; lastSlotEndedAtFrom names "
                "the slot it was read from, and both are null when no slot of the "
                "prefix carries a timestamp at all. The headline reports 'R of 30 "
                "rounds completed', and an incomplete batch returns no verdict of any "
                "kind: every level verdict is UNRESOLVED-BY-DESIGN and no contrast is "
                "computed (§2.8 [D-21]).",
    })
    print("shortfall declared: %d of %d rounds, %d of %d slots completed"
          % (whole_rounds, ROUNDS, present, REGISTERED_SLOTS))
    return 0


def _argument(argv: list, flag: str, default=None):
    if flag not in argv:
        return default
    index = argv.index(flag)
    if index + 1 >= len(argv):
        raise BatchError("%s needs a value" % flag)
    return argv[index + 1]


USAGE = (
    "usage: batch.py run --scratch-parent DIR [--resume] [--runs N] [--pins PATH]\n"
    "                    [--golden PATH] [--cli-override PATH] [--dry-run]\n"
    "       batch.py capture --scratch-parent DIR [--captures DIR] [--out PATH]\n"
    "                    [--runs N] [--pins PATH] [--cli-override PATH]\n"
    "       batch.py capture-golden --slots DIR --out PATH [--min-slots N]\n"
    "       batch.py capture-isolation-negative --scratch-parent DIR [--out DIR]\n"
    "                    [--pins PATH] [--golden PATH] [--cli-override PATH]\n"
    "       batch.py shortfall --reason TEXT [--pins PATH]")

COMMANDS = ("run", "capture", "capture-golden", "capture-isolation-negative",
            "shortfall")

# Flags a command line may still carry from Study 011's driver, each removed by
# a registered decision. They refuse by name rather than being ignored: a
# command line that means something else now must not quietly do something
# else. (`capture-golden` keeps its own `--slots`, which names a capture
# attempt directory and not the population.)
REMOVED = {
    "--start": "resumption is by global schedule index, not by slot index: "
               "`run --resume` continues at the ledger's next index [D-22]",
    "--start-round": "a round number cannot resume a partly completed round "
                     "without either overlapping recorded slots or silently "
                     "omitting the rest of that round, and neither is "
                     "detectable after the fact from one. Use `run --resume` "
                     "[D-22]",
    "--slots": "the population root is derived from the harness's own "
               "location (harness/../arms) and no argument names it [D-23]",
}


def main(argv: list) -> int:
    if len(argv) < 2 or argv[1] not in COMMANDS:
        print(USAGE, file=sys.stderr)
        return 2
    command = argv[1]
    try:
        pins_path = _argument(argv, "--pins", DEFAULT_PINS)
        if command in ("run", "shortfall"):
            for flag, why in REMOVED.items():
                if flag in argv:
                    raise BatchError("%s is removed from `batch.py %s`: %s"
                                     % (flag, command, why))
        if command == "run":
            runs = _argument(argv, "--runs")
            scratch_parent = _argument(argv, "--scratch-parent")
            if scratch_parent is None:
                raise BatchError("--scratch-parent is required")
            # An omitted --runs runs the registered order to its end from
            # wherever the ledger leaves off; there is no count to infer,
            # because the order is the registry's and its length is 150.
            return run_batch(int(runs) if runs is not None else None,
                             "--resume" in argv, scratch_parent, pins_path,
                             _argument(argv, "--cli-override"),
                             "--dry-run" in argv,
                             _argument(argv, "--golden"))
        if command == "capture":
            scratch_parent = _argument(argv, "--scratch-parent")
            if scratch_parent is None:
                raise BatchError("--scratch-parent is required")
            return run_capture(int(_argument(argv, "--runs", 2)),
                               _argument(argv, "--captures", DEFAULT_CAPTURES),
                               _argument(argv, "--out", DEFAULT_GOLDEN),
                               scratch_parent, pins_path,
                               _argument(argv, "--cli-override"))
        if command == "capture-isolation-negative":
            scratch_parent = _argument(argv, "--scratch-parent")
            if scratch_parent is None:
                raise BatchError("--scratch-parent is required")
            return capture_isolation_negative(
                _argument(argv, "--out", DEFAULT_NEGATIVE), scratch_parent,
                pins_path, _argument(argv, "--cli-override"),
                _argument(argv, "--golden"))
        if command == "capture-golden":
            slots_dir = _argument(argv, "--slots")
            if slots_dir is None:
                raise BatchError("--slots is required")
            return capture_golden(slots_dir, _argument(argv, "--out"),
                                  int(_argument(argv, "--min-slots", 2)), pins_path)
        return declare_shortfall(_argument(argv, "--reason"), pins_path)
    except (BatchError, score_rates.ScoreError, transcript_check.TranscriptError) as error:
        print("refused: %s" % error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
