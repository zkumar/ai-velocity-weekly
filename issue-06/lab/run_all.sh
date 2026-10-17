#!/usr/bin/env bash
# AI Velocity Weekly 06 lab. Runs every script on the previous release and on this week's release.
# No API key is read or needed. Python 3.11+; Node 20+ only for the one .mjs script (skipped if absent).
set -euo pipefail
cd "$(dirname "$0")"
unset OPENAI_API_KEY ANTHROPIC_API_KEY GOOGLE_API_KEY AZURE_OPENAI_API_KEY || true
export PYDANTIC_AI_NO_BANNER=1 FASTMCP_SHOW_SERVER_BANNER=false FASTMCP_LOG_LEVEL=CRITICAL

[ -d .venv-prev ] || { python3 -m venv .venv-prev && .venv-prev/bin/pip -q install -r requirements-previous.txt; }
[ -d .venv ]      || { python3 -m venv .venv      && .venv/bin/pip -q install -r requirements.txt; }
PREV=.venv-prev/bin/python; NEW=.venv/bin/python
mkdir -p tmp; rm -f tmp/*.db

echo "=== 1 langgraph: what the paused thread says is still waiting (mechanism of the week) ==="
$PREV test_lg_pending_interrupts.py inbox
$NEW  test_lg_pending_interrupts.py inbox
echo "--- control: the same gates, each returning a state update ---"
LAB_GATE_OUTPUT=1 $PREV test_lg_pending_interrupts.py inbox | tail -1
LAB_GATE_OUTPUT=1 $NEW  test_lg_pending_interrupts.py inbox | tail -1
echo "--- a thread paused and half-answered on 1.2.12, then opened after the upgrade ---"
$PREV test_lg_pending_interrupts.py legacy-pause tmp/upgrade.db
$NEW  test_lg_pending_interrupts.py legacy-read  tmp/upgrade.db
echo "--- the same half-answered thread finished on 1.2.12 ---"
$PREV test_lg_pending_interrupts.py legacy-pause tmp/old.db | tail -1
$PREV test_lg_pending_interrupts.py legacy-read  tmp/old.db | tail -1
echo "--- the same thread shape created and finished on 1.2.13 ---"
$NEW  test_lg_pending_interrupts.py legacy-pause tmp/new.db
$NEW  test_lg_pending_interrupts.py legacy-read  tmp/new.db

echo; echo "=== 2 agent-framework-core: a question for a human and a write in one response ==="
$PREV test_af_mixed_batch.py 2>/dev/null
$NEW  test_af_mixed_batch.py 2>/dev/null

echo; echo "=== 3 fastmcp: a tool that finishes after its timeout ==="
$PREV test_fm_late_result.py 2>/dev/null
$NEW  test_fm_late_result.py 2>/dev/null

echo; echo "=== 4 pydantic-ai-slim: audit hooks and a wrapper that short-circuits ==="
$PREV test_pai_wrap_hooks.py 2>/dev/null
$NEW  test_pai_wrap_hooks.py 2>/dev/null

echo; echo "=== 5 @openai/agents-core: the turn budget after an approval ==="
if command -v node >/dev/null 2>&1; then
  for pair in prev:0.19.0 new:0.20.0; do
    d=node-${pair%%:*}; v=${pair##*:}
    if [ ! -d "$d/node_modules" ]; then
      mkdir -p "$d"
      printf '{"name":"avw06-%s","private":true,"type":"module"}\n' "${pair%%:*}" > "$d/package.json"
      (cd "$d" && npm install --silent --no-fund --no-audit "@openai/agents-core@$v" zod >/dev/null)
    fi
    cp test_oa_maxturns_after_approval.mjs "$d/"
    (cd "$d" && node test_oa_maxturns_after_approval.mjs)
  done
else
  echo "node not found; skipped"
fi

echo; echo "=== 6 model table ==="
$NEW build_models.py
