#!/usr/bin/env bash
# AI Velocity Weekly 11 lab. Runs the mechanism of the week on the release before this week's
# window (pydantic-ai 2.66.0), on the release that closed it (2.67.0) and on the release that moved
# the question inside the run (2.68.0); then the supporting check on langgraph 1.2.20 and 1.2.21;
# then the model table. No API key is read or needed. Python 3.11+.
set -euo pipefail
cd "$(dirname "$0")"
unset OPENAI_API_KEY ANTHROPIC_API_KEY GOOGLE_API_KEY GEMINI_API_KEY AZURE_OPENAI_API_KEY AZURE_OPENAI_ENDPOINT || true
export PYDANTIC_AI_NO_BANNER=1

[ -d .venv-prev ] || { python3 -m venv .venv-prev && .venv-prev/bin/pip -q install -r requirements-previous.txt; }
[ -d .venv-mid ]  || { python3 -m venv .venv-mid  && .venv-mid/bin/pip  -q install -r requirements-2.67.0.txt; }
[ -d .venv ]      || { python3 -m venv .venv      && .venv/bin/pip      -q install -r requirements.txt; }
PREV=.venv-prev/bin/python; MID=.venv-mid/bin/python; NEW=.venv/bin/python

echo "=== 1 pydantic-ai: the approval that left the run with the call (mechanism of the week) ==="
for py in $PREV $MID $NEW; do echo "--- $py ---"; $py test_pydantic_ai_external_approval.py; done

echo; echo "=== 2 pydantic-ai: the question that leaves the run on a token, and who answered it ==="
for py in $PREV $MID $NEW; do echo "--- $py ---"; $py test_pydantic_ai_request_input.py; done
echo "--- $NEW, answered_by set to a name nobody authorised ---"
LAB_ANSWERER=anyone@example.invalid $NEW test_pydantic_ai_request_input.py

echo; echo "=== 3 langgraph: the child's record, read from the parent ==="
$PREV test_langgraph_subgraph_state.py
$NEW  test_langgraph_subgraph_state.py

echo; echo "=== 4 model table ==="
$NEW build_models.py
