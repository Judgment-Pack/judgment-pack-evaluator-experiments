#!/usr/bin/env bash
# One authoring call, ported from Study 010's registered wrapper
# (harness/PORTS.md records the source digest and every change). Every element
# of the invocation is 010's, validated there against the pinned CLI: a fresh
# HOME and a fresh CODEX_HOME beneath it (skills load from $HOME/.agents and DO
# reach the model — --ignore-user-config alone does not stop them), an explicit
# model, --ignore-user-config, an env -i scrubbed environment, an exclusively
# created scratch path outside every git worktree and free of study vocabulary,
# a binary digest checked against the pinned one, and the prompt passed as the
# byte-exact contents of transcription/PROMPT.txt (no trailing newline).
#
# What this port changes, and only this: the slot is an argument rather than
# the single call-1 (Study 011 runs N of these, and a failed run does not end
# the study — see batch.py), the pins come from a registry file passed in, the
# helper interpreter is $PYTHON_BIN, the codex binary may be named explicitly
# (its digest is still checked, so a test CLI needs a test registry naming its
# digest), and a missing operator credential is recorded rather than fatal.
#
# What it deliberately does NOT do: retry, judge the completion, compile
# records, or decide admissibility. It retains bytes and exits with a code.
#
# Usage: authoring_call.sh <scratch-parent> <slot-dir> <pins-json> [codex-binary]
# Env:   PYTHON_BIN  - interpreter for the helper steps (default python3)
#        PROMPT_KIND - "registered" (default, transcription/PROMPT.txt) or
#                      "probe" (transcription/PROBE-PROMPT.txt). The probe is
#                      the golden recapture's prompt: the pre-prompt context
#                      does not depend on the prompt, and running the
#                      registered one before the batch would show coverage
#                      profiles first. Either way the file's digest must equal
#                      the one the registry pins for that kind.
#
# Retains into <slot-dir>/:
#   CALL.json      - argv, cwd, isolated home, env allowlist, model, CLI
#                    identity and binary digest, exit status, session count
#   stdout.raw / stderr.raw
#   session.jsonl  - the transcript from the isolated CODEX_HOME/HOME
#   completion.txt - the transcript's last assistant message (compiler
#                    input), written ONLY when the process exited 0
#   context.json   - the normalized pre-prompt context digests, which
#                    score_rates.py compares to this study's golden capture
#
# Exit status (batch.py maps these to refusal codes):
#   0  the call exited 0 and the slot is complete
#   1  pre-flight refusal — nothing was called, no slot was left behind
#   10 the call exited non-zero; the slot is retained without completion.txt
#   11 the isolated home held other than exactly one session; slot retained
set -euo pipefail

if [ "$#" -lt 3 ] || [ "$#" -gt 4 ]; then
  echo "usage: authoring_call.sh <scratch-parent> <slot-dir> <pins-json> [codex-binary]" >&2
  exit 1
fi

STUDY="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
GIT_ROOT="$(cd "$(git -C "$STUDY" rev-parse --show-toplevel)" && pwd -P)"
PYTHON="${PYTHON_BIN:-python3}"
PINS="$3"
SLOT="$2"

pin() { "$PYTHON" -c 'import json,sys
d = json.load(open(sys.argv[1]))
for key in sys.argv[2:]:
    d = d[key]
print(d)' "$PINS" "$@"; }
PINNED_DIGEST="$(pin codex binarySha256)"
PINNED_MODEL="$(pin codex model)"

PROMPT_KIND="${PROMPT_KIND:-registered}"
case "$PROMPT_KIND" in
  registered) PROMPT_NAME="PROMPT.txt"; PINNED_PROMPT="$(pin prompt sha256)";;
  probe)      PROMPT_NAME="PROBE-PROMPT.txt"; PINNED_PROMPT="$(pin probePrompt sha256)";;
  *) echo "refused: PROMPT_KIND must be registered or probe, not $PROMPT_KIND" >&2; exit 1;;
esac

