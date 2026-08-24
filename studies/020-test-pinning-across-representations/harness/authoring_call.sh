#!/usr/bin/env bash
# One authoring call, ported from Study 012's wrapper
# (transcription/authoring_call.sh, sha256
# d8877f3d78af54a7c43b8c53571b76ac4e0d540048f57ddcdaa7826f3c6b3fee — the
# destination digest Study 012's own harness/PORTS.md records for it), itself a
# port of Study 011's, itself a port of Study 010's registered wrapper. This
# study's harness/PORTS.md records the source digest and every change; the
# enumerated changes are:
#
#   1. THREE arms (A, B, C), not five, and the scratch/home/bin names are
#      s020-… so two studies' same-numbered runs cannot collide under one
#      scratch parent;
#   2. the REGISTERED PER-CALL TIMEOUT CEILING (PREREGISTRATION.md §2 "Batch
#      shape"): the call runs under `timeout`, and a call that reaches the
#      ceiling is TERMinated, then KILLed after a grace, and the wrapper exits
#      12. A timeout is an APPARATUS failure (§1a) — pipeline-invalid, excluded
#      from every rate's denominator, reported with its own rate — and the
#      ceiling, the grace and whether it fired are stamped into CALL.json so the
#      classification is read off retained bytes rather than inferred from a
#      duration. The design-phase pilot driver mis-filed timeouts as an
#      authoring outcome; that is why the code, the stamp and the exit status
#      are all registered rather than left to the driver;
#   3. a NULL registry model refuses. The model is named by explicit flag at
#      batch time and is null in the registry until then; a null member reaches
#      this shell as the string `None`, which -m would accept as a model name,
#      so a run under an unregistered model is refused before anything is spent;
#   4. the wrapper lives in harness/ rather than transcription/ (this study's
#      transcription/ tree does not exist yet). $STUDY is the parent of this
#      script's own directory, which is the same expression at either location —
#      the anchor and every guard built on it are unchanged;
#   5. the SCRATCH-PATH LEAK SCREEN reads harness/leak_tokens.py's
#      SCRATCH_TOKENS instead of transcript_check.py's design-time tuple
#      (SCAFFOLD item G3). The policy half of that list is DERIVED from the
#      stimulus prose by three registered rules and is shown to have power on
#      mutated inputs; the union with the design-time instrument vocabulary is
#      what the screen takes, so the list can only grow. The screen's site,
#      its refusal and its exit status are unchanged.
#
# The PROMPT-DIGEST GATE is carried, not new, and is per arm: the pinned digest
# is read from the registry at arms.<ARM>.promptSha256, an unregistered arm id
# refuses before anything is called, and a prompt whose bytes are another arm's
# refuses too. What changes with three arms is only the set of ids it accepts.
#
# Every element of the isolation invocation is 012's (and through it 011's),
# unchanged but for the repair harness/PORTS.md registers (the worktree line
# below):
# a fresh HOME and a fresh CODEX_HOME beneath it (skills load from $HOME/.agents
# and DO reach the model — --ignore-user-config alone does not stop them), an
# explicit model, --ignore-user-config, an env -i scrubbed environment with PATH
# and TMPDIR constructed rather than inherited, an exclusively created scratch
# path outside every git worktree and free of study vocabulary, a binary digest
# and CLI version checked BEFORE the call, the prompt passed byte-exact with
# stdin closed, the credential copied and deleted on the seal path and on EXIT,
# INT, TERM and HUP, the recursive pre-call inventory of the isolated home, and
# new-session identification by set difference.
#
# What Study 012's port changed, carried here: the wrapper
# takes the ARM ID and the ARM'S PROMPT PATH as arguments and writes into
# arms/<ARM>/authoring/run-NNN/ — this study runs three cells, not one, and the
# prompt is the arm's own PROMPT.txt at that arm's pinned digest; it stamps
# `arm` and `armPromptSha256` into CALL.json, so a slot names the arm it was
# made under and the exact prompt bytes it was made with (§3.3's arm-mismatch
# is then a per-slot check rather than a claim about the driver's bookkeeping);
# and its scratch, isolated home and per-run binary directory are named
# `s020-…`.
#
# What it deliberately does NOT do: retry, judge a completion, compile records,
# decide admissibility, or seal the slot — SLOT-MANIFEST.json and the ledger
# chain of §2.9 are the driver's (batch.py), which sees every exit path of this
# process and seals refused slots too. It retains bytes and exits with a code.
#
# Usage: authoring_call.sh <scratch-parent> <slot-dir> <pins-json> <arm-id> \
#                          <arm-prompt-path> [codex-binary]
#   <arm-id> is one of the registry's arms (A, B, C) for PROMPT_KIND=registered,
#   and the literal `none` for PROMPT_KIND=probe — a capture call is made
#   under no arm, and stamps `arm: null`.
# Env:   PYTHON_BIN  - interpreter for the helper steps (default python3). It
#                     must be the implementation and version series the
#                     registry's `python` member pins, checked before anything
#                     is called.
#        GOLDEN_SHA256 - the golden capture digest the driver verified at
#                     preflight, stamped into CALL.json so the
#                     golden-before-slots ordering is checkable per slot.
#                     Empty for the probe calls, which precede the golden.
#        PROMPT_KIND - "registered" (default: the arm's PROMPT.txt, at that
#                      arm's pinned digest) or "probe"
#                      (transcription/PROBE-PROMPT.txt, §3.2: one golden
#                      recapture serves all three arms, because the pre-prompt
#                      context precedes the prompt and does not depend on it).
#                      Either way the file's digest must equal the one the
#                      registry pins for it.
#        ISOLATION   - "isolated" (default: a fresh HOME and CODEX_HOME for
#                      this run alone) or "operator-home" (PREREGISTRATION.md
#                      §6 C7 only: the operator's real HOME and its .codex,
#                      everything else as registered, so the golden gate can be
#                      shown to have power. No credential is copied or removed,
#                      and no inventory of the operator's home is taken or
#                      published; batch.py capture-isolation-negative is the
#                      only caller; it retains a verdict, a stripped call
#                      record and — when there is one — the context digests,
#                      never the transcript, whose deletion it verifies.)
#
# Retains into <slot-dir>/:
#   CALL.json      - argv, cwd, isolated home, environment names AND values,
#                    the isolated home's recursive pre-call inventory, model,
#                    CLI identity and binary digest, exit status, new-session
#                    count, credential copied/removed, the arm id and the arm
#                    prompt digest, and the digests of the registry and the
#                    golden capture this run was made under
#   stdout.raw / stderr.raw
#   session.jsonl  - the NEW transcript from the run's CODEX_HOME
#   completion.txt - the transcript's last assistant message (compiler
#                    input), written ONLY when the process exited 0
#   context.json   - the normalized pre-prompt context digests, which
#                    score_rates.py compares to this study's golden capture
#
# Exit status (batch.py maps these to refusal codes):
#   0  the call exited 0 and the slot is complete
#   1  pre-flight refusal — the model was never invoked. Usually no slot is
#      left behind; a refusal after the slot directory is made leaves an empty
#      one, which the driver seals and files under the same APPARATUS code
#   10 the call exited non-zero; the slot is retained without completion.txt
#   11 the run produced other than exactly one new session; slot retained
#   12 the call reached the registered per-call timeout ceiling and was
#      terminated; the slot is retained without completion.txt and the
#      outcome is APPARATUS (pipeline-invalid), never an authoring outcome
#   13 a POST-CALL stage of this wrapper failed after the call returned: the
#      completion extraction, the CALL.json write, or the context digests. The
#      slot is retained with whatever the stage had written, and the outcome is
#      APPARATUS — round 1's R1-4. Before this status existed, `set -e` killed
#      the shell with the failing helper's own status 1, and the driver read
#      that as status 1's meaning: "a pre-call refusal; nothing was called".
#      The call HAD been made and the slot HAD been left behind, and the two
#      events wore one status, so this file now sets a phase flag before the
#      call and traps every unexpected post-call failure to 13.
#
# THE STATUS SET IS CLOSED: {0, 1, 10, 11, 12, 13} on every path this process
# can take by itself, because the ERR trap below converts any unexpected failure
# to 1 (before the call) or 13 (after it). The three signal traps exit 129/130/
# 143, which the driver does NOT register — a signalled wrapper is an operator
# event, and the driver refuses the batch rather than filing a slot under a code
# no partition names.
set -euo pipefail
# errtrace, so the ERR trap below fires inside functions and command
# substitutions too and not only for top-level simple commands.
set -E

