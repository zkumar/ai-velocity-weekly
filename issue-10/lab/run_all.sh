#!/usr/bin/env bash
# AI Velocity Weekly 10 lab. Runs the mechanism of the week and the supporting check on the
# releases before this week's window and on the releases in it, then prints the model table.
# No API key is read or needed. Python 3.11+.
set -euo pipefail
cd "$(dirname "$0")"
unset OPENAI_API_KEY ANTHROPIC_API_KEY GOOGLE_API_KEY GEMINI_API_KEY AZURE_OPENAI_API_KEY AZURE_OPENAI_ENDPOINT || true
export PYDANTIC_AI_NO_BANNER=1

[ -d .venv-prev ] || { python3 -m venv .venv-prev && .venv-prev/bin/pip -q install -r requirements-previous.txt; }
[ -d .venv ]      || { python3 -m venv .venv      && .venv/bin/pip -q install -r requirements.txt; }
PREV=.venv-prev/bin/python; NEW=.venv/bin/python

echo "=== 1 agent-framework: the tool the approval policy does not name (mechanism of the week) ==="
for case in listed unlisted default approved joined; do
  echo "--- case=$case ---"
  LAB_CASE=$case $PREV test_af_mcp_unlisted_tool.py
  LAB_CASE=$case $NEW  test_af_mcp_unlisted_tool.py
done

echo; echo "=== 2 pydantic-ai: a toolset that requires approval, and a Tool instance inside it ==="
$PREV test_pydantic_ai_toolset_approval.py
$NEW  test_pydantic_ai_toolset_approval.py

echo; echo "=== 3 model table ==="
$NEW build_models.py
