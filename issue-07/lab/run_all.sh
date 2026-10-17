#!/usr/bin/env bash
# AI Velocity Weekly 07 lab. Runs the mechanism of the week on the previous release and on this
# week's release, in both tool-execution modes and both failure cases, then prints the model table.
# No API key is read or needed. Python 3.11+.
set -euo pipefail
cd "$(dirname "$0")"
unset OPENAI_API_KEY ANTHROPIC_API_KEY GOOGLE_API_KEY AZURE_OPENAI_API_KEY || true
export PYDANTIC_AI_NO_BANNER=1

[ -d .venv-prev ] || { python3 -m venv .venv-prev && .venv-prev/bin/pip -q install -r requirements-previous.txt; }
[ -d .venv ]      || { python3 -m venv .venv      && .venv/bin/pip -q install -r requirements.txt; }
PREV=.venv-prev/bin/python; NEW=.venv/bin/python

echo "=== 1 pydantic-ai-slim: the write that finished beside a tool that failed (mechanism of the week) ==="
for mode in parallel_ordered_events parallel; do
  for cancel in 0 1; do
    echo "--- mode=$mode  case=$([ "$cancel" = 1 ] && echo 'caller cancels' || echo 'sibling raises') ---"
    LAB_MODE=$mode LAB_CANCEL=$cancel $PREV test_pai_sibling_failure.py
    LAB_MODE=$mode LAB_CANCEL=$cancel $NEW  test_pai_sibling_failure.py
  done
done

echo; echo "=== 2 model table ==="
$NEW build_models.py