# false until the model call has returned; true from then on. Nothing else
# writes it, and it is what makes the two failure phases two statuses.
POST_CALL=false

on_unexpected_error() {
  # $1 the failing command's status, $2 the line it was on. Both are recorded
  # rather than swallowed: a wrapper that died somewhere unplanned is a fact the
  # driver retains in REFUSAL.json's stderr tail.
  if [ "$POST_CALL" = "true" ]; then
    echo "refused: a post-call wrapper stage failed at line $2 with status $1; the call had already returned and the slot is retained with whatever that stage had written" >&2
    exit 13
  fi
  echo "refused: the wrapper failed at line $2 with status $1 before the call; the model was never invoked" >&2
  exit 1
}
trap 'on_unexpected_error "$?" "$LINENO"' ERR

if [ "$#" -lt 5 ] || [ "$#" -gt 6 ]; then
  echo "usage: authoring_call.sh <scratch-parent> <slot-dir> <pins-json> <arm-id> <arm-prompt-path> [codex-binary]" >&2
  exit 1
fi

STUDY="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
# The one repair harness/PORTS.md registers, and the only line of 011's
# isolation invocation not carried byte-for-byte: read the toplevel first and
# refuse an empty one. Nested in the `cd` 011 wrote, a failed `rev-parse` left
# the substitution empty, `cd ""` succeeded, and GIT_ROOT silently became the
# caller's cwd — so the scratch check at the bottom of this block compared
# against a directory nobody chose. Production is always in a worktree; this
# refuses rather than degrades when it is not. It is none of §2.7's three
# differences — it changes no argument, no stamp and no name, and no run this
# study can make reaches it (round 9, incidental to finding 6; registered as a
# repair in round 10, so a later round reads it as recorded and not as drift).
GIT_ROOT="$(git -C "$STUDY" rev-parse --show-toplevel 2>/dev/null || true)"
[ -n "$GIT_ROOT" ] || { echo "refused: $STUDY is not inside a git worktree" >&2; exit 1; }
GIT_ROOT="$(cd "$GIT_ROOT" && pwd -P)"
PYTHON="${PYTHON_BIN:-python3}"
PINS="$3"
SLOT="$2"
ARM="$4"
ARM_PROMPT="$5"

