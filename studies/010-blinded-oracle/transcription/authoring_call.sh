#!/usr/bin/env bash
# The registered authoring call (PREREGISTRATION.md §4): one codex exec
# invocation from a freshly created empty directory outside the repository,
# prompt = the exact bytes of transcription/PROMPT.txt (no trailing
# newline, so the shell argument is byte-identical), scrubbed environment,
# pinned binary, everything retained in an immutable numbered call slot.
#
# Usage: authoring_call.sh <empty-scratch-dir>
#
# Retains into transcription/authoring/call-N/ (first free N, at most 3;
# refuses if an earlier slot already completed):
#   CALL.json      - argv, cwd, env allowlist, CLI identity + binary
#                    digest, exit status, new-session count
#   stdout.raw     - the full exec stdout
#   stderr.raw     - the full exec stderr
#   session.jsonl  - the codex session transcript (the evidence)
#   completion.txt - the transcript's last assistant message (compiler input)
set -euo pipefail

STUDY="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GIT_ROOT="$(git -C "$STUDY" rev-parse --show-toplevel)"
LOCK="$STUDY/PROTOCOL-LOCK.json"
SCRATCH_RAW="$1"
mkdir -p "$SCRATCH_RAW"
SCRATCH="$(cd "$SCRATCH_RAW" && pwd -P)"

if [ -n "$(ls -A "$SCRATCH")" ]; then
  echo "refused: $SCRATCH is not empty" >&2
  exit 1
fi
case "$SCRATCH/" in
  "$(cd "$GIT_ROOT" && pwd -P)"/*)
    echo "refused: the scratch dir resolves inside the repository" >&2
    exit 1;;
esac

# The pinned executable: the binary on PATH must be the one the lock pinned.
CODEX_BIN="$(command -v codex)"
LOCKED_DIGEST="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["codex"]["binarySha256"])' "$LOCK")"
ACTUAL_DIGEST="sha256:$(sha256sum "$CODEX_BIN" | cut -d' ' -f1)"
if [ "$LOCKED_DIGEST" != "$ACTUAL_DIGEST" ]; then
  echo "refused: codex binary $ACTUAL_DIGEST is not the locked $LOCKED_DIGEST" >&2
  exit 1
fi

# The call slot: first free call-N; an earlier COMPLETED slot refuses (the
# no-retry-after-completion rule; transport failures may retry, max 3 slots).
mkdir -p "$STUDY/transcription/authoring"
N=1
while [ -e "$STUDY/transcription/authoring/call-$N" ]; do
  STATUS="$(python3 -c 'import json,sys; s=json.load(open(sys.argv[1])).get("exitStatus"); print(s if isinstance(s,int) and not isinstance(s,bool) else "bad")' "$STUDY/transcription/authoring/call-$N/CALL.json" 2>/dev/null || echo bad)"
  if [ "$STATUS" = "0" ]; then
    echo "refused: call-$N already completed; a completed call may not be retried" >&2
    exit 1
  fi
  N=$((N+1))
done
if [ "$N" -gt 3 ]; then
  echo "refused: all three call slots are used" >&2
  exit 1
fi
OUT="$STUDY/transcription/authoring/call-$N"
mkdir "$OUT"

PROMPT="$(cat "$STUDY/transcription/PROMPT.txt")"
if [ "${#PROMPT}" -eq 0 ]; then
  echo "refused: empty prompt" >&2
  exit 1
fi

SESSIONS_BEFORE="$(mktemp)"
find "$HOME/.codex/sessions" -name '*.jsonl' 2>/dev/null | sort > "$SESSIONS_BEFORE"

# Scrubbed environment: exactly PATH and HOME reach the process.
set +e
( cd "$SCRATCH" && env -i PATH="$PATH" HOME="$HOME" \
    codex exec --sandbox workspace-write -c 'mcp_servers={}' \
    "$PROMPT" < /dev/null > "$OUT/stdout.raw" 2> "$OUT/stderr.raw" )
EXIT=$?
set -e

SESSIONS_AFTER="$(mktemp)"
find "$HOME/.codex/sessions" -name '*.jsonl' 2>/dev/null | sort > "$SESSIONS_AFTER"
NEW_SESSIONS="$(comm -13 "$SESSIONS_BEFORE" "$SESSIONS_AFTER")"
COUNT="$(printf '%s' "$NEW_SESSIONS" | grep -c . || true)"
rm -f "$SESSIONS_BEFORE" "$SESSIONS_AFTER"

if [ "$COUNT" = "1" ]; then
  cp "$NEW_SESSIONS" "$OUT/session.jsonl"
  python3 - "$OUT" "$STUDY" <<'PY'
import sys, os
out, study = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(study, "harness"))
import transcript_check
try:
    completion = transcript_check.extract_completion(os.path.join(out, "session.jsonl"))
    with open(os.path.join(out, "completion.txt"), "wb") as handle:
        handle.write(completion.encode("utf-8"))
except transcript_check.TranscriptError as error:
    print("no completion extracted: %s" % error, file=sys.stderr)
PY
fi

python3 - "$OUT" "$SCRATCH" "$EXIT" "$ACTUAL_DIGEST" "$COUNT" <<'PY'
import json, subprocess, sys
out, scratch, exit_status, digest, count = sys.argv[1:6]
version = subprocess.run(["codex", "--version"], capture_output=True, text=True).stdout.strip()
with open(out + "/CALL.json", "w") as handle:
    json.dump({
        "argv": ["codex", "exec", "--sandbox", "workspace-write", "-c", "mcp_servers={}",
                 "<the exact bytes of transcription/PROMPT.txt>"],
        "cwd": scratch,
        "environment": ["PATH", "HOME"],
        "environmentScrubbed": True,
        "cli": version,
        "binarySha256": digest,
        "exitStatus": int(exit_status),
        "newSessionCount": int(count),
        "stdin": "closed (/dev/null)",
        "note": "PREREGISTRATION.md §4 governs; session.jsonl is the transcript evidence.",
    }, handle, indent=2)
    handle.write("\n")
PY

if [ "$COUNT" != "1" ]; then
  echo "refused: expected exactly one new codex session, found $COUNT (slot retained as inadmissible)" >&2
  exit 1
fi
echo "authoring call retained under $OUT (exit $EXIT)"
