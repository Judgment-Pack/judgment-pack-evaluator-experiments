#!/usr/bin/env python3
"""The scorer: five arms of authoring slots in, per-class per-arm rates and the
registered §5 verdicts out.

It is the study's one counting authority (PREREGISTRATION.md §3-§5, §6 C5). For
every slot it re-derives admission from the retained bytes — it never trusts the
batch's own refusal record, and a slot the batch refused whose bytes now admit
it is itself invalid, code `refusal-conflict` — recompiles the completion with
the ported compiler, splits the accepted records into H and Q with **that arm's
mirror instantiation**, and intersects them with **that arm's** `FAMILY.json`
predicates. The valid-run population is computed by `admit()` and by nothing
else (§6 C5, the Study 001 lesson: a preregistration constrains what you may
claim, only code can enforce the population a claim was computed on).

PORTED FROM Study 011's `harness/score_rates.py`, at the commit §2.2's port
table records; 011 pinned none of its own harness files, so this port answers to
that commit, to the cross-vendor review of the diff, and to §2.10's tree
manifest, and to nothing older (§6 C1). The enumerated changes, and nothing
else:

  1. **Per-arm scoring.** Every quantity is computed per arm X ∈ {A,B,C,D,E}
     against **that arm's** mirror instantiation — the one registered module
     `harness/policy_mirror.py` at the `(T_low, T_high)` of that arm's pinned
     `arms/<X>/ARM.json` (§2.2 [D-14], §4.1) — and **that arm's**
     `arms/<X>/FAMILY.json`. There is no default threshold pair anywhere in this
     file: a caller that does not say which arm it is scoring gets a TypeError
     from the mirror, not arm A's numbers.
  2. **Three new refusal codes** (§3.3): `arm-mismatch`, `schedule-mismatch`,
     `session-reused`, each evaluated at the position §3.3's table gives it.
     Every other code, and every registration behind it, is 011 §3.3's.
  3. **C5's population rules 1-7**, in code: terminal outcomes, the ledger↔slot
     bijection, the ledger as an exact prefix of §2.8's registered call order,
     contiguous per-arm slot indices derived from that prefix, shortfall-prefix
     equality, the hash chain and the per-slot manifests of §2.9, and the
     complete-150 rule.
  4. **The §5 verdicts are computed here**, from the integers this file just
     wrote, by the registered rules: §5.1's level verdicts on three endpoints,
     §5.2's contrast, placement-contrast and COLLAPSE-DISJOINT verdicts, and
     §5.3's ordered decision table. The tables are module constants that mirror
     the preregistration's own tables member for member, because a harness test
     parses them out of `PREREGISTRATION.md` and diffs them against these. No
     operator input, no flag that changes a cut.
  5. **The denominators are §2.8 [D-13]'s.** The primary is intent-to-treat
     over the arm's scheduled N (= 30) with the `[k/N, (k+I)/N]` sensitivity
     bound beside it; `k/V_X` survives as the per-protocol secondary S11 with
     the `V_X` < 11 floor; N, `I_X` and `V_X` are published beside every arm's
     rates; and valid counts differing by more than 2 across arms raise a
     stated caution on the per-protocol secondary. Every rate block names which
     denominator it is over (§4.7).
  6. **§4.3's interval procedure is 011's, ported verbatim** — the same
     `Fraction` tails, the same exactly-200 bisection, the same `alpha`. §4.3
     registers it as a verbatim port and registers test vectors at n = 30,
     n = 25 and n = 50; those vectors are carried here as data so a harness
     test can diff them against the preregistration's tables.
  7. **The §4.5 census is a registered secondary**, computed by
     `harness/census.py` per arm and rendered into `CENSUS.md` by this file,
     which §4.7 makes the scorer's output alongside `RESULTS.json` and
     `RATES.md`. (`ANALYSIS.md` is written by hand from those three and is not
     this file's output.)
  8. **S10, old-edge cross-scoring** (§4.6 [D-12]): every arm's records are
     *also* keyed to **arm A's** family predicates, with labels still taken
     from that arm's own mirror, and the §5.1 level rule is applied to the
     result. Class membership only.
  9. **The surface is [D-23]'s**: `score_rates.py score [--emit-records DIR]`.
     `--slots` **does not exist**, on this command or any other; the canonical
     `arms/` root is `harness/../arms`, resolved from this module's own
     location. An earlier draft's `--slots` let the population be pointed at a
     copy with a slot removed, a duplicated arm or a renamed tree, and every
     per-slot check would still have passed.
 10. **011's §5 machinery that this study does not register is gone**: its
     LIGHT/STANDARD/FULL cuts survive only as the S9 secondary (§4.6), its
     row-level tier composition rule and its LIGHT operating-characteristic
     table are not registered here and are not computed. What replaces them is
     §5.1's HIGH/LOW/MID cuts and §5.4's operating characteristics.
 11. **§4.6's S5 cut, and the comprehension-collapse reading** (round 3,
     finding 9): the load-bearing table §4.6 registers is `READING_TABLE` here,
     and `reading_verdict()` computes which of its three rows arm E's integers
     fall on. A placement collapse whose labels are NOT at the ceiling is a
     *comprehension* collapse — "at least one accepted record was mislabelled"
     — and §4.6 registers that it does not confirm R1, so it does not reach
     §5.3's row 5. **What the ceiling establishes is a fact about labels and
     not about the author** (round 9, finding 2): `policy_mirror.verdict()`
     returns at the sanctions clause and then at the embargo clause before it
     reads `riskScore`, so such a record is labelled correctly at every
     threshold pair and `|Q| = 0` is not comprehension evidence. The `reading`
     cells below say what the integers show and nothing more, and §5.3's row 5
     carries a fifth conjunct — class 3, the interior review band, must not
     collapse in arm E — which excludes the degenerate arm and, §4.6 registers,
     establishes no comprehension either.
 12. **Arm D's three registered outcomes** (round 3, finding 10): §5.3 (ii)
     registers `OLD-EDGE-PREFERENCE` and a general degradation beside the
     predicted tracking, and `arm_d_outcome()` computes them from D's own-keyed
     levels and its S10 old-keyed levels, with both registered explanations of
     the first published beside it and neither asserted.
 13. **§5.4's operating characteristics for the rules §5.3 actually registers**
     (round 3, finding 11): `decision_operating_characteristics()` computes,
     with this file's own interval and threshold code, both the MARGINAL
     pattern probabilities and the JOINT probability of reaching a decision-table
     row — which requires the class-4 gate and the B/C control gate as well as
     the pattern. A harness test pins both, because §5.4 labelled the marginal
     as the power to reach row 4 and they are not the same number. Row 5's joint
     is named COVERAGE-SIDE wherever it is named at all (round 6, finding 4):
     §5.4's model has no label-error term, so the figure is exact for the
     coverage pattern and an upper bound for CONFIRMED.
 14. **`authoring-empty` is §3.3's row and nothing wider** (round 3,
     finding 13): the published `authoringEmpty` count is the partition's own
     outcome — no code, no parseable array — and the wider "produced nothing
     that reached a class" quantity is published beside it as `coveredNothing`,
     so neither is read as the other.
 15. **S3's denominators agree** (round 3, finding 14): the coverage-breadth
     distribution, its mean and the all-six rate are all over the arm's
     registered N, with the slots the schedule holds and the batch never
     executed published as `absent` in the 0 bucket, so an incomplete batch's
     descriptive surface says what its denominator is (§2.8's stopping rule).
 16. **C6's credential evidence is two booleans** (round 3, finding 18):
     `check_environment()` type-checks `credentialCopied` and
     `credentialRemoved` rather than coercing them, because `bool("false")` is
     True and a string there would read a live credential as a removed one.
 17. **Arm D's first outcome is §5.3 (ii)'s registered condition, and not a
     stricter one** (round 4, finding 6): COVERAGE-FOLLOWS-THE-NUMBERS is
     new-keyed HIGH on at least `D_NARROW_MINIMUM` of the four narrow numeric
     classes AND the old-keyed (S10) levels not HIGH-patterned. The earlier code
     required all six D-vs-A contrasts to read TRACKING and never checked the
     old-keyed exclusion at all, so it withheld the outcome from a D the
     registration awards it to and published it for a D that reproduced BOTH
     threshold pairs — the one shape the exclusion exists to catch.
 18. **`coveredNothing` is computed from the covered-class set** (round 4,
     finding 9): the published surface defines it as a valid run that reached no
     class, so the member is `coveredClasses == []` and nothing else. The earlier
     `empty or not accepted or not high` asked whether the run held any correctly
     labelled record, which called a run whose one correctly labelled record
     satisfies no class predicate a covering run.
 19. **Malformed identity evidence refuses its own slot and no other** (round 5,
     finding 6): `session_reuse()` runs over the whole population BEFORE any
     slot's admission, and it used to put arbitrary `CALL.json` member values in
     a dict key. A slot recording `startedAt: []` raised
     `TypeError: unhashable type: 'list'` out of that pass — outside §7's
     per-slot catch, so one malformed slot ended the scoring of all 150.
     `call_identity_defect()` checks the three identity members instead of
     hashing them, `slot_identity()` drops only the member it cannot read (the
     session bytes and session id of a slot with a malformed `CALL.json` still
     hold every other slot to cross-slot uniqueness), and `admit()` refuses that
     slot `call-unreadable`.
 20. **`completion-unreadable` is reachable, as §3.3 registers it** (round 5,
     finding 7): the transcript binding reads `completion.txt` to bind it to the
     transcript's last assistant message, and its decode used to raise a bare
     `UnicodeDecodeError` — a `ValueError`, indistinguishable from the ported
     gate's own refusals, so a completion that is not UTF-8 scored
     `transcript-refused` and the registered code named no run.
     `transcript_check.CompletionUndecodable` separates the decode from the
     binding and `admit()` catches it first.
 21. **S5's ceiling is decided on the integer `|Q|`** (round 5, finding 13):
     §4.6 registers the cut as `|Q| = 0`, and `label_branch()` compared the
     float accuracy against 1.0 — `H/(H+1)` rounds to 1.0 for large H, so an arm
     with a mislabelled record read as at the ceiling. The float is still
     published; nothing decides on it.
 22. **The three identity members are PRESENT strings** (round 6, finding 5):
     `call_identity_defect()` read them with `call.get()`, which exempts an
     absent member and a JSON `null` alike — and nothing downstream owns
     `startedAt`, so a slot with no start clock scored valid. §3.3 registers the
     three as the evidence a copied slot cannot agree with itself over, and an
     absent member agrees with every other absent one.
 23. **`compile-refused` has its registered life** (round 6, finding 7): §3.3
     registers it as "the compiler failed other than by finding no array" and it
     could never fire, because the ported `extract_array()` swallows every
     decoder `ValueError` per candidate — so an array with duplicate object keys
     or a `NaN` reached the scorer wearing the no-array refusal and was scored
     `authoring-empty`, VALID. `strict_decode_refusal()` asks the bytes which of
     the two it was, at the port's own strictness boundary.
 24. **Ledger records are type-checked at the read** (round 6, finding 8):
     `load_ledger()` checked only that `records` was a list, so `{"records":
     [null]}` reached `schedule_key()` and left the scoring as a bare
     `AttributeError` — a traceback where C5 registers a refusal.

The partition that decides every denominator (§3.3):

  pipeline-invalid  the apparatus or the transport failed. Under §4.2's
                    intent-to-treat endpoint the slot **stays in the primary
                    denominator and counts as covering nothing** — the gates are
                    arm-independent, the probability of tripping them is not,
                    and conditioning the primary on surviving them is
                    post-treatment selection that flatters the arm whose text
                    most disrupts authoring. It leaves `V_X` only, which is the
                    per-protocol secondary's denominator
  authoring-empty   admissible evidence and NO PARSEABLE ARRAY — §3.3's own
                    row, and exactly that row (round 3, finding 13): VALID,
                    counted, coverage zero in every class. The wider quantity —
                    a valid run whose covered-class set is EMPTY, for any
                    reason: no array, every element dropped, no record this
                    arm's mirror labelled correctly, or a correctly labelled
                    record that satisfies no class predicate — is a real and
                    reportable outcome, so it is published beside it as
                    `coveredNothing` rather than folded into the partition's
                    name (round 4, finding 9)

Pipeline-invalid codes, in the order admission evaluates them (the same set
CODE_PARTITION carries, which §3.3 enumerates member for member and the harness
admission test diffs against both this source and that table):

  slot-symlink           the slot tree holds a symlink — anywhere, under any
                         name, dangling or not (§3.3)
  slot-irregular         the slot tree holds an entry that is neither a regular
                         file nor a directory nor a symlink — a FIFO, a socket,
                         a device, a door. Decided by lstat BEFORE anything is
                         opened, because opening a FIFO blocks
  slot-shape             a required slot file is missing or not a regular file
  call-unreadable        CALL.json is not duplicate-free JSON, is not a JSON
                         object, or does not record all three identity members
                         (startedAt, cwd, home) as strings — absent and `null`
                         included (round 5 finding 6; round 6 finding 5)
  model-mismatch         CALL.json names a model other than the pinned one
  binary-mismatch        CALL.json names a binary digest other than the pinned one
  cli-mismatch           CALL.json names a CLI version other than the pinned one
  registry-mismatch      the run was made under a registry that is not the
                         committed harness/PINS.json (§2.10)
  golden-mismatch        the run was made against a golden capture that is not
                         the one this scoring is using (§3.2)
  arm-mismatch           the slot's recorded arm or arm-prompt digest is not the
                         arm whose tree it sits in, or its transcript carries
                         another arm's prompt bytes (§3.3, §3.1 gate 2)
  schedule-mismatch      the slot's recorded (globalIndex, round, position, arm)
                         is not what §2.8's registered call order assigns to that
                         global index, or the ledger's record for this slot names
                         something else (§3.3)
  session-reused         the slot's session bytes, session id, or the identifying
                         members of its CALL.json are shared with another slot in
                         any arm; the LATER slot in schedule order takes the code
  isolation-unproven     CALL.json does not record the per-run isolation (C6)
  session-count          the run produced other than exactly one new session
  call-nonzero-exit      the process did not exit with integer status 0
  no-session             session.jsonl was not retained
  no-completion          completion.txt was not retained (exit-0 only)
  no-context             context.json was not retained
  transcript-refused     the ported transcript binding refused (detail retained)
  context-mismatch       the retained context.json is not what the session yields
  completion-unreadable  completion.txt is not decodable UTF-8
  compile-refused        the compiler failed other than by finding no array
  regeneration-mismatch  the compiler does not regenerate its own output bytes
  refusal-conflict       the batch refused this slot but the bytes now admit it
  scorer-error           admission raised: the run is recorded invalid with the
                         error, because a scorer that dies mid-tree scores
                         nothing (§7 totality)

**One class of failure is deliberately not a code, because a code would
understate it** (§2.9, §3.3, C5 rule 6). A slot whose recomputed
`SLOT-MANIFEST.json` disagrees with the ledger, or a ledger whose hash chain
does not verify, does not mark that slot invalid: it makes **every** level
verdict `UNRESOLVED-BY-DESIGN`, reports no contrast, and publishes the
discrepancy with the slot named. A code that moved one slot out of `V_X` would
hand an alteration precisely the denominator change that produces the verdict it
was made to produce.

**The stopping rule is [D-21]'s and this file writes it itself.** Any incomplete
batch — at any round, for any reason — and any arm short of its 30 scheduled
slots yields `UNRESOLVED-BY-DESIGN` on every level verdict, no contrast verdict,
no COLLAPSE-DISJOINT, no §5.3 pattern verdict and no decision-table adjudication
beyond row 1. What is published is the descriptive surface — slots, rates,
intervals and census — with "R of 30 rounds completed" in the headline. "The
rule could not have fired" is a published fact here, not a reader's inference
from a table of INDETERMINATEs.

Before it reads a slot it verifies, and refuses on: the three-level ported-byte
chain and the running interpreter (`harness/integrity.py`, §6 C1); the single
registered mirror module against its pin (§2.2 [D-14]); every arm's `ARM.json`,
`PROMPT.txt`, `FAMILY.json` and `POLICY.md` against the digests the registry
records (§2.10); §2.8's registered call order against the registry's copy of it;
the golden capture against the digest `harness/PINS.json` registers for it
(§3.2); and the preregistration's own digest, which must be registered and must
match — a null there is a refusal, not a skip (§2.10). Then, per slot, it
requires the run to name the registry, the golden capture, the arm and the
schedule position it was made under.

What this file deliberately does NOT do: run the evaluator (jpack never executes
in this study — the mirror is the reference semantics), apply a FAMILY patch or
build a pack D, fit or tune any §5 cut, consult a clock, or use randomness.
Per-slot wall clock is retained in each CALL.json; §4.6 S8 registers it as a
secondary, so what is published here is each slot's DURATION derived from the
retained start and end stamps — never a timestamp, so two scorings of one slot
tree stay byte-identical.

**The registered scoring interface is `score_registered()`, and it is the only
thing in this harness that publishes** (§7, [D-23]). It takes an optional
record-emission directory and NOTHING ELSE: the registry, the arms root, every
arm's artifacts and the golden capture are all derived from this module's own
location, so there is no flag, default, argument or environment variable through
which an alternate registry could redefine N, the class definitions, the
thresholds an arm is labelled at, or which slots are the population — this
module reads no environment at all. It computes the results and hands them
straight to the module-private `_write_outputs()`, which writes `RESULTS.json`,
`RATES.md` and `CENSUS.md` to the study root and nowhere else.

The `registry_sha256` override on `score()`, `score_arm()` and `admit()` exists
for library callers whose slots were made under a stand-in registry (the
wrapper-driven harness tests). Those callers get a dict and no way to publish
it: `score()` records the override in `cell.registryOverride`, and
`_write_outputs()` refuses any results carrying one AND re-derives every pin
from the study tree — and then re-derives the WHOLE result by scoring the arms
tree again, requiring equality, so no member of a handed-in dict is trusted.
What no check inside a file can refuse is a caller who edits this file or
rebinds its module constants in process; §7 states that ceiling once.

Usage:
  score_rates.py score [--emit-records DIR]

Any other argument refuses. An ignored flag is how a stale command line lies
silently, so an unknown one is a refusal rather than a no-op.
"""
from __future__ import annotations
import contextlib
import hashlib
import io
import json
import math
import os
import stat
import sys
import tempfile
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)

# The ceremony's commands run with bytecode writing disabled (§2.10,
# round 5 finding 3): set structurally, not left to the operator's
# environment, before any harness module is imported — which means before
# the `import integrity` below, not after it. Round 9, finding 1: this
# command is one of the ceremony's and set the flag nowhere, so the plural
# was a claim about one file.
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


if __name__ == "__main__":
    _refuse_untracked_python_sources()

# Nothing is put on the import path until the tree has been scanned.
sys.path.insert(0, HERE)
import integrity  # noqa: E402


# The mirror is imported LAZILY (round 7, finding 1): the bytecode gate in
# integrity.verify() must run before any grid module loads, and this module
# is imported by batch.py before its preflight can call the gate.
def _policy_mirror():
    import policy_mirror  # noqa: E402
    return policy_mirror
# The census is imported lazily for the SAME reason, and it had to be (round 8,
# finding 1): `census.py` imports the mirror, so an eager `import census` here
# executed the mirror before the gate however deferred this module's own mirror
# import was — the lazy wrapper above closed one path into the grid and left the
# other open. `census.py`'s mirror import is deferred too, and
# `test_batch.py::ImportDiscipline` probes a fresh interpreter for both.
def _census():
    import census  # noqa: E402
    return census
import records_compile  # noqa: E402
import transcript_check  # noqa: E402

SLOT_FILES = ("CALL.json", "stdout.raw", "stderr.raw")
# §2.10: the registry of record is the COMMITTED harness/PINS.json, and the
# scorer computes its digest rather than accepting one. §2.10 [D-23]: the
# canonical arms/ root is `harness/../arms`, resolved from this module's own
# location, and there is no flag that supplies it or any of the paths below.
# `batch.py --pins` still exists, because the harness tests drive the real
# wrapper against a stand-in binary; a slot stamped with any other registry's
# digest is pipeline-invalid.
REGISTRY_OF_RECORD = os.path.join(HERE, "PINS.json")
REGISTERED_ARMS = os.path.join(STUDY, "arms")
REGISTERED_GOLDEN = os.path.join(STUDY, "transcription", "GOLDEN-CONTEXT.json")
# §6 C7's control record, at the canonical path and nowhere else. `batch.py`
# takes a `--out`; the precondition does not consult it, for [D-23]'s reason.
REGISTERED_ISOLATION_NEGATIVE = os.path.join(STUDY, "controls",
                                             "isolation-negative")
REGISTERED_MIRROR = os.path.join(HERE, "policy_mirror.py")
# §6 C7's three registered outcomes, in the registration's own order. They live
# here rather than in `batch.py` because `batch.py` imports this module and not
# the reverse, and the driver that WRITES a verdict, the preflight that reads
# one and the scorer below must take the list from one place — the same reason
# `batch._load_json` borrows this module's duplicate-key rule instead of
# keeping a second one (round 9, finding 3).
C7_OUTCOMES = ("refused", "matched", "no-context")
# The five arms, in the registered order, and the baseline every §5.2 contrast
# is taken against. Arm A is also S10's coordinate system (§4.6).
ARMS = ("A", "B", "C", "D", "E")
BASELINE_ARM = "A"
# Per-arm artifacts, all under the canonical arms/ root.
ARM_FILES = {"arm": "ARM.json", "family": "FAMILY.json",
             "policy": "POLICY.md", "prompt": "PROMPT.txt"}
# §2.7: the wrapper writes into arms/<ARM>/authoring/run-NNN/.
AUTHORING = "authoring"
# §2.8/§2.9: the append-only chained ledger and the shortfall declaration sit at
# the arms root, because both are statements about the WHOLE batch across the
# five arms rather than about one arm's tree. 011 kept both beside its single
# slot tree; there is no single slot tree here.
LEDGER_FILE = "BATCH.json"
SHORTFALL_FILE = "SHORTFALL.json"
# The four members every ledger record must carry to be comparable with §2.8's
# registered order at all — `schedule_key()`'s tuple — and the type §2.9 gives
# each. Checked at the READ (round 6, finding 8), so a malformed record refuses
# the whole scoring through C5's registered path instead of reaching a `.get`
# call that raises. Booleans are refused wherever an integer is registered,
# because `isinstance(True, int)` is True in Python and `round: true` is not a
# round.
LEDGER_RECORD_MEMBERS = (("globalIndex", int, "an integer"),
                         ("round", int, "an integer"),
                         ("position", int, "an integer"),
                         ("arm", str, "a string"))
# §2.9: every slot is sealed by a terminal manifest, and the manifest cannot
# cover itself.
MANIFEST_FILE = "SLOT-MANIFEST.json"
# §2.9 as amended (round 7, finding 3): the seal covers EVERY entry in the slot
# tree, so that an entry ADDED after it breaks it. A regular file is
# `[path, byte length, sha256]`; every other entry is
# `[path, NON_FILE_LENGTH, "type:<marker>"]`, by path and type alone, because it
# is not a byte range to hash. The two row shapes cannot collide: no file has a
# negative length and no sha256 hex string begins with `type:`. `batch.py` writes
# the same two shapes and the same markers — the driver seals and the scorer
# recomputes, and neither reads the other's list to find out what to write.
NON_FILE_LENGTH = -1
# Round 8, finding 4: the slot ROOT is an entry of its own list, at the one
# relative path no entry beneath it can take — `os.path.relpath(child, slot)`
# is never `.`. `batch.py`'s `SLOT_ROOT_ENTRY` is the same string.
SLOT_ROOT_ENTRY = "."
MANIFEST_TYPE_MARKERS = (
    (stat.S_ISLNK, "symlink"),
    (stat.S_ISDIR, "directory"),
    (stat.S_ISFIFO, "fifo"),
    (stat.S_ISSOCK, "socket"),
    (stat.S_ISCHR, "char-device"),
    (stat.S_ISBLK, "block-device"),
    (stat.S_ISDOOR if hasattr(stat, "S_ISDOOR") else (lambda mode: False), "door"),
)
# The member every scoring carries: null when the registry digest was computed
# from REGISTRY_OF_RECORD (the registered path), and the supplied digest when a
# library caller overrode it. The module-private _write_outputs() refuses to
# publish a table whose cell does not carry this member, or carries it non-null.
REGISTRY_OVERRIDE = "registryOverride"
# §2.2 / C6: the environment the wrapper constructs rather than inherits. The
# child PATH is exactly these six system directories plus one per-run directory
# holding a single symlink to the pinned binary.
SYSTEM_PATH = ("/usr/local/sbin", "/usr/local/bin", "/usr/sbin", "/usr/bin",
               "/sbin", "/bin")
ENVIRONMENT_NAMES = ["PATH", "HOME", "TMPDIR", "CODEX_HOME"]
CLOSED_STDIN = "closed (/dev/null)"
ALPHA = Fraction(1, 40)          # one tail of a two-sided 95% interval
BISECTIONS = 200                 # fixed; no early exit, no tolerance

# --- §5.1's cuts, and §5.2's and §5.3's tables (registered before the data) ---
#
# Every table below mirrors PREREGISTRATION.md §5 row for row, in the
# preregistration's own order and with the preregistration's own condition
# text, because a harness test parses those tables out of that file and diffs
# them against these. A cut is a number here and a number there, and neither
# may move without the other.

