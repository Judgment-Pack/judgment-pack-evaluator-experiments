#!/usr/bin/env bash
# The registered authoring call (PREREGISTRATION.md §4): one codex exec
# invocation from a freshly created empty directory outside this repository,
# prompt = the exact bytes of transcription/PROMPT.txt, everything retained.
#
# Usage: authoring_call.sh <empty-scratch-dir>
#
# Retains into transcription/authoring/:
#   CALL.json     - argv, cwd, env allowlist, CLI identity, exit status
#   stdout.raw    - the full exec stdout (records_compile.py's input)
#   stderr.raw    - the full exec stderr
#   session.jsonl - the codex session transcript (the no-tool-use evidence)
set -euo pipefail

STUDY="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRATCH="$1"
OUT="$STUDY/transcription/authoring"

if [ -e "$OUT" ]; then
  echo "refused: $OUT already exists; the call is not repeatable" >&2
  exit 1
fi
mkdir -p "$SCRATCH"
if [ -n "$(ls -A "$SCRATCH")" ]; then
  echo "refused: $SCRATCH is not empty" >&2
  exit 1
fi
case "$SCRATCH" in
  "$STUDY"*) echo "refused: the scratch dir must be outside the repository" >&2; exit 1;;
esac

mkdir -p "$OUT"
PROMPT="$(cat "$STUDY/transcription/PROMPT.txt")"
SESSIONS_BEFORE="$(mktemp)"
find "$HOME/.codex/sessions" -name '*.jsonl' 2>/dev/null | sort > "$SESSIONS_BEFORE"

set +e
( cd "$SCRATCH" && codex exec --sandbox workspace-write -c 'mcp_servers={}' \
    "$PROMPT" < /dev/null > "$OUT/stdout.raw" 2> "$OUT/stderr.raw" )
EXIT=$?
set -e

SESSION="$(find "$HOME/.codex/sessions" -name '*.jsonl' 2>/dev/null | sort | comm -13 "$SESSIONS_BEFORE" - | head -1)"
rm -f "$SESSIONS_BEFORE"
if [ -n "$SESSION" ]; then
  cp "$SESSION" "$OUT/session.jsonl"
  # The registered completion: the transcript's last assistant message,
  # extracted by the locked checker (PREREGISTRATION.md §4).
  python3 - "$OUT" <<'PY'
import sys, os
out = sys.argv[1]
sys.path.insert(0, os.path.join(os.path.dirname(out), "..", "harness"))
import transcript_check
completion = transcript_check.extract_completion(os.path.join(out, "session.jsonl"))
with open(os.path.join(out, "completion.txt"), "wb") as handle:
    handle.write(completion.encode("utf-8"))
PY
fi

python3 - "$OUT" "$SCRATCH" "$EXIT" <<'PY'
import json, subprocess, sys
out, scratch, exit_status = sys.argv[1], sys.argv[2], int(sys.argv[3])
version = subprocess.run(["codex", "--version"], capture_output=True, text=True).stdout.strip()
with open(out + "/CALL.json", "w") as handle:
    json.dump({
        "argv": ["codex", "exec", "--sandbox", "workspace-write", "-c", "mcp_servers={}",
                 "<the exact bytes of transcription/PROMPT.txt>"],
        "cwd": scratch,
        "environmentAllowlist": ["PATH", "HOME"],
        "cli": version,
        "exitStatus": exit_status,
        "stdin": "closed (/dev/null)",
        "note": "PREREGISTRATION.md §4's no-retry rule governs; session.jsonl is the no-tool-use evidence.",
    }, handle, indent=2)
    handle.write("\n")
PY

echo "authoring call retained under $OUT (exit $EXIT)"
