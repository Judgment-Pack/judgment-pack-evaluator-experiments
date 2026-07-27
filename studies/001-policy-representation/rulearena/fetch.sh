#!/usr/bin/env bash
# Fetch RuleArena at the pinned commit. We do not vendor it; see ATTRIBUTION.md.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHA="$(tr -d '[:space:]' < "$HERE/PINNED_COMMIT")"
DEST="${1:-$HERE/checkout}"

if [ -d "$DEST/.git" ]; then
  echo "already present: $DEST"
else
  git clone --quiet https://github.com/skyriver-2000/RuleArena.git "$DEST"
fi
git -C "$DEST" fetch --quiet origin "$SHA" 2>/dev/null || git -C "$DEST" fetch --quiet origin
git -C "$DEST" checkout --quiet "$SHA"

ACTUAL="$(git -C "$DEST" rev-parse HEAD)"
if [ "$ACTUAL" != "$SHA" ]; then
  echo "ERROR: expected $SHA, got $ACTUAL" >&2
  exit 1
fi
echo "RuleArena at $SHA -> $DEST"
