#!/usr/bin/env bash
# The registered authoring call (PREREGISTRATION.md §4). Every element below
# was validated against the pinned CLI before locking: an isolated
# CODEX_HOME (so the session lands in a known empty directory and the
# operator's own config, rules, and AGENTS.md cannot reach the model), an
# explicit model, --ignore-user-config, a scrubbed environment, a neutral
# scratch path outside every git worktree, and the prompt passed as the
# byte-exact contents of PROMPT.txt (which carries no trailing newline).
#
# Usage: authoring_call.sh <scratch-parent>
#
# Retains into transcription/authoring/call-N/:
#   CALL.json      - argv, cwd, home, env allowlist, model, CLI identity and
#                    binary digest, exit status, session count
#   stdout.raw / stderr.raw
#   session.jsonl  - the transcript from the isolated CODEX_HOME
#   completion.txt - the transcript's last assistant message (compiler
#                    input), written ONLY when the process exited 0
set -euo pipefail

STUDY="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
GIT_ROOT="$(cd "$(git -C "$STUDY" rev-parse --show-toplevel)" && pwd -P)"
LOCK="$STUDY/PROTOCOL-LOCK.json"

pin() { python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["codex"][sys.argv[2]])' "$LOCK" "$1"; }
LOCKED_DIGEST="$(pin binarySha256)"
LOCKED_MODEL="$(pin model)"

# The scratch: an exclusively created directory whose resolved path is
# outside every git worktree and free of study vocabulary (the transcript
# checker screens prior context after excising environment paths, so a
# path carrying a study term would blunt that screen).
PARENT="$(cd "$1" && pwd -P)"
SCRATCH="$PARENT/s010-authoring-$$"
mkdir "$SCRATCH"
case "$SCRATCH/" in
  "$GIT_ROOT"/*) echo "refused: the scratch dir resolves inside the repository" >&2; exit 1;;
esac
if git -C "$SCRATCH" rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "refused: the scratch dir is inside some git worktree" >&2; exit 1
fi
python3 - "$SCRATCH" "$STUDY" <<'PY' || exit 1
import sys, os
scratch, study = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(study, "harness"))
import transcript_check
bad = [t for t in transcript_check.LEAK_TOKENS if t in scratch.lower()]
if bad:
    print("refused: the scratch path carries leak tokens %r" % bad, file=sys.stderr)
    raise SystemExit(1)
PY

CODEX_BIN="$(command -v codex)"
ACTUAL_DIGEST="sha256:$(sha256sum "$CODEX_BIN" | cut -d' ' -f1)"
if [ "$LOCKED_DIGEST" != "$ACTUAL_DIGEST" ]; then
  echo "refused: codex binary $ACTUAL_DIGEST is not the locked $LOCKED_DIGEST" >&2
  exit 1
fi

# The call slot: first free call-N; an earlier COMPLETED slot refuses.
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
if [ "$N" -gt 3 ]; then echo "refused: all three call slots are used" >&2; exit 1; fi
OUT="$STUDY/transcription/authoring/call-$N"
mkdir "$OUT"

# The isolated codex home: only the credential is carried across, so no
# user config, rules, skills, or AGENTS.md can reach the model, and the
# session file is the single new file under it.
CODEX_HOME_DIR="$SCRATCH/.codex-home"
mkdir "$CODEX_HOME_DIR"
cp "$HOME/.codex/auth.json" "$CODEX_HOME_DIR/auth.json"

PROMPT="$(cat "$STUDY/transcription/PROMPT.txt")"
[ -n "$PROMPT" ] || { echo "refused: empty prompt" >&2; exit 1; }

set +e
( cd "$SCRATCH" && env -i \
    PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$HOME/.local/bin" \
    HOME="$HOME" TMPDIR=/tmp CODEX_HOME="$CODEX_HOME_DIR" \
    "$CODEX_BIN" exec --ignore-user-config -m "$LOCKED_MODEL" \
    --sandbox workspace-write -c 'mcp_servers={}' \
    "$PROMPT" < /dev/null > "$OUT/stdout.raw" 2> "$OUT/stderr.raw" )
EXIT=$?
set -e

SESSIONS="$(find "$CODEX_HOME_DIR" -name '*.jsonl' -type f | sort)"
COUNT="$(printf '%s' "$SESSIONS" | grep -c . || true)"
if [ "$COUNT" = "1" ]; then
  cp "$SESSIONS" "$OUT/session.jsonl"
fi

# The completion is extracted ONLY from a process that exited 0: a call
# killed after its answer was persisted leaves a retained transcript but no
# compiler input, so a retry cannot shop between outputs (§4's retry rule).
if [ "$COUNT" = "1" ] && [ "$EXIT" = "0" ]; then
  python3 - "$OUT" "$STUDY" <<'PY'
import sys, os
out, study = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(study, "harness"))
import transcript_check
completion = transcript_check.extract_completion(os.path.join(out, "session.jsonl"))
with open(os.path.join(out, "completion.txt"), "wb") as handle:
    handle.write(completion.encode("utf-8"))
PY
fi

python3 - "$OUT" "$SCRATCH" "$EXIT" "$ACTUAL_DIGEST" "$COUNT" "$LOCKED_MODEL" "$HOME" <<'PY'
import json, subprocess, sys
out, scratch, exit_status, digest, count, model, home = sys.argv[1:8]
version = subprocess.run(["codex", "--version"], capture_output=True, text=True).stdout.strip()
with open(out + "/CALL.json", "w") as handle:
    json.dump({
        "argv": ["codex", "exec", "--ignore-user-config", "-m", model,
                 "--sandbox", "workspace-write", "-c", "mcp_servers={}",
                 "<the exact bytes of transcription/PROMPT.txt>"],
        "cwd": scratch,
        "home": home,
        "environment": ["PATH", "HOME", "TMPDIR", "CODEX_HOME"],
        "environmentScrubbed": True,
        "codexHomeIsolated": True,
        "ignoreUserConfig": True,
        "model": model,
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
  echo "refused: expected exactly one session in the isolated home, found $COUNT (slot retained)" >&2
  exit 1
fi
echo "authoring call retained under $OUT (exit $EXIT)"
