#!/usr/bin/env bash
# Report whether a vendored upstream repository has moved since our snapshot.
#
# Exit codes: 0 = unchanged, 1 = upstream moved, 2 = error (safe to cron).
#
# usage: scripts/check-upstream.sh [remote] [branch] [vendor-branch]
#        BASE=<ref> scripts/check-upstream.sh ...     # compare against an explicit ref
set -euo pipefail

case "${1:-}" in
  -h|--help)
    sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
    ;;
esac

REMOTE="${1:-akshara}"
BRANCH="${2:-main}"
VENDOR="${3:-vendor/erzberger-addons}"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "error: not a git repository" >&2
  exit 2
fi

if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
  echo "error: remote '$REMOTE' is not configured in this clone" >&2
  echo "       git remote add $REMOTE <upstream-url>" >&2
  exit 2
fi

if ! git fetch --no-tags --quiet "$REMOTE" "$BRANCH"; then
  echo "error: could not fetch $REMOTE/$BRANCH" >&2
  exit 2
fi

upstream=$(git rev-parse "$REMOTE/$BRANCH")
if [ -n "${BASE:-}" ]; then
  base=$(git rev-parse "$BASE")
else
  base=$(git rev-parse "origin/$VENDOR" 2>/dev/null || git rev-parse "$VENDOR")
fi

if [ "$upstream" = "$base" ]; then
  echo "unchanged: $REMOTE/$BRANCH = ${upstream:0:7}, snapshot $VENDOR = ${base:0:7}"
  exit 0
fi

echo "moved: $REMOTE/$BRANCH = ${upstream:0:7}, snapshot $VENDOR = ${base:0:7}"

new=$(git rev-list --count "$base..$upstream")
if [ "$new" -gt 0 ]; then
  echo "$new new upstream commit(s):"
  git log --oneline --no-decorate "$base..$upstream" | sed 's/^/  /'
fi

gone=$(git rev-list --count "$upstream..$base")
if [ "$gone" -gt 0 ]; then
  echo "warning: $gone commit(s) in our snapshot are absent upstream (history rewritten or we diverged)" >&2
fi

echo "changed files:"
git diff --stat "$base" "$upstream" | sed 's/^/  /'

exit 1