HIGH_CUT = 0.70                  # §5.1: L_{i,X} >= 0.70 is HIGH
LOW_CUT = 0.30                   # §5.1: U_{i,X} <= 0.30 is LOW
UNRESOLVED = "UNRESOLVED-BY-DESIGN"
LEVEL_TABLE = (
    ("L_{i,X} >= 0.70", "HIGH"),
    ("otherwise, U_{i,X} <= 0.30", "LOW"),
    ("otherwise", "MID"),
)
# §5.1 registers THREE endpoints the level rule applies to unchanged, and every
# level verdict names which one it is a verdict on. §4.6 S10 adds a fourth —
# "level verdicts under S10 old-edge cross-scoring, up to 5 x 6 = 30" is one of
# §4's counted verdict families — under the same rule, so it is named here
# rather than left as an unlabelled column.
LEVEL_ENDPOINTS = ("primary", "placement", "perProtocol", "oldEdge")
# §5.1: below V_X = 11 a perfect arm cannot read HIGH (L = 0.6915 at V = 10,
# 0.7151 at V = 11), so the per-protocol verdicts are UNRESOLVED-BY-DESIGN
# rather than a table of MIDs a reader might mistake for a measurement. The
# primary and S1 have NO denominator floor: ITT fixes their denominator at N.
PER_PROTOCOL_FLOOR = 11
CONTRAST_TABLE = (
    ("level(A) = HIGH and level(X) = LOW", "COLLAPSE"),
    ("level(A) = HIGH and level(X) = HIGH", "TRACKING"),
    ("otherwise", "INDETERMINATE"),
)
PLACEMENT_CONTRAST_TABLE = (
    ("level(A, S1) = HIGH and level(X, S1) = LOW", "PLACEMENT-COLLAPSE"),
    ("level(A, S1) = HIGH and level(X, S1) = HIGH", "PLACEMENT-TRACKING"),
    ("otherwise", "PLACEMENT-INDETERMINATE"),
)
# §5.2 [D-17]: reported BESIDE the level-gated verdict, never in place of it.
# It gates nothing and falsifies nothing.
SECOND_CONTRAST_TABLE = (
    ("U_X < L_A", "COLLAPSE-DISJOINT"),
    ("otherwise", None),
)
# §5.3: the four narrow numeric classes the E prediction is stated over, and the
# embargo-membership class whose collapse overrides every other reading of E.
NARROW_NUMERIC_CLASSES = (0, 1, 2, 5)
EMBARGO_CLASS = 4
# §5.3 row 5's fifth conjunct (round 9, finding 2): class 3 is the interior
# review band `¬S ∧ ¬E ∧ T_low <= risk < T_high`, and it is the one class whose
# members are scored BETWEEN the two thresholds — so covering it means placing
# records the two numbers bracket, and a record decided at the sanctions or
# embargo clause never reaches the comparison. Requiring that arm E not COLLAPSE
# here excludes an arm E whose accepted records carry no threshold information
# at all; §4.6 registers that it excludes a degenerate case and establishes no
# comprehension.
INTERIOR_CLASS = 3
# §5.3: "three or more of the four", and the control gate's "five of six".
PATTERN_MINIMUM = 3
CONTROL_GATE_MINIMUM = 5
CONTROL_ARMS = ("B", "C")
# §5.3's decision table, ordered, exhaustive and total: evaluated top to bottom,
# the first row whose condition holds is the outcome, and the last row always
# holds. The scorer computes the row and writes its number and its name into
# RESULTS.json (§4.7); no operator selects a row.
DECISION_TABLE = (
    {"row": 1,
     "condition": "the batch is incomplete (§2.8), or any arm holds fewer than "
                  "30 scheduled slots, or a slot manifest or the ledger chain "
                  "fails to verify (§2.9)",
     "outcome": "not adjudicated",
     "publishedAs": UNRESOLVED,
     "gloss": "descriptive publication only, no contrast reported"},
    {"row": 2,
     "condition": "arm E reads COLLAPSE on class 4",
     "outcome": "not adjudicated",
     "publishedAs": "E-DEGRADED-GENERALLY",
     "gloss": "the denamed text degraded authoring generally; every other "
              "reading of arm E is withdrawn"},
    {"row": 3,
     "condition": "`gate` is false",
     "outcome": "not adjudicated",
     "publishedAs": "CONTROLS-FAILED",
     "gloss": "arm E's verdicts published in full, with the weaker reading "
              "named: paraphrase-driven if B fell short, order-driven if C"},
    {"row": 4,
     "condition": "`nH >= 3`",
     "outcome": "unsupported",
     "publishedAs": "R1-UNSUPPORTED",
     "gloss": "§8's correction fires"},
    {"row": 5,
     "condition": "`nP >= 3` **and arm E's S5 labels are at the ceiling (§4.6) "
                  "and arm E does not read COLLAPSE on class 3**",
     "outcome": "confirmed for this instance",
     "publishedAs": "CONFIRMED",
     "gloss": ""},
    {"row": 6,
     "condition": "`nC >= 3` and `nP < 3`",
     "outcome": "not adjudicated",
     "publishedAs": "LABEL-COLLAPSE-ONLY",
     "gloss": "the records are still at the boundary; the labels are not"},
    {"row": 7,
     "condition": "(else)",
     "outcome": "neither confirmed nor unsupported",
     "publishedAs": "INDETERMINATE",
     "gloss": ""},
)
# --- §4.6's load-bearing table: S1 and S5 separate three readings of a collapse
#
# Round 3 finding 9: §4.6 registers that S5 is what separates a placement
# collapse whose accepted records are all correctly labelled from one whose
# labels failed, and that the second — a COMPREHENSION collapse — does not
# confirm R1. The scorer computed nP, nC and nH and confirmed from nP alone, so
# the registered distinction was unreachable. It is data and code here, and
# `test_verdict_parity.py` diffs the table below against §4.6's own.
#
# Round 9 finding 2: the readings are named for the explanations they make
# available, not for propositions this rule establishes, and the `reading` cells
# say only what the integers show. `|Q| = 0` says no accepted record was
# mislabelled; it does not say the author derived either threshold, because
# `policy_mirror.verdict()` returns at the sanctions clause and then at the
# embargo clause before it reads `riskScore`. §4.6 registers what the ceiling
# establishes and what it does not, and this table no longer asserts a mental
# state a set of correct labels cannot pin down.
#
# The cut is the word the file uses: **the ceiling** of a proportion is 1, so
# arm E's pooled S5 accuracy `|H| / (|H| + |Q|)` is at the ceiling exactly when
# no accepted record was mislabelled. No other number is registered anywhere in
# the file for this quantity, and the two candidates were both refused: S9's
# `mislabel share >= 0.20` escalation, which §4.6 says is not this study's
# decision rule and which no contrast may read, and a cut chosen here, which
# would be a §5 threshold this file invented after the design. The literal
# reading also makes §4.6's third row exact rather than approximate: a class
# reached raw but not in H holds a mislabelled record, so "degraded, so
# H-coverage falls" and `|Q| > 0` are the same event.
S5_CEILING = 1.0
S5_BRANCHES = ("at the ceiling", "degraded")
# The three readings, in §4.6's own order and words. `branch` is the S5 cut the
# row is keyed on; `placementLevel` is the S1 level the row is keyed on.
READING_TABLE = (
    {"placementLevel": "LOW",
     "placementGloss": "the records are not at the boundary",
     "labels": "at the ceiling",
     "branch": S5_BRANCHES[0],
     "reading": "no accepted record was mislabelled, and none was placed at "
                "the boundary",
     "publishedAs": "PLACEMENT collapse",
     "gloss": "this is what R1 predicts, and the only thing that confirms it"},
    {"placementLevel": "LOW",
     "placementGloss": "",
     "labels": "degraded",
     "branch": S5_BRANCHES[1],
     "reading": "at least one accepted record was mislabelled",
     "publishedAs": "comprehension collapse",
     "gloss": "published as one, R1 not confirmed"},
    {"placementLevel": "HIGH or MID",
     "placementGloss": "the records are at the boundary",
     "labels": "degraded, so H-coverage falls",
     "branch": S5_BRANCHES[1],
     "reading": "the author placed records at the boundary and labelled them "
                "wrong",
     "publishedAs": "label collapse",
     "gloss": "the hugging did not go away; R1 is not confirmed and saying "
              "otherwise would be reading a labelling failure as an anchoring "
              "result"},
)

# --- §5.3 (ii)'s three registered outcomes for arm D ------------------------
#
# Round 3 finding 10: "Three outcomes are registered for arm D, not two", and
# the scorer aggregated outcomes for arm E alone. They are computed here from
# D's own-keyed level verdicts (the primary ITT rate under D's own family) and
# its old-keyed ones (S10, the same records under ARM A's family predicates,
# labels still D's own).
#
# Two counts the file does not spell, and where each comes from. §5.3 (ii)
# states its conditions over "the narrow numeric classes" with no count —
# round 2 recorded that gap and the decision table it built to close it covers
# arm E only — so the count used here is §5.3 (i)'s own registered
# `PATTERN_MINIMUM`, three or more of the four, rather than a new number; and
# the mixed case, for which §5.3 (ii) names no outcome, is published as
# D-INDETERMINATE rather than silently as one of the three. The first three rows
# are mutually exclusive — a class reading LOW cannot read HIGH, and no class
# reads HIGH and LOW at once — so the order decides no case; it is stated
# anyway, for the reason §5.3's own table states its order.
#
# Round 4, finding 6: row 1's condition is §5.3 (ii)'s own, quoted — "new-keyed
# HIGH on three or more of the four narrow numeric classes, old-keyed not
# HIGH-patterned" — and BOTH halves are computed. The earlier row 1 asked for
# TRACKING on all six contrasts and asked nothing about the old-keyed levels,
# which is a different rule in both directions: it withheld the outcome from a D
# that satisfies the registration but reads INDETERMINATE on a non-narrow class,
# and it awarded the outcome to a D whose records reach the old edges too, which
# is precisely what "old-keyed not HIGH-patterned" excludes.
D_NARROW_MINIMUM = PATTERN_MINIMUM
D_OUTCOME_TABLE = (
    {"row": 1,
     "condition": "arm D's new-keyed level verdicts are HIGH on %d or more of "
                  "the four narrow numeric classes and its old-keyed (S10) "
                  "verdicts are not HIGH-patterned — HIGH on fewer than %d of "
                  "them" % (D_NARROW_MINIMUM, D_NARROW_MINIMUM),
     "publishedAs": "COVERAGE-FOLLOWS-THE-NUMBERS",
     "gloss": "§5.3 (ii)'s prediction: coverage follows the numbers the policy "
              "names, and D's records moved to D's edges",
     "explanations": ()},
    {"row": 2,
     "condition": "arm D's new-keyed level verdicts are LOW on at least %d of "
                  "the four narrow numeric classes and its old-keyed (S10) "
                  "verdicts are HIGH on at least %d of them"
                  % (D_NARROW_MINIMUM, D_NARROW_MINIMUM),
     "publishedAs": "OLD-EDGE-PREFERENCE",
     "gloss": "the model reproduced 40 and 70 in the face of a text that says "
              "45 and 72",
     "explanations": (
         "contamination — this policy family has been public in this "
         "repository since Study 010 merged (2026-08-06), and a snapshot that "
         "has seen it can reproduce 40 and 70 against a text that says "
         "otherwise",
         "round-number salience — 40 and 70 are decade-round and 45 and 72 are "
         "not, so an author drawn to round values rather than to the stated "
         "literal produces the same table, having seen nothing ([D-18])")},
    {"row": 3,
     "condition": "arm D's new-keyed level verdicts are LOW on at least %d of "
                  "the four narrow numeric classes and its old-keyed (S10) "
                  "verdicts are LOW on at least %d of them"
                  % (D_NARROW_MINIMUM, D_NARROW_MINIMUM),
     "publishedAs": "GENERAL-DEGRADATION",
     "gloss": "the author placed records at neither threshold pair; published "
              "as one, and not read as evidence for or against R1",
     "explanations": ()},
    {"row": 4,
     "condition": "(else)",
     "publishedAs": "D-INDETERMINATE",
     "gloss": "the mixed case §5.3 (ii) names no outcome for: neither the "
              "predicted tracking, nor an old-edge preference, nor a general "
              "degradation",
     "explanations": ()},
)
# §5.3 (ii): nothing in this study separates the two explanations of an
# old-edge preference, and the earlier name ("contamination signal") asserted
# the first. The scorer publishes both and asserts neither.
D_OLD_EDGE_NOTE = (
    "Nothing in this study separates the two explanations. What would separate "
    "them is an arm at a non-round pair with the same roundness profile as "
    "(45, 72) but no public history, which is a different study.")

# §4.6 S9: Study 011 §5's review-depth mapping, applied per arm unchanged.
# Reported because it is the product quantity the previous study registered; it
# is NOT this study's decision rule and no contrast reads it.
TIERS = ("LIGHT", "STANDARD", "FULL")
LIGHT_LOWER_BOUND = 0.80
STANDARD_LOWER_BOUND = 0.40
MISLABEL_ESCALATION = 0.20
# §4.4: at rho_X >= 0.10 the arm's contrasts carry a stated caution over the
# whole arm. Not a level change: the loss already lowered the ITT rate, and
# charging it twice would count one event twice.
PIPELINE_CAUTION = 0.10
# §2.8 [D-13]: the arms are not truncated to a common denominator, and if two
# arms' valid counts differ by more than 2 the per-protocol secondary carries a
# stated caution.
VALID_COUNT_DIVERGENCE = 2

# §4.3's registered test vectors, as data, so a harness test can diff them
# against the preregistration's tables rather than against a re-derivation. The
# n = 30 row is this study's own denominator with the two §5.1 cut locations
# marked; n = 25 is [D-1]'s live alternative; n = 50 is Study 011's own
# denominator, retained as a port control against numbers a predecessor already
# published.
REGISTERED_VECTORS = {
    30: {0: (0.0000, 0.1157), 1: (0.0008, 0.1722), 2: (0.0082, 0.2207),
         3: (0.0211, 0.2653), 4: (0.0376, 0.3072), 15: (0.3130, 0.6870),
         26: (0.6928, 0.9624), 27: (0.7347, 0.9789), 28: (0.7793, 0.9918),
         29: (0.8278, 0.9992), 30: (0.8843, 1.0000)},
    25: {0: (0.0000, 0.1372), 1: (0.0010, 0.2035), 2: (0.0098, 0.2603),
         3: (0.0255, 0.3122), 12: (0.2780, 0.6869), 22: (0.6878, 0.9745),
         23: (0.7397, 0.9902), 24: (0.7965, 0.9990), 25: (0.8628, 1.0000)},
    50: {0: (0.0000, 0.0711), 1: (0.0005, 0.1065), 25: (0.3553, 0.6447),
         40: (0.6628, 0.8997), 45: (0.7819, 0.9667), 50: (0.9289, 1.0000)},
}

# --- §2.8's registered call order -------------------------------------------
#
# The two facts §2.8 states about its own table, rather than a transcription of
# it: W1…W5 are the cyclic rows of the Williams first row for five treatments,
# W6…W10 are those five reversed, and the batch is three blocks of the ten in
# their own registered orders. Encoded as the same two facts `batch.py` encodes,
# so the driver and the scorer cannot hold two different schedules — and the
# registry carries the same two facts, which this file requires to agree, so
# neither the code nor the registry can move the schedule alone. A transcribed
# table would be ten more chances to mistype a letter with no way to notice;
# the derivation either reproduces §2.8's published transition matrix or it does
# not, and a harness test checks it against that matrix rather than against this
# code.
WILLIAMS_FIRST_ROW = ("A", "B", "E", "C", "D")
BLOCKS = (
    ("W2", "W4", "W7", "W10", "W1", "W9", "W8", "W6", "W3", "W5"),
    ("W4", "W3", "W2", "W10", "W9", "W8", "W5", "W1", "W7", "W6"),
    ("W4", "W6", "W5", "W7", "W1", "W2", "W10", "W8", "W9", "W3"),
)

# §3.3's partition, member for member. Every code admit() and score_run() can
# name is here; the harness admission test diffs this table against the codes
# the two functions can actually return AND against the enumeration §3.3
# registers, so prose and code cannot drift apart.
CODE_PARTITION = {
    "slot-symlink": "pipeline-invalid",
    "slot-irregular": "pipeline-invalid",
    "slot-shape": "pipeline-invalid",
    "call-unreadable": "pipeline-invalid",
    "model-mismatch": "pipeline-invalid",
    "binary-mismatch": "pipeline-invalid",
    "cli-mismatch": "pipeline-invalid",
    "registry-mismatch": "pipeline-invalid",
    "golden-mismatch": "pipeline-invalid",
    "arm-mismatch": "pipeline-invalid",
    "schedule-mismatch": "pipeline-invalid",
    "session-reused": "pipeline-invalid",
    "isolation-unproven": "pipeline-invalid",
    "session-count": "pipeline-invalid",
    "call-nonzero-exit": "pipeline-invalid",
    "no-session": "pipeline-invalid",
    "no-completion": "pipeline-invalid",
    "no-context": "pipeline-invalid",
    "transcript-refused": "pipeline-invalid",
    "context-mismatch": "pipeline-invalid",
    "completion-unreadable": "pipeline-invalid",
    "compile-refused": "pipeline-invalid",
    "regeneration-mismatch": "pipeline-invalid",
    "refusal-conflict": "pipeline-invalid",
    "scorer-error": "pipeline-invalid",
}
# The two outcomes that carry no code and stay valid (§3.3). Under §4.2 the
# pipeline-invalid runs stay in the PRIMARY denominator too; "valid" here is
# the per-protocol population and the population the census reads.
VALID_OUTCOMES = ("valid", "authoring-empty")
# §3.3 / §3.2: the raw retained evidence of WHICH call produced a slot. Raw,
# deliberately: the session file's bytes, the session id, and the call record's
# own start clock, working directory and isolated home. Not the normalized
# context digests — those are what two independent calls are SUPPOSED to share.
# 011 applied this to its two capture slots; §3.3 applies it to all 150, where a
# copied slot would otherwise add a covered run to a denominator.
SESSION_IDENTITY = (
    ("sessionSha256", "the retained transcript bytes"),
    ("sessionId", "the session id the transcript records"),
    ("callIdentity", "the call record's own start clock, working directory and "
                     "isolated home"),
)
# The three `CALL.json` members `callIdentity` is built from, in the order a
# refusal names them. The wrapper writes all three as STRINGS — a UTC stamp and
# two absolute paths — so any other JSON type there is malformed evidence rather
# than evidence of another shape (round 5, finding 6).
CALL_IDENTITY_MEMBERS = ("startedAt", "cwd", "home")


class ScoreError(Exception):
    """A population-level refusal: the scoring itself cannot be trusted, as
    distinct from a single run being invalid."""


def _refuse_duplicate_keys(pairs):
    keys = [key for key, _ in pairs]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate object keys")
    return dict(pairs)


def load_json(path: str):
    """Duplicate-key-rejecting JSON: a shadowed member cannot mean one thing
    to this scorer and another to a reader."""
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"),
                          object_pairs_hook=_refuse_duplicate_keys)


def file_digest(path: str) -> str:
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


def tree_digest(files: dict) -> str:
    """One digest over a compiled record tree: relative paths in sorted
    order, each length-prefixed, so no rename or split can collide."""
    hasher = hashlib.sha256()
    for relative in sorted(files):
        body = files[relative]
        hasher.update(relative.encode("utf-8"))
        hasher.update(b"\n%d\n" % len(body))
        hasher.update(body)
    return "sha256:" + hasher.hexdigest()


# --- the interval (PREREGISTRATION.md §4.3, normative, ported verbatim) -----

def _tail_ge(k: int, n: int, p: Fraction) -> Fraction:
    """P(X >= k) for X ~ Binomial(n, p), summed in ascending j as exact
    rationals: math.comb is exact, and a double is an exact binary rational,
    so nothing here rounds."""
    q = 1 - p
    total = Fraction(0)
    for j in range(k, n + 1):
        total += math.comb(n, j) * p ** j * q ** (n - j)
    return total


def _tail_le(k: int, n: int, p: Fraction) -> Fraction:
    """P(X <= k) for X ~ Binomial(n, p)."""
    q = 1 - p
    total = Fraction(0)
    for j in range(0, k + 1):
        total += math.comb(n, j) * p ** j * q ** (n - j)
    return total


def _bisect(predicate) -> float:
    """The crossing point of a monotone predicate — true on [0, root), false
    after — found by EXACTLY 200 halvings of [0, 1] in IEEE-754 doubles. A
    fixed iteration count and an exact comparison mean the same inputs give
    the same bits on any platform: no libm, no tolerance, no seed."""
    low, high = 0.0, 1.0
    for _ in range(BISECTIONS):
        middle = (low + high) / 2.0
        if predicate(middle):
            low = middle
        else:
            high = middle
    return low


def clopper_pearson(k: int, n: int) -> tuple:
    """The exact (Clopper-Pearson) 95% interval for k successes in n trials.

    The bounds are the p values that make the observed count exactly as
    extreme as alpha/2 allows: the lower bound solves P(X >= k | p) = alpha
    (increasing in p), the upper solves P(X <= k | p) = alpha (decreasing in
    p), with the degenerate ends pinned at 0 and 1.

    "Exact" is doing more work than it can carry, and §4.3 says so: the
    arithmetic is exact rationals with no libm, and the COVERAGE is exact only
    conditional on the slots of a class being independent Bernoulli trials with
    a constant success probability. §7 records that this design cannot rule out
    provider-side state shared across calls, which would break both halves of
    that model. Every interval in this study is an exact interval for a model
    this design cannot verify.
    """
    if n <= 0:
        raise ValueError("an interval needs at least one trial")
    if not 0 <= k <= n:
        raise ValueError("k=%d is not a count out of n=%d" % (k, n))
    return lower_bound(k, n), upper_bound(k, n)


def lower_bound(k: int, n: int) -> float:
    """The interval's lower bound alone — §5.1's HIGH criterion, so it is worth
    computing without the upper root nobody asked for."""
    return 0.0 if k == 0 else _bisect(lambda p: _tail_ge(k, n, Fraction(p)) < ALPHA)


def upper_bound(k: int, n: int) -> float:
    return 1.0 if k == n else _bisect(lambda p: _tail_le(k, n, Fraction(p)) > ALPHA)


def rate_block(k: int, n: int, denominator: str) -> dict:
    """The reported shape for one proportion: the integers, the point estimate,
    the exact interval, and — new in this study, because §4.7 requires every
    rate to be labelled by which denominator it is over — the name of that
    denominator. Never a rate without its denominator, and never a bound a
    reader cannot recompute from the integers."""
    if n <= 0:
        return {"count": k, "trials": n, "denominator": denominator,
                "rate": None, "ci95": None}
    low, high = clopper_pearson(k, n)
    return {"count": k, "trials": n, "denominator": denominator,
            "rate": k / n, "ci95": [low, high]}


def probability_at_least(k: int, n: int, p: Fraction) -> Fraction:
    """P(X >= k) for X ~ Binomial(n, p), exactly. Same arithmetic as the
    interval: math.comb and Fractions, no libm and no rounding."""
    return _tail_ge(k, n, p)


def high_threshold(n: int) -> int:
    """The smallest k whose exact lower bound reaches §5.1's HIGH cut at n
    trials — 27 at n = 30. The lower bound is increasing in k, so this is a
    bisection over k and not a scan."""
    low, high = 0, n
    while low < high:
        middle = (low + high) // 2
        if lower_bound(middle, n) >= HIGH_CUT:
            high = middle
        else:
            low = middle + 1
    return low


def low_threshold(n: int) -> int:
    """The largest k whose exact upper bound stays at or below §5.1's LOW cut
    at n trials — 3 at n = 30. The upper bound is increasing in k, so this is a
    bisection over k as well; -1 when no k qualifies."""
    low, high = 0, n
    while low < high:
        middle = (low + high + 1) // 2
        if upper_bound(middle, n) <= LOW_CUT:
            low = middle
        else:
            high = middle - 1
    return low if upper_bound(low, n) <= LOW_CUT else -1


def level_operating_characteristics(n: int, p: Fraction) -> dict:
    """§5.4's table, exactly: P(HIGH), P(LOW) and P(MID) that §5.1's rule
    assigns a class whose TRUE coverage is p, at n trials. Registered rather
    than left to a reader's intuition, and asserted by a harness test.

    Every 0.0000 in §5.4's table is a rounded figure and not a zero except in
    the two degenerate rows, where four are exact (at p = 1 no outcome has
    k <= 3; at p = 0 none has k >= 27) — P(HIGH) at p = 0.30 is about 1.1e-11
    — and no rule in §5 reads these numbers (round 9, finding 12)."""
    high_k = high_threshold(n)
    low_k = low_threshold(n)
    p_high = probability_at_least(high_k, n, p)
    p_low = _tail_le(low_k, n, p) if low_k >= 0 else Fraction(0)
    return {"trials": n, "p": str(p),
            "highThresholdK": high_k, "lowThresholdK": low_k,
            "pHigh": float(p_high), "pLow": float(p_low),
            "pMid": float(1 - p_high - p_low)}


# §5.4's registered scenario, as exact rationals: p = 0.95 on every class of
# arms A, B and C and on E's classes 3 and 4; p = 0.05 on arm E's four narrow
# numeric classes when R1 holds, and 0.95 on them when it does not. Independence
# layers 1-3 (across classes within an arm, across arms, across slots).
SCENARIO_P = Fraction(19, 20)
SCENARIO_P_COLLAPSED = Fraction(1, 20)


def _binomial_at_least(k: int, n: int, p: Fraction) -> Fraction:
    """P(X >= k) for X ~ Binomial(n, p), exactly, over a pattern of n class
    indicators rather than over slots. Same arithmetic as `_tail_ge()`; kept
    separate because that one is the interval's and this one is §5.4's."""
    if k <= 0:
        return Fraction(1)
    return sum((Fraction(math.comb(n, j)) * p ** j * (1 - p) ** (n - j)
                for j in range(k, n + 1)), Fraction(0))


def decision_operating_characteristics(n: int) -> dict:
    """§5.4's operating characteristics for the rules §5.3 actually registers,
    computed with this file's own interval and threshold code, exactly, with no
    simulation and no rounding until the last float.

    Round 3 finding 11, dispositioned: §5.4 labelled `P(nH >= 3)` "the power to
    reach decision row 4", and those are different numbers. Row 4 is reached
    only when the batch is complete and sealed (row 1 does not fire), arm E does
    not read COLLAPSE on class 4 (row 2), the B/C control gate passes (row 3),
    AND `nH >= 3`. So both are computed here and both are published:

      MARGINAL   `nH >= 3` alone, and `nP >= 3` alone
      JOINT      row 4: the probability of reaching that row, which reads
                 coverage alone;
                 row 5: the COVERAGE-SIDE quantity, and an upper bound for
                 CONFIRMED — not the probability of reaching the row

    Round 6, finding 4: this note used to call BOTH joints "the probability of
    actually reaching the row", which contradicts the name the same figures are
    published under three lines below and the name §5.4 gives its own row.
    §5.4's model carries no label-error term, so row 5's S5 conjunct — arm E's
    labels at the ceiling — is outside it; `row5` is exact for the coverage
    pattern and an upper bound for the confirmatory outcome, which is the whole
    of what "coverage-side" names. Row 4 reads coverage alone and is unaffected.

    The joint figures are computed over ARM A's six-class HIGH pattern rather
    than as a product of marginals, because the gate and the collapse both
    condition on the same arm-A HIGH verdicts — §5.4's own construction for its
    coverage-side CONFIRMED-and-gate row, reused here for row 4, and it
    reproduces that row's registered 0.0364/0.3536/0.7359 as a control on the
    model.

    Under the registered scenario, with `q = P(HIGH | p = 0.95)` and
    `l = P(LOW | p = 0.05)` at n trials:

      TRACKING on class i, control arm X   arm A HIGH and X HIGH -> q^2
      the gate                             sum over the classes A reads HIGH:
                                           P(|S| = a) * P(Bin(a, q) >= 5)^2,
                                           which is 0 below a = 5
      PLACEMENT-COLLAPSE on class i        arm A HIGH and E LOW  -> q * l
      `nH >= 3`                            E alone: Bin(4, q) >= 3
      class 4 does not collapse            1 - P(A HIGH) * P(E class 4 LOW),
                                           and E's class 4 sits at p = 0.95 in
                                           both scenarios, so this term is
                                           within 1e-23 of 1 at every N
      class 3 does not collapse            row 5 only (round 9, finding 2): the
                                           same shape and the same magnitude,
                                           E's class 3 also sitting at p = 0.95
                                           under §5.4's scenario, so no printed
                                           figure moves

    Row 5's joint reads ONE arm-A pattern for a primary rule and an S1 rule at
    once (round 9, finding 9): `nP`, the class-4 term and now the class-3 term
    all condition on the same arm-A HIGH verdicts, and `H ⊆ raw` makes the two
    endpoints dependent — §5.4's fourth independence layer is exactly that
    assumption, and its paragraph states what the figure assumes.

    Every figure assumes the independence layers §5.4 names and is not a bound;
    §5.4's Fréchet column is what the marginals alone imply.
    """
    q = probability_at_least(high_threshold(n), n, SCENARIO_P)
    low_k = low_threshold(n)
    # P(LOW | p = 0.05): the collapsed class reads LOW. Symmetric to q under
    # these cuts, and computed rather than assumed to be.
    collapsed_low = (_tail_le(low_k, n, SCENARIO_P_COLLAPSED) if low_k >= 0
                     else Fraction(0))
    # P(LOW | p = 0.95): arm E's class 4 collapsing when it truly sits at 0.95.
    intact_low = (_tail_le(low_k, n, SCENARIO_P) if low_k >= 0 else Fraction(0))
    narrow = len(NARROW_NUMERIC_CLASSES)
    classes = narrow + 2                      # the six classes of §3.1's family
    marginal_h = _binomial_at_least(PATTERN_MINIMUM, narrow, q)
    marginal_p = _binomial_at_least(PATTERN_MINIMUM, narrow, q * collapsed_low)
    # Arm A's HIGH pattern, by shape. The gate needs TRACKING on five of six in
    # both control arms, and a class arm A does not read HIGH can never be
    # TRACKING, so only patterns of five or six matter; among the five-class
    # patterns what matters is whether the missing class is one of the four
    # narrow numeric ones (which removes it from `nP`'s reach), whether it is
    # class 4 (which removes row 2's precondition) and whether it is class 3
    # (which removes row 5's fifth conjunct: with A not HIGH there, no contrast
    # verdict exists and COLLAPSE is unavailable).
    shapes = ((classes, narrow, True, True, 1),          # A HIGH on all six
              (classes - 1, narrow - 1, True, True, narrow),  # missing a narrow
              (classes - 1, narrow, True, False, 1),     # missing class 3
              (classes - 1, narrow, False, True, 1))     # missing class 4
    gate = row_four = row_five = Fraction(0)
    for size, narrow_in, embargo_in, interior_in, ways in shapes:
        weight = ways * q ** size * (1 - q) ** (classes - size)
        # Both control arms, independently, over the classes A reads HIGH.
        passes = _binomial_at_least(CONTROL_GATE_MINIMUM, size, q) ** 2
        no_embargo_collapse = (1 - intact_low) if embargo_in else Fraction(1)
        # Round 9, finding 2: row 5's fifth conjunct, in the class-4 term's own
        # shape. Row 4 does not read it — the falsification half is untouched.
        no_interior_collapse = (1 - intact_low) if interior_in else Fraction(1)
        gate += weight * passes
        row_four += weight * passes * no_embargo_collapse
        row_five += (weight * passes * no_embargo_collapse
                     * no_interior_collapse
                     * _binomial_at_least(PATTERN_MINIMUM, narrow_in,
                                          collapsed_low))
    # `nH` reads arm E's own levels and nothing of arm A's, so it factors out of
    # the pattern sum; `nP` does not, and is inside it above.
    row_four *= marginal_h
    return {
        "trials": n,
        "pHigh": float(q),
        "pLowCollapsed": float(collapsed_low),
        "pLowIntact": float(intact_low),
        "marginal": {"nH": float(marginal_h), "nP": float(marginal_p)},
        "gate": float(gate),
        "joint": {"row4": float(row_four), "row5": float(row_five)},
        "note": "§5.4, for the rules §5.3 registers. `marginal` is the pattern "
                "alone; `joint` is the probability of reaching that row of the "
                "decision table through the class-4 gate (row 2) and the B/C "
                "control gate (row 3), conditional on a complete, sealed batch "
                "(row 1). Independence layers 1-3. For row 4 that is the power "
                "to publish R1-UNSUPPORTED; for row 5 it is the COVERAGE-SIDE "
                "quantity and an upper bound for CONFIRMED — the S5 ceiling "
                "conjunct is outside this model (§5.4, round 5 finding 5), "
                "while row 5's class-3 conjunct is inside it, in the class-4 "
                "term's own shape (round 9, finding 2).",
    }


