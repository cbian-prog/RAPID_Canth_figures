#!/usr/bin/env bash
# Reduce compute.py's output to each figure's data/, then redraw every figure.
set -euo pipefail
cd "$(dirname "$0")/.."
source cluster/setup.sh 2>/dev/null || true
python export_figure_data.py
bash ../Figures/run_all.sh