pin() { "$PYTHON" -c 'import json,sys
d = json.load(open(sys.argv[1]))
for key in sys.argv[2:]:
    d = d[key]
print(d)' "$PINS" "$@"; }
PINNED_DIGEST="$(pin codex binarySha256)"
PINNED_MODEL="$(pin codex model)"
PINNED_CLI="$(pin codex version)"
# The model is named by an explicit flag at batch time and is NULL in the
# registry until then (a model name is not a digest — Study 012's correction).
# A null member reaches this shell as the string `None`, which -m would accept
# as a model name, so the wrapper refuses it here: a run made under an
# unregistered model is not a run of this study.
if [ -z "$PINNED_MODEL" ] || [ "$PINNED_MODEL" = "None" ] || [ "$PINNED_MODEL" = "null" ]; then
  echo "refused: harness/PINS.json names no codex model (codex.model is $PINNED_MODEL); the batch names it before any call" >&2
  exit 1
fi

# THE EFFORT-FLAG SEAT — new in Study 020 (PREREGISTRATION.md section 2.1,
# rulings M-24 and M-25), and it is TWO registered branches rather than one.
#
# The registered compute condition is the reasoning-effort value AND the per-arm
# N together, and both are OUTPUTS of the pre-pilot sweep. So the wrapper has to
# hold two states that Study 019 never had to distinguish:
#
#   the PRIMARY state — codex.reasoningEffort is filled, the flag is passed
#   explicitly, and CALL.json stamps the value, so every retained slot records
#   the condition it ran under whether or not a transcript witnesses it (M-24:
#   019's session.jsonl carries no effort member, so the stamp may be the ONLY
#   record, and the preregistration says in terms that such a pin is a recorded
#   intention);
#
#   the SWEEP state — the sweep is the procedure that RESOLVES the value, so a
#   gate that refuses a null effort refuses the sweep's own input. M-25 registers
#   one exemption, one value and one label wide.
#
# The exemption is claimed by PIN_LABEL=SWEEP, which harness/batch.py sets under
# --sweep and nothing else does. It exempts the EFFORT and never the MODEL, it
# stamps its own state into CALL.json rather than leaving the slot looking like a
# primary one, and it marks the slot citable:false. Running the sweep outside the
# harness is rejected on sight — that is the 019 failure exactly (section 2a.1).
#
# The FLAG'S SPELLING is read from the registry (codex.reasoningEffortFlag) and
# is not written into this shell: section 2.1 registers the spelling as resolved
# empirically at pin time, and a spelling hard-coded here would be a guess the
# registry could not correct.
PINNED_EFFORT="$(pin codex reasoningEffort)"
PINNED_EFFORT_FLAG="$(pin codex reasoningEffortFlag)"
PIN_LABEL="${PIN_LABEL:-PRIMARY}"
EFFORT_SOURCE="registry"
case "$PINNED_EFFORT" in
  ""|None|null) EFFORT_NULL=true ;;
  *)            EFFORT_NULL=false ;;
esac
case "$PINNED_EFFORT_FLAG" in
  ""|None|null) EFFORT_FLAG_NULL=true ;;
  *)            EFFORT_FLAG_NULL=false ;;
esac
if [ "$PIN_LABEL" = "SWEEP" ]; then
  # The registered exemption. The effort is left at the CLI default, the flag is
  # omitted, and the slot says so in its own bytes.
  PINNED_EFFORT=""
  EFFORT_SOURCE="sweep-default"
  CITABLE=false
elif [ "$PIN_LABEL" = "PRIMARY" ]; then
  CITABLE=true
  if [ "$EFFORT_NULL" = true ]; then
    echo "refused: harness/PINS.json names no codex reasoning effort (codex.reasoningEffort is null); section 2.1 registers it as a design-time pin the pre-pilot sweep resolves, and only the sweep's own label (PIN_LABEL=SWEEP) is exempt" >&2
    exit 1
  fi
  if [ "$EFFORT_FLAG_NULL" = true ]; then
    echo "refused: codex.reasoningEffort is $PINNED_EFFORT and codex.reasoningEffortFlag is null; the flag's spelling is resolved at pin time (section 2.1) and this wrapper will not guess it" >&2
    exit 1
  fi
else
  echo "refused: PIN_LABEL=$PIN_LABEL is not a registered label; the registered labels are PRIMARY and SWEEP, and an unrecognised one is refused rather than treated as PRIMARY" >&2
  exit 1
fi

# The registry this run was made under, stamped into CALL.json below.
#
# ROUND-10 FINDING R10-1, and the CORRECTION of what these lines used to say.
# They said the scorer computes the committed harness/PINS.json digest itself
# and scores any slot whose stamp differs pipeline-invalid
# ("registry-mismatch"), so `--pins` could serve the harness tests without
# letting an alternate registry redefine the study's cell. The scorer does no
# such thing — it records `pinsRawSha256` in ATTEMPT.json and compares it with
# nothing — and no code anywhere named `registry-mismatch`. BOTH ENDS ARE NOW
# BUILT, and neither of them is this comment:
#
#   the calling end — `batch.require_canonical_registry()` refuses a `--pins`
#   that is not harness/PINS.json whenever the production study is the study in
#   effect, so a slot authored under an alternate registry is not reachable from
#   this tree; and
#
#   the scoring end — `score.read_slot()` requires this stamp to equal the
#   digest the attempt took of the registry it reads, and codes any slot that
#   differs, or carries no stamp at all, §1a's `registry-mismatch`: an apparatus
#   code the population rule now names.
#
# The stamp is therefore what the scoring end reads, and the sentence that used
# to describe it is a check that exists rather than one that was promised.
PINS_DIGEST="sha256:$(sha256sum "$PINS" | cut -d' ' -f1)"
# The golden capture the driver verified at preflight, stamped per slot so the
# golden-before-slots ordering is checkable per run rather than asserted. Empty
# for the probe calls (the recapture and §6 C7), which have no golden yet.
GOLDEN_SHA256="${GOLDEN_SHA256:-}"

# The interpreter is a pin (§2.10), so it is a pre-call gate here too: every
# helper step below runs under $PYTHON, and a run made under an unregistered
# interpreter is not the registered harness.
PINNED_PY_IMPL="$(pin python implementation)"
PINNED_PY_SERIES="$(pin python series)"
ACTUAL_PY="$("$PYTHON" -c 'import platform, sys
print("%s %d.%d" % (platform.python_implementation(), sys.version_info[0], sys.version_info[1]))')"
if [ "$ACTUAL_PY" != "$PINNED_PY_IMPL $PINNED_PY_SERIES" ]; then
  echo "refused: PYTHON_BIN is $ACTUAL_PY, not the registered $PINNED_PY_IMPL $PINNED_PY_SERIES" >&2
  exit 1