# --- §5.1, §5.2 and §5.3, applied — never fitted ---------------------------

def level_verdict(block: dict) -> str:
    """§5.1's level verdict for one rate block, by LEVEL_TABLE's rows in
    LEVEL_TABLE's order. One quantity in one unit: the exact Clopper-Pearson
    bounds. The cuts are stated ON BOUNDS, not on observed coverage, so that a
    denominator carrying more misses faces a boundary that already carries
    them — Study 011 §5's own correction, reused."""
    if block is None or block["rate"] is None:
        return UNRESOLVED
    low, high = block["ci95"]
    if low >= HIGH_CUT:
        return "HIGH"
    if high <= LOW_CUT:
        return "LOW"
    return "MID"


def contrast_verdict(baseline: str, arm: str) -> str:
    """§5.2's contrast, on the primary ITT rate, against arm A in the same
    batch. COLLAPSE entails disjoint 95% intervals in the predicted direction
    (U_X <= 0.30 < 0.70 <= L_A) without a separate difference statistic and
    without a distribution for a difference of proportions. INDETERMINATE
    covers both "the arm landed in the middle" and "the baseline itself was not
    HIGH", and it is a publishable outcome, not a failure to report."""
    if UNRESOLVED in (baseline, arm):
        return UNRESOLVED
    if baseline == "HIGH" and arm == "LOW":
        return CONTRAST_TABLE[0][1]
    if baseline == "HIGH" and arm == "HIGH":
        return CONTRAST_TABLE[1][1]
    return CONTRAST_TABLE[2][1]


def placement_contrast_verdict(baseline: str, arm: str) -> str:
    """The same rule computed on S1, and a DISTINCT registered verdict rather
    than a gloss on the first (§5.2). Because H(r) is a subset of A(r) for
    every run, k_H <= k_raw always, so PLACEMENT-COLLAPSE implies COLLAPSE on
    the same class and the converse fails exactly in the case §4.6's table
    calls a label collapse."""
    if UNRESOLVED in (baseline, arm):
        return UNRESOLVED
    if baseline == "HIGH" and arm == "LOW":
        return PLACEMENT_CONTRAST_TABLE[0][1]
    if baseline == "HIGH" and arm == "HIGH":
        return PLACEMENT_CONTRAST_TABLE[1][1]
    return PLACEMENT_CONTRAST_TABLE[2][1]


def second_contrast_verdict(baseline_block: dict, arm_block: dict):
    """§5.2 [D-17]'s weaker contrast: U_X < L_A. Computed from the same
    integers, adds no distribution for a difference of proportions, and is
    reported BESIDE the level-gated verdict, never in place of it. §5.3's
    predictions and falsification conditions are stated on the level-gated
    COLLAPSE alone; this gates nothing and falsifies nothing."""
    if baseline_block is None or arm_block is None:
        return None
    if baseline_block["rate"] is None or arm_block["rate"] is None:
        return None
    return (SECOND_CONTRAST_TABLE[0][1]
            if arm_block["ci95"][1] < baseline_block["ci95"][0]
            else SECOND_CONTRAST_TABLE[1][1])


def label_branch(accuracy: dict) -> dict:
    """§4.6's S5 cut for one arm: are that arm's labels **at the ceiling** or
    **degraded**?

    The ceiling of a proportion is 1, so the cut is `|Q| = 0` — no accepted
    record mislabelled — and no threshold is chosen here (see `S5_CEILING`).
    An arm with no accepted record at all has no label accuracy to read: it is
    published as `degraded` with `rate: null`, because the conservative
    direction of an absent measurement is the one that does not confirm.

    **The cut is decided on the INTEGER `q`** (round 5, finding 13). §4.6
    registers `|Q| = 0`, and this compared the float `rate` against 1.0:
    `|H| / (|H| + 1)` rounds to exactly 1.0 once |H| passes about 2^53, so an
    arm with mislabelled records read as at the ceiling — the one reading §4.6's
    table says confirms R1. No batch of this size reaches that |H|, which is
    exactly why the fix is the integer and not a tolerance: the rule must be the
    registered one at every |H|, not at the ones this study expects. The float
    `rate` and `S5_CEILING` are still published; neither decides anything now.
    An arm with no accepted record has `q == 0` and `rate is None`, so the
    absent measurement is still read off `rate` and still reads `degraded`.
    """
    rate = accuracy["rate"]
    q = accuracy["q"]
    at_ceiling = rate is not None and q == 0
    return {"rate": rate, "h": accuracy["h"], "q": q,
            "ceiling": S5_CEILING,
            "branch": S5_BRANCHES[0] if at_ceiling else S5_BRANCHES[1],
            "note": "§4.6's S5, cut at the ceiling of the pooled accuracy "
                    "|H|/(|H|+|Q|): at the ceiling iff no accepted record was "
                    "mislabelled, decided on the integer |Q| and not on the "
                    "published float, which rounds to 1.0 for large |H| (round "
                    "5, finding 13). An arm with no accepted record has no "
                    "accuracy and reads `degraded`."}


def reading_verdict(counts: dict, branch: str) -> dict:
    """§4.6's three readings of a collapse in arm E, by READING_TABLE's rows in
    READING_TABLE's order (round 3, finding 9).

    The rows are keyed on S1's placement level and on the S5 branch, and the
    scorer reaches them through the counts §5.3's notation already registers:

      row 1  PLACEMENT collapse    `nP >= 3` and the labels at the ceiling
      row 2  comprehension collapse `nP >= 3` and the labels degraded
      row 3  label collapse        `nC >= 3` and `nP < 3`

    Row 3 is read from the coverage integers and not from the S5 branch, and
    §4.6's own wording is why: its label condition is "degraded, **so H-coverage
    falls**", and a class reached raw but not in H is a mislabelled record in
    that class. `nC >= 3` with `nP < 3` IS that condition observed, which is
    also exactly §5.3's decision row 6.

    None when arm E's integers fall on no row of the table.
    """
    if counts["nP"] is None:
        return None
    row = None
    if counts["nP"] >= PATTERN_MINIMUM:
        row = READING_TABLE[0] if branch == S5_BRANCHES[0] else READING_TABLE[1]
    elif counts["nC"] >= PATTERN_MINIMUM:
        row = READING_TABLE[2]
    if row is None:
        return {"publishedAs": None, "labels": branch, "confirmsR1": False,
                "why": "nP = %d and nC = %d: arm E's integers fall on no row of "
                       "§4.6's table" % (counts["nP"], counts["nC"])}
    return {"publishedAs": row["publishedAs"], "reading": row["reading"],
            "gloss": row["gloss"], "labels": branch,
            "confirmsR1": row is READING_TABLE[0],
            "why": "nP = %d, nC = %d, and this arm's S5 labels are %s"
                   % (counts["nP"], counts["nC"], branch)}


def arm_d_outcome(new_levels: list, old_levels: list, contrasts: list) -> dict:
    """§5.3 (ii)'s three registered outcomes for arm D, plus the mixed case it
    names none for, by D_OUTCOME_TABLE's rows in that table's order (round 3,
    finding 10).

    `new_levels` are arm D's level verdicts on the primary ITT rate under its
    OWN family (the new-keyed verdicts), `old_levels` its level verdicts on the
    S10 old-edge rate — the same records keyed to arm A's family predicates,
    labels still D's own — and `contrasts` its §5.2 contrast verdicts against
    arm A. All three are indexed by class.

    The conditions are stated on the LEVELS, class by class, because that is
    what §5.3 (ii) states them on (round 4, finding 6). `contrasts` decides no
    row: it carries §5.3 (ii)'s *prediction* — "TRACKING on all six classes
    under D's own family" — and the count is published beside the outcome as the
    context a reader wants, never as the condition. An earlier version made the
    all-six TRACKING count the condition for row 1, which is neither half of the
    registered sentence.
    """
    narrow = [index for index in NARROW_NUMERIC_CLASSES]
    new_high = sum(1 for index in narrow if new_levels[index] == "HIGH")
    new_low = sum(1 for index in narrow if new_levels[index] == "LOW")
    old_high = sum(1 for index in narrow if old_levels[index] == "HIGH")
    old_low = sum(1 for index in narrow if old_levels[index] == "LOW")
    tracking = sum(1 for row in contrasts
                   if row["contrast"] == CONTRAST_TABLE[1][1])
    # "old-keyed not HIGH-patterned", at §5.3 (i)'s own pattern minimum: the
    # exclusion that separates coverage following D's numbers from a D that
    # covers both threshold pairs at once.
    old_high_patterned = old_high >= D_NARROW_MINIMUM
    if new_high >= D_NARROW_MINIMUM and not old_high_patterned:
        entry = D_OUTCOME_TABLE[0]
        why = ("new-keyed HIGH on %d of the four narrow numeric classes and "
               "old-keyed HIGH on %d, which is short of the %d that would make "
               "the old-keyed levels HIGH-patterned"
               % (new_high, old_high, D_NARROW_MINIMUM))
    elif new_low >= D_NARROW_MINIMUM and old_high >= D_NARROW_MINIMUM:
        entry = D_OUTCOME_TABLE[1]
        why = ("new-keyed LOW on %d of the four narrow numeric classes and "
               "old-keyed HIGH on %d" % (new_low, old_high))
    elif new_low >= D_NARROW_MINIMUM and old_low >= D_NARROW_MINIMUM:
        entry = D_OUTCOME_TABLE[2]
        why = ("new-keyed LOW on %d of the four narrow numeric classes and "
               "old-keyed LOW on %d" % (new_low, old_low))
    else:
        entry = D_OUTCOME_TABLE[3]
        why = ("new-keyed HIGH on %d of the four narrow numeric classes and LOW "
               "on %d, old-keyed HIGH on %d and LOW on %d, TRACKING on %d of %d"
               % (new_high, new_low, old_high, old_low, tracking, len(contrasts)))
    return {"row": entry["row"], "publishedAs": entry["publishedAs"],
            "condition": entry["condition"], "gloss": entry["gloss"],
            "explanations": list(entry["explanations"]),
            "separates": D_OLD_EDGE_NOTE if entry["explanations"] else None,
            "counts": {"newKeyedHigh": new_high, "newKeyedLow": new_low,
                       "oldKeyedHigh": old_high, "oldKeyedLow": old_low,
                       "tracking": tracking,
                       "narrowMinimum": D_NARROW_MINIMUM,
                       "classes": len(contrasts)},
            "why": why,
            "note": "§5.3 (ii): the new-keyed verdicts are arm D's own-family "
                    "primary levels and the old-keyed ones are S10's, under "
                    "ARM A's predicates with D's own labels. The rows are "
                    "decided by those levels; `tracking` is §5.3 (ii)'s "
                    "prediction reported beside them and decides no row (round "
                    "4, finding 6). This outcome adjudicates nothing about R1 "
                    "and no §5.3 (i) row reads it."}


def review_tier(coverage: dict, mislabel_share) -> dict:
    """§4.6 S9: Study 011 §5's registered mapping, applied per arm unchanged —
    never fitted, and never read by any §5 decision of this study.

    ONE criterion in ONE unit: the exact Clopper-Pearson lower bound. LIGHT iff
    lower >= 0.80, STANDARD iff lower >= 0.40, FULL otherwise, with one
    escalation on distinct evidence — a class reached mostly with wrong labels
    moves one step toward FULL. Reported because it is the product quantity the
    previous study registered. [D-2] records why this study's own cuts are 0.70
    and 0.30 instead: 011's 0.80 lands at k >= 29 at n = 30, so a single stray
    miss in a control arm would read as inconclusive.
    """
    if coverage is None or coverage["rate"] is None:
        return {"base": None, "escalations": [], "tier": None, "lower": None}
    lower = coverage["ci95"][0]
    if lower >= LIGHT_LOWER_BOUND:
        base = "LIGHT"
    elif lower >= STANDARD_LOWER_BOUND:
        base = "STANDARD"
    else:
        base = "FULL"
    escalations = []
    if mislabel_share is not None and mislabel_share >= MISLABEL_ESCALATION:
        escalations.append("mislabel")
    index = min(len(TIERS) - 1, TIERS.index(base) + len(escalations))
    return {"base": base, "escalations": escalations, "tier": TIERS[index],
            "lower": lower}


# --- §2.8's registered call order ------------------------------------------

def williams() -> dict:
    """{"W1"…"W10": (arm, …)} — the ten registered sequences, derived from the
    first row. W1…W5 are its cyclic rows, each the one before it with every arm
    advanced one step through A→B→C→D→E→A; W6…W10 are those five reversed. Over
    the ten, each arm holds each of the five positions exactly twice and each of
    the twenty ordered pairs X→Y is adjacent exactly twice."""
    rows = {}
    for step in range(len(ARMS)):
        row = tuple(ARMS[(ARMS.index(arm) + step) % len(ARMS)]
                    for arm in WILLIAMS_FIRST_ROW)
        rows["W%d" % (step + 1)] = row
        rows["W%d" % (step + 1 + len(ARMS))] = tuple(reversed(row))
    return rows


def registered_schedule() -> list:
    """The 150-slot call order §2.8 registers, expanded from the ten sequences
    and the three block orders.

    One record per slot: `(globalIndex, round, position, arm, slotIndex)`, all
    1-based. Thirty rounds, each running one slot of each arm; the round's
    within-round order is the Williams sequence its block order names.
    `slotIndex` is the count of that arm's slots so far — derived from the order
    and not stored in it, which is what makes C5 rule 4's "the contiguous range
    1…count_X, derived from that prefix" true of any prefix, complete or not,
    without reference to a round number.

    A harness test asserts §2.8's registered properties over what this returns —
    30 slots per arm, each arm in each within-round position exactly 6 times,
    each of the 20 ordered pairs adjacent exactly 6 times within rounds, 29
    round-boundary transitions with no arm following itself, 149 total
    transitions with max minus min of 1 — and diffs the expansion against
    `batch.py`'s, which derives it from the same two facts.
    """
    rows = williams()
    # A block is a PERMUTATION of the ten sequences, not a selection from them:
    # every sequence holds every arm once, so a block that ran W4 twice and W3
    # never would still give 30 slots per arm and would destroy the transition
    # balance §2.8 registers. The per-arm counts cannot see it, so it is checked
    # here.
    for number, block in enumerate(BLOCKS, 1):
        if sorted(block) != sorted(rows):
            raise ScoreError("block %d of §2.8's registered order is %r, which is "
                             "not a permutation of the ten sequences"
                             % (number, list(block)))
    order, counts = [], {arm: 0 for arm in ARMS}
    index = 0
    for block in BLOCKS:
        for sequence in block:
            round_number = len(order) // len(ARMS) + 1
            for position, arm in enumerate(rows[sequence], start=1):
                index += 1
                counts[arm] += 1
                order.append({"globalIndex": index, "round": round_number,
                              "position": position, "arm": arm,
                              "slotIndex": counts[arm],
                              "sequence": sequence})
    return order


def schedule_key(entry: dict) -> tuple:
    """The four members §3.3 and C5 compare: `(globalIndex, round, position,
    arm)`. `slotIndex` is derived from the prefix (C5 rule 4) and is checked
    separately, so it is not part of the identity a slot is matched on."""
    return (entry.get("globalIndex"), entry.get("round"),
            entry.get("position"), entry.get("arm"))


def transition_census(entries: list) -> dict:
    """§2.8's realised directed-transition counts over the order that actually
    ran, and the within-round position counts. §4.7 reports both against §2.8's
    registered values; nothing here gates anything, and a truncated batch
    claims no balance at all — §2.8 says so."""
    transitions: dict = {}
    for first, second in zip(entries, entries[1:]):
        key = "%s->%s" % (first["arm"], second["arm"])
        transitions[key] = transitions.get(key, 0) + 1
    positions: dict = {}
    for entry in entries:
        key = "%s@%d" % (entry["arm"], entry["position"])
        positions[key] = positions.get(key, 0) + 1
    return {"transitions": dict(sorted(transitions.items())),
            "positions": dict(sorted(positions.items())),
            "transitionCount": max(0, len(entries) - 1)}


# --- the arms ---------------------------------------------------------------

def arm_path(arms_root: str, arm: str, name: str) -> str:
    return os.path.join(arms_root, arm, ARM_FILES[name])


def slots_root(arms_root: str, arm: str) -> str:
    return os.path.join(arms_root, arm, AUTHORING)


def load_arm(arms_root: str, arm: str, pinned: dict) -> dict:
    """One arm's registered artifacts, at the pinned digests: its
    `(T_low, T_high)` and its six coverage classes.

    The thresholds come from `ARM.json` and from nowhere else (§2.2 [D-14]);
    the classes come from that arm's own `FAMILY.json`, whose predicates carry
    their own numbers (§2.3). The patches are not read — this study plants
    nothing and evaluates no pack.
    """
    for name in ("arm", "family", "policy", "prompt"):
        path = arm_path(arms_root, arm, name)
        if not os.path.isfile(path):
            raise ScoreError("arm %s is missing %s" % (arm, ARM_FILES[name]))
        actual = file_digest(path)
        expected = pinned.get("%sSha256" % name)
        if actual != expected:
            raise ScoreError("arm %s's %s is %s, not the pinned %r"
                             % (arm, ARM_FILES[name], actual, expected))
    definition = load_json(arm_path(arms_root, arm, "arm"))
    if definition.get("arm") != arm:
        raise ScoreError("arms/%s/ARM.json names arm %r: an arm's own artifact "
                         "cannot name another arm" % (arm, definition.get("arm")))
    thresholds = definition.get("thresholds")
    if not isinstance(thresholds, dict) or "tLow" not in thresholds \
            or "tHigh" not in thresholds:
        raise ScoreError("arms/%s/ARM.json registers no (tLow, tHigh) pair: the "
                         "mirror has no default and this arm cannot be labelled"
                         % arm)
    # The pair the mirror is instantiated at is bound to the REGISTRY as well as
    # to the arm's own artifact, so a labelled arm answers to both. The registry
    # carries the pair as strings; `Decimal` reads either, and comparing as
    # strings keeps 45 and "45" from being two registrations of one number.
    pinned_pair = (str(pinned.get("tLow")), str(pinned.get("tHigh")))
    if (str(thresholds["tLow"]), str(thresholds["tHigh"])) != pinned_pair:
        raise ScoreError("arms/%s/ARM.json registers the pair %r and harness/PINS.json "
                         "pins %r: an arm's thresholds are one registration, not two"
                         % (arm, (thresholds["tLow"], thresholds["tHigh"]),
                            pinned_pair))
    family = load_json(arm_path(arms_root, arm, "family"))
    mutations = family.get("mutations")
    if not isinstance(mutations, list) or not mutations:
        raise ScoreError("arms/%s/FAMILY.json carries no mutations" % arm)
    classes = [{"index": mutation["index"], "title": mutation["title"],
                "predicate": mutation["predicate"],
                "predicateProse": mutation["predicateProse"]}
               for mutation in mutations]
    indexes = [entry["index"] for entry in classes]
    if indexes != list(range(len(classes))):
        raise ScoreError("arms/%s/FAMILY.json's indexes are not contiguous from "
                         "0: %r" % (arm, indexes))
    embargo = family.get("embargoList")
    if not isinstance(embargo, list) or not embargo:
        raise ScoreError("arms/%s/FAMILY.json carries no embargoList" % arm)
    return {"arm": arm,
            "tLow": thresholds["tLow"], "tHigh": thresholds["tHigh"],
            "perturbation": definition.get("perturbation"),
            "classes": classes, "embargo": tuple(embargo),
            "promptSha256": file_digest(arm_path(arms_root, arm, "prompt")),
            "familySha256": file_digest(arm_path(arms_root, arm, "family")),
            "policySha256": file_digest(arm_path(arms_root, arm, "policy")),
            "armSha256": file_digest(arm_path(arms_root, arm, "arm"))}


def split_records(accepted: dict, t_low, t_high) -> tuple:
    """(H ids, Q ids) for one arm: H is the records whose own recorded outcome
    equals the mirror's verdict AT THIS ARM'S THRESHOLDS, Q is the rest. Both
    are kept; neither is repaired. The threshold pair is required, not
    defaulted — a silent default would label a slot of arm D at (40, 70) with
    nothing refusing (§2.2 [D-14])."""
    high, quarantine = [], []
    for case_id, record in accepted.items():
        if _policy_mirror().verdict(record["vendor"], t_low, t_high) \
                == record["decision"]["outcome"]:
            high.append(case_id)
        else:
            quarantine.append(case_id)
    return sorted(high), sorted(quarantine)


def class_members(accepted: dict, ids: list, predicate: dict) -> list:
    return sorted(case_id for case_id in ids
                  if _policy_mirror().predicate_matches(predicate,
                                                     accepted[case_id]["vendor"]))


# --- admission -------------------------------------------------------------

def _regular(path: str) -> bool:
    """A regular file, decided by lstat: a symlink to one is not one, and
    nothing here is opened to find out."""
    try:
        return stat.S_ISREG(os.lstat(path).st_mode)
    except OSError:
        return False


# The file types a slot tree may not hold, named so a refusal says which one
# was found rather than "not a regular file". Anything not in this table and
# not a regular file, directory or symlink is reported as `unknown type`.
IRREGULAR_KINDS = (
    (stat.S_ISFIFO, "FIFO"),
    (stat.S_ISSOCK, "socket"),
    (stat.S_ISCHR, "character device"),
    (stat.S_ISBLK, "block device"),
    (stat.S_ISDOOR if hasattr(stat, "S_ISDOOR") else (lambda mode: False), "door"),
)


def _kind(mode: int) -> str:
    for predicate, name in IRREGULAR_KINDS:
        if predicate(mode):
            return name
    return "unknown type"


def slot_irregularities(slot: str) -> tuple:
    """(symlinks, irregular entries) in a slot tree, relative to the slot and
    sorted — everything in it that is not a regular file or a directory.

    A slot tree may hold REGULAR FILES AND DIRECTORIES ONLY. A link is a
    retained byte the slot does not contain, or a file whose existence depends
    on a target outside the published evidence. A FIFO, a socket or a device is
    worse: it is not retained evidence at all, and a FIFO named `REFUSAL.json`
    does not merely mislead a reader — `open()` on it BLOCKS, so a scorer that
    reached it would hang over the whole batch rather than refuse one slot. That
    is why every entry's type is decided by `os.lstat` BEFORE anything in the
    tree is opened, and why this runs before every other check in `admit()`.

    Two codes, because the two say different things and §3.3 registers both:
    `slot-symlink` for links (dangling or resolving), `slot-irregular` for every
    other non-regular, non-directory type.

    Nothing here follows a link: the walk is iterative over `os.scandir`'s
    cheaper cousin `os.listdir`, descends only into entries `lstat` calls
    directories, and a dangling link is found because `S_ISLNK` is a question
    about the entry and not about its target.
    """
    symlinks, irregular = [], []

    def classify(path: str, relative: str) -> bool:
        """True when this entry is a directory to descend into."""
        try:
            mode = os.lstat(path).st_mode
        except OSError as error:
            irregular.append("%s (unreadable: %s)" % (relative, error.strerror))
            return False
        if stat.S_ISLNK(mode):
            symlinks.append(relative)
            return False
        if stat.S_ISDIR(mode):
            return True
        if stat.S_ISREG(mode):
            return False
        irregular.append("%s (%s)" % (relative, _kind(mode)))
        return False

    if classify(slot, "."):
        pending = [(slot, "")]
        while pending:
            base, prefix = pending.pop()
            try:
                names = sorted(os.listdir(base))
            except OSError as error:
                irregular.append("%s (unreadable: %s)" % (prefix or ".", error.strerror))
                continue
            for name in names:
                relative = os.path.join(prefix, name) if prefix else name
                if classify(os.path.join(base, name), relative):
                    pending.append((os.path.join(base, name), relative))
    return sorted(symlinks), sorted(irregular)


def compiled_files(completion_path: str) -> dict:
    """{relative path: bytes} for one run's records, regenerated from the
    retained completion bytes every time it is asked. The regeneration IS the
    artifact — every run has its own — and its digest is published per run so a
    reader recomputes rather than trusts. The compiler is arm-independent: it
    validates record SHAPE, never policy semantics (§3.1)."""
    raw = records_compile.read_completion(completion_path)
    accepted, ledger, span = records_compile.compile_records(raw)
    return records_compile.render(accepted, ledger, span)


def _under(path: str, root: str) -> bool:
    """True when `path` is strictly inside `root`. String containment on
    normalized paths: these are recorded strings from a run that has already
    ended, not live paths to resolve, and a symlink question cannot be asked
    of them."""
    if not isinstance(path, str) or not isinstance(root, str) or not root:
        return False
    return os.path.normpath(path).startswith(os.path.normpath(root) + os.sep)


