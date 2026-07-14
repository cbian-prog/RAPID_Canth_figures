#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source cluster/setup.sh 2>/dev/null || true
python plot.py