fi

PROMPT_KIND="${PROMPT_KIND:-registered}"
case "$PROMPT_KIND" in
  registered)
    # The arm is the cell (§2.6). An unregistered arm id refuses before
    # anything is called, and the prompt is the ARM'S prompt at that arm's
    # pinned digest — the arm-keyed form of 011's prompt gate.
    case "$ARM" in
      none)
        echo "refused: PROMPT_KIND=registered needs an arm id, not none" >&2
        exit 1;;
    esac
    PINNED_PROMPT="$(pin arms "$ARM" promptSha256)" || {
      echo "refused: arm $ARM is not in the registry" >&2; exit 1; }
    # §2.7: the wrapper writes into arms/<ARM>/authoring/run-NNN/ — checked
    # here so that sentence is true of the wrapper itself, not only of the
    # driver's bookkeeping. An off-by-one in the driver's arm sequence would
    # otherwise place a slot in the wrong tree silently.
    #
    # Round 9, finding 6: a suffix is not a location. Four trailing components
    # accepted <anywhere>/arms/<ARM>/authoring/run-NNN under any absolute root,
    # which §2.7's sentence does not say and the driver never produces. $STUDY
    # is already resolved from this script's own location above, so the whole
    # path is required — no new argument and no new environment member
    # (batch.py's environment contract stays 011's four).
    SLOT_NAME_GUARD="$(basename "$SLOT")"
    ARMS_ANCHOR="$STUDY/arms/$ARM/authoring"
    SLOT_SHAPE=ok
    case "$SLOT_NAME_GUARD" in run-[0-9][0-9][0-9]) ;; *) SLOT_SHAPE=bad;; esac
    if [ "$SLOT" != "$ARMS_ANCHOR/$SLOT_NAME_GUARD" ] || [ "$SLOT_SHAPE" != "ok" ]; then
      echo "refused: slot $SLOT is not under arms/$ARM/authoring/ as this study's arms/$ARM/authoring/run-NNN path" >&2
      exit 1
    fi;;
  probe)
    if [ "$ARM" != "none" ]; then
      echo "refused: PROMPT_KIND=probe is made under no arm; pass none, not $ARM" >&2
      exit 1
    fi
    PINNED_PROMPT="$(pin probePrompt sha256)";;
  *) echo "refused: PROMPT_KIND must be registered or probe, not $PROMPT_KIND" >&2; exit 1;;
esac

ISOLATION="${ISOLATION:-isolated}"
case "$ISOLATION" in
  isolated) ;;
  operator-home)
    # §6 C7 only, and only through batch.py capture-isolation-negative, which
    # requires the operator's recorded assent. No registered prompt is ever
    # run this way: the probe is.
    if [ "$PROMPT_KIND" != "probe" ]; then
      echo "refused: ISOLATION=operator-home runs the probe prompt only" >&2; exit 1
    fi;;
  *) echo "refused: ISOLATION must be isolated or operator-home, not $ISOLATION" >&2; exit 1;;
esac

# The prompt is the cell. A prompt whose bytes are not the pinned ones is a
# different study — and here a prompt whose bytes are another ARM'S is a
# different cell — so this refuses before anything is called.
PROMPT_FILE="$ARM_PROMPT"
PROMPT_NAME="$(basename "$PROMPT_FILE")"
PROMPT_DIGEST="sha256:$(sha256sum "$PROMPT_FILE" | cut -d' ' -f1)"
if [ "$PINNED_PROMPT" != "$PROMPT_DIGEST" ]; then
  echo "refused: $PROMPT_FILE is $PROMPT_DIGEST, not the pinned $PINNED_PROMPT" >&2
  exit 1
fi
# BYTE-EXACT, including the trailing newline. `$(cat FILE)` strips every trailing
# newline, so the argv the model received was not the bytes the digest above
# pinned — and §3.1 gate 2, which requires the transcript's user message to EQUAL
# the arm's prompt bytes, could never pass for a prompt file that ends in a
# newline. Nothing noticed, because round 1 found that gate was never invoked for
# a scored slot (R1-5); wiring it in is what makes this reachable, and the
# wrapper's own header has claimed "the prompt passed byte-exact" all along. The
# `printf x` idiom is the standard one: append a byte the substitution cannot
# strip, then remove exactly that byte.
# DEVIATION D-1 (2026-08-21, DEVIATIONS.md): the prompt is no longer passed as
# an argv string — Linux caps one exec argument at 128KiB and arms B/C's
# registered prompts are ~204KiB, so every such call died at exec. The call
# redirects "$PROMPT_FILE" into codex's stdin, which the pinned CLI reads as
# the instructions when no prompt argument is given; the kernel streams the
# file's exact bytes, so byte-exactness is by construction and the printf-x
# idiom (port difference 8) is retired with the string it protected. The
# emptiness refusal stays: a zero-byte prompt is still a refusal, not a call.
[ -s "$PROMPT_FILE" ] || { echo "refused: empty prompt" >&2; exit 1; }