def _same(first: str, second: str) -> bool:
    """The case `_under()` does not cover, and the one C6 needs covered: two
    recorded paths that are the SAME directory."""
    if not isinstance(first, str) or not isinstance(second, str) or not first:
        return False
    return os.path.normpath(first) == os.path.normpath(second)


def _resolved(path) -> bool:
    """C6 registers the RESOLVED isolated home and working directory, and this
    is as much of "resolved" as a recorded string can be held to: absolute,
    and already in normal form, so no `..`, no `.`, and no doubled separator
    can make two names for one directory read as two directories."""
    return isinstance(path, str) and bool(path) and os.path.isabs(path) \
        and os.path.normpath(path) == path


def check_environment(call: dict) -> str:
    """§6 C6's clause list, ported unchanged and enforced per run, or a sentence
    saying which clause failed.

    These are checks on the wrapper's own record — §7 says plainly that
    CALL.json is self-reported — but a record that contradicts the registered
    invocation is not evidence of it, and that much is checkable.
    """
    home, codex_home, cwd = call.get("home"), call.get("codexHome"), call.get("cwd")
    if call.get("isolation") != "isolated":
        return "CALL.json records isolation %r, not the registered isolated run" % (
            call.get("isolation"),)
    # C6 registers the RESOLVED isolated home and working directory. A relative
    # or unnormalized one is not resolved, and — worse for the clauses below —
    # `../home` and `home` are two names the nesting test would not relate.
    if not _resolved(home):
        return ("CALL.json records the isolated home %r, which is not a resolved "
                "absolute path" % (home,))
    if not isinstance(codex_home, str) or codex_home != os.path.join(home, ".codex"):
        return ("CALL.json records CODEX_HOME %r, which is not the .codex directory "
                "of its own isolated home %r" % (codex_home, home))
    if not _resolved(cwd):
        return ("CALL.json records the working directory %r, which is not a resolved "
                "absolute path" % (cwd,))
    if _same(cwd, home) or _under(cwd, home) or _under(home, cwd):
        return ("the isolated home %r and the working directory %r are the same "
                "directory or nested: the registered invocation puts the model's "
                "workspace outside the home it was given" % (home, cwd))
    # C6's leak-token screen on the scratch path, re-checked here from the
    # recorded path rather than left to the wrapper alone. The wrapper refuses
    # before the call; this refuses after it, from the retained record, which is
    # the half of that clause a scorer can re-derive. (The other half — that the
    # scratch resolved outside every git worktree — is a fact about a directory
    # that no longer exists by scoring time, so it stays a wrapper gate and §6
    # C6 says so.) A study term in the working directory blunts the transcript
    # screen, which excises environment paths before it looks for leak tokens.
    leaked = sorted(token for token in transcript_check.LEAK_TOKENS
                    if token in cwd.lower())
    if leaked:
        return ("the working directory %r carries the leak token(s) %r: the scratch "
                "path is screened before the call and re-screened here, because the "
                "transcript's own leak screen excises environment paths before it "
                "looks for tokens — so a study term hiding in one would be excised "
                "rather than found (§6 C6)" % (cwd, leaked))
    if call.get("environment") != ENVIRONMENT_NAMES:
        return ("CALL.json records the environment %r, not the registered %r"
                % (call.get("environment"), ENVIRONMENT_NAMES))
    values = call.get("environmentValues")
    if not isinstance(values, dict) or sorted(values) != sorted(ENVIRONMENT_NAMES) \
            or not all(isinstance(value, str) and value for value in values.values()):
        return ("CALL.json records environmentValues %r, not one string per registered "
                "variable" % (values,))
    if values["HOME"] != home or values["CODEX_HOME"] != codex_home:
        return ("the recorded HOME/CODEX_HOME values %r do not agree with the isolated "
                "home this run reports" % ({"HOME": values["HOME"],
                                            "CODEX_HOME": values["CODEX_HOME"]},))
    entries = values["PATH"].split(":")
    if tuple(entries[:len(SYSTEM_PATH)]) != SYSTEM_PATH or len(entries) != len(SYSTEM_PATH) + 1:
        return ("the child PATH %r is not the six registered system directories plus "
                "one per-run binary directory" % (values["PATH"],))
    # `_same` as well as `_under`, for the same reason the working-directory
    # clause needs both: `_under()` is strict descent, and a PATH entry that IS
    # the isolated home is not outside it.
    if not entries[-1].startswith("/") or _same(entries[-1], home) \
            or _under(entries[-1], home):
        return ("the per-run binary directory %r is not an absolute path outside the "
                "isolated home: Study 010's PATH ended in the operator's real home, "
                "which is the defect this clause exists to catch" % (entries[-1],))
    if values["TMPDIR"] == "/tmp" or not _under(values["TMPDIR"], cwd):
        return ("TMPDIR %r is not inside this run's own scratch: the pinned CLI's "
                "sandbox is writable at [workdir, /tmp, $TMPDIR], so a shared TMPDIR "
                "puts every other run's tree in this run's writable set"
                % (values["TMPDIR"],))
    if call.get("stdin") != CLOSED_STDIN:
        return "CALL.json records stdin %r, not %r" % (call.get("stdin"), CLOSED_STDIN)
    # C6's credential clause is TWO BOOLEANS and this reads them as two booleans
    # (round 3, finding 18). The earlier form coerced the copy flag with
    # `bool()`, and `bool("false")` is True — so a slot recording the string
    # "false" beside `credentialRemoved: true` agreed with itself and passed,
    # which is a live credential reported as removed. A type check, not a
    # truthiness test: `1`, `"true"`, `None` and `[]` are all refusals.
    copied, removed = call.get("credentialCopied"), call.get("credentialRemoved")
    if not isinstance(copied, bool) or not isinstance(removed, bool):
        return ("CALL.json records credentialCopied %r and credentialRemoved %r: C6's "
                "copy and removal evidence is two booleans, and a string or a number "
                "there is not evidence of either — bool('false') is True" % (copied, removed))
    if removed is not copied:
        return ("the run copied a credential %r and records credentialRemoved %r: a "
                "copy that was made and not removed is a live credential left on disk, "
                "and a removal recorded without a copy is a record of nothing"
                % (copied, removed))
    return None


def _transcript_is_another_arm(session: str, completion: str, call_path: str,
                               arms_root: str, arm: str, golden_path: str,
                               model: str) -> str:
    """The arm whose registered prompt this transcript is terminal under, when
    that arm is not the one whose tree the slot sits in — else None.

    §3.1 gate 2 and §3.3 register that a slot whose transcript carries ANOTHER
    arm's prompt is `arm-mismatch` and not a generic `transcript-refused`, and
    C4 fixture 1 requires exactly that code. The question is asked by RE-RUNNING
    the ported gate against each other arm's prompt bytes rather than by reading
    the refusal message the first run produced: a code decided by string
    matching on an error sentence is a code that moves when a message is
    reworded. If the transcript is admissible under exactly one other arm's
    prompt, that is the arm it was made with.
    """
    for other in ARMS:
        if other == arm:
            continue
        try:
            transcript_check.check(session, arm_path(arms_root, other, "prompt"),
                                   completion, call_path, golden_path,
                                   model=model, arm=other)
        except (transcript_check.TranscriptError, ValueError, OSError):
            continue
        return other
    return None


# The ported compiler's OWN strictness, and the same decoder without it. The
# two differ in exactly the hooks `records_compile.extract_array()` builds its
# decoder from — duplicate object keys and the non-JSON constants — and in
# nothing else, so the boundary between "no array" and "an array this compiler
# refuses" is the port's boundary rather than a second definition of it beside
# it. Both parse numbers to the port's `JsonNumber`, which is why the host's
# integer-string digit limit cannot make the two disagree (round 6, finding 7).
_STRICT_DECODER = json.JSONDecoder(
    object_pairs_hook=records_compile._refuse_duplicate_keys,
    parse_constant=records_compile._refuse_constants,
    parse_int=records_compile.JsonNumber,
    parse_float=records_compile.JsonNumber)
_ARRAY_SHAPE_DECODER = json.JSONDecoder(parse_int=records_compile.JsonNumber,
                                        parse_float=records_compile.JsonNumber)


def strict_decode_refusal(raw: str):
    """The refusal detail when a completion HOLDS an array and the ported
    compiler's strict decoder will not accept one, or None when the stream holds
    no array at all.

    Round 6, finding 7: `compile-refused` was dead. §3.3 registers it as "the
    compiler failed other than by finding no array", and 011 §3.3 registers the
    boundary it is the other side of — "`records_compile`'s 'no parseable array'
    refusal classifies the run authoring-empty and valid; every other compiler
    error classifies it pipeline-invalid". But `extract_array()` swallows every
    decoder `ValueError` per candidate, so a completion whose only array carries
    duplicate object keys or a `NaN` produced the SAME `CompileError` as a
    completion of pure prose, and the scorer called both authoring-empty: a
    valid run, in every denominator, covering nothing. That is the wrong side of
    the line twice over — it is a pipeline outcome scored as an authoring one,
    and §4.2's intent-to-treat arithmetic puts pipeline losses in `I_X` and
    publishes the sensitivity bound over them.

    The question is asked of the bytes and not of the exception: the widest
    span that decodes to a JSON ARRAY at all, ties to the earliest — the
    port's own selection rule — and then whether the port's strict decoder
    refuses that same span. An array it refuses is an array; a `[` that opens
    nothing is not, and the run stays authoring-empty as §3.3 registers.
    """
    best = None
    start = raw.find("[")
    while start >= 0:
        try:
            decoded, end = _ARRAY_SHAPE_DECODER.raw_decode(raw, start)
        except ValueError:
            decoded, end = None, start
        if isinstance(decoded, list) and (best is None or end - start > best[0]):
            try:
                _STRICT_DECODER.raw_decode(raw, start)
            except ValueError as error:
                best = (end - start, start, end, str(error))
        start = raw.find("[", start + 1)
    if best is None:
        return None
    _width, first, last, detail = best
    return ("characters %d-%d of the completion are a JSON array the ported "
            "compiler's strict decoder refuses (%s): §3.3 reserves "
            "authoring-empty for a completion with NO parseable array, and an "
            "array the compiler will not decode is a compiler refusal"
            % (first, last, detail))


def admit(slot: str, arm: str, arms_root: str, golden_path: str, pins: dict,
          arm_definition: dict, scheduled: dict, ledger_record: dict,
          reuse_detail: str = None, registry_sha256: str = None) -> tuple:
    """(code, detail, authoring-empty): code is None when the run is valid.

    The checks run in §3.3's documented order and the FIRST failure names the
    run. Nothing here consults the batch's own refusal record; reconciling with
    it is score_run()'s job, so that a batch refusal can never make an
    inadmissible run look examined or an admissible one look refused.

    `scheduled` is what §2.8's registered call order assigns to this slot's
    global index, `ledger_record` is the ledger's record for this slot, and
    `reuse_detail` is the population-level session-uniqueness verdict computed
    before any slot was admitted (§3.3). All three are computed once over the
    whole batch and passed in, because none of them is a question one slot can
    answer about itself.

    `registry_sha256` defaults to the digest of the committed
    `harness/PINS.json` — the strict value, and the only one `main()` can
    produce, because the registered interface has no parameter for it. The
    override exists so the wrapper-driven tests, whose slots are made under a
    stand-in registry naming a stand-in binary, can say which registry their
    slots' stamps are supposed to name; a scoring that uses it can never be
    published.
    """
    if registry_sha256 is None:
        registry_sha256 = file_digest(REGISTRY_OF_RECORD)
    # §3.3, first: regular files and directories only, anywhere in the tree,
    # decided by lstat before anything is opened. This precedes every other
    # check for two reasons — a symlink decides what a later check reads (a
    # dangling REFUSAL.json link answers `exists()` with False and made the
    # batch's own refusal record disappear), and a FIFO decides whether a later
    # check RETURNS at all (open() on one blocks forever).
    links, irregular = slot_irregularities(slot)
    if links:
        return ("slot-symlink",
                "the slot tree holds %d symlink(s) (%s): a slot may hold regular "
                "files and directories only, and a link — dangling or not — is a "
                "retained byte the slot does not contain"
                % (len(links), ", ".join(links)), False)
    if irregular:
        return ("slot-irregular",
                "the slot tree holds %d entry/entries that are neither regular files "
                "nor directories (%s): a slot may hold regular files and directories "
                "only. These are not retained evidence at all, and one of them — a "
                "FIFO — would block the scorer in open() rather than refuse a slot"
                % (len(irregular), ", ".join(irregular)), False)
    for name in SLOT_FILES:
        if not _regular(os.path.join(slot, name)):
            return "slot-shape", "%s is missing or not a regular file" % name, False
    try:
        call = load_json(os.path.join(slot, "CALL.json"))
    except ValueError as error:
        return "call-unreadable", str(error), False
    if not isinstance(call, dict):
        return "call-unreadable", "CALL.json is not a JSON object", False
    # Round 5, finding 6: read here, next to the other readability checks and
    # before anything downstream indexes, hashes or joins these members. The
    # population's session-uniqueness pass already had to skip this slot's
    # `callIdentity` (`slot_identity()`), and this is the check that makes its
    # docstring's "already refused by an earlier code" true.
    identity_defect = call_identity_defect(call)
    if identity_defect is not None:
        return "call-unreadable", identity_defect, False
    if call.get("model") != pins["codex"]["model"]:
        return "model-mismatch", "CALL.json names model %r" % call.get("model"), False
    if call.get("binarySha256") != pins["codex"]["binarySha256"]:
        return "binary-mismatch", "CALL.json names binary %r" % call.get("binarySha256"), False
    if call.get("cli") != pins["codex"]["version"]:
        return "cli-mismatch", "CALL.json names CLI %r" % call.get("cli"), False
    # §2.10: the cell is defined by the committed registry, and a run made under
    # another one is not a run in this cell. Without this a `--pins` registry
    # naming a different model, binary, arm digest or N would define its own
    # study and publish under this one's name.
    if call.get("pinsSha256") != registry_sha256:
        return ("registry-mismatch",
                "the run was made under registry %r and this study's registry of "
                "record is %s: a slot made under another registry is not a slot in "
                "this cell" % (call.get("pinsSha256"), registry_sha256), False)
    # §3.2: the golden capture the batch verified at preflight, stamped per
    # slot. The scorer's own precondition binds the golden FILE to the pin; this
    # binds each RUN to that file, so a capture derived after the batch and
    # re-pinned cannot change which runs were admissible. One recapture serves
    # all five arms ([D-8]), so this is one digest and not five.
    golden_digest = file_digest(golden_path)
    if call.get("goldenSha256") != golden_digest:
        return ("golden-mismatch",
                "the run was made against golden capture %r and this scoring uses %s: "
                "a golden capture is registered before the first slot and a run cannot "
                "be re-admitted against a later one"
                % (call.get("goldenSha256"), golden_digest), False)
    # §3.3's first new code, from the stamps alone (§3.1 gate 9). The transcript
    # half of `arm-mismatch` is checked at the transcript gate below, where the
    # bytes are read.
    if call.get("arm") != arm:
        return ("arm-mismatch",
                "the slot sits in arm %s's tree and its CALL.json records arm %r: a "
                "run made with another arm's policy text cannot enter this arm's "
                "denominator" % (arm, call.get("arm")), False)
    if call.get("armPromptSha256") != arm_definition["promptSha256"]:
        return ("arm-mismatch",
                "the slot records arm %s and arm-prompt digest %r, and arm %s's "
                "registered PROMPT.txt is %s: the arm stamp and the prompt digest "
                "disagree, so the run does not say which policy text it was made with"
                % (arm, call.get("armPromptSha256"), arm,
                   arm_definition["promptSha256"]), False)
    # §3.3's second new code. `arm-mismatch` cannot see a same-arm copy, a
    # rename or a duplicate — all three name the right arm and carry the right
    # prompt digest — and this is what they trip.
    recorded = schedule_key(call)
    if recorded != schedule_key(scheduled):
        return ("schedule-mismatch",
                "the slot records (globalIndex, round, position, arm) = %r and §2.8's "
                "registered call order assigns %r to that position: a same-arm copy, a "
                "rename or a duplicated slot names the right arm and carries the right "
                "prompt digest, and this is the check that sees it"
                % (recorded, schedule_key(scheduled)), False)
    if recorded != schedule_key(ledger_record):
        return ("schedule-mismatch",
                "the slot records %r and the ledger's record for this slot records %r: "
                "the ledger is the append-only account of what ran and a slot that "
                "disagrees with it is not the slot the ledger recorded"
                % (recorded, schedule_key(ledger_record)), False)
    if call.get("slotIndex") != scheduled["slotIndex"]:
        return ("schedule-mismatch",
                "the slot records slotIndex %r and the registered prefix puts arm %s's "
                "global index %d at slot %d of that arm"
                % (call.get("slotIndex"), arm, scheduled["globalIndex"],
                   scheduled["slotIndex"]), False)
    # §3.3's third new code, decided over the whole population before any rate
    # is computed: a copied slot must not be able to agree with itself.
    if reuse_detail is not None:
        return "session-reused", reuse_detail, False
    # C6: isolation demonstrated per run, not asserted once. The wrapper's own
    # record of what it did — a fresh home, a scrubbed environment, and an
    # isolated home whose RECURSIVE inventory is exactly the .codex directory
    # and, when one was copied, the credential inside it.
    for flag in ("homeIsolated", "codexHomeIsolated", "environmentScrubbed",
                 "ignoreUserConfig"):
        if call.get(flag) is not True:
            return "isolation-unproven", "CALL.json does not record %s" % flag, False
    if not isinstance(call.get("home"), str) or not call["home"]:
        return "isolation-unproven", "CALL.json records no isolated home", False
    # Which inventory a fresh home should hold depends on whether a credential
    # was copied. `check_environment()` below refuses any non-boolean flag
    # outright (C6, round 3 finding 18), so no run reaches a rate through this
    # branch on a truthy string — it decides which of two refusal sentences a
    # malformed slot gets, never whether it is refused.
    expected_inventory = ([".codex", ".codex/auth.json"]
                          if call.get("credentialCopied") else [".codex"])
    if call.get("isolatedHomeInventory") != expected_inventory:
        return ("isolation-unproven",
                "the isolated home held %r before the call, not the %r a fresh home "
                "with %s accounts for"
                % (call.get("isolatedHomeInventory"), expected_inventory,
                   "the copied credential" if call.get("credentialCopied")
                   else "no credential to copy"), False)
    environment_failure = check_environment(call)
    if environment_failure is not None:
        return "isolation-unproven", environment_failure, False
    # An integer 1, and not `True`: Python calls those equal, so a slot
    # recording `newSessionCount: true` — a record of nothing counted — passed
    # this clause while §6 C6 registers exactly one new session file.
    sessions = call.get("newSessionCount")
    if not isinstance(sessions, int) or isinstance(sessions, bool) or sessions != 1:
        return ("session-count",
                "the call records %r new sessions, not the integer 1" % (sessions,), False)
    status = call.get("exitStatus")
    if not isinstance(status, int) or isinstance(status, bool) or status != 0:
        return "call-nonzero-exit", "exit status %r" % status, False
    session = os.path.join(slot, "session.jsonl")
    completion = os.path.join(slot, "completion.txt")
    context = os.path.join(slot, "context.json")
    call_path = os.path.join(slot, "CALL.json")
    if not _regular(session):
        return "no-session", "session.jsonl was not retained", False
    if not _regular(completion):
        return "no-completion", "completion.txt was not retained", False
    if not _regular(context):
        return "no-context", "context.json was not retained", False
    try:
        transcript_check.check(session, arm_path(arms_root, arm, "prompt"),
                               completion, call_path, golden_path,
                               model=pins["codex"]["model"], arm=arm)
    except transcript_check.CompletionUndecodable as error:
        # §3.3 registers `completion-unreadable` — "completion.txt is not
        # decodable UTF-8" — and the transcript binding reads that file before
        # `records_compile.read_completion()` does, to bind it to the
        # transcript's last assistant message. Its decode used to raise a bare
        # `UnicodeDecodeError`, which is a `ValueError`, so every undecodable
        # completion was named a transcript refusal and the registered code
        # named no run (round 5, finding 7). Caught FIRST, ahead of the ported
        # gate's own refusals, because it is not one of them.
        return "completion-unreadable", str(error), False
    except (transcript_check.TranscriptError, ValueError) as error:
        # §3.1 gate 2 / §3.3: a transcript that is terminal under ANOTHER arm's
        # registered prompt is `arm-mismatch`, not `transcript-refused` — the
        # stamps were honest and the bytes were not.
        other = _transcript_is_another_arm(session, completion, call_path,
                                           arms_root, arm, golden_path,
                                           pins["codex"]["model"])
        if other is not None:
            return ("arm-mismatch",
                    "the slot sits in arm %s's tree and its transcript is terminal "
                    "under arm %s's registered prompt bytes: the stamps name this arm "
                    "and the bytes name another (§3.1 gate 2)" % (arm, other), False)
        return "transcript-refused", str(error), False
    try:
        retained = load_json(context)
    except ValueError as error:
        return "context-mismatch", str(error), False
    if retained != transcript_check.context_digests(session, call):
        return "context-mismatch", "context.json is not what session.jsonl yields", False
    try:
        raw = records_compile.read_completion(completion)
    except (UnicodeDecodeError, OSError) as error:
        return "completion-unreadable", str(error), False
    try:
        records_compile.compile_records(raw)
    except records_compile.CompileError as error:
        # §3.3: a completion with no parseable array is an AUTHORING outcome,
        # not a pipeline failure. The run is valid and covers nothing — and in
        # this study that matters more than it did in 011, because a
        # perturbation that makes the author fail outright must not be scored as
        # if it had never been tried.
        #
        # But only NO ARRAY is that outcome (round 6, finding 7). The ported
        # `extract_array()` catches every decoder ValueError per candidate, so
        # an array it REFUSES — duplicate object keys, a non-JSON constant —
        # arrives here wearing the no-array refusal's message. The bytes are
        # asked which of the two it was, and an array the compiler will not
        # decode is `compile-refused`: pipeline-invalid, in `I_X`, inside the
        # sensitivity bound, and not a valid run that covered nothing.
        refusal = strict_decode_refusal(raw)
        if refusal is not None:
            return "compile-refused", refusal, False
        return None, str(error), True
    except ValueError as error:
        return "compile-refused", str(error), False
    # The committed-tree check 010 ran against its records/ tree, run here
    # against a throwaway one: compile it, then require the ported verify to
    # regenerate it byte-for-byte with the exact file set.
    try:
        with tempfile.TemporaryDirectory() as root:
            with contextlib.redirect_stdout(io.StringIO()):
                records_compile.cmd_compile(completion, root)
                records_compile.cmd_verify(completion, root)
    except (records_compile.CompileError, ValueError, OSError) as error:
        return "regeneration-mismatch", str(error), False
    return None, None, False


# --- the seal: per-slot manifests and the chained ledger (§2.9) -------------

def _entry_type(mode: int) -> str:
    """The type marker a non-regular entry is sealed by — `batch.py`'s markers,
    string for string, because the driver writes the seal this recomputes
    (round 7, finding 3)."""
    for predicate, marker in MANIFEST_TYPE_MARKERS:
        if predicate(mode):
            return marker
    return "other"


def manifest_files(slot: str) -> list:
    """§2.9's sorted list, recomputed over the slot ROOT and EVERY entry beneath
    it: a regular file as `[relative path, byte length, bare sha256 hex]`, and
    every other entry — a symlink, a directory, a FIFO, a socket, a device — as
    `[relative path, NON_FILE_LENGTH, "type:<marker>"]`.

    **Round 8, finding 4: the root is an entry too, at path `.`.** Round 7's fix
    walked only what lay BENEATH the slot, and the `run-NNN` directory itself
    was never `lstat`ed — so the whole of it could be evaded one level up.
    Renaming a sealed slot and planting a symlink at its old path leaves every
    entry this list covers byte-identical through the link: `verify_seal()`
    returned None, and §3.3's lstat-first rule then scored the slot
    `slot-symlink` and moved it out of `V_X` into `I_X` with `sealed` still
    true. That is the denominator change §2.9 registers as the one thing a
    post-seal alteration must not buy, taken at the one path round 7 left
    unsealed. The root's own `lstat` type is now a row of the list, so the move
    is a manifest discrepancy and the consequence is the WHOLE batch's (C5 rule
    6). No entry beneath the root can forge that row: `os.path.relpath` of a
    child is never `.`.

    **Round 7, finding 3: every entry, not every regular file.** Both manifest
    implementations omitted non-regular entries, so a symlink ADDED after the
    seal left this list recomputing exactly as written and `verify_seal()`
    returning None — and then §3.3's lstat-first rule scored that slot
    `slot-symlink`, moving it out of `V_X` into `I_X` with the batch still
    `sealed`. That is exactly the denominator change §2.9 registers as the one
    thing a post-seal alteration must not be able to buy: "It is *not* handled
    by moving the slot into `V_X`'s complement". With every entry sealed, the
    addition is a manifest discrepancy, and §2.9's consequence for one of those
    is the WHOLE batch's — every level verdict `UNRESOLVED-BY-DESIGN`, no
    contrast reported (C5 rule 6).

    `SLOT-MANIFEST.json` is excluded from its own list — a file cannot carry its
    own digest — and is sealed instead by the ledger, which records the digest of
    the manifest FILE. `os.walk` does not descend into symlinked directories, so
    a link cannot smuggle a subtree into the seal: the link is one typed row and
    the tree it points at is not the slot's. Every type is decided by `lstat` and
    only regular files are opened, so a FIFO is sealed rather than read — an
    `open()` on one would block the whole scoring.

    This is `batch.py`'s `slot_files()` recomputed rather than re-specified: the
    driver writes the seal and the scorer checks it, and the study has one
    manifest convention rather than two that happen to agree.
    """
    rows = [[SLOT_ROOT_ENTRY, NON_FILE_LENGTH,
             "type:%s" % _entry_type(os.lstat(slot).st_mode)]]
    for base, directories, names in os.walk(slot):
        directories.sort()
        for name in sorted(directories + names):
            path = os.path.join(base, name)
            relative = os.path.relpath(path, slot)
            if relative == MANIFEST_FILE:
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


def manifest_digest(files: list) -> str:
    """§2.9's "sha256 of that sorted list", in the encoding this study already
    uses for a manifest: one `<path> <bytes> <sha256>` line per file, sorted,
    newline-terminated. That is `harness/integrity.py`'s tree-manifest line for
    line (§2.10's whole-tree manifest) and `batch.py`'s `files_digest()`, so a
    reader who can recompute one can recompute the others.

    A non-regular entry's row encodes in the same three fields (round 7,
    finding 3): `<path> -1 type:<marker>`. §2.10's whole-tree manifest is over
    git-tracked regular files and never produces one; a slot tree can hold
    anything, and the seal has to be able to say so."""
    listing = "\n".join("%s %d %s" % tuple(row) for row in sorted(files)) + "\n"
    return "sha256:" + hashlib.sha256(listing.encode("utf-8")).hexdigest()