# The prompt is the cell. A prompt whose bytes are not the pinned ones is a
# different study, so this refuses before anything is called.
PROMPT_FILE="$STUDY/transcription/$PROMPT_NAME"
PROMPT_DIGEST="sha256:$(sha256sum "$PROMPT_FILE" | cut -d' ' -f1)"
if [ "$PINNED_PROMPT" != "$PROMPT_DIGEST" ]; then
  echo "refused: $PROMPT_NAME is $PROMPT_DIGEST, not the pinned $PINNED_PROMPT" >&2
  exit 1
fi
PROMPT="$(cat "$PROMPT_FILE")"
[ -n "$PROMPT" ] || { echo "refused: empty prompt" >&2; exit 1; }

# The scratch: an exclusively created directory whose resolved path is
# outside every git worktree and free of study vocabulary (the transcript
# checker screens prior context after excising environment paths, so a
# path carrying a study term would blunt that screen).
PARENT="$(cd "$1" && pwd -P)"
SLOT_NAME="$(basename "$SLOT")"
SCRATCH="$PARENT/s011-authoring-$SLOT_NAME-$$"
mkdir "$SCRATCH"
case "$SCRATCH/" in
  "$GIT_ROOT"/*) echo "refused: the scratch dir resolves inside the repository" >&2; exit 1;;
esac
if git -C "$SCRATCH" rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "refused: the scratch dir is inside some git worktree" >&2; exit 1
fi
"$PYTHON" - "$SCRATCH" "$STUDY" <<'PY' || exit 1
import sys, os
scratch, study = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(study, "harness"))
import transcript_check
bad = [t for t in transcript_check.LEAK_TOKENS if t in scratch.lower()]
if bad:
    print("refused: the scratch path carries leak tokens %r" % bad, file=sys.stderr)
    raise SystemExit(1)
PY

if [ "$#" -eq 4 ]; then
  CODEX_BIN="$(cd "$(dirname "$4")" && pwd -P)/$(basename "$4")"
else
  CODEX_BIN="$(command -v codex)"
fi
ACTUAL_DIGEST="sha256:$(sha256sum "$CODEX_BIN" | cut -d' ' -f1)"
if [ "$PINNED_DIGEST" != "$ACTUAL_DIGEST" ]; then
  echo "refused: codex binary $ACTUAL_DIGEST is not the pinned $PINNED_DIGEST" >&2
  exit 1
fi

# One slot per run, created exclusively: this study repeats the call, but it
# never overwrites a retained one. Study 010's zero-retry rule protected a
# single unrepeatable draw; here the protection that matters is that every
# invocation leaves its own slot and no slot is ever written twice.
mkdir -p "$(dirname "$SLOT")"
if [ -e "$SLOT" ]; then
  echo "refused: slot $SLOT already exists" >&2
  exit 1
fi
mkdir "$SLOT"
OUT="$(cd "$SLOT" && pwd -P)"

# A fresh HOME as well as a fresh CODEX_HOME, per run. Both live outside the
# scratch the model can write to, and the isolated home is new and empty but
# for the credential — recorded in CALL.json, so the isolation is shown per
# run rather than asserted once.
ISOLATED_HOME="$PARENT/s011-home-$SLOT_NAME-$$"
mkdir "$ISOLATED_HOME"
CODEX_HOME_DIR="$ISOLATED_HOME/.codex"
mkdir "$CODEX_HOME_DIR"
CREDENTIAL=false
if [ -f "$HOME/.codex/auth.json" ]; then
  cp "$HOME/.codex/auth.json" "$CODEX_HOME_DIR/auth.json"
  CREDENTIAL=true
fi
HOME_ENTRIES="$(ls -A "$ISOLATED_HOME" | wc -l | tr -d ' ')"
SKILLS_PRESENT=false
if [ -d "$HOME/.agents" ]; then
  # Recorded, not incidental: this is the directory Study 010 found leaking
  # into the transcript through the operator's real HOME. Its presence here
  # is what the fresh HOME excludes, per run.
  SKILLS_PRESENT=true
fi

# Wall clock, recorded per slot (§4.4 S9). It is retained here and nowhere
# else: the scorer never reads it, so RESULTS.json stays byte-stable.
STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
set +e
( cd "$SCRATCH" && env -i \
    PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$HOME/.local/bin" \
    HOME="$ISOLATED_HOME" TMPDIR=/tmp CODEX_HOME="$CODEX_HOME_DIR" \
    "$CODEX_BIN" exec --ignore-user-config -m "$PINNED_MODEL" \
    --sandbox workspace-write -c 'mcp_servers={}' \
    "$PROMPT" < /dev/null > "$OUT/stdout.raw" 2> "$OUT/stderr.raw" )
EXIT=$?
set -e
ENDED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

SESSIONS="$(find "$CODEX_HOME_DIR" -name '*.jsonl' -type f | sort)"
COUNT="$(printf '%s' "$SESSIONS" | grep -c . || true)"
if [ "$COUNT" = "1" ]; then
  cp "$SESSIONS" "$OUT/session.jsonl"
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
completion = transcript_check.extract_completion(os.path.join(out, "session.jsonl"))
with open(os.path.join(out, "completion.txt"), "wb") as handle:
    handle.write(completion.encode("utf-8"))
PY
fi

VERSION="$("$CODEX_BIN" --version 2>/dev/null || echo unknown)"
"$PYTHON" - "$OUT" "$SCRATCH" "$EXIT" "$ACTUAL_DIGEST" "$COUNT" "$PINNED_MODEL" \
    "$ISOLATED_HOME" "$VERSION" "$CREDENTIAL" "$HOME_ENTRIES" "$SKILLS_PRESENT" \
    "$PROMPT_KIND" "$PROMPT_NAME" "$PROMPT_DIGEST" "$SLOT_NAME" \
    "$STARTED_AT" "$ENDED_AT" <<'PY'
import json, sys
(out, scratch, exit_status, digest, count, model, home, version,
 credential, home_entries, skills, prompt_kind, prompt_name, prompt_digest,
 slot_name, started_at, ended_at) = sys.argv[1:18]
digits = "".join(ch for ch in slot_name if ch.isdigit())
with open(out + "/CALL.json", "w") as handle:
    json.dump({
        "argv": ["codex", "exec", "--ignore-user-config", "-m", model,
                 "--sandbox", "workspace-write", "-c", "mcp_servers={}",
                 "<the exact bytes of transcription/%s>" % prompt_name],
        "slot": slot_name,
        "slotIndex": int(digits) if digits else None,
        "promptKind": prompt_kind,
        "promptSha256": prompt_digest,
        "startedAt": started_at,
        "endedAt": ended_at,
        "cwd": scratch,
        "home": home,
        "environment": ["PATH", "HOME", "TMPDIR", "CODEX_HOME"],
        "environmentScrubbed": True,
        "codexHomeIsolated": True,
        "homeIsolated": True,
        "isolatedHomeEntriesBefore": int(home_entries),
        "operatorHomeSkillsPresent": skills == "true",
        "credentialCopied": credential == "true",
        "ignoreUserConfig": True,
        "model": model,
        "cli": version,
        "binarySha256": digest,
        "exitStatus": int(exit_status),
        "newSessionCount": int(count),
        "stdin": "closed (/dev/null)",
        "note": "One run of Study 011's single cell; session.jsonl is the transcript evidence.",
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
context = transcript_check.context_digests(os.path.join(out, "session.jsonl"), call)
with open(os.path.join(out, "context.json"), "w") as handle:
    json.dump(context, handle, indent=2)
    handle.write("\n")
PY
fi

if [ "$COUNT" != "1" ]; then
  echo "refused: expected exactly one session in the isolated home, found $COUNT (slot retained)" >&2
  exit 11
fi
if [ "$EXIT" != "0" ]; then
  echo "refused: the call exited $EXIT (slot retained, no completion extracted)" >&2
  exit 10
fi
echo "authoring call retained under $OUT (exit $EXIT)"
