#!/usr/bin/env bash
# Package the repository (analysis/ and Figures/) for upload to a cluster or LEAP JupyterHub
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="rapid_figures"
STAMP="$(date +%Y%m%d)"
OUT="${ROOT}/dist/${NAME}_${STAMP}.tar.gz"
mkdir -p "${ROOT}/dist"

tar -czf "$OUT" \
  --exclude='outputs' \
  --exclude='dist' \
  --exclude='__pycache__' \
  --exclude='.DS_Store' \
  --exclude='.git' \
  -C "$ROOT" \
  .

echo "Created: $OUT"
echo ""
echo "On cluster:"
echo "  tar -xzf ${NAME}_${STAMP}.tar.gz && cd ${NAME}"
echo "  cd analysis && bash cluster/setup.sh"
echo "  python compute.py              # CMIP6 on GCS -> outputs/data"
echo "  python export_figure_data.py   # outputs/data -> ../Figures/*/data"
echo "  bash ../Figures/run_all.sh     # redraw every figure"