def verify_seal(slot: str, ledger_record: dict) -> str:
    """None when this slot's seal holds, else the discrepancy in one sentence.

    §2.9's registered consequence is NOT a refusal code: a slot whose recomputed
    manifest disagrees with the ledger invalidates confirmatory scoring for the
    WHOLE batch (§3.3, C5 rule 6), because a code that moved one slot out of
    `V_X` would hand an alteration precisely the denominator change that
    produces the verdict it was made to produce. So this returns a sentence and
    the caller decides what the batch's verdicts are worth.

    Three bindings, because the seal is three artifacts: the slot's bytes must
    recompute to the manifest's list, the list must recompute to the manifest's
    own `filesSha256`, and the ledger's `manifestSha256` must be the digest of
    the manifest FILE — which is what carries the first two into the chain.

    The recomputed list covers the slot ROOT (round 8, finding 4) and every
    ENTRY beneath it (round 7, finding 3), so an addition to a sealed slot —
    or a rename of the slot with a symlink planted at its old path — fails the
    first binding. Before those two, each of them in turn passed all three
    bindings and then bought that slot a `slot-symlink` code and the
    denominator change it carries, with `sealed` still true.
    """
    path = os.path.join(slot, MANIFEST_FILE)
    if not _regular(path):
        return ("%s is missing or not a regular file: an unsealed slot cannot be "
                "shown to be the slot the ledger recorded" % MANIFEST_FILE)
    try:
        manifest = load_json(path)
    except ValueError as error:
        return "%s is not duplicate-free JSON: %s" % (MANIFEST_FILE, error)
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list):
        return "%s is not a manifest object with a files list" % MANIFEST_FILE
    try:
        recomputed = manifest_files(slot)
    except OSError as error:
        return "the slot tree cannot be re-read to recompute its manifest: %s" % error
    if [list(row) for row in manifest["files"]] != recomputed:
        return ("the recomputed file list does not match %s: the slot's bytes are "
                "not the bytes it was sealed over" % MANIFEST_FILE)
    computed = manifest_digest(recomputed)
    if manifest.get("filesSha256") != computed:
        return ("%s records list digest %r and its own list recomputes to %s"
                % (MANIFEST_FILE, manifest.get("filesSha256"), computed))
    sealed = file_digest(path)
    if ledger_record.get("manifestSha256") != sealed:
        return ("the ledger records manifest %r for this slot and %s hashes to %s"
                % (ledger_record.get("manifestSha256"), MANIFEST_FILE, sealed))
    return None


def ledger_record_digest(record: dict) -> str:
    """The digest one ledger record contributes to the next one's
    `previousSha256`: sha256 over the record's canonical JSON — sorted keys, no
    insignificant whitespace — with the record's own `previousSha256` member
    INCLUDED, which is what makes `BATCH.json` a hash chain over the batch in
    schedule order rather than a list of independently digested lines (§2.9).

    A record is a structure and not a file, so the bytes being digested have to
    be defined somewhere, once, in a form both the driver and the scorer
    reproduce exactly. `batch.py`'s `_canonical()` is that definition and this is
    it recomputed."""
    body = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(body).hexdigest()


def verify_chain(records: list) -> str:
    """None when the ledger's hash chain verifies, else the first break.

    The first record links to `null`: there is nothing before it, and a genesis
    constant would be one more registered byte string with nothing to say.
    Registered honestly, because a hash chain in the same tree is not a
    transparency log: the operator can recompute the whole chain. What it
    establishes is that a slot was not altered IN ISOLATION or after the ledger
    was published; it does not establish that the ledger was written honestly,
    and §7 lists it under "recorded, not proven" in those words.
    """
    previous = None
    for index, record in enumerate(records):
        if record.get("previousSha256") != previous:
            return ("ledger record %d (%r) links to %r and the record before it "
                    "digests to %r: the chain does not verify"
                    % (index + 1, record.get("slot"),
                       record.get("previousSha256"), previous))
        previous = ledger_record_digest(record)
    return None


# --- cross-slot session uniqueness (§3.3 `session-reused`) ------------------

def session_identity(session_path: str):
    """The session id the transcript records for itself, or None.

    `session_meta` is metadata the transcript checker skips — no conversation
    content reaches the model through it — but it is exactly the right evidence
    here: it names the session, and two slots naming one session are one call
    however their directories are named. Ported from 011's `batch.py`, which
    applied it to the two capture slots; §3.3 applies it to all 150, and
    `batch.py` imports it from here so one definition serves both.
    """
    with open(session_path, "rb") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            entry = json.loads(raw.decode("utf-8"),
                               object_pairs_hook=_refuse_duplicate_keys)
            if not isinstance(entry, dict) or entry.get("type") != "session_meta":
                continue
            payload = entry.get("payload")
            if isinstance(payload, dict):
                for key in ("id", "session_id"):
                    if isinstance(payload.get(key), str) and payload[key]:
                        return payload[key]
    return None


def call_identity_defect(call: dict):
    """The sentence naming the first `CALL.json` identity member this scorer
    cannot read, or None when all three are readable.

    Round 5, finding 6. §3.3 registers the identifying members of `CALL.json` —
    working directory, isolated home, start clock — as the raw evidence of which
    call produced a slot, and the wrapper writes all three as strings. A slot
    recording one of them as a list or an object is malformed evidence, and it
    was previously discovered by HASHING it: `session_reuse()` put the value in
    a dict key and a `startedAt: []` raised `TypeError: unhashable type: 'list'`
    out of a population-level pass that has no per-slot catch, ending the
    scoring of every other slot.

    The registered code for that slot is `call-unreadable` and NOT
    `scorer-error`, and §3.3 is why. `call-unreadable` is this study's code for a
    `CALL.json` the scorer cannot read as a call record — the file, and the
    reading of it, are exactly what is wrong here. `scorer-error` is §7's
    totality rule, ported unchanged from 011 §3.3: "an unexpected exception
    during one slot's ADMISSION becomes that slot's recorded verdict". This
    exception was not raised during that slot's admission — it was raised before
    any slot was admitted — and it is no longer unexpected: it is an anticipated
    shape of a named file, checked before anything can hash it. Recording it as
    `scorer-error` would file an anticipated malformation under the code
    registered for the ones nobody anticipated.

    Round 6, finding 5: PRESENT and a string, not "a string if it is there". The
    check read `call.get(member)` and exempted `None`, which is both an absent
    member and a JSON `null` — so a slot whose `startedAt` the wrapper never
    wrote, or wrote as `null`, passed the guard, and no later gate owns it
    (`model`, `binarySha256`, `pinsSha256` and the rest each own their own
    member; nothing else reads `startedAt` for admission at all). The exemption
    was not a weaker version of the registered rule but a hole in it: §3.3
    registers these three as "the identifying members of its `CALL.json`
    (working directory, isolated home, start clock)" and as evidence a copied
    slot cannot agree with itself over — and an ABSENT member agrees with every
    other absent one, so two slots stripped of the same member would have been
    compared on nothing and found distinct. The wrapper writes all three
    whenever it writes a `CALL.json` at all, so an honest slot never reaches
    this; a slot that does is one whose own identity cannot be read.
    """
    for member in CALL_IDENTITY_MEMBERS:
        if member not in call:
            return ("CALL.json records no %s, and §3.3's identifying members — "
                    "working directory, isolated home, start clock — are the "
                    "strings the wrapper wrote: a call record that omits one is "
                    "not evidence of which call produced this slot, and an "
                    "absent member agrees with every other absent one" % member)
        if not isinstance(call[member], str):
            return ("CALL.json records %s as %r, and §3.3's identifying members "
                    "are the strings the wrapper wrote: a call record whose own "
                    "identity cannot be read is not evidence of which call "
                    "produced this slot" % (member, call[member]))
    return None


def slot_identity(slot: str) -> dict:
    """The raw retained evidence of WHICH call produced this slot, or None when
    the slot cannot be read far enough to say. A slot that cannot be read is
    already refused by an earlier code; it is not additionally accused of
    sharing a session it never produced.

    A malformed identity member costs this slot its `callIdentity` and NOTHING
    else (round 5, finding 6): the retained session bytes and the session id are
    still published to the population's uniqueness check, so a copy of a slot
    whose `CALL.json` is malformed is still caught by the two members that are
    readable. `admit()` refuses the slot itself `call-unreadable`.

    Round 6, finding 5: `callIdentity` is now three strings or nothing. The
    all-`None` tuple this used to fold back to `None` was the shape an absent
    member produced, and `call_identity_defect()` no longer lets one through —
    so that fold is a branch no call can take, and a check that can never fire
    is removed rather than kept as decoration.

    **Round 7, finding 5: the raw digest is computed FIRST and unconditionally,
    and a parse failure nulls the parsed members alone.** The digest and the two
    parses used to share one `try`, so a malformed `session.jsonl` — or a
    `CALL.json` with duplicate keys — discarded the one member that needs no
    parser at all, and two slots holding byte-identical malformed sessions were
    each scored `transcript-refused` rather than the second one `session-reused`.
    §3.3 registers the code on "the slot's `session.jsonl` BYTES, session id, or
    the identifying members of its `CALL.json`", and bytes are readable whether
    or not they are JSON.

    The registered precedence is §3.3's own table order, which `admit()`
    evaluates in: `session-reused` sits above `transcript-refused` in it, and
    `admit()` returns `session-reused` before the transcript binding is run at
    all. So a copied slot whose transcript would also refuse is named a copy —
    the more exact statement about why it is out of the denominator, and the one
    a reader can act on. A slot this cannot read far enough to identify is
    already refused by an earlier code and is not additionally accused.
    """
    session = os.path.join(slot, "session.jsonl")
    call_path = os.path.join(slot, "CALL.json")
    links, irregular = slot_irregularities(slot)
    if links or irregular or not _regular(call_path) or not _regular(session):
        return None
    try:
        identity = {"sessionSha256": file_digest(session),
                    "sessionId": None, "callIdentity": None}
    except OSError:
        # The bytes cannot be read at all, so this slot has no raw evidence to
        # be compared with anyone's. `admit()` refuses it on its own account.
        return None
    try:
        identity["sessionId"] = session_identity(session)
    except (ValueError, OSError):
        # A transcript that is not parseable JSON has no session id to publish,
        # and `admit()` refuses the slot `transcript-refused` on its own
        # account. Its BYTES are still published above.
        pass
    try:
        call = load_json(call_path)
    except (ValueError, OSError):
        call = None
    # A CALL.json that is not an object has no members at all, and `admit()`
    # already refuses it `call-unreadable`; reading `.get` off it here would
    # raise an AttributeError out of the same population-level pass.
    if isinstance(call, dict) and call_identity_defect(call) is None:
        identity["callIdentity"] = tuple(call[member]
                                         for member in CALL_IDENTITY_MEMBERS)
    return identity


def session_reuse(ordered: list) -> dict:
    """{slot key: detail} for every slot that shares raw call evidence with an
    EARLIER slot in schedule order (§3.3, C5 rule 6).

    `ordered` is [(key, slot path)] in the ledger's global-index order, so "the
    later one" is the later one on the registered schedule and not the later one
    in a directory listing. Cross-slot uniqueness is checked over the whole
    population, in every arm, before any rate is computed: a copied slot would
    otherwise add a covered run to a denominator.
    """
    seen: dict = {}
    reused: dict = {}
    for key, slot in ordered:
        identity = slot_identity(slot)
        if identity is None:
            continue
        for member, prose in SESSION_IDENTITY:
            value = identity[member]
            if value is None:
                continue
            earlier = seen.get((member, value))
            if earlier is not None and key not in reused:
                reused[key] = (
                    "this slot and %s share %s (%r): two slots holding one call's "
                    "evidence are one call however their directories are named, and "
                    "the later one on the registered schedule is the one that leaves "
                    "the denominator" % (earlier, prose, value))
            seen.setdefault((member, value), key)
    return reused


# --- scoring ---------------------------------------------------------------

def batch_refusal_code(slot: str):
    """The code the batch recorded for this slot, or None when it recorded no
    refusal at all.

    Every read of REFUSAL.json goes through this, and through the
    duplicate-key-rejecting loader: a shadowed `code` member cannot mean one
    thing here and another to a reader. A file that exists and is not a JSON
    object, or carries no code, or carries a code that is not a string, is
    MALFORMED refusal evidence and raises — score_run() turns that into the
    slot's own pipeline-invalid verdict.
    """
    path = os.path.join(slot, "REFUSAL.json")
    if not os.path.exists(path):
        return None
    record = load_json(path)
    if not isinstance(record, dict):
        raise ValueError("REFUSAL.json is not a JSON object")
    code = record.get("code")
    if not isinstance(code, str) or not code:
        raise ValueError("REFUSAL.json records code %r, not a refusal code" % (code,))
    return code


def _duration(call: dict):
    """§4.6 S8's per-slot wall clock, as a DURATION in seconds derived from the
    retained UTC stamps — never a timestamp.

    011 kept the clock out of `RESULTS.json` entirely so that two scorings of
    one slot tree are byte-identical; §4.6 registers the wall clock as a
    secondary here, so the property is preserved the only way it can be: a
    duration is a fact about retained bytes and a timestamp is a fact about when
    someone looked. Nothing in this file reads a clock.
    """
    started, ended = call.get("startedAt"), call.get("endedAt")
    if not isinstance(started, str) or not isinstance(ended, str):
        return None
    try:
        return _epoch(ended) - _epoch(started)
    except ValueError:
        return None


def _epoch(stamp: str) -> int:
    """Seconds since 1970-01-01 for a `YYYY-MM-DDTHH:MM:SSZ` stamp, by
    arithmetic rather than by a library that consults a timezone database. The
    wrapper writes UTC and nothing else; a stamp in any other shape raises and
    the duration is published as null."""
    if len(stamp) != 20 or stamp[4] != "-" or stamp[7] != "-" \
            or stamp[10] != "T" or stamp[13] != ":" or stamp[16] != ":" \
            or stamp[19] != "Z":
        raise ValueError("%r is not a UTC stamp" % stamp)
    year, month, day = int(stamp[0:4]), int(stamp[5:7]), int(stamp[8:10])
    hour, minute, second = int(stamp[11:13]), int(stamp[14:16]), int(stamp[17:19])
    # Days from the civil epoch, Howard Hinnant's shift-to-March algorithm: no
    # table, no locale, exact for every proleptic Gregorian date.
    year -= month <= 2
    era = (year if year >= 0 else year - 399) // 400
    year_of_era = year - era * 400
    day_of_year = (153 * (month + (-3 if month > 2 else 9)) + 2) // 5 + day - 1
    day_of_era = year_of_era * 365 + year_of_era // 4 - year_of_era // 100 + day_of_year
    days = era * 146097 + day_of_era - 719468
    return ((days * 24 + hour) * 60 + minute) * 60 + second


def score_run(slot: str, arm: str, arms_root: str, golden_path: str, pins: dict,
              arm_definition: dict, scheduled: dict, ledger_record: dict,
              reuse_detail: str = None, registry_sha256: str = None) -> tuple:
    """(row, accepted records in compiler order) for one slot: valid or not,
    and — when valid — its coverage under BOTH its own arm's family and, for
    S10, arm A's.

    The records are returned beside the row rather than inside it: `RESULTS.json`
    publishes the row, and the census (§4.5) needs the records. Returning them
    is what keeps the census and the rates on one derivation of one population.
    """
    name = os.path.basename(slot)
    batch_code = None
    try:
        code, detail, empty = admit(slot, arm, arms_root, golden_path, pins,
                                    arm_definition, scheduled, ledger_record,
                                    reuse_detail, registry_sha256)
        # §7 totality: the refusal record is read INSIDE the total path, and
        # only from a slot whose tree is regular files and directories. A
        # symlinked REFUSAL.json is not this slot's refusal evidence, and the
        # link already refused the slot with its own code; a FIFO named
        # REFUSAL.json would block the whole scoring instead of refusing a slot.
        if code not in ("slot-symlink", "slot-irregular"):
            batch_code = batch_refusal_code(slot)
    except Exception as error:  # noqa: BLE001 — totality is the point
        # §7: a malformed or missing slot artifact yields a recorded verdict,
        # never a bare exception that stops the scoring of every other slot.
        code, detail, empty = "scorer-error", "%s: %s" % (type(error).__name__, error), False
    if batch_code is not None and code is None:
        code, detail, empty = "refusal-conflict", (
            "the batch recorded %r but the retained bytes admit the run" % batch_code), False
    row = {"arm": arm, "slot": name, "globalIndex": scheduled["globalIndex"],
           "round": scheduled["round"], "position": scheduled["position"],
           "valid": code is None, "code": code, "detail": detail,
           "batchCode": batch_code, "wallClockSeconds": None}
    # S8's duration, read only from a slot whose tree admission has already
    # found to be regular files and directories: a CALL.json reached through a
    # link is not this slot's record, and a FIFO would block.
    call_path = os.path.join(slot, "CALL.json")
    if code not in ("slot-symlink", "slot-irregular") and _regular(call_path):
        try:
            row["wallClockSeconds"] = _duration(load_json(call_path))
        except (ValueError, OSError):
            row["wallClockSeconds"] = None
    if code is not None:
        return row, []
    completion = os.path.join(slot, "completion.txt")
    if empty:
        accepted, ledger = {}, []
    else:
        raw = records_compile.read_completion(completion)
        accepted, ledger, _ = records_compile.compile_records(raw)
    drops: dict = {}
    for _, case_id, drop in ledger:
        if not case_id:
            drops[drop] = drops.get(drop, 0) + 1
    high, quarantine = split_records(accepted, arm_definition["tLow"],
                                     arm_definition["tHigh"])
    covered, raw_covered, q_reached, q_only = [], [], [], []
    members = {}
    for entry in arm_definition["classes"]:
        index = entry["index"]
        in_h = class_members(accepted, high, entry["predicate"])
        in_q = class_members(accepted, quarantine, entry["predicate"])
        if in_h:
            covered.append(index)
        if in_h or in_q:
            raw_covered.append(index)
        if in_q:
            q_reached.append(index)
        if in_q and not in_h:
            q_only.append(index)
        members[str(index)] = {"h": in_h, "q": in_q}
    # §4.6 S10: the same records, the same labels — this arm's mirror — keyed to
    # ARM A's family predicates. Class membership only: it asks where this arm's
    # records land in the BASELINE's coordinate system.
    old_edge = [entry["index"] for entry in arm_definition["oldEdgeClasses"]
                if class_members(accepted, high, entry["predicate"])]
    row.update({
        "accepted": len(accepted),
        "dropped": len(ledger) - len(accepted),
        "dropCodes": dict(sorted(drops.items())),
        "h": len(high), "q": len(quarantine),
        # §3.3's own row, and exactly that row (round 3, finding 13): the
        # partition reserves `authoring-empty` for a completion with NO
        # PARSEABLE ARRAY, and that is what this member counts.
        "authoringEmpty": empty,
        "noParseableArray": empty,
        # The wider quantity the narrowed member used to carry, published under
        # its own name so nothing is lost: this run reached NO class. Computed
        # from the covered set this scoring just derived and from nothing else
        # (round 4, finding 9) — `empty or not accepted or not high` asked
        # whether the run held any correctly labelled record at all, so a run
        # whose one correctly labelled record satisfies no class predicate
        # published `coveredClasses: []` beside `coveredNothing: false`. It is a
        # real authoring outcome and a reader wants it; it is not §3.3's
        # partition row, which is `authoringEmpty` above.
        "coveredNothing": not covered,
        "coveredClasses": covered,
        "rawClasses": raw_covered,
        "qClasses": q_reached,
        "qOnlyClasses": q_only,
        "oldEdgeClasses": old_edge,
        "classesCovered": len(covered),
        "classMembers": members,
        "completionSha256": file_digest(completion),
        "compiledSha256": None if empty else tree_digest(compiled_files(completion)),
    })
    return row, [accepted[case_id] for _index, case_id, _drop in ledger if case_id]


def collect_slots(root: str) -> tuple:
    """(slot paths in run order, unexpected entry names) for one arm's authoring
    tree. A slot is a directory named run-<digits>; anything else is reported,
    never scored.

    An entry named run-NNN is collected as a slot WHATEVER ITS TYPE — a
    directory, a symlink, a FIFO, a regular file. Skipping the ones that are not
    directories punched a hole in the indices and refused the whole scoring,
    where §3.3 wants the entry named: `admit()` scores it `slot-symlink`,
    `slot-irregular` or `slot-shape` on its first checks, so it enters no
    denominator and the other slots are still counted. The name is what claims
    the index, so the name is what has to answer for it.

    The contiguity rule that lived here in 011 has moved to C5 rule 4, which
    states it over the ledger's prefix rather than over whatever is on disk:
    §2.8's own text leaves arms holding R or R−1 slots after a partly completed
    round, so `1…R` from a round number was never the right range.

    An ABSENT root is an empty population, not a refusal (round 9, finding 4).
    The driver creates `arms/<X>/authoring/` with that arm's FIRST slot
    (`batch.py`'s `os.makedirs(slot, exist_ok=True)`), so an arm the registered
    prefix has not reached yet has no root at all: §2.8's round-1 order is B, C,
    A, D, E, and a prefix shorter than five leaves 5−k roots uncreated. Refusing
    them made §2.8's own descriptive publication unreachable for exactly the
    prefixes [D-21] is most obviously about — a batch that dies in round 1.
    The tolerance is not free: `check_population()` validates it against the
    declared shortfall and the prefix's own per-arm counts (C5 rules 2 and 4).
    `lexists`, not `exists`: a DANGLING symlink at the authoring root is
    something that was created and broken, not an arm never reached, and it
    still refuses; a symlink to a real directory keeps its old behaviour,
    because `isdir` follows.
    """
    if not os.path.isdir(root):
        if os.path.lexists(root):
            raise ScoreError("%s is not a directory" % root)
        return [], []
    slots, unexpected = [], []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        parts = name.split("-", 1)
        if len(parts) == 2 and parts[0] == "run" and parts[1].isdigit():
            slots.append(path)
        else:
            unexpected.append(name)
    return slots, unexpected


def _range_block(rows: list, member: str) -> dict:
    """S4's per-run range for one count: min, max and mean over the rows given,
    all None when there are none. Integers in, one mean out — no interval, and
    no rate: these are volumes, not proportions.

    `trials` is the number of rows that carried the member at all, published
    because S8's wall clock is defined only "over the slots that reached the
    call" and a mean over an unnamed denominator is a mean over nothing."""
    values = [row[member] for row in rows if row.get(member) is not None]
    return {"min": min(values) if values else None,
            "max": max(values) if values else None,
            "mean": sum(values) / len(values) if values else None,
            "trials": len(values)}


def _sequence_halves(sequence: list) -> dict:
    """S7: the ordered 0/1 sequence over the arm's scheduled slots in round
    order, split in half. A drift check, published rather than tested — no trend
    statistic is registered."""
    half = len(sequence) // 2
    return {"sequence": sequence,
            "firstHalf": sum(sequence[:half]),
            "secondHalf": sum(sequence[half:])}


def verify_preconditions(pins_path: str, arms_root: str, golden_path: str,
                         study: str = STUDY) -> dict:
    """Everything that must hold before a single slot is read (§6 C1, §2.10,
    §3.2). A drifted port, an unregistered interpreter, an unregistered mirror,
    an unregistered arm artifact, a schedule the registry does not agree with,
    an unregistered golden capture, or an unregistered or post-freeze-edited
    preregistration refuses the whole scoring — none of them can be discovered
    afterwards from a published rate."""
    try:
        ported = integrity.verify(study=study)
    except integrity.IntegrityError as error:
        raise ScoreError("the ported bytes are not the registered ones: %s" % error)
    pins = load_json(pins_path)
    # §2.2 [D-14]: ONE mirror module serves all five arms. `integrity.verify()`
    # binds it to its registered destination digest already; it is re-derived
    # here because the cell publishes it and a published digest the scorer did
    # not compute is a digest copied from the registry.
    mirror_pin = pins.get("mirror", {}).get("sha256")
    mirror_digest = file_digest(REGISTERED_MIRROR)
    if not mirror_pin or mirror_digest != mirror_pin:
        raise ScoreError("harness/policy_mirror.py is %s and harness/PINS.json "
                         "registers %r: the arbiter of every arm's labels is a "
                         "registered artifact (§2.2 [D-14])"
                         % (mirror_digest, mirror_pin))
    # §2.8: the registered call order is an artifact of this preregistration AND
    # a member of the registry, and the two must be the same order. The registry
    # carries the same two facts this module encodes — the Williams first row and
    # the three block orders — and requiring them to agree is what stops either
    # one moving alone.
    order_pin = pins.get("batch", {}).get("order")
    if not isinstance(order_pin, dict):
        raise ScoreError("harness/PINS.json registers no batch.order: §2.8's call "
                         "order is a registry member and a scoring cannot check a "
                         "ledger against an order it does not have")
    if list(order_pin.get("firstRow") or ()) != list(WILLIAMS_FIRST_ROW):
        raise ScoreError("harness/PINS.json's Williams first row is %r and §2.8's is %r"
                         % (order_pin.get("firstRow"), list(WILLIAMS_FIRST_ROW)))
    if [list(block) for block in order_pin.get("blocks") or ()] \
            != [list(block) for block in BLOCKS]:
        raise ScoreError("harness/PINS.json's block orders are not §2.8's")
    schedule = registered_schedule()
    per_arm = {arm: sum(1 for entry in schedule if entry["arm"] == arm)
               for arm in ARMS}
    if len(set(per_arm.values())) != 1:
        raise ScoreError("the registered call order does not give every arm the same "
                         "number of slots: %r" % per_arm)
    registered_n = pins.get("batch", {}).get("n")
    if registered_n != per_arm[ARMS[0]]:
        raise ScoreError("harness/PINS.json registers N = %r per arm and §2.8's call "
                         "order schedules %d" % (registered_n, per_arm[ARMS[0]]))
    if pins.get("batch", {}).get("slots") != len(schedule):
        raise ScoreError("harness/PINS.json registers %r slots and §2.8's call order "
                         "expands to %d"
                         % (pins.get("batch", {}).get("slots"), len(schedule)))
    arm_pins = pins.get("arms")
    if not isinstance(arm_pins, dict) or sorted(arm_pins) != sorted(ARMS):
        raise ScoreError("harness/PINS.json pins the arms %r, not the registered %r"
                         % (sorted(arm_pins) if isinstance(arm_pins, dict) else arm_pins,
                            list(ARMS)))
    if not os.path.isfile(golden_path):
        raise ScoreError("no golden context at %s: recapture it before the batch "
                         "(batch.py capture --scratch-parent DIR)" % golden_path)
    # §3.2 step 2: the capture's digest replaces the null in the registry, and
    # both are committed BEFORE the first round runs. A golden file that is not
    # the registered one — including one derived after the batch from the batch's
    # own slots — scores nothing.
    golden_pin = pins.get("golden", {}).get("sha256")
    if not golden_pin:
        raise ScoreError(
            "harness/PINS.json registers no golden.sha256: the golden capture must be "
            "captured, registered and committed before the first round (§3.2)")
    golden_digest = file_digest(golden_path)
    if golden_digest != golden_pin:
        raise ScoreError("the golden capture at %s is %s, not the registered %s"
                         % (golden_path, golden_digest, golden_pin))
    # §2.10: the freeze digest is not optional at scoring time. Skipping this
    # check while the pin is null would let the registry be merged with its null
    # intact and no rate would ever notice. The path is structural —
    # PREREGISTRATION.md at the study root — so the registry pins the digest and
    # not a path a registry could redirect.
    prereg_pin = pins.get("freeze", {}).get("preregistrationSha256")
    if not prereg_pin:
        raise ScoreError(
            "harness/PINS.json registers no freeze.preregistrationSha256: this "
            "file's digest at the freeze must replace the null before any rate is "
            "computed, or a post-freeze edit would be undetectable (§2.10)")
    prereg_path = os.path.join(study, "PREREGISTRATION.md")
    if not os.path.isfile(prereg_path):
        raise ScoreError("the preregistration is missing from %s" % study)
    prereg_digest = file_digest(prereg_path)
    if prereg_digest != prereg_pin:
        raise ScoreError("PREREGISTRATION.md is %s, not the %s registered at the "
                         "freeze: it was edited after the freeze"
                         % (prereg_digest, prereg_pin))
    # §6 C7, re-checked here for the same reason the freeze and the golden are:
    # none of it can be discovered afterwards from a published rate. The driver
    # refuses a batch whose control never ran (round 9, finding 3); a rate could
    # still be published over a study whose control record was removed after the
    # batch, and §7 promises the record among the published artifacts. The path
    # is the canonical one and `context.json` is NOT required — a `no-context`
    # verdict is a registered outcome and leaves none.
    c7_assent = pins.get("isolationNegative", {}).get("assent")
    if c7_assent != "granted":
        raise ScoreError(
            "harness/PINS.json records isolationNegative.assent %r: §6 C7 runs "
            "before the batch and the registry records the assent it ran under, "
            "so no rate is computed while it is unrecorded" % (c7_assent,))
    c7_path = os.path.join(REGISTERED_ISOLATION_NEGATIVE, "VERDICT.json")
    c7_relative = os.path.relpath(c7_path, study)
    if not os.path.isfile(c7_path):
        raise ScoreError("no §6 C7 record at %s: the isolation negative control "
                         "runs once, before the batch, and its verdict is among "
                         "the artifacts §7 publishes" % c7_relative)
    try:
        c7 = load_json(c7_path)
    except ValueError as error:
        raise ScoreError("%s cannot be read as duplicate-free JSON (%s): §6 C7's "
                         "verdict is read, not taken on trust" % (c7_relative, error))
    if not isinstance(c7, dict):
        raise ScoreError("%s is a %s and §6 C7's verdict is an object"
                         % (c7_relative, type(c7).__name__))
    if c7.get("outcome") not in C7_OUTCOMES:
        raise ScoreError("%s records outcome %r and §6 C7 registers %r"
                         % (c7_relative, c7.get("outcome"), list(C7_OUTCOMES)))
    if c7.get("assent") != c7_assent:
        raise ScoreError("%s: the control was authorized by %r and the registry "
                         "records %r: the record is not this study's"
                         % (c7_relative, c7.get("assent"), c7_assent))
    if c7.get("goldenSha256") != golden_digest:
        raise ScoreError("%s: the control was compared against golden capture %r "
                         "and this population was scored against %s: C7 "
                         "demonstrates the power of the gate these slots ran "
                         "behind (§3.2, §6 C7)"
                         % (c7_relative, c7.get("goldenSha256"), golden_digest))
    arms = {}
    for arm in ARMS:
        arms[arm] = load_arm(arms_root, arm, arm_pins[arm])
    # §4.6 S10 / §4.1: every arm keeps its own family for its own classes, and
    # takes arm A's for the cross-scoring. The baseline's predicates are read
    # once and shared, so no arm can be cross-scored against a different A.
    for arm in ARMS:
        arms[arm]["oldEdgeClasses"] = arms[BASELINE_ARM]["classes"]
    return {"portedFiles": ported["portedFiles"],
            "study010LockSha256": ported.get("study010LockSha256"),
            "mirrorSha256": mirror_digest,
            "goldenSha256": golden_digest,
            "preregistrationSha256": prereg_digest,
            "registeredN": registered_n,
            "schedule": schedule,
            "arms": arms}


