#!/usr/bin/env bash
# Ralph-style loop.
#
# Repeatedly hands a build prompt to the coding agent until a VERIFIABLE GOAL
# (the test suite passing) is met, or we hit the iteration cap. The repo is the
# memory: each iteration the agent reads SPEC.md / PLAN.md / progress.md, does
# the next task, runs tests, commits, and updates progress.md -- so the next
# iteration knows what is done and what is left.
#
# Usage:  ./loop.sh [prompt_file]        (default: build_prompt.md)
#         MAX_ITERS=20 ./loop.sh         (override the iteration cap)

set -u

PROMPT_FILE="${1:-build_prompt.md}"
MAX_ITERS="${MAX_ITERS:-15}"

if [ ! -f "$PROMPT_FILE" ]; then
  echo "prompt file not found: $PROMPT_FILE" >&2
  exit 2
fi

for i in $(seq 1 "$MAX_ITERS"); do
  echo "================= loop iteration $i / $MAX_ITERS ================="

  # Trigger the agent. --dangerously-skip-permissions lets it run unattended.
  claude -p "$(cat "$PROMPT_FILE")" --dangerously-skip-permissions

  # Verifiable goal: stop the moment the test suite is green.
  if python3 -m pytest -q; then
    echo "================= GOAL MET on iteration $i ================="
    exit 0
  fi
  echo "tests not green yet -- looping"
done

echo "================= hit MAX_ITERS ($MAX_ITERS) without green tests ================="
exit 1
