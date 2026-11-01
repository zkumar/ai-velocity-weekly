#!/usr/bin/env bash
# AI Velocity Weekly 09 lab. Runs the mechanism of the week and the supporting check on the
# releases before this week's window and on the releases that opened it, then prints the model
# table. No API key is read or needed. Python 3.11+.
set -euo pipefail
cd "$(dirname "$0")"
unset OPENAI_API_KEY ANTHROPIC_API_KEY GOOGLE_API_KEY GEMINI_API_KEY AZURE_OPENAI_API_KEY AZURE_OPENAI_ENDPOINT || true

[ -d .venv-prev ] || { python3 -m venv .venv-prev && .venv-prev/bin/pip -q install -r requirements-previous.txt; }
[ -d .venv ]      || { python3 -m venv .venv      && .venv/bin/pip -q install -r requirements.txt; }
PREV=.venv-prev/bin/python; NEW=.venv/bin/python

echo "=== 1 semantic-kernel: what the framework's log keeps about an order (mechanism of the week) ==="
for case in placed refused; do
  echo "--- case=$case ---"
  LAB_CASE=$case $PREV test_sk_function_log.py
  LAB_CASE=$case $NEW  test_sk_function_log.py
done

echo; echo "=== 2 langgraph: the checkpoint the approval UI resumes from ==="
$PREV test_langgraph_interrupt_checkpoint.py
$NEW  test_langgraph_interrupt_checkpoint.py

echo; echo "=== 3 model table ==="
$NEW build_models.py