def _declares_no_slot_ran(shortfall) -> bool:
    """§2.8's declaration over the EMPTY prefix, exactly as
    `batch.declare_shortfall()` writes it when the ledger holds no record: zero
    rounds, zero through global index zero, zero slots, and no last slot and no
    clock to name. A batch that died before global index 1 wrote no
    `BATCH.json` — the driver writes it inside the run loop, after a slot — so
    requiring the file would make §2.8's own descriptive publication
    unreachable for the one prefix it is most obviously about.

    The bool exclusion is the house rule the ledger's own type checks use
    (round 8, finding 9): JSON `false` is an `int` in Python and must not
    satisfy `== 0`, or a declaration that says `"completedSlots": false` would
    be read as a declaration that no slot ran."""
    if not isinstance(shortfall, dict):
        return False
    for member in ("completedRounds", "completedThroughGlobalIndex",
                   "completedSlots"):
        value = shortfall.get(member)
        if isinstance(value, bool) or not isinstance(value, int) or value:
            return False
    return all(shortfall.get(member) is None
               for member in ("lastSlot", "lastSlotEndedAt",
                              "lastSlotEndedAtFrom"))


def load_ledger(arms_root: str, shortfall: dict = None,
                present: int = None) -> list:
    """§2.9's append-only chained ledger, as a list of records in file order.
    Read before any slot, because C5 rules 2-5 are questions about the ledger
    and the slot set together.

    `shortfall` and `present` are §2.8's declaration and the count of slots on
    disk, and they exist for one case (round 9, finding 4): the batch that died
    before its first slot finished has no `BATCH.json` at all, because the
    driver writes the ledger inside the run loop. That population is admitted
    as an empty one ONLY when no slot is present and the declaration records
    that no slot ran — `terminality()` has already refused the two neighbouring
    cases, a complete batch that also declares and an over-full one, so by the
    time `present == 0` reaches here a declaration is guaranteed to exist. The
    defaults keep the single-argument call a refusal, which is what a caller
    holding no declaration is entitled to.

    Every record is TYPE-CHECKED here, at the read (round 6, finding 8). C5
    registers that a malformed ledger refuses the whole scoring through the
    registered path, and this function checked only that `records` was a list:
    `{"records": [null]}` reached `schedule_key()`, which called `.get` on
    `None`, and the scoring ended in a bare `AttributeError` — `main()` catches
    `ScoreError` and nothing else, so the operator got a traceback where the
    registration promises a refusal, and a reader of the exit could not tell a
    malformed ledger from a crashed scorer. The four members checked are the
    ones §3.3 and C5 rules 2-4 compare a slot on; `path` and `slot` are checked
    against the registered order in `check_population()`, which can say what
    they should have been and is where their refusals belong.

    Round 7, finding 6: the READ itself refuses too. A `BATCH.json` that is not
    JSON, or that shadows a member with a duplicate key, raised the loader's
    bare `ValueError` out of a `main()` that catches `ScoreError` and nothing
    else — a traceback where C5 registers a refusal, and no way for a reader of
    the exit status to tell a malformed ledger from a crashed scorer.
    """
    path = os.path.join(arms_root, LEDGER_FILE)
    if not os.path.isfile(path):
        if present == 0 and _declares_no_slot_ran(shortfall):
            return []
        raise ScoreError("no ledger at %s: the population is the registered "
                         "schedule and the ledger is the record of what ran (§2.9, "
                         "C5)" % path)
    try:
        ledger = load_json(path)
    except (ValueError, OSError) as error:
        raise ScoreError(
            "%s cannot be read as duplicate-free JSON (%s): the population is read "
            "from this file before any slot, and a ledger that cannot be read "
            "cannot be compared with §2.8's registered order at all, so the whole "
            "scoring refuses (C5)" % (path, error))
    if not isinstance(ledger, dict) or not isinstance(ledger.get("records"), list):
        raise ScoreError("%s is not a ledger object with a records list" % path)
    for offset, record in enumerate(ledger["records"]):
        if not isinstance(record, dict):
            raise ScoreError(
                "%s's record %d is %r and a ledger record is a JSON object: the "
                "population is read from this file before any slot, and a record "
                "that is not one cannot be compared with §2.8's registered order "
                "at all (C5 rules 2-4)" % (path, offset + 1, record))
        for member, kinds, name in LEDGER_RECORD_MEMBERS:
            if member not in record:
                found = "records no %s" % member
            elif isinstance(record[member], bool) \
                    or not isinstance(record[member], kinds):
                found = "records %s as %r" % (member, record[member])
            else:
                continue
            raise ScoreError(
                "%s's record %d %s, and §2.9 registers it as %s: the ledger names "
                "each slot's place in §2.8's registered order, and a record that "
                "cannot be read there is a malformed ledger and refuses the whole "
                "scoring (C5)" % (path, offset + 1, found, name))
    return ledger["records"]


def terminality(arms_root: str, slots: dict, registered_total: int) -> dict:
    """§2.8's terminality rule, over the batch rather than over one arm: exactly
    the registered number of slots XOR a shortfall declaration whose recorded
    prefix is the slots actually present. Both, or neither, refuses — a
    shortfall over a full batch is not a short batch, and an over-full batch is
    not a population this study contemplates. The declaration's agreement with
    the ledger is C5 rule 5's, checked in `check_population()`.

    Round 7, finding 6: the declaration is READ here and TYPE-CHECKED here. A
    `SHORTFALL.json` that is not JSON raised the loader's bare `ValueError`, and
    one holding `[]` — not `None`, so every test below passed it through —
    reached `check_population()`'s `.get()` and raised `AttributeError`. C5
    registers a malformed population record as a refusal of the whole scoring
    through the registered path, and `main()` catches `ScoreError` alone, so
    both used to end in a traceback instead."""
    path = os.path.join(arms_root, SHORTFALL_FILE)
    try:
        shortfall = load_json(path) if os.path.isfile(path) else None
    except (ValueError, OSError) as error:
        raise ScoreError(
            "%s cannot be read as duplicate-free JSON (%s): §2.8's declaration is "
            "what makes a short batch terminal, and one that cannot be read "
            "declares nothing — the whole scoring refuses (C5 rule 5)"
            % (path, error))
    if shortfall is not None and not isinstance(shortfall, dict):
        raise ScoreError(
            "%s is %r and §2.8 registers a declaration object: the scoring compares "
            "its completed prefix with the ledger's slot for slot, and a "
            "declaration with no members to compare is not a declaration (C5 rule "
            "5)" % (path, shortfall))
    present = sum(len(paths) for paths in slots.values())
    complete = present == registered_total
    if complete and shortfall is not None:
        raise ScoreError("all %d registered slots are present and %s also declares a "
                         "short batch: the batch cannot be both"
                         % (registered_total, SHORTFALL_FILE))
    if not complete and shortfall is None:
        raise ScoreError("%d of %d registered slots are present and no %s declares "
                         "why: the batch is not terminal"
                         % (present, registered_total, SHORTFALL_FILE))
    if not complete and present > registered_total:
        raise ScoreError("%d slots are present but only %d were registered: a "
                         "shortfall declaration does not admit an over-full batch"
                         % (present, registered_total))
    return shortfall


def check_population(arms_root: str, slots: dict, ledger: list, schedule: list,
                     shortfall: dict) -> dict:
    """C5's rules 1-5, which refuse the whole scoring, and the bookkeeping the
    rest of the scoring runs on.

    Returns {slot key: (schedule entry, ledger record, path)} for every slot in
    the population, plus the ordered list of slot keys in registered call order.
    Rules 6 (the seal) and 7 (completeness) are NOT refusals: §2.9 and §2.8
    register both as `UNRESOLVED-BY-DESIGN` over the whole batch, with the
    descriptive surface still published, and `score()` computes them.
    """
    # Rule 1: every slot carries a terminal outcome. A slot the driver started
    # and never finished has neither the success path's CALL.json nor the
    # refusal path's REFUSAL.json, and no §3.3 code describes it honestly.
    # Decided by lstat, so a FIFO named CALL.json is not opened to find out.
    #
    # A slot whose tree already breaks the regular-files-and-directories rule is
    # SKIPPED here, not refused: it carries a terminal outcome — the scorer's
    # own `slot-symlink` or `slot-irregular` — and §3.3 registers those as
    # per-slot codes. Turning a dangling REFUSAL.json link into a whole-scoring
    # refusal would take the more exact of the two verdicts away.
    for arm in ARMS:
        for path in slots[arm]:
            links, irregular = slot_irregularities(path)
            if links or irregular:
                continue
            if not _regular(os.path.join(path, "CALL.json")) \
                    and not _regular(os.path.join(path, "REFUSAL.json")):
                raise ScoreError(
                    "arm %s's %s carries neither CALL.json nor REFUSAL.json: it is "
                    "not a terminal slot, and no rate is computed over a population "
                    "holding one (C5 rule 1)" % (arm, os.path.basename(path)))
    # Rule 3, checked before rule 2 because the bijection is stated AGAINST the
    # registered prefix: the ledger's (globalIndex, round, position, arm)
    # sequence is exactly a prefix of §2.8's call order, with no gap and no
    # reordering.
    if len(ledger) > len(schedule):
        raise ScoreError("the ledger holds %d records and §2.8's call order registers "
                         "%d slots" % (len(ledger), len(schedule)))
    for index, (record, entry) in enumerate(zip(ledger, schedule)):
        if schedule_key(record) != schedule_key(entry):
            raise ScoreError(
                "ledger record %d records %r and §2.8's registered call order assigns "
                "%r: the ledger is not a prefix of the registered order (C5 rule 3)"
                % (index + 1, schedule_key(record), schedule_key(entry)))
    prefix = schedule[:len(ledger)]
    # Rule 2: the ledger and the slot set are in bijection — one ledger record
    # per slot, one slot per record, at the path the record names.
    # The ledger's `path` is STUDY-relative, so the ledger is portable and the
    # population is not addressed by an absolute path one machine happens to
    # have. The scorer resolves it against the study root the canonical arms/
    # root sits in, and never against a root a caller supplied.
    study_root = os.path.dirname(arms_root)
    by_key: dict = {}
    for record, entry in zip(ledger, prefix):
        path = record.get("path")
        if not isinstance(path, str) or not path:
            raise ScoreError("ledger record %d names no slot path (C5 rule 2)"
                             % entry["globalIndex"])
        absolute = os.path.join(study_root, path)
        # `lexists`, not `isdir`: an entry named run-NNN that is a symlink, a
        # FIFO or a regular file IS a slot for bijection purposes, and §3.3
        # gives it `slot-symlink`, `slot-irregular` or `slot-shape` per slot.
        # Requiring a directory here would convert those registered per-slot
        # codes into a whole-scoring refusal.
        if not os.path.lexists(absolute):
            raise ScoreError(
                "the ledger records a slot at %s and no slot is there: a ledger "
                "record with no slot refuses the whole scoring rather than scoring "
                "that slot (C5 rule 2)" % path)
        name = "run-%03d" % entry["slotIndex"]
        expected = os.path.join(os.path.basename(arms_root), entry["arm"],
                                AUTHORING, name)
        if os.path.normpath(path) != expected:
            raise ScoreError(
                "the ledger puts global index %d at %s and the registered prefix puts "
                "arm %s's slot %d at %s (C5 rules 2 and 4)"
                % (entry["globalIndex"], path, entry["arm"], entry["slotIndex"],
                   expected))
        if record.get("slot") != name:
            raise ScoreError(
                "the ledger record for global index %d names slot %r and its own path "
                "is %s (C5 rule 2)"
                % (entry["globalIndex"], record.get("slot"), path))
        by_key[(entry["arm"], name)] = (entry, record, absolute)
    on_disk = {(arm, os.path.basename(path))
               for arm in ARMS for path in slots[arm]}
    missing = sorted(on_disk - set(by_key))
    if missing:
        raise ScoreError(
            "these slots have no ledger record: %s. A slot with no ledger record "
            "refuses the whole scoring rather than being scored (C5 rule 2)"
            % ", ".join("%s/%s" % key for key in missing))
    # Rule 4: each arm's slot indices are exactly the contiguous range 1…count_X,
    # where count_X is DERIVED from the prefix rather than from a round number —
    # §2.8's own text leaves arms holding R or R−1 slots after a partly completed
    # round, and a partly completed round satisfies neither `1…R` nor `1…R−1`.
    counts = {arm: sum(1 for entry in prefix if entry["arm"] == arm)
              for arm in ARMS}
    for arm in ARMS:
        # `collect_slots()` reads an ABSENT authoring root as an empty
        # population (round 9, finding 4), and this is where that tolerance is
        # validated rather than inferred: a missing root is admitted only when
        # a shortfall is declared AND the declared prefix derives no slot for
        # this arm. `counts` is the LEDGER's prefix, and rule 5 below pins that
        # prefix to the declaration slot for slot, so the pair is the strict
        # condition. A root deleted after the fact cannot pass here — its
        # ledger records still name paths that are gone and rule 2 above
        # refuses first, with the more exact per-slot message.
        if not os.path.isdir(slots_root(arms_root, arm)):
            if shortfall is None or counts[arm]:
                raise ScoreError(
                    "arm %s has no authoring/ root and the registered prefix derives %d "
                    "slot(s) for it%s: a missing root is an arm the prefix has not "
                    "reached, never an arm dropped from the population (C5 rules 2 and 4)"
                    % (arm, counts[arm], "" if shortfall is not None
                       else ", and no %s declares a short batch" % SHORTFALL_FILE))
        indexes = sorted(int(os.path.basename(path).split("-", 1)[1])
                         for path in slots[arm])
        if indexes != list(range(1, counts[arm] + 1)):
            raise ScoreError(
                "arm %s holds slot indices %r and the registered prefix derives the "
                "contiguous range 1..%d for it: a gap is a slot that was created and "
                "removed, and no rate is computed over a population with a hole in it "
                "(C5 rule 4)" % (arm, indexes, counts[arm]))
    # Rule 5: when a shortfall is declared, the declared prefix equals the
    # ledger's prefix, slot for slot — the global index it stops at, the slot it
    # names as last, and the count of slots present. §2.8 registers the
    # declaration as "the exact completed prefix of the registered schedule",
    # and three members is what that means when the prefix is not restated in
    # full: the same length, the same last slot, the same population size.
    if shortfall is not None:
        declared = shortfall.get("completedThroughGlobalIndex")
        if declared != len(ledger):
            raise ScoreError(
                "%s declares the completed prefix through global index %r and the "
                "ledger holds %d records: the declaration is not this batch's "
                "(C5 rule 5)" % (SHORTFALL_FILE, declared, len(ledger)))
        if ledger and ledger[-1].get("globalIndex") != declared:
            raise ScoreError(
                "%s declares global index %r and the ledger's last record is %r"
                % (SHORTFALL_FILE, declared, ledger[-1].get("globalIndex")))
        if ledger and shortfall.get("lastSlot") != ledger[-1].get("path"):
            raise ScoreError(
                "%s names %r as the last completed slot and the ledger's last record "
                "is %r (C5 rule 5)"
                % (SHORTFALL_FILE, shortfall.get("lastSlot"),
                   ledger[-1].get("path")))
        present = sum(len(paths) for paths in slots.values())
        if shortfall.get("completedSlots") != present:
            raise ScoreError(
                "%s records %r completed slots and %d are present: the declared "
                "prefix is not the slots actually present (C5 rule 5)"
                % (SHORTFALL_FILE, shortfall.get("completedSlots"), present))
    return {"byKey": by_key, "prefix": prefix, "counts": counts}


def score(arms_root: str, pins_path: str, golden_path: str,
          registry_sha256: str = None) -> dict:
    """The counting, with the registry of record either computed or supplied.

    `registry_sha256` is the LIBRARY override (§2.10, §7): it exists so the
    wrapper-driven harness tests, whose slots are stamped with a stand-in
    registry naming a stand-in binary, can say which registry their own slots are
    supposed to name. Whether it was used is recorded in `cell.registryOverride`,
    and this function has no way to publish anything: the writer is
    module-private and is called by `score_registered()` alone, on results it
    computed itself. The registered command calls `score_registered()`, which
    takes no path parameter at all ([D-23]).
    """
    override = registry_sha256
    if registry_sha256 is None:
        registry_sha256 = file_digest(REGISTRY_OF_RECORD)
    preconditions = verify_preconditions(pins_path, arms_root, golden_path)
    pins = load_json(pins_path)
    schedule = preconditions["schedule"]
    arms = preconditions["arms"]
    n = preconditions["registeredN"]

    slots, unexpected = {}, {}
    for arm in ARMS:
        slots[arm], unexpected[arm] = collect_slots(slots_root(arms_root, arm))
    # The declaration is read BEFORE the ledger (round 9, finding 4).
    # `terminality()` takes no ledger, so the order costs nothing and buys the
    # empty prefix its honest reading: a batch that died before global index 1
    # has no `BATCH.json`, and reading the ledger first made the operator see
    # "no ledger" — or, before `collect_slots()` learned the difference, "arms/A/
    # authoring is not a directory" — where §2.8 promises a descriptive batch.
    shortfall = terminality(arms_root, slots, len(schedule))
    ledger = load_ledger(arms_root, shortfall,
                         sum(len(paths) for paths in slots.values()))
    population = check_population(arms_root, slots, ledger, schedule, shortfall)
    by_key, prefix, counts = (population["byKey"], population["prefix"],
                              population["counts"])
    ordered = [(key, entry[2]) for key, entry in
               sorted(by_key.items(), key=lambda item: item[1][0]["globalIndex"])]

    # C5 rule 6 (§2.9): the seal, over the whole batch, before any rate. A
    # failure here does NOT move a slot out of a denominator — it makes every
    # level verdict UNRESOLVED-BY-DESIGN and reports no contrast.
    seal_failures = []
    for key, path in ordered:
        _entry, record, _ = by_key[key]
        detail = verify_seal(path, record)
        if detail is not None:
            seal_failures.append({"arm": key[0], "slot": key[1], "detail": detail})
    chain_failure = verify_chain(ledger)
    sealed = not seal_failures and chain_failure is None

    # §3.3's `session-reused`, over the whole population in every arm, before
    # any rate is computed.
    reused = session_reuse(ordered)

    rows, records_by_arm = [], {arm: {} for arm in ARMS}
    for key, path in ordered:
        entry, record, _ = by_key[key]
        arm = key[0]
        row, accepted = score_run(path, arm, arms_root, golden_path, pins,
                                  arms[arm], entry, record, reused.get(key),
                                  registry_sha256)
        rows.append(row)
        if row["valid"]:
            records_by_arm[arm][key[1]] = accepted

    # C5 rule 7 / §2.8 [D-21]: the stopping rule keys on COMPLETENESS, not on
    # size. Any incomplete batch, at any round, for any reason — and any arm
    # short of its 30 scheduled slots — is descriptive-only.
    complete = len(ledger) == len(schedule) and all(counts[arm] == n
                                                    for arm in ARMS)

    arm_blocks = {}
    for arm in ARMS:
        arm_blocks[arm] = score_arm(arm, arms[arm], n,
                                    [row for row in rows if row["arm"] == arm],
                                    records_by_arm[arm], unexpected[arm])
    # §4.5 is a registered secondary and §4.7 gives it its own top-level member
    # and its own rendered file. It is lifted out of the arm blocks rather than
    # copied, so RESULTS.json carries each arm's census exactly once.
    census_blocks = [arm_blocks[arm].pop("census") for arm in ARMS]

    verdicts = compute_verdicts(arm_blocks, n, complete, sealed)

    return results_document(
        pins=pins, preconditions=preconditions, registry_sha256=registry_sha256,
        override=override, arms=arms, schedule=schedule, prefix=prefix,
        ledger=ledger, counts=counts, shortfall=shortfall, complete=complete,
        n=n, sealed=sealed, seal_failures=seal_failures,
        chain_failure=chain_failure, arm_blocks=arm_blocks,
        census_blocks=census_blocks, rows=rows, verdicts=verdicts)


def results_document(*, pins: dict, preconditions: dict, registry_sha256: str,
                     override, arms: dict, schedule: list, prefix: list,
                     ledger: list, counts: dict, shortfall, complete: bool,
                     n: int, sealed: bool, seal_failures: list, chain_failure,
                     arm_blocks: dict, census_blocks: list, rows: list,
                     verdicts: dict) -> dict:
    """`RESULTS.json` itself: every top-level member §4.7 publishes, assembled
    from quantities that are already computed.

    Round 7, finding 8. This was `score()`'s closing `return {…}`, and the only
    way to obtain the published SHAPE was to run a whole registered scoring —
    which no fixture can, because `verify_preconditions()` binds the study's own
    committed artifacts and three of its pins are null until their registered
    moments arrive (§2.10, §3.2). So §4.3's frozen-interval-scope test walked a
    fixture's own reduced object instead: no `cell`, no `schedule`, no
    `crossArm`, and a `census` of a different shape. The test that §4.3
    registers over `RESULTS.json` was in fact over about half of it, and an
    interval published in a member the fixture did not build would not have
    failed it.

    Splitting the writer out changes nothing about what is published — the
    members, their order and their values are `score()`'s own — and gives the
    harness a way to build the WHOLE published surface from a fixture
    population. `harness/tests/fixtures.py`'s `Population.publish()` calls this
    function, so the walk is over the shape production emits rather than over a
    stand-in for it, and a member added here appears there without anyone
    remembering to add it.
    """
    rounds_registered = len(schedule) // len(ARMS)
    rounds_completed = len(ledger) // len(ARMS)
    valid_counts = [arm_blocks[arm]["population"]["valid"] for arm in ARMS]
    return {
        "resultsVersion": "1",
        "study": "012-policy-perturbation",
        "cell": {
            "model": pins["codex"]["model"],
            "cli": pins["codex"]["version"],
            "binarySha256": pins["codex"]["binarySha256"],
            "mirrorSha256": preconditions["mirrorSha256"],
            "goldenSha256": preconditions["goldenSha256"],
            "preregistrationSha256": preconditions["preregistrationSha256"],
            "registryOfRecordSha256": registry_sha256,
            REGISTRY_OVERRIDE: override,
            "portedFiles": preconditions["portedFiles"],
            "study010LockSha256": preconditions["study010LockSha256"],
            "arms": {arm: {"perturbation": arms[arm]["perturbation"],
                           "tLow": arms[arm]["tLow"], "tHigh": arms[arm]["tHigh"],
                           "armSha256": arms[arm]["armSha256"],
                           "promptSha256": arms[arm]["promptSha256"],
                           "familySha256": arms[arm]["familySha256"],
                           "policySha256": arms[arm]["policySha256"]}
                     for arm in ARMS},
            "note": "Five arms, one model, one day, one policy family. Nothing here "
                    "is a claim about other prompts, other models, or real "
                    "operational records. Every arm's labels come from the ONE "
                    "registered mirror module at that arm's registered "
                    "(T_low, T_high) (§2.2 [D-14]); the digests above were verified "
                    "before any slot was read, and every counted run names the "
                    "registry, the golden capture, the arm and the schedule position "
                    "it was made under (§2.10, §3.2, §3.3).",
        },
        "schedule": {
            "registeredSlots": len(schedule),
            "registeredRoundsTotal": rounds_registered,
            "perArm": n,
            "complete": complete,
            "ledgerRecords": len(ledger),
            "roundsCompleted": rounds_completed,
            "perArmCounts": counts,
            "shortfallDeclaration": shortfall,
            "realised": transition_census(prefix),
            "note": "§2.8's registered call order is three blocks of ten Williams "
                    "sequences. A truncated batch is not balanced and no balance is "
                    "claimed over one: the realised census is published as computed "
                    "and every registered balance property is reported as not "
                    "established.",
        },
        "seal": {
            "verified": sealed,
            "manifestFailures": seal_failures,
            "chainFailure": chain_failure,
            "note": "§2.9: a slot whose recomputed SLOT-MANIFEST.json disagrees with "
                    "the ledger, or a ledger whose chain does not verify, does NOT "
                    "move that slot out of a denominator — it makes every level "
                    "verdict UNRESOLVED-BY-DESIGN and reports no contrast (§3.3, C5 "
                    "rule 6). Registered honestly: the operator can recompute the "
                    "whole chain, so it establishes that a slot was not altered in "
                    "isolation, not that the ledger was written honestly (§7).",
        },
        "arms": arm_blocks,
        "crossArm": {
            # §4.6 S6: distinct completions ACROSS arms as well as within them.
            # Identical completions are data, not defects, but they weaken the
            # independence premise every interval rests on (§4.3 layer 3), so
            # ANALYSIS.md reports this before the rates if any group exceeds one.
            "distinctOutputs": _distinct_outputs(rows),
            "validCounts": {arm: arm_blocks[arm]["population"]["valid"]
                            for arm in ARMS},
            "validCountSpread": (max(valid_counts) - min(valid_counts)
                                 if valid_counts else 0),
            "validCountCaution": bool(valid_counts) and
                                 (max(valid_counts) - min(valid_counts)
                                  > VALID_COUNT_DIVERGENCE),
            "invalidCodes": _code_histogram(rows),
            "wallClockSeconds": _range_block(rows, "wallClockSeconds"),
            "wallClockMissing": sum(1 for row in rows
                                    if row["wallClockSeconds"] is None),
            "note": "[D-13]: the arms are not truncated to a common denominator; "
                    "every arm's N, I_X and V_X are published beside its rates, and "
                    "valid counts differing by more than %d raise a stated caution on "
                    "the per-protocol secondary (S11) alone." % VALID_COUNT_DIVERGENCE,
        },
        "verdicts": verdicts,
        "census": census_blocks,
        "runs": rows,
    }


