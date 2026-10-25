#!/usr/bin/env bash
# AI Velocity Weekly 08 lab. Runs the mechanism of the week and the supporting check on the
# previous Google ADK release and on this week's release, then prints the model table.
# No API key is read or needed. Python 3.11+.
set -euo pipefail
cd "$(dirname "$0")"
unset OPENAI_API_KEY ANTHROPIC_API_KEY GOOGLE_API_KEY GEMINI_API_KEY AZURE_OPENAI_API_KEY || true
export ADK_SUPPRESS_EXPERIMENTAL_FEATURE_WARNINGS=1

[ -d .venv-prev ] || { python3 -m venv .venv-prev && .venv-prev/bin/pip -q install -r requirements-previous.txt; }
[ -d .venv ]      || { python3 -m venv .venv      && .venv/bin/pip -q install -r requirements.txt; }
PREV=.venv-prev/bin/python; NEW=.venv/bin/python
quiet() { grep -v "Skipping missing token usage\|UserWarning\|warnings.warn\|declaration = tool\|check_feature_enabled\|context_cache_config\|Dropping function calls" || true; }

echo "=== 1 google-adk: the gate inside the tool (mechanism of the week) ==="
for case in tool subagent direct; do
  echo "--- case=$case ---"
  LAB_CASE=$case $PREV test_adk_agenttool_pause.py 2>&1 | quiet
  LAB_CASE=$case $NEW  test_adk_agenttool_pause.py 2>&1 | quiet
done

echo; echo "=== 2 google-adk: the hold written into nested state ==="
$PREV test_adk_nested_state_delta.py 2>&1 | quiet
$NEW  test_adk_nested_state_delta.py 2>&1 | quiet

echo; echo "=== 3 model table ==="
$NEW build_models.py
