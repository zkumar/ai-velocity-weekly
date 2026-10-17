#!/usr/bin/env bash
# Creates two clean virtual environments, the week's releases and the ones before them,
# installs pinned versions, and runs every script in both. No API key is used.
set -e
cd "$(dirname "$0")"
export PYDANTIC_AI_NO_BANNER=1
for env in current previous; do
  req=requirements.txt; [ "$env" = previous ] && req=requirements-previous.txt
  mkdir -p .venv && python3 -m venv ".venv/$env" && . ".venv/$env/bin/activate"
  pip install -q -r "$req"
  echo "##### $env ($req)"
  for f in test_*.py; do echo "=== $f"; python -W ignore "$f"; done
  deactivate
done
echo "##### upgrade in flight (state saved on previous; resumed on previous, then on current)"
.venv/previous/bin/python -W ignore upgrade_oa_paused_state.py save .venv/paused
.venv/previous/bin/python -W ignore upgrade_oa_paused_state.py load .venv/paused
.venv/current/bin/python -W ignore upgrade_oa_paused_state.py load .venv/paused
echo "##### model table"
python3 build_models.py