def _distinct_outputs(rows: list) -> dict:
    outputs: dict = {}
    for row in rows:
        if row["valid"]:
            outputs.setdefault(row["completionSha256"], []).append(
                "%s/%s" % (row["arm"], row["slot"]))
    return {"validRuns": sum(1 for row in rows if row["valid"]),
            "distinctCompletions": len(outputs),
            "largestIdenticalGroup": max((len(group) for group in outputs.values()),
                                         default=0),
            "bySlot": {digest: sorted(group)
                       for digest, group in sorted(outputs.items())}}


def _code_histogram(rows: list) -> dict:
    codes: dict = {}
    for row in rows:
        if not row["valid"]:
            codes[row["code"]] = codes.get(row["code"], 0) + 1
    return dict(sorted(codes.items()))


def score_arm(arm: str, definition: dict, n: int, rows: list,
              records: dict, unexpected: list) -> dict:
    """One arm's endpoints, over its N scheduled slots.

    Every rate that §4.3's frozen interval scope names carries an interval and
    the name of its denominator; nothing else does. The primary, S1 and S3 are
    intent-to-treat over N — every slot the schedule created is in the
    denominator and a slot that did not yield an admissible, compiled,
    class-reaching record counts as not reaching the class, whatever the reason
    (§4.2). S11 is the same numerator over `V_X`.
    """
    valid = [row for row in rows if row["valid"]]
    invalid = [row for row in rows if not row["valid"]]
    # An arm short of its scheduled slots is not a denominator's business — the
    # ITT denominator stays N, and the shortfall is the stopping rule's business
    # ([D-21]), which `compute_verdicts()` applies to every level verdict at
    # once. `scheduled` is published beside N so the two are never conflated.
    scheduled = len(rows)
    v = len(valid)
    i = len(invalid)
    codes = _code_histogram(rows)
    pipeline = rate_block(i, n, "N")

    class_rows = []
    for entry in definition["classes"]:
        index = entry["index"]
        # §5.4 S7 and the primary alike are ITT: the sequence runs over the
        # arm's scheduled slots in round order, and an invalid slot is a 0.
        sequence = [1 if row["valid"] and index in row["coveredClasses"] else 0
                    for row in rows]
        k = sum(sequence)
        raw_k = sum(1 for row in rows
                    if row["valid"] and index in row["rawClasses"])
        q_reached = sum(1 for row in rows
                        if row["valid"] and index in row["qClasses"])
        q_only = sum(1 for row in rows
                     if row["valid"] and index in row["qOnlyClasses"])
        old_edge_k = sum(1 for row in rows
                         if row["valid"] and index in row["oldEdgeClasses"])
        primary = rate_block(k, n, "N")
        placement = rate_block(raw_k, n, "N")
        per_protocol = rate_block(k, v, "V_X")
        # §4.2: ITT is conservative in the other direction and this file will
        # not pretend otherwise. The upper end assumes every invalid slot
        # covered; when I_X = 0 the two ends coincide and the bound is a point.
        sensitivity_upper = rate_block(k + i, n, "N")
        # S2's mislabel share: of the runs that reached the class at all, the
        # share that reached it only with a wrong label. 0 when none reached it.
        # No interval — its denominator is neither N nor V_X (§4.3).
        share = q_only / raw_k if raw_k else 0.0
        class_rows.append({
            "index": index,
            "title": entry["title"],
            "predicateProse": entry["predicateProse"],
            "primary": primary,
            "sensitivity": {"lower": primary, "upper": sensitivity_upper,
                            "invalidSlots": i},
            "placement": placement,
            "perProtocol": per_protocol,
            "oldEdge": rate_block(old_edge_k, n, "N"),
            "rawIntersection": placement,
            "qIntersection": rate_block(q_reached, n, "N"),
            "qOnlyIntersection": rate_block(q_only, n, "N"),
            "mislabelShare": share,
            "drift": _sequence_halves(sequence),
            "reviewTier": review_tier(primary, share),
        })

    # §4.2: the six denominators are identical within an arm by construction —
    # and the scorer asserts it rather than asking the reader to trust the
    # construction. A per-class denominator would make the six rates
    # incomparable and no published integer would show it.
    for member, expected in (("primary", n), ("placement", n),
                             ("oldEdge", n), ("perProtocol", v)):
        seen = set(row[member]["trials"] for row in class_rows)
        if seen != {expected}:
            raise ScoreError(
                "arm %s's %s denominators are %r, not the %d the endpoint is defined "
                "over: the six rates are not comparable (§4.2)"
                % (arm, member, sorted(seen), expected))

    # S3's three quantities are over ONE denominator (round 3, finding 14): the
    # distribution used to iterate the rows present while the mean and the
    # all-six rate divided by N, so a short batch published a distribution
    # totalling 3 beside a rate over 30 and nothing said which was which. The
    # denominator is N — §4.2's intent-to-treat, the same one the primary
    # carries — and the slots the schedule holds that the batch never executed
    # are counted into the 0 bucket and published as `absent`, so an incomplete
    # batch's descriptive surface says exactly what it is over (§2.8 [D-21]).
    distribution = {str(count): 0 for count in range(len(definition["classes"]) + 1)}
    for row in rows:
        distribution[str(row["classesCovered"] if row["valid"] else 0)] += 1
    absent = max(0, n - scheduled)
    distribution["0"] += absent
    if sum(distribution.values()) != n:
        # Asserted rather than intended: the whole point of finding 14 is that
        # a distribution and a rate beside it were over different denominators
        # and no published integer said so.
        raise ScoreError(
            "arm %s's coverage-breadth distribution totals %d over a denominator "
            "of %d: S3's buckets and its rates are not over one denominator "
            "(§4.6 S3, §4.2)"
            % (arm, sum(distribution.values()), n))
    all_six = sum(1 for row in rows
                  if row["valid"] and row["classesCovered"] == len(definition["classes"]))

    h_total = sum(row["h"] for row in valid)
    q_total = sum(row["q"] for row in valid)
    accuracies = [row["h"] / (row["h"] + row["q"]) for row in valid
                  if row["h"] + row["q"]]
    drop_codes: dict = {}
    for row in valid:
        for code, count in row["dropCodes"].items():
            drop_codes[code] = drop_codes.get(code, 0) + count

    return {
        "arm": arm,
        "perturbation": definition["perturbation"],
        "thresholds": {"tLow": definition["tLow"], "tHigh": definition["tHigh"]},
        "population": {
            "scheduled": scheduled,
            "registeredN": n,
            "valid": v,
            "invalid": i,
            "pipelineInvalidRate": pipeline,
            "invalidCodes": codes,
            # §3.3's partition row: no code, no parseable array. Narrowed to the
            # table's meaning in round 3 (finding 13); `coveredNothing` beside
            # it is the wider count — every valid run whose `coveredClasses` is
            # empty, whatever the reason — so neither is read as the other. The
            # note below says exactly what each one counts (round 4, finding 9).
            "authoringEmpty": sum(1 for row in valid if row["authoringEmpty"]),
            "coveredNothing": sum(1 for row in valid if row["coveredNothing"]),
            "unexpectedEntries": unexpected,
            # §4.4: at rho_X >= 0.10 this arm's contrasts carry a stated caution
            # over the whole arm. It changes no level and no contrast.
            "pipelineCaution": (pipeline["rate"] is not None
                                and pipeline["rate"] >= PIPELINE_CAUTION),
            # §5.1: below this floor a perfect arm cannot read HIGH, so the six
            # S11 verdicts are UNRESOLVED-BY-DESIGN.
            "perProtocolFloorMet": v >= PER_PROTOCOL_FLOOR,
            "note": "The primary denominator is N = %d, intent-to-treat: every slot "
                    "the schedule created is in it and a pipeline-invalid slot counts "
                    "as covering nothing (§4.2 [D-24]). V_X = %d is the per-protocol "
                    "secondary's denominator (S11) and the census's population. An "
                    "authoring-empty run is VALID and covers nothing. "
                    "`authoringEmpty` is §3.3's partition row — no code, no "
                    "parseable array — and `coveredNothing` is the wider count: "
                    "valid runs whose `coveredClasses` is empty, meaning no "
                    "class was reached by a record this arm's mirror labelled "
                    "correctly, for any reason (no array, every element "
                    "dropped, every record quarantined, or correctly labelled "
                    "records that satisfy no class predicate)." % (n, v),
        },
        "classes": class_rows,
        "coverageBreadth": {
            "distribution": distribution,
            # Named beside the numbers rather than left to a reader to infer:
            # every bucket, the mean and the all-six rate are over this many
            # slots, and `present` + `absent` is that number.
            "trials": n,
            "denominator": "N",
            "present": scheduled,
            "absent": absent,
            "mean": sum(row["classesCovered"] for row in rows if row["valid"]) / n
                    if n else None,
            "allSix": rate_block(all_six, n, "N"),
            "note": "S3, intent-to-treat over N = %d: an invalid slot covers nothing "
                    "and sits in the 0 bucket, and so do the %d scheduled slots this "
                    "batch did not execute (`absent`). The distribution, the mean and "
                    "the all-six rate are over that one denominator; a batch with "
                    "`absent` > 0 returns no verdict at all ([D-21]) and this surface "
                    "is descriptive." % (n, absent),
        },
        "labelAccuracy": {
            "h": h_total, "q": q_total,
            "rate": h_total / (h_total + q_total) if h_total + q_total else None,
            "perRunMean": sum(accuracies) / len(accuracies) if accuracies else None,
            "perRunMin": min(accuracies) if accuracies else None,
            "perRunMax": max(accuracies) if accuracies else None,
            "perRunTrials": len(accuracies),
            "perRunExcluded": v - len(accuracies),
            "note": "S5, pooled over this arm's valid runs' accepted records. No "
                    "interval: records within one completion share an author turn and "
                    "are not independent trials. The per-run mean and range are over "
                    "the perRunTrials valid runs with at least one accepted record; "
                    "the perRunExcluded runs have no accuracy to average and are "
                    "counted rather than scored 0.",
        },
        "records": {
            "acceptedTotal": sum(row["accepted"] for row in valid),
            "droppedTotal": sum(row["dropped"] for row in valid),
            "dropCodes": dict(sorted(drop_codes.items())),
            "acceptedPerRun": _range_block(valid, "accepted"),
            "hPerRun": _range_block(valid, "h"),
            "qPerRun": _range_block(valid, "q"),
            "droppedPerRun": _range_block(valid, "dropped"),
        },
        "distinctOutputs": _distinct_outputs(rows),
        "wallClock": {
            "seconds": _range_block(rows, "wallClockSeconds"),
            "missing": sum(1 for row in rows if row["wallClockSeconds"] is None),
            "note": "S8, over the slots that reached the call; the count that did not "
                    "is `missing`. Durations derived from each CALL.json's retained "
                    "UTC stamps — no timestamp is published and no clock is read, so "
                    "re-scoring the same tree is byte-identical.",
        },
        "census": _census().census(arm, records, definition["classes"],
                                   definition["embargo"], definition["tLow"],
                                   definition["tHigh"]),
    }


def compute_verdicts(arm_blocks: dict, n: int, complete: bool,
                     sealed: bool) -> dict:
    """§5.1's level verdicts, §5.2's contrasts, §4.6's reading of arm E,
    §5.3 (ii)'s outcome for arm D and §5.3's decision-table row, computed from
    the integers `score_arm()` just wrote.

    No operator input and no flag that changes a cut (C5). When the batch is
    incomplete or the seal fails, decision-table row 1 fires: every level
    verdict is UNRESOLVED-BY-DESIGN, no contrast is computed, and the
    descriptive surface — slots, rates, intervals and census — is what gets
    published ([D-21], §2.9). The reading and arm D's outcome are read off
    level verdicts, so row 1 withdraws both; the S5 label branch is a statement
    about the records an arm produced rather than about the rule, so it is
    published either way.
    """
    resolved = complete and sealed
    levels = {}
    for arm in ARMS:
        rows = arm_blocks[arm]["classes"]
        floor_met = arm_blocks[arm]["population"]["perProtocolFloorMet"]
        # §5.1's second floor: the primary and S1 have NO denominator floor,
        # because ITT fixes their denominator at N for every arm and every
        # class; the per-protocol rate keeps the `V_X` floor, below which a
        # perfect arm cannot read HIGH.
        available = {"primary": resolved, "placement": resolved,
                     "perProtocol": resolved and floor_met,
                     "oldEdge": resolved}
        levels[arm] = {
            endpoint: [level_verdict(row[endpoint]) if available[endpoint]
                       else UNRESOLVED for row in rows]
            for endpoint in LEVEL_ENDPOINTS}
    classes = len(arm_blocks[BASELINE_ARM]["classes"])
    contrasts = None
    gate = None
    counts = {"nP": None, "nC": None, "nH": None}
    if resolved:
        contrasts = {}
        for arm in ARMS:
            if arm == BASELINE_ARM:
                continue
            rows = []
            for index in range(classes):
                baseline_primary = levels[BASELINE_ARM]["primary"][index]
                baseline_placement = levels[BASELINE_ARM]["placement"][index]
                rows.append({
                    "index": index,
                    "contrast": contrast_verdict(baseline_primary,
                                                 levels[arm]["primary"][index]),
                    "placementContrast": placement_contrast_verdict(
                        baseline_placement, levels[arm]["placement"][index]),
                    "collapseDisjoint": second_contrast_verdict(
                        arm_blocks[BASELINE_ARM]["classes"][index]["primary"],
                        arm_blocks[arm]["classes"][index]["primary"]),
                })
            contrasts[arm] = rows
        # §5.3 (iii): the control gate is a GATE and not a caution — arm B
        # TRACKING on at least five of its six classes AND arm C TRACKING on at
        # least five of its six. Every TRACKING verdict requires arm A HIGH on
        # that class as well, so this is a statement about eighteen level
        # verdicts and not twelve; §5.4 records that it passes 0.7658 of the
        # time at N = 30 under the registered scenario.
        tracking = {arm: sum(1 for row in contrasts[arm]
                             if row["contrast"] == CONTRAST_TABLE[1][1])
                    for arm in CONTROL_ARMS}
        gate = {"arms": tracking,
                "minimum": CONTROL_GATE_MINIMUM,
                "classes": classes,
                "passed": all(tracking[arm] >= CONTROL_GATE_MINIMUM
                              for arm in CONTROL_ARMS),
                "shortfall": [arm for arm in CONTROL_ARMS
                              if tracking[arm] < CONTROL_GATE_MINIMUM]}
        e_rows = {row["index"]: row for row in contrasts["E"]}
        counts = {
            "nP": sum(1 for index in NARROW_NUMERIC_CLASSES
                      if e_rows[index]["placementContrast"]
                      == PLACEMENT_CONTRAST_TABLE[0][1]),
            "nC": sum(1 for index in NARROW_NUMERIC_CLASSES
                      if e_rows[index]["contrast"] == CONTRAST_TABLE[0][1]),
            "nH": sum(1 for index in NARROW_NUMERIC_CLASSES
                      if levels["E"]["primary"][index] == "HIGH"),
        }
    # §4.6's S5 cut, per arm, and the reading it keys: computed whether or not
    # the batch resolves, because the branch is a statement about the records
    # this arm produced and not about the decision rule (§4.6 S5 carries no
    # interval and no level verdict).
    branches = {arm: label_branch(arm_blocks[arm]["labelAccuracy"])
                for arm in ARMS}
    reading = reading_verdict(counts, branches["E"]["branch"]) if resolved else None
    # §5.3 (ii)'s three outcomes for arm D, on the same integers.
    d_outcome = arm_d_outcome(levels["D"]["primary"], levels["D"]["oldEdge"],
                              contrasts["D"]) if resolved else None

    row = decision_row(complete, sealed, contrasts, gate, counts, reading)
    if reading is not None and row["row"] == 2:
        # §5.3 (iv) and decision row 2: if class 4 collapses in arm E, "every
        # other reading of arm E is withdrawn in favour of that one". The
        # reading is published with that fact attached rather than deleted, so a
        # reader can see what was withdrawn.
        reading = dict(reading, withdrawn=True,
                       withdrawnBy="decision row 2: arm E reads COLLAPSE on "
                                   "class %d, and every other reading of arm E "
                                   "is withdrawn in favour of that one"
                                   % EMBARGO_CLASS)
    return {
        "resolved": resolved,
        "unresolvedReason": None if resolved else (
            "the batch is incomplete: §2.8's stopping rule [D-21] returns no verdict "
            "of any kind, and the descriptive surface is what is published"
            if not complete else
            "a slot manifest or the ledger chain did not verify: §2.9 invalidates "
            "confirmatory scoring for the whole batch rather than moving a slot out "
            "of a denominator"),
        "cuts": {"highCut": HIGH_CUT, "lowCut": LOW_CUT,
                 "highThresholdK": high_threshold(n),
                 "lowThresholdK": low_threshold(n),
                 "trials": n,
                 "note": "§5.1's two cuts are symmetric about 0.5 and are stated on "
                         "exact interval BOUNDS, not on observed coverage, so a "
                         "denominator carrying more misses faces a boundary that "
                         "already carries them."},
        "levels": levels,
        "contrasts": contrasts,
        "gate": gate,
        "patternCounts": counts,
        "narrowNumericClasses": list(NARROW_NUMERIC_CLASSES),
        "labelBranches": branches,
        "reading": reading,
        "armD": d_outcome,
        "decisionRow": row,
        "note": "Every verdict here is MARGINAL and no simultaneous claim is made "
                "over any of them (§4). §5.4 says where multiplicity bites — in the "
                "pattern thresholds of §5.3 — and gives the joint arithmetic before "
                "the data. No verdict in this study is a statement about defect "
                "detection: no pack is evaluated, no mutation is applied, no "
                "evaluator runs (§5.5).",
    }


def decision_row(complete: bool, sealed: bool, contrasts, gate, counts,
                 reading=None) -> dict:
    """§5.3's decision table, evaluated top to bottom: the first row whose
    condition holds is the outcome, and the last row always holds.

    Rows 4 and 5 cannot both hold — `k_H <= k_raw` per class, so a class with
    E's primary HIGH has E's placement HIGH too and cannot be a placement
    collapse — but the order is stated anyway, because a decision table with an
    unreachable ambiguity is still a decision table with an ambiguity. Rows 1-3
    are gates and produce no R1 verdict in either direction: a study that would
    publish CONFIRMED through a failed control but not R1-UNSUPPORTED through
    one would be a study with a preferred answer.

    **Row 5 reads §4.6's reading as well as `nP`** (round 3, finding 9). Two
    registered statements of the CONFIRMED rule now agree (the round-3 and
    round-6 amendments carried the S5 conjunct into §5.3's row 5, the [D-10]
    box, the summary table and §5.5): confirmation requires the placement
    pattern, arm E's S5 labels at the ceiling, the B/C gate and class 4 not
    collapsing. A placement collapse with degraded labels falls through to the
    last row, published as INDETERMINATE with §4.6's comprehension-collapse
    reading beside it (round 7, finding 9: an earlier version of this docstring
    described the pre-amendment split as live, which was itself the stale
    statement).

    **Row 5 also requires that arm E not read COLLAPSE on class 3** (round 9,
    finding 2) — the fifth conjunct of the five-conjunct rule this function
    computes. `|Q| = 0` cannot see whether any accepted record exercised a
    threshold: `policy_mirror.verdict()` returns at the sanctions and embargo
    clauses before it reads `riskScore`, so an arm E whose accepted records are
    all such records reads the ceiling, keeps class 4 out of collapse and would
    have confirmed having exercised neither number. Class 3 is the interior
    review band: its members are scored BETWEEN the two thresholds, so a record
    covered there is one the two numbers bracket and one the mirror labelled
    after reading `riskScore`, and an arm that covers none of it has produced no
    such record. It excludes a degenerate case and establishes no comprehension,
    which is what §4.6 registers — and it is why §4.6's reading can confirm
    while this table's row 5 does not fire.
    """
    def published(number: int, why: str) -> dict:
        entry = DECISION_TABLE[number - 1]
        return {"row": entry["row"], "publishedAs": entry["publishedAs"],
                "outcome": entry["outcome"], "condition": entry["condition"],
                "gloss": entry["gloss"], "why": why,
                "reading": None if reading is None else reading["publishedAs"]}

    if not complete or not sealed:
        return published(1, "the batch is incomplete or an arm is short of its "
                            "scheduled slots" if not complete else
                            "a slot manifest or the ledger chain did not verify")
    if reading is None:
        # Rows 5 and 7 read §4.6's reading, so a caller that computed contrasts
        # and no reading would silently lose the CONFIRMED outcome. Refused
        # rather than downgraded: this is a caller error, not a data condition,
        # and §7's totality is about the bytes a slot retains.
        raise ScoreError(
            "decision_row() was given contrasts and no §4.6 reading: rows 5 and "
            "7 read the S5 branch (round 3, finding 9) and a missing one is not "
            "a degraded label")
    e_rows = {row["index"]: row for row in contrasts["E"]}
    if e_rows[EMBARGO_CLASS]["contrast"] == CONTRAST_TABLE[0][1]:
        return published(2, "arm E reads COLLAPSE on class %d" % EMBARGO_CLASS)
    if not gate["passed"]:
        return published(3, "the control gate failed: %s short of TRACKING on %d of "
                            "%d" % (" and ".join("arm %s" % arm
                                                 for arm in gate["shortfall"]),
                                    CONTROL_GATE_MINIMUM, gate["classes"]))
    if counts["nH"] >= PATTERN_MINIMUM:
        return published(4, "nH = %d" % counts["nH"])
    if counts["nP"] >= PATTERN_MINIMUM and reading is not None \
            and reading["confirmsR1"] \
            and e_rows[INTERIOR_CLASS]["contrast"] != CONTRAST_TABLE[0][1]:
        return published(5, "nP = %d and arm E's S5 labels are %s, which is "
                            "§4.6's %s, and arm E does not read COLLAPSE on "
                            "class %d" % (counts["nP"], reading["labels"],
                                          reading["publishedAs"],
                                          INTERIOR_CLASS))
    if counts["nC"] >= PATTERN_MINIMUM and counts["nP"] < PATTERN_MINIMUM:
        return published(6, "nC = %d and nP = %d" % (counts["nC"], counts["nP"]))
    if reading is None or reading["publishedAs"] is None:
        tail = ""
    elif reading["confirmsR1"]:
        # The one way the last row is reached with a CONFIRMING reading, and it
        # is new (round 9, finding 2): rows 4 and 6 are unreachable at `nP >= 3`
        # with `nP >= 3` holding, so row 5's fifth conjunct is what failed. The
        # gloss says which conjunct, because saying "does not confirm R1" of a
        # reading that does would be the smaller rule stated again.
        tail = ("; §4.6 reads arm E as a %s (%s), and arm E reads COLLAPSE on "
                "class %d, which row 5 requires it not to"
                % (reading["publishedAs"], reading["why"], INTERIOR_CLASS))
    else:
        tail = ("; §4.6 reads arm E as a %s (%s), which does not confirm R1"
                % (reading["publishedAs"], reading["why"]))
    return published(7, "nP = %d, nC = %d, nH = %d%s"
                        % (counts["nP"], counts["nC"], counts["nH"], tail))


def score_registered(records_dir: str = None) -> dict:
    """THE REGISTERED SCORING INTERFACE (§7, §2.10 [D-23]): the only thing that
    publishes.

    Every input is DERIVED from this module's own location — the registry, the
    canonical `arms/` root, every arm's artifacts, the golden capture, and the
    study root the tables are written to. There is no parameter, flag, default
    or environment variable through which any of them could be supplied, so an
    alternate registry cannot redefine N, the class definitions, the thresholds
    an arm is labelled at, or where a rate table lands — and no `--slots` can
    point the population at a copy with a slot removed, a duplicated arm or a
    renamed tree.

    It computes and publishes in ONE call. The emission directory is validated
    BEFORE anything is scored or written, so a target that would write into the
    population refuses the whole command rather than refusing after the rates
    are on disk, and the arms root is RESOLVED ONCE here so that "the tree that
    was scored" and "the tree that must not be written into" are the same words
    everywhere below.
    """
    arms_root = os.path.realpath(REGISTERED_ARMS)
    if records_dir is not None:
        _check_records_target(arms_root, records_dir)
    results = score(arms_root, REGISTRY_OF_RECORD, REGISTERED_GOLDEN)
    _write_outputs(results, arms_root)
    if records_dir is not None:
        _emit_records(results["runs"], arms_root, records_dir)
    return results


# --- reporting -------------------------------------------------------------

def _rate_cell(block: dict) -> str:
    """Two markdown cells — the rate and its interval — or two dashes when
    there is no valid run to compute them from."""
    if block is None or block["rate"] is None:
        return "— | — |"
    return "%d/%d = %.3f | [%.4f, %.4f] |" % (
        block["count"], block["trials"], block["rate"],
        block["ci95"][0], block["ci95"][1])


def _rate_inline(block: dict) -> str:
    """One rate in running prose, integers first."""
    if block is None or block["rate"] is None:
        return "—"
    return "%d/%d = %.3f, 95%% CI [%.4f, %.4f]" % (
        block["count"], block["trials"], block["rate"],
        block["ci95"][0], block["ci95"][1])


def _number(value, places: int = 4) -> str:
    return "—" if value is None else ("%." + str(places) + "f") % value


def _range_cell(block: dict) -> str:
    """One S4 per-run range: integers at the ends, a mean in the middle."""
    if block["min"] is None:
        return "— / — / —"
    return "%s / %s / %s" % (block["min"], _number(block["mean"], 3), block["max"])


