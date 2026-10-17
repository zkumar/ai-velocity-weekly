#!/usr/bin/env bash
# Creates a clean virtual environment, installs pinned versions, runs every script.
set -e
cd "$(dirname "$0")"
python3 -m venv .venv && . .venv/bin/activate
pip install -q -r requirements.txt
for f in *.py; do
  case "$f" in build_models.py) continue;; esac
  echo "=== $f"; python -W ignore "$f"
done
