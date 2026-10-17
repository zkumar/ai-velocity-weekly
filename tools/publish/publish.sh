#!/usr/bin/env bash
# Build the GitHub-ready copy in ./publish (see publish.py).
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 tools/publish/publish.py "$@"