def render_markdown(results: dict) -> str:
    schedule = results["schedule"]
    verdicts = results["verdicts"]
    lines = [
        "# Coverage rates — Study 012",
        "",
        "Generated by `harness/score_rates.py` from the retained authoring slots of",
        "all five arms; every number recomputes from those bytes, and every bound",
        "recomputes from the integers in `RESULTS.json`. No clock and no randomness",
        "enter this file, so re-scoring the same slots reproduces it byte-for-byte.",
        "",
        "**%d of %d rounds completed.**%s"
        % (schedule["roundsCompleted"], schedule["registeredRoundsTotal"],
           "" if schedule["complete"] else
           " The batch is incomplete, so §2.8's stopping rule [D-21] applies: every"
           " level verdict is `%s`, no contrast is computed or reported, and what"
           " follows is the descriptive surface only." % UNRESOLVED),
        "",
    ]
    if not results["seal"]["verified"]:
        lines += [
            "**The seal did not verify (§2.9).** Confirmatory scoring is invalidated",
            "for the whole batch: every level verdict is `%s` and no contrast is"
            % UNRESOLVED,
            "reported. The discrepancy is named below, and the slot is NOT moved out of",
            "any denominator — a code that did would hand an alteration the very",
            "denominator change that produces the verdict it was made to produce.",
            "",
        ]
        for failure in results["seal"]["manifestFailures"]:
            lines.append("- `%s/%s`: %s" % (failure["arm"], failure["slot"],
                                            failure["detail"]))
        if results["seal"]["chainFailure"]:
            lines.append("- ledger chain: %s" % results["seal"]["chainFailure"])
        lines.append("")
    cell = results["cell"]
    lines += [
        "## The cell",
        "",
        "| what | value |",
        "|------|-------|",
        "| model | `%s` |" % cell["model"],
        "| CLI | `%s` |" % cell["cli"],
        "| binary | `%s` |" % cell["binarySha256"],
        "| mirror module | `%s` |" % cell["mirrorSha256"],
        "| golden context | `%s` |" % cell["goldenSha256"],
        "| preregistration (freeze) | `%s` |" % cell["preregistrationSha256"],
        "",
        "| arm | perturbation | (T_low, T_high) | POLICY.md | PROMPT.txt | FAMILY.json |",
        "|-----|--------------|-----------------|-----------|------------|-------------|",
    ]
    for arm in ARMS:
        entry = cell["arms"][arm]
        lines.append("| %s | %s | (%s, %s) | `%s` | `%s` | `%s` |"
                     % (arm, entry["perturbation"], entry["tLow"], entry["tHigh"],
                        entry["policySha256"], entry["promptSha256"],
                        entry["familySha256"]))
    lines += [
        "",
        "## Population, per arm",
        "",
        "N is the arm's scheduled slots; `I_X` its pipeline-invalid runs; "
        "`V_X = N − I_X`.",
        "The primary denominator is N (intent-to-treat, §4.2 [D-24]).",
        "",
        "`authoring-empty` is §3.3's partition row — no code, no parseable array;",
        "`covered nothing` is the wider count: valid runs whose covered-class "
        "set is empty, so no class was reached by a correctly labelled record.",
        "",
        "| arm | N | I_X | V_X | rho_X = I_X/N | 95% CI | authoring-empty | "
        "covered nothing | caution |",
        "|-----|---|-----|-----|---------------|--------|-----------------|"
        "-----------------|---------|",
    ]
    for arm in ARMS:
        population = results["arms"][arm]["population"]
        lines.append("| %s | %d | %d | %d | %s %d | %d | %s |"
                     % (arm, population["registeredN"], population["invalid"],
                        population["valid"],
                        _rate_cell(population["pipelineInvalidRate"]),
                        population["authoringEmpty"],
                        population["coveredNothing"],
                        "**rho_X >= %.2f: stated caution over the whole arm**"
                        % PIPELINE_CAUTION
                        if population["pipelineCaution"] else "none"))
    codes = results["crossArm"]["invalidCodes"]
    if codes:
        lines += ["", "| refusal code | runs (pooled) |", "|--------------|------|"]
        for code, count in codes.items():
            lines.append("| `%s` | %d |" % (code, count))
    lines += [
        "",
        "Valid counts %s; spread %d.%s"
        % (", ".join("%s=%d" % (arm, results["crossArm"]["validCounts"][arm])
                     for arm in ARMS),
           results["crossArm"]["validCountSpread"],
           " **Stated caution ([D-13]): two arms' valid counts differ by more than"
           " %d, so the per-protocol secondary is read under it.**"
           % VALID_COUNT_DIVERGENCE
           if results["crossArm"]["validCountCaution"] else ""),
        "",
    ]
    for arm in ARMS:
        block = results["arms"][arm]
        lines += [
            "## Arm %s — %s, (T_low, T_high) = (%s, %s)"
            % (arm, block["perturbation"], block["thresholds"]["tLow"],
               block["thresholds"]["tHigh"]),
            "",
            "`c_i` is the primary (ITT) rate: the fraction of the arm's N scheduled",
            "slots in which a correctly-labelled record fell in class i. The",
            "sensitivity bound `[k/N, (k+I)/N]` is published beside it; `a_i` is S1's",
            "raw placement rate (label irrelevant); `p_i` is S11's per-protocol rate",
            "over `V_X`; `o_i` is S10's rate under **arm A's** family predicates.",
            "Intervals are exact Clopper-Pearson at 95%, marginal per class.",
            "",
            "| # | class | c_i | 95% CI | sensitivity upper | 95% CI | a_i (S1) | 95% CI "
            "| p_i (S11) | 95% CI | o_i (S10) | 95% CI |",
            "|---|-------|-----|--------|-------------------|--------|----------|--------"
            "|-----------|--------|-----------|--------|",
        ]
        for entry in block["classes"]:
            lines.append("| %d | %s | %s %s %s %s %s" % (
                entry["index"], entry["predicateProse"],
                _rate_cell(entry["primary"]),
                _rate_cell(entry["sensitivity"]["upper"]),
                _rate_cell(entry["placement"]),
                _rate_cell(entry["perProtocol"]),
                _rate_cell(entry["oldEdge"])))
        lines += [
            "",
            "| # | Q | 95% CI | Q-only | 95% CI | mislabel share | S9 tier |",
            "|---|---|--------|--------|--------|----------------|---------|",
        ]
        for entry in block["classes"]:
            lines.append("| %d | %s %s %s | %s |" % (
                entry["index"], _rate_cell(entry["qIntersection"]),
                _rate_cell(entry["qOnlyIntersection"]),
                _number(entry["mislabelShare"], 3),
                entry["reviewTier"]["tier"] or "—"))
        records = block["records"]
        accuracy = block["labelAccuracy"]
        lines += [
            "",
            "| what | value |",
            "|------|-------|",
            "| accepted records (valid runs) | %d |" % records["acceptedTotal"],
            "| dropped elements | %d |" % records["droppedTotal"],
            "| drop codes | %s |" % (", ".join("`%s`x%d" % (code, count)
                                               for code, count
                                               in records["dropCodes"].items()) or "none"),
            "| accepted per run (min/mean/max) | %s |" % _range_cell(records["acceptedPerRun"]),
            "| H per run (min/mean/max) | %s |" % _range_cell(records["hPerRun"]),
            "| Q per run (min/mean/max) | %s |" % _range_cell(records["qPerRun"]),
            "| dropped per run (min/mean/max) | %s |" % _range_cell(records["droppedPerRun"]),
            "| H / Q | %d / %d |" % (accuracy["h"], accuracy["q"]),
            "| label accuracy \\|H\\|/(\\|H\\|+\\|Q\\|) | %s |" % _number(accuracy["rate"]),
            "| per-run label accuracy (min/mean/max) | %s / %s / %s, over %d of %d valid runs |"
            % (_number(accuracy["perRunMin"]), _number(accuracy["perRunMean"]),
               _number(accuracy["perRunMax"]), accuracy["perRunTrials"],
               accuracy["perRunTrials"] + accuracy["perRunExcluded"]),
            "| all six classes covered | %s |" % _rate_inline(block["coverageBreadth"]["allSix"]),
            "| coverage breadth (S3) | distribution %s over %d slots (%d run, %d "
            "never executed), mean %s |"
            % ("/".join("%s:%d" % (bucket, block["coverageBreadth"]["distribution"][bucket])
                        for bucket in sorted(block["coverageBreadth"]["distribution"],
                                             key=int)),
               block["coverageBreadth"]["trials"], block["coverageBreadth"]["present"],
               block["coverageBreadth"]["absent"],
               _number(block["coverageBreadth"]["mean"], 3)),
            "| distinct completions | %d of %d valid runs (largest identical group %d) |"
            % (block["distinctOutputs"]["distinctCompletions"],
               block["distinctOutputs"]["validRuns"],
               block["distinctOutputs"]["largestIdenticalGroup"]),
            "| wall clock per slot (min/mean/max seconds) | %s, over %d slots |"
            % (_range_cell(block["wallClock"]["seconds"]),
               block["wallClock"]["seconds"]["trials"]),
            "",
            "### Coverage against round index (S7)",
            "",
            "| # | first half | second half | sequence |",
            "|---|------------|-------------|----------|",
        ]
        for entry in block["classes"]:
            drift = entry["drift"]
            lines.append("| %d | %d | %d | `%s` |" % (
                entry["index"], drift["firstHalf"], drift["secondHalf"],
                "".join(str(value) for value in drift["sequence"]) or "—"))
        lines.append("")

    lines += [
        "## §5 verdicts",
        "",
        "Computed by the scorer from the integers above, by the rules registered",
        "before the data. HIGH iff `L >= %.2f`; LOW iff `U <= %.2f`; MID otherwise —"
        % (HIGH_CUT, LOW_CUT),
        "at n = %d that is `k >= %d` and `k <= %d`."
        % (verdicts["cuts"]["trials"], verdicts["cuts"]["highThresholdK"],
           verdicts["cuts"]["lowThresholdK"]),
        "",
        "| arm | endpoint | class 0 | 1 | 2 | 3 | 4 | 5 |",
        "|-----|----------|---------|---|---|---|---|---|",
    ]
    for arm in ARMS:
        for endpoint in LEVEL_ENDPOINTS:
            lines.append("| %s | %s | %s |" % (
                arm, endpoint,
                " | ".join(verdicts["levels"][arm][endpoint])))
    if verdicts["contrasts"] is None:
        lines += [
            "",
            "**No contrast is computed or reported.** %s"
            % verdicts["unresolvedReason"],
            "",
        ]
    else:
        lines += [
            "",
            "| arm vs A | class | contrast (primary) | placement contrast (S1) | "
            "second contrast |",
            "|----------|-------|--------------------|-------------------------|"
            "-----------------|",
        ]
        for arm in ARMS:
            if arm == BASELINE_ARM:
                continue
            for row in verdicts["contrasts"][arm]:
                lines.append("| %s | %d | %s | %s | %s |"
                             % (arm, row["index"], row["contrast"],
                                row["placementContrast"],
                                row["collapseDisjoint"] or "—"))
        gate = verdicts["gate"]
        counts = verdicts["patternCounts"]
        lines += [
            "",
            "Control gate (§5.3 (iii)): %s — %s."
            % ("PASSED" if gate["passed"] else "FAILED",
               ", ".join("arm %s TRACKING on %d of %d"
                         % (arm, gate["arms"][arm], gate["classes"])
                         for arm in CONTROL_ARMS)),
            "",
            "Pattern counts over the four narrow numeric classes %s: nP = %d, "
            "nC = %d, nH = %d."
            % (list(NARROW_NUMERIC_CLASSES), counts["nP"], counts["nC"],
               counts["nH"]),
            "",
        ]
        reading = verdicts["reading"]
        lines += [
            "§4.6's reading of arm E (S1 placement against S5 labels): **%s**%s"
            % (reading["publishedAs"] or "no row of §4.6's table",
               " — %s" % reading["gloss"] if reading.get("gloss") else ""),
            "",
            "Why: %s.%s" % (reading["why"],
                            " **Withdrawn:** %s." % reading["withdrawnBy"]
                            if reading.get("withdrawn") else ""),
            "",
            "| arm | S5 label accuracy | branch (§4.6) |",
            "|-----|-------------------|---------------|",
        ]
        for arm in ARMS:
            branch = verdicts["labelBranches"][arm]
            lines.append("| %s | %s (H %d / Q %d) | %s |"
                         % (arm, _number(branch["rate"]), branch["h"],
                            branch["q"], branch["branch"]))
        d_outcome = verdicts["armD"]
        lines += [
            "",
            "### Arm D's registered outcome (§5.3 (ii))",
            "",
            "| row | condition | published as |",
            "|-----|-----------|--------------|",
            "| %d | %s | **%s** |" % (d_outcome["row"], d_outcome["condition"],
                                      d_outcome["publishedAs"]),
            "",
            "Why this row: %s. %s" % (d_outcome["why"], d_outcome["gloss"]),
            "",
        ]
        if d_outcome["explanations"]:
            lines += ["Registered explanations, neither asserted:", ""]
            lines += ["%d. %s" % (number, text) for number, text
                      in enumerate(d_outcome["explanations"], 1)]
            lines += ["", d_outcome["separates"], ""]
    row = verdicts["decisionRow"]
    lines += [
        "### The §5.3 decision-table row",
        "",
        "| row | condition | outcome for R1 | published as |",
        "|-----|-----------|----------------|--------------|",
        "| %d | %s | %s | **%s** |" % (row["row"], row["condition"],
                                       row["outcome"], row["publishedAs"]),
        "",
        "Why this row: %s.%s" % (row["why"],
                                 " " + row["gloss"] if row["gloss"] else ""),
        "",
        "### Every run, in registered call order",
        "",
        "| global | round | pos | arm | run | valid | accepted | dropped | H | Q | "
        "classes covered |",
        "|--------|-------|-----|-----|-----|-------|----------|---------|---|---|"
        "-----------------|",
    ]
    for run in results["runs"]:
        if run["valid"]:
            lines.append("| %d | %d | %d | %s | `%s` | yes%s | %d | %d | %d | %d | %s |"
                         % (run["globalIndex"], run["round"], run["position"],
                            run["arm"], run["slot"],
                            " (authoring-empty)" if run["authoringEmpty"]
                            else " (covered nothing)" if run["coveredNothing"] else "",
                            run["accepted"], run["dropped"], run["h"], run["q"],
                            ", ".join(str(index) for index in run["coveredClasses"])
                            or "none"))
        else:
            lines.append("| %d | %d | %d | %s | `%s` | no — `%s` | — | — | — | — | — |"
                         % (run["globalIndex"], run["round"], run["position"],
                            run["arm"], run["slot"], run["code"]))
    lines += [
        "",
        "## What these rates are and are not",
        "",
        "They are frequencies of five prompts against one model on one synthetic",
        "policy family, counted by this study's own mirror at each arm's registered",
        "thresholds. The mirror is the reference semantics, not ground truth; a record",
        "is \"correctly labelled\" here when the model's recorded outcome agrees with",
        "it. Coverage of a class means a record fell in the class, not that any defect",
        "was found — no pack is evaluated, no mutation is applied and no evaluator runs",
        "in this study. Every interval is an exact interval **for a model this design",
        "cannot verify** (§4.3). Each arm is one instance of its perturbation type, and",
        "§5.5 states what a verdict does not license. Byte-lineage, not truth.",
        "",
    ]
    return "\n".join(lines)


def _check_records_target(arms_root: str, records_dir: str) -> None:
    """`--emit-records DIR` may not write anywhere inside the population (§7).

    Emission is a DERIVED artifact of a scored population; it may not be a
    member of one. The two directories must therefore be disjoint in both
    directions: not equal, not one inside the other — and the population here is
    the WHOLE `arms/` root, not one arm's tree, because a record tree emitted
    into any arm would add a slot to a batch that had just been published.

    Checked before the target exists, so the refusal happens before anything is
    scored and before anything is written — and checked on BOTH sides'
    `realpath`, because a lexical comparison decides nothing about two names for
    one directory. `realpath` resolves what exists and leaves the rest lexical,
    so a target that does not exist yet is still compared against the directory
    it would be created in.

    `realpath` alone is still mount-blind: a bind mount or host re-exposure gives
    one directory two names that BOTH survive resolution (this machine shows /tmp
    again at /mnt/wslg/distro/tmp; `os.path.samefile` says True while the
    resolved strings differ). So the comparison is also made on filesystem
    identity: the (device, inode) of each side against the other side's
    existing-ancestor chain (`_identity_overlap`), which is the mount-blind twin
    of the `startswith` test and needs no privileges to check.
    """
    population = os.path.normpath(os.path.realpath(arms_root))
    target = os.path.normpath(os.path.realpath(records_dir))
    if target == population or target.startswith(population + os.sep) \
            or population.startswith(target + os.sep) \
            or _identity_overlap(population, target):
        raise ScoreError(
            "--emit-records %s (%s) is inside the population %s (%s), or contains "
            "it: the compiled record trees are DERIVED from a scored population and "
            "may not be written into one. Emitting a run-NNN directory into any arm "
            "adds a slot to the batch that was just scored, so the retained tree no "
            "longer reproduces the published rates (§7). The two paths are compared "
            "resolved AND by filesystem identity (device and inode, up each ancestor "
            "chain), so a symlink alias OR a second mount name for either one is the "
            "same directory here. Name a directory outside the arms tree."
            % (records_dir, target, arms_root, population))


def _object_id(path: str):
    """(st_dev, st_ino) of an existing path, else None. Two names are one
    directory exactly when these agree — which is what `realpath` cannot see
    across mounts."""
    try:
        entry = os.stat(path)
    except OSError:
        return None
    return (entry.st_dev, entry.st_ino)


def _identity_chain(path: str) -> set:
    """The (st_dev, st_ino) of `path` and every EXISTING ancestor, to the root.

    A not-yet-created emission target contributes its existing ancestors, so a
    target planned inside the population through a second mount name is caught
    before anything is written."""
    identities = set()
    while True:
        identity = _object_id(path)
        if identity is not None:
            identities.add(identity)
        parent = os.path.dirname(path)
        if parent == path:
            return identities
        path = parent


def _identity_overlap(population: str, target: str) -> bool:
    """True when the two trees share a directory OBJECT even though their
    resolved names differ."""
    population_id = _object_id(population)
    target_id = _object_id(target)
    if population_id is not None and population_id in _identity_chain(target):
        return True
    return target_id is not None and target_id in _identity_chain(population)


def _emit_records(rows: list, arms_root: str, out_dir: str) -> None:
    """Write each valid run's compiled record tree, under `<out>/<arm>/<slot>/`,
    so a reader can diff the records themselves. Deterministic and derived —
    nothing here enters a rate.

    It READS only each slot's `completion.txt` and WRITES only under `out_dir`,
    which `_check_records_target()` has already required to be outside the
    population. Runs with no parseable array have no compiled tree and are
    skipped, which is stated rather than implied. The arms root is RESOLVED at
    entry, as it is at `score_registered()`'s entry, so this function cannot be
    handed an alias by any caller.
    """
    arms_root = os.path.realpath(arms_root)
    for row in rows:
        if not row["valid"] or row.get("noParseableArray"):
            continue
        target = os.path.join(out_dir, row["arm"], row["slot"])
        completion = os.path.join(arms_root, row["arm"], AUTHORING, row["slot"],
                                  "completion.txt")
        for relative, body in compiled_files(completion).items():
            path = os.path.join(target, relative)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as handle:
                handle.write(body)


def _write_outputs(results: dict, arms_root: str) -> None:
    """`RESULTS.json`, `RATES.md` and `CENSUS.md`, into the study root and
    nowhere else (§4.7).

    MODULE-PRIVATE, and called by `score_registered()` alone, on the results it
    computed in the same call, over the arms root it resolved in the same call.
    There is no public writer: a public one trusted a mutable member of an
    ordinary dict, so editing `cell.registryOverride` to None published an
    alternate-registry scoring anywhere the caller named. The output directory is
    STILL not a parameter — a rate table written elsewhere would let the operator
    read thirty rates while the driver still accepted new slots (§2.8) — and the
    arms root that is a parameter names an input to re-derive from, never an
    output to write to.

    What it checks, because "called by one caller" is a property of this file
    and the checks are properties of the study tree:

    1. every pin the results claim is re-derived here from the committed tree,
       one member at a time, and must agree — including the registered N;
    2. the whole result is RE-DERIVED from the arms tree by scoring it again
       through the registered derivation, and must be equal member for member.

    (1) alone leaves a gap: forge the checked members to the committed values and
    any other member — a run row, a class count, a rate, a denominator, a
    verdict, a decision-table row — could be anything at all. So the arithmetic
    is not trusted from the dict either. What is published is what the retained
    tree yields on a second, independent derivation.

    The cost is that the arms tree is scored twice per publication. That is
    deliberate: the second scoring is the check, and a check that reuses the
    first scoring's numbers would be checking a dict against itself.

    What no check inside a file can refuse is a caller who edits this file or
    rebinds its module constants in process. §7 states that ceiling once.
    """
    cell = results.get("cell") if isinstance(results, dict) else None
    if not isinstance(cell, dict) or REGISTRY_OVERRIDE not in cell:
        raise ScoreError(
            "these results did not come from score(): they carry no cell.%s, so "
            "there is no saying which registry of record they were counted under, "
            "and an unattributable rate table is not published (§7)"
            % REGISTRY_OVERRIDE)
    if cell[REGISTRY_OVERRIDE] is not None:
        raise ScoreError(
            "this scoring was given the registry digest %s as an override; "
            "RESULTS.json, RATES.md and CENSUS.md are written only for a scoring "
            "that computed the committed harness/PINS.json's digest itself "
            "(§2.10, §7)" % cell[REGISTRY_OVERRIDE])
    pins = load_json(REGISTRY_OF_RECORD)
    expected = {
        "registryOfRecordSha256": file_digest(REGISTRY_OF_RECORD),
        "mirrorSha256": file_digest(REGISTERED_MIRROR),
        "goldenSha256": pins.get("golden", {}).get("sha256"),
        "preregistrationSha256": pins.get("freeze", {}).get("preregistrationSha256"),
        "model": pins["codex"]["model"],
        "cli": pins["codex"]["version"],
        "binarySha256": pins["codex"]["binarySha256"],
    }
    for member, value in sorted(expected.items()):
        if cell.get(member) != value:
            raise ScoreError(
                "these results record cell.%s = %r and the committed harness/PINS.json "
                "and study tree give %r: a rate table is published only for a scoring "
                "of this cell under the committed registry (§2.10, §7)"
                % (member, cell.get(member), value))
    for arm in ARMS:
        pinned = pins.get("arms", {}).get(arm, {})
        recorded = cell.get("arms", {}).get(arm, {})
        for member in ("armSha256", "promptSha256", "familySha256", "policySha256"):
            if recorded.get(member) != pinned.get(member):
                raise ScoreError(
                    "these results record arm %s's %s = %r and the committed registry "
                    "pins %r: an arm is a registered artifact and a scoring of another "
                    "one is not this study's (§2.6, §7)"
                    % (arm, member, recorded.get(member), pinned.get(member)))
    registered = pins.get("batch", {}).get("n")
    if results.get("schedule", {}).get("perArm") != registered:
        raise ScoreError(
            "these results were counted against a registered N of %r per arm and the "
            "committed harness/PINS.json registers %r: N is the committed registry's "
            "to state, and a scoring over another one is not this study's (§2.8, §7)"
            % (results.get("schedule", {}).get("perArm"), registered))
    # …and then the arithmetic itself, re-derived from the retained tree rather
    # than read out of the dict. `score()` is deterministic over a fixed tree, so
    # the only dict that survives this is the one the tree yields.
    recomputed = score(os.path.realpath(arms_root), REGISTRY_OF_RECORD,
                       REGISTERED_GOLDEN)
    if recomputed != results:
        differing = sorted(
            member for member in set(recomputed) | set(results)
            if recomputed.get(member) != results.get(member))
        raise ScoreError(
            "these results are not what scoring %s yields: %s. RESULTS.json is the "
            "tree's arithmetic, re-derived here rather than taken from the dict it "
            "was handed — a rate, a run row, a class count, a denominator or a "
            "verdict that the retained slots do not produce is not this study's (§7)"
            % (arms_root,
               ("these members differ: " + ", ".join(differing)) if differing
               else "the two derivations are not the same object"))
    os.makedirs(STUDY, exist_ok=True)
    with open(os.path.join(STUDY, "RESULTS.json"), "wb") as handle:
        handle.write((json.dumps(results, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    with open(os.path.join(STUDY, "RATES.md"), "wb") as handle:
        handle.write(render_markdown(results).encode("utf-8"))
    with open(os.path.join(STUDY, "CENSUS.md"), "wb") as handle:
        handle.write(_census().render_markdown(results["census"]).encode("utf-8"))


# The registered command's whole argument surface (§2.10 [D-23]).
# `--emit-records` names a derived-output directory outside the population, and
# nothing else is accepted: an unknown argument REFUSES rather than being
# ignored, because a flag that is silently dropped is how a stale command line
# lies about what it ran (§7).
SCORE_FLAGS = ("--emit-records",)
WITHDRAWN_FLAGS = {
    "--slots": "--slots does not exist on this command or on `batch.py shortfall` "
               "([D-23]). The population IS the registered schedule under the "
               "canonical arms/ root, `harness/../arms`, resolved from the harness's "
               "own location. A supplied root could be a copy with a slot removed, a "
               "duplicated arm or a renamed tree, and every per-slot check would "
               "still pass — a same-arm slot copied into the same arm is not "
               "arm-mismatch (§2.10, §6 C5).",
    "--arm": "--arm was never a flag: all five arms are scored in one pass, because "
             "§5.2's contrasts are taken against arm A IN THE SAME BATCH and an "
             "arm-at-a-time scorer could publish one arm's rates without the "
             "baseline they are read against.",
    "--out": "--out was removed: RESULTS.json, RATES.md and CENSUS.md go to the study "
             "root, and nowhere else. A rate table written elsewhere would let the "
             "operator see the rates while the driver still accepted new slots "
             "(§2.8).",
    "--pins": "--pins was removed from the scorer: the registry of record is the "
              "COMMITTED harness/PINS.json and the registered command derives it from "
              "its own location. A supplied registry — even one whose cell values "
              "match — would define N, the arm digests and the class definitions of "
              "the population it published (§2.10, §7). batch.py still takes --pins, "
              "for the stand-in binary the harness tests drive.",
    "--family": "--family was removed: each arm's six coverage classes are that arm's "
                "own FAMILY.json at the committed pin, derived from the harness's own "
                "location (§2.10, §7).",
    "--prompt": "--prompt was removed: each arm's prompt is derived from the "
                "harness's own location and checked against the committed pin "
                "(§2.10).",
    "--golden": "--golden was removed: the golden capture is derived from the "
                "harness's own location and checked against the committed pin (§3.2).",
    "--start-round": "--start-round was removed from the harness entirely ([D-22]): "
                     "resumption is by global schedule index, and it is batch.py's "
                     "flag in any case, never the scorer's.",
    "--registry-sha256": "there is no flag for the registry digest and never was: the "
                         "registered interface computes the committed "
                         "harness/PINS.json's digest itself (§2.10, §7).",
}
USAGE = "usage: score_rates.py score [--emit-records DIR]"


def _parse_score(argv: list) -> dict:
    """{flag: value} for the `score` command, or ScoreError. Strict: every
    token must be a registered flag with a value, no flag twice."""
    options: dict = {}
    index = 0
    while index < len(argv):
        token = argv[index]
        if token in WITHDRAWN_FLAGS:
            raise ScoreError(WITHDRAWN_FLAGS[token])
        if token not in SCORE_FLAGS:
            raise ScoreError(
                "unknown argument %r. The registered scoring command takes %s and "
                "nothing else, and an argument it does not know is a refusal rather "
                "than a no-op: a silently ignored flag is how a stale command line "
                "lies about what it ran (§7). %s"
                % (token, " and ".join(SCORE_FLAGS), USAGE))
        if index + 1 >= len(argv):
            raise ScoreError("%s needs a value" % token)
        if token in options:
            raise ScoreError("%s was given twice" % token)
        options[token] = argv[index + 1]
        index += 2
    return options


def main(argv: list) -> int:
    if len(argv) < 2 or argv[1] != "score":
        print(USAGE, file=sys.stderr)
        return 2
    try:
        options = _parse_score(argv[2:])
        # §7, [D-23]: the registered interface. It scores and publishes in one
        # call and derives every input from its own location, so no argv, no
        # default and no environment can reach the registry, the arms root, an
        # arm's artifacts, the golden capture, or where the tables land.
        results = score_registered(options.get("--emit-records"))
    except ScoreError as error:
        print("refused: %s" % error, file=sys.stderr)
        return 1
    verdicts = results["verdicts"]
    print("scored: %d slots over %d arms; decision-table row %d — %s"
          % (len(results["runs"]), len(ARMS),
             verdicts["decisionRow"]["row"],
             verdicts["decisionRow"]["publishedAs"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