# The scratch: an exclusively created directory whose resolved path is
# outside every git worktree and free of study vocabulary (the transcript
# checker screens prior context after excising environment paths, so a
# path carrying a study term would blunt that screen).
PARENT="$(cd "$1" && pwd -P)"
SLOT_NAME="$(basename "$SLOT")"
SCRATCH="$PARENT/s020-authoring-$ARM-$SLOT_NAME-$$"
mkdir "$SCRATCH"
case "$SCRATCH/" in
  "$GIT_ROOT"/*) echo "refused: the scratch dir resolves inside the repository" >&2; exit 1;;
esac
if git -C "$SCRATCH" rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "refused: the scratch dir is inside some git worktree" >&2; exit 1
fi
# The screen reads harness/leak_tokens.py's SCRATCH_TOKENS, not
# transcript_check.py's design-time tuple (SCAFFOLD item G3, the fifth
# registered difference): the policy half of that list is DERIVED from the
# stimulus prose — bold and backticked terms, clause ids, threshold numerals and
# their spellings — and `leak_tokens.check_power()` shows it has power on
# mutated inputs. SCRATCH_TOKENS is the union of the derived policy vocabulary
# and the design-time INSTRUMENT vocabulary (jpack, the preregistration, the
# mutant machinery), because a scratch path naming either would blunt the
# transcript screen. `leak_tokens.check_negative_corpus()` proves no derived
# token fires on the names this file constructs below.
"$PYTHON" - "$SCRATCH" "$STUDY" <<'PY' || exit 1
import sys, os
scratch, study = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(study, "harness"))
import leak_tokens
bad = [t for t in leak_tokens.SCRATCH_TOKENS if t in scratch.lower()]
if bad:
    print("refused: the scratch path carries leak tokens %r" % bad, file=sys.stderr)
    raise SystemExit(1)
PY
# TMPDIR is this run's own, inside its own scratch: the pinned CLI grants its
# sandbox write access to [workdir, /tmp, $TMPDIR], and pointing TMPDIR at the
# shared /tmp would put every other run's tree inside this run's writable set.
# What /tmp itself still exposes is recorded in PREREGISTRATION.md §7.
RUN_TMP="$SCRATCH/tmp"
mkdir "$RUN_TMP"

if [ "$#" -eq 6 ]; then
  CODEX_BIN="$(cd "$(dirname "$6")" && pwd -P)/$(basename "$6")"
else
  CODEX_BIN="$(command -v codex)"
fi
ACTUAL_DIGEST="sha256:$(sha256sum "$CODEX_BIN" | cut -d' ' -f1)"
if [ "$PINNED_DIGEST" != "$ACTUAL_DIGEST" ]; then
  echo "refused: codex binary $ACTUAL_DIGEST is not the pinned $PINNED_DIGEST" >&2
  exit 1
fi
# The CLI version is a PRE-call gate, not only a recorded field: §2.2 says the
# study does not run with a substitute, and a version read after the call would
# only let the scorer mark the spent run invalid. Read from the resolved binary
# rather than from PATH.
VERSION="$("$CODEX_BIN" --version 2>/dev/null || echo unknown)"
if [ "$VERSION" != "$PINNED_CLI" ]; then
  echo "refused: codex reports '$VERSION', not the pinned '$PINNED_CLI'" >&2
  exit 1
fi

# The registered per-call timeout ceiling (PREREGISTRATION.md §2 "Batch shape"),
# read from the REGISTRY rather than written here, so the driver, the registry
# and this wrapper cannot hold three ceilings. A harness test asserts the
# registry's value equals batch.py's CALL_TIMEOUT_SECONDS.
#
# Resolved and validated BEFORE the call, like every other gate in this file: a
# missing `timeout`, a non-numeric ceiling or a zero one refuses with nothing
# spent, rather than running one unbounded call and discovering it afterwards.
CALL_TIMEOUT_SECONDS="$(pin batch callTimeoutSeconds)"
TIMEOUT_KILL_AFTER_SECONDS="$(pin batch timeoutKillAfterSeconds)"
for VALUE in "$CALL_TIMEOUT_SECONDS" "$TIMEOUT_KILL_AFTER_SECONDS"; do
  case "$VALUE" in
    ''|*[!0-9]*|0) echo "refused: the registry's timeout members are '$CALL_TIMEOUT_SECONDS' and '$TIMEOUT_KILL_AFTER_SECONDS'; both must be positive integer seconds" >&2; exit 1;;
  esac
done
TIMEOUT_BIN="$(command -v timeout || true)"
[ -n "$TIMEOUT_BIN" ] || { echo "refused: no timeout(1) on PATH; the registered per-call ceiling cannot be enforced" >&2; exit 1; }
TIMEOUT_BIN="$(cd "$(dirname "$TIMEOUT_BIN")" && pwd -P)/$(basename "$TIMEOUT_BIN")"

# One slot per run, created exclusively: this study repeats the call, but it
# never overwrites a retained one. Study 010's zero-retry rule protected a
# single unrepeatable draw; here the protection that matters is that every
# invocation leaves its own slot and no slot is ever written twice.
if [ "$PROMPT_KIND" = "registered" ]; then
  # Round 9, finding 6: the registered branch creates inside its own study and
  # nowhere else — the anchor the guard above pinned is the only tree this
  # branch may make, which is what keeps this file's own exit-1 promise
  # ("nothing was called, no slot was left behind") true of a foreign path too.
  #
  # …and the textual anchor cannot see a REPLACED component: `arms` or
  # `authoring` may be a symlink pointing out of the study, which no comparison
  # of the path's own text can see.
  #
  # Round 10, finding 6: resolved BEFORE created, component by component. This
  # was one `mkdir -p` and then a physical check, and `mkdir -p` FOLLOWS a
  # replaced component — so a symlinked `arms` had it create the two missing
  # descendants outside the study and only then be refused, under a comment
  # asserting it created nothing outside the study. The descent below makes
  # each component only after the one above it has resolved to itself, so
  # nothing is ever made beneath a component that resolves elsewhere. Still
  # pre-call. $STUDY is this script's own physically resolved location, so the
  # three components below it are the whole of what a replacement can reach.
  ANCHOR_PHYS="$STUDY"
  for COMPONENT in arms "$ARM" authoring; do
    # -e OR -L, as at the slot path below: a DANGLING symlink is absent to `-e`
    # and present to `mkdir`, so the mkdir is skipped, the `cd` fails, and the
    # refusal below says so rather than `set -e` killing the run silently.
    if [ ! -e "$ANCHOR_PHYS/$COMPONENT" ] && [ ! -L "$ANCHOR_PHYS/$COMPONENT" ]; then
      mkdir "$ANCHOR_PHYS/$COMPONENT"
    fi
    NEXT="$(cd "$ANCHOR_PHYS/$COMPONENT" 2>/dev/null && pwd -P || true)"
    if [ "$NEXT" != "$ANCHOR_PHYS/$COMPONENT" ]; then
      echo "refused: arms/$ARM/authoring resolves to ${NEXT:-nothing} at $COMPONENT, outside this study's tree" >&2
      exit 1
    fi
    ANCHOR_PHYS="$NEXT"
  done
else
  # The probe calls (§3.2's recapture and §6 C7) are made under no arm and have
  # no anchor: their slot is the capture directory the driver names.
  mkdir -p "$(dirname "$SLOT")"
fi
# -e OR -L: a DANGLING symlink at the slot path is absent to `-e` and present
# to `mkdir`, so the wrapper used to pass this check and then die in `mkdir`
# under `set -e` with no refusal message. A link at a slot path is a slot that
# already exists, whatever it points at.
if [ -e "$SLOT" ] || [ -L "$SLOT" ]; then
  echo "refused: slot $SLOT already exists" >&2
  exit 1
fi
mkdir "$SLOT"
OUT="$(cd "$SLOT" && pwd -P)"

# The pinned binary reaches the child by name through a per-run directory
# holding one symlink to it, and by nothing else. Study 010's wrapper wrote
# `PATH=...:$HOME/.local/bin`, which the OUTER shell expands: the "scrubbed"
# child PATH then ended in the operator's real home — on this machine a
# directory that also holds an executable named `jpack`, one of the leak
# tokens the same wrapper screens the scratch path for. Here PATH is fixed
# system directories plus this one per-run directory, and CALL.json records
# the exact string so a published slot shows it.
RUN_BIN="$PARENT/s020-bin-$ARM-$SLOT_NAME-$$"
mkdir "$RUN_BIN"
ln -s "$CODEX_BIN" "$RUN_BIN/codex"
CHILD_PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$RUN_BIN"

# A fresh HOME as well as a fresh CODEX_HOME, per run — except under the §6 C7
# negative control, which is the one registered step that deliberately uses the
# operator's real home. Both live outside the scratch the model is given as its
# workdir, and the isolated home's RECURSIVE inventory is recorded in CALL.json
# so the isolation is shown per run rather than asserted once: score_rates.py
# requires it to be exactly the copied credential and the .codex directory
# holding it, so a config.toml, an AGENTS.md, or a skills tree in the isolated
# home refuses the run.
CREDENTIAL=false
CREDENTIAL_REMOVED=false
INVENTORY='null'
if [ "$ISOLATION" = "isolated" ]; then
  ISOLATED_HOME="$PARENT/s020-home-$ARM-$SLOT_NAME-$$"
  mkdir "$ISOLATED_HOME"
  CODEX_HOME_DIR="$ISOLATED_HOME/.codex"
  mkdir "$CODEX_HOME_DIR"
  if [ -f "$HOME/.codex/auth.json" ]; then
    cp "$HOME/.codex/auth.json" "$CODEX_HOME_DIR/auth.json"
    CREDENTIAL=true
    # The copy must not survive this process on any exit path this process can
    # observe: the normal seal path below removes it and records
    # credentialRemoved, and these traps cover the abnormal ones — a normal or
    # set -e death (EXIT), and SIGINT, SIGTERM and SIGHUP, each of which
    # cleans up and then exits with the conventional 128+signal status. All of
    # them are idempotent with the seal-path rm. SIGKILL and power loss run no
    # handler and are not preventable by any process; §2.9 says so, and says
    # what the residual is.
    remove_credential_copy() { rm -f "$CODEX_HOME_DIR/auth.json"; }
    trap remove_credential_copy EXIT
    trap 'remove_credential_copy; exit 130' INT
    trap 'remove_credential_copy; exit 143' TERM
    trap 'remove_credential_copy; exit 129' HUP
  fi
  INVENTORY="$("$PYTHON" - "$ISOLATED_HOME" <<'PY'
import json, os, sys
root = sys.argv[1]
items = []
for base, directories, files in os.walk(root):
    for name in list(directories) + list(files):
        items.append(os.path.relpath(os.path.join(base, name), root))
print(json.dumps(sorted(items)))
PY
)"
  HOME_ISOLATED=true
else
  ISOLATED_HOME="$HOME"
  CODEX_HOME_DIR="$HOME/.codex"
  HOME_ISOLATED=false
fi
SKILLS_PRESENT=false
if [ -d "$HOME/.agents" ]; then
  # Recorded, not incidental: this is the directory Study 010 found leaking
  # into the transcript through the operator's real HOME. Its presence here
  # is what the fresh HOME excludes, per run.
  SKILLS_PRESENT=true
fi

# Which transcripts existed before the call, so the one this run produced is
# identified by difference rather than by being the only file in the tree. In
# the isolated case the set is empty and this is 010's rule unchanged; under
# C7 the operator's real .codex holds hundreds, and counting them all would
# refuse the control before its registered comparison could run.
SESSIONS_BEFORE="$(find "$CODEX_HOME_DIR" -name '*.jsonl' -type f 2>/dev/null | LC_ALL=C sort || true)"

# Wall clock, recorded per slot (§2.9). It is retained here and nowhere
# else: the scorer never reads it, so RESULTS.json stays byte-stable.
STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
# The ERR trap comes OFF for the call and only for the call. bash runs an ERR
# trap on any failed command whether or not errexit is set — verified, not
# assumed — so leaving it installed would turn every ordinary nonzero call (the
# registered status 10) and every ceiling hit (status 12) into a wrapper error
# before the branches below could read `$EXIT`. The call's status is READ, and
# the three branches at the bottom of this file are what classify it.
trap - ERR
set +e
# The call under the registered ceiling. `timeout` is the outermost thing the
# scrubbed environment runs, so the bound holds over the whole call and not over
# a stage of it; TERM first and KILL after the registered grace, so a terminated
# call still gets its chance to flush the transcript this slot retains.
( cd "$SCRATCH" && env -i \
    PATH="$CHILD_PATH" \
    HOME="$ISOLATED_HOME" TMPDIR="$RUN_TMP" CODEX_HOME="$CODEX_HOME_DIR" \
    "$TIMEOUT_BIN" --signal=TERM --kill-after="$TIMEOUT_KILL_AFTER_SECONDS" \
    "$CALL_TIMEOUT_SECONDS" \
    "$CODEX_BIN" exec --ignore-user-config -m "$PINNED_MODEL" \
    ${PINNED_EFFORT:+"$PINNED_EFFORT_FLAG" "$PINNED_EFFORT"} \
    --sandbox workspace-write -c 'mcp_servers={}' \
    < "$PROMPT_FILE" > "$OUT/stdout.raw" 2> "$OUT/stderr.raw" )
EXIT=$?
set -e
# THE PHASE BOUNDARY (R1-4). Everything below this line runs after the model
# call returned, so an unexpected failure below is status 13 and not status 1.
# It is set here — immediately after `set -e` is restored and before any other
# post-call command — because the first thing that can fail below is the `date`
# on the next line, and the trap is re-installed on the same line as the flag so
# no command can run in the window between them.
POST_CALL=true; trap 'on_unexpected_error "$?" "$LINENO"' ERR
ENDED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
# 124 is timeout(1)'s own status when TERM sufficed; 137 is 128+9, which it
# returns when the KILL was needed. A 137 that some other agent produced would
# be recorded here as a ceiling hit — stated rather than hidden, and it cannot
# move a run across §1a's partition: both a timeout and a nonzero exit are
# APPARATUS failures, so the misreading costs a code and never a denominator.
TIMED_OUT=false
if [ "$EXIT" = "124" ] || [ "$EXIT" = "137" ]; then
  TIMED_OUT=true
fi

SESSIONS_AFTER="$(find "$CODEX_HOME_DIR" -name '*.jsonl' -type f 2>/dev/null | LC_ALL=C sort || true)"
NEW_SESSIONS="$(LC_ALL=C comm -13 <(printf '%s\n' "$SESSIONS_BEFORE") \
                                  <(printf '%s\n' "$SESSIONS_AFTER") || true)"
COUNT="$(printf '%s' "$NEW_SESSIONS" | grep -c . || true)"
if [ "$COUNT" = "1" ]; then
  cp "$(printf '%s' "$NEW_SESSIONS" | grep .)" "$OUT/session.jsonl"
fi

# The completion is extracted ONLY from a process that exited 0: a call
# killed after its answer was persisted leaves a retained transcript but no
# compiler input.
if [ "$COUNT" = "1" ] && [ "$EXIT" = "0" ]; then
  "$PYTHON" - "$OUT" "$STUDY" <<'PY'
import sys, os
out, study = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(study, "harness"))
import transcript_check
try:
    completion = transcript_check.extract_completion(
        os.path.join(out, "session.jsonl"))
except transcript_check.TranscriptError as error:
    # THE AUTHOR'S OWN PROTOCOL VIOLATION IS NOT THIS STAGE'S FAILURE (R1-5).
    # `extract_completion()` parses the transcript with the same whitelist the
    # full binding uses, so a run in which the model used a TOOL refuses here —
    # and refusing here would exit this wrapper non-zero, which is an APPARATUS
    # code, which would quietly delete from every denominator exactly the runs
    # §3's no-tools instruction exists to catch. So an author-side refusal
    # leaves this stage with nothing written and the slot otherwise whole: the
    # driver's binding files it as `author-protocol-violation`, an AUTHORING
    # outcome, counted and scoring zero. No completion is written, because
    # nothing is compiled from a transcript that broke the protocol.
    side = transcript_check.REASON_CAUSE.get(
        getattr(error, "reason", None), ("apparatus", None))[0]
    if side != "authoring":
        raise
else:
    with open(os.path.join(out, "completion.txt"), "wb") as handle:
        handle.write(completion.encode("utf-8"))
PY
fi

# The credential copy dies with the run. The call has terminated and its bytes
# are in the slot, so the copy has no further use; leaving a hundred and fifty
# of them under one scratch parent is a live credential spread across a disk
# for no reason. Only a copy this wrapper made is ever removed — under C7
# there is none.
if [ "$CREDENTIAL" = "true" ] && [ -f "$CODEX_HOME_DIR/auth.json" ]; then
  rm -f "$CODEX_HOME_DIR/auth.json"
  if [ ! -e "$CODEX_HOME_DIR/auth.json" ]; then
    CREDENTIAL_REMOVED=true
  fi
fi
rm -rf "$RUN_BIN"

"$PYTHON" - "$OUT" "$SCRATCH" "$EXIT" "$ACTUAL_DIGEST" "$COUNT" "$PINNED_MODEL" \
    "$ISOLATED_HOME" "$VERSION" "$CREDENTIAL" "$INVENTORY" "$SKILLS_PRESENT" \
    "$PROMPT_KIND" "$PROMPT_NAME" "$PROMPT_DIGEST" "$SLOT_NAME" \
    "$STARTED_AT" "$ENDED_AT" "$CHILD_PATH" "$RUN_TMP" "$CODEX_HOME_DIR" \
    "$HOME_ISOLATED" "$CREDENTIAL_REMOVED" "$ISOLATION" "$PINS_DIGEST" \
    "$GOLDEN_SHA256" "$ARM" "$CALL_TIMEOUT_SECONDS" \
    "$TIMEOUT_KILL_AFTER_SECONDS" "$TIMED_OUT" \
    "$PINNED_EFFORT" "$PINNED_EFFORT_FLAG" "$EFFORT_SOURCE" "$PIN_LABEL" \
    "$CITABLE" <<'PY'
import json, sys
(out, scratch, exit_status, digest, count, model, home, version,
 credential, inventory, skills, prompt_kind, prompt_name, prompt_digest,
 slot_name, started_at, ended_at, child_path, tmpdir, codex_home,
 home_isolated, credential_removed, isolation, pins_digest,
 golden_digest, arm, timeout_seconds, timeout_kill_after,
 timed_out, effort, effort_flag, effort_source, pin_label,
 citable) = sys.argv[1:35]
digits = "".join(ch for ch in slot_name if ch.isdigit())
with open(out + "/CALL.json", "w") as handle:
    json.dump({
        "argv": (["codex", "exec", "--ignore-user-config", "-m", model]
                 + ([effort_flag, effort] if effort else [])
                 + ["--sandbox", "workspace-write", "-c", "mcp_servers={}"]),
        "slot": slot_name,
        "slotIndex": int(digits) if digits else None,
        "arm": None if arm == "none" else arm,
        "armPromptSha256": None if arm == "none" else prompt_digest,
        "promptKind": prompt_kind,
        "promptSha256": prompt_digest,
        "pinsSha256": pins_digest,
        "goldenSha256": golden_digest or None,
        "isolation": isolation,
        "startedAt": started_at,
        "endedAt": ended_at,
        "cwd": scratch,
        "home": home,
        "codexHome": codex_home,
        "environment": ["PATH", "HOME", "TMPDIR", "CODEX_HOME"],
        "environmentValues": {"PATH": child_path, "HOME": home,
                              "TMPDIR": tmpdir, "CODEX_HOME": codex_home},
        "environmentScrubbed": True,
        "codexHomeIsolated": home_isolated == "true",
        "homeIsolated": home_isolated == "true",
        "isolatedHomeInventory": json.loads(inventory),
        "operatorHomeSkillsPresent": skills == "true",
        "credentialCopied": credential == "true",
        "credentialRemoved": credential_removed == "true",
        "ignoreUserConfig": True,
        "model": model,
        # M-24: the effort condition, stamped by the WRAPPER. Where no
        # transcript witness exists this stamp is the only record of it, which
        # `reasoningEffortWitnessed: false` says in the slot's own bytes rather
        # than leaving a reader to infer it from an absence. `pinLabel` and
        # `citable` are what separate a sweep call from a registered one.
        "reasoningEffort": effort or None,
        "reasoningEffortFlag": (effort_flag or None) if effort else None,
        "reasoningEffortSource": effort_source,
        "reasoningEffortWitnessed": False,
        "pinLabel": pin_label,
        "citable": citable == "true",
        "cli": version,
        "binarySha256": digest,
        "exitStatus": int(exit_status),
        "timeoutSeconds": int(timeout_seconds),
        "timeoutKillAfterSeconds": int(timeout_kill_after),
        "timedOut": timed_out == "true",
        "newSessionCount": int(count),
        "stdin": "the exact bytes of %s, piped (deviation D-1)" % prompt_name,
        "note": "One run of one of Study 020's three cells; session.jsonl is the transcript evidence.",
    }, handle, indent=2)
    handle.write("\n")
PY

if [ "$COUNT" = "1" ]; then
  "$PYTHON" - "$OUT" "$STUDY" <<'PY'
import json, sys, os
out, study = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(study, "harness"))
import transcript_check
call = json.load(open(os.path.join(out, "CALL.json")))
try:
    context = transcript_check.context_digests(
        os.path.join(out, "session.jsonl"), call)
except transcript_check.TranscriptError as error:
    # Same rule as the completion stage above, for the same reason: this stage
    # parses with the same whitelist, so an author who used a tool refuses it,
    # and an apparatus exit here would file the author's failure as the
    # apparatus's. Author-side refusals leave no context.json and the slot is
    # otherwise whole; everything else is a real post-call failure and exits 13.
    side = transcript_check.REASON_CAUSE.get(
        getattr(error, "reason", None), ("apparatus", None))[0]
    if side != "authoring":
        raise
else:
    with open(os.path.join(out, "context.json"), "w") as handle:
        json.dump(context, handle, indent=2)
        handle.write("\n")
PY
fi

if [ "$TIMED_OUT" = "true" ]; then
  # FIRST of the three refusal branches, ahead of the session-count one as well
  # as the generic nonzero one. A call terminated at the ceiling frequently
  # produces no session at all, and 012's ordering would have filed exactly
  # those runs as `slot-shape`: both codes are APPARATUS, so no denominator
  # moves, but the registered per-arm TIMEOUT RATE is what the control gate in
  # §5 reads, and undercounting it would let a batch pass a cap it breached.
  echo "refused: the call reached the registered ${CALL_TIMEOUT_SECONDS}s ceiling and was terminated (exit $EXIT; slot retained, no completion extracted)" >&2
  exit 12
fi
if [ "$COUNT" != "1" ]; then
  echo "refused: expected exactly one new session for this call, found $COUNT (slot retained)" >&2
  exit 11
fi
if [ "$EXIT" != "0" ]; then
  echo "refused: the call exited $EXIT (slot retained, no completion extracted)" >&2
  exit 10
fi
echo "authoring call retained under $OUT (exit $EXIT)"
