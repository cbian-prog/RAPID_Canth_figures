#!/usr/bin/env bash
# 集群 / LEAP 环境初始化（在 rapid_figures 目录内运行）
set -euo pipefail

cd "$(dirname "$0")/.."

# ---------- 按需修改 ----------
# LEAP JupyterHub 通常已有 notebook 环境，可注释掉 conda 部分
# conda activate notebook

export RAPID_GCS_BASE="${RAPID_GCS_BASE:-gs://leap-persistent/cbian-prog}"
export RAPID_MASK_AREA_PATH="${RAPID_MASK_AREA_PATH:-/home/jovyan/RAPID_mask_area.nc}"
export RAPID_OBS_CANTH_MAT="${RAPID_OBS_CANTH_MAT:-/home/jovyan/RAPID_Canth_20042014.mat}"
export RAPID_FIG_OUTPUT="${RAPID_FIG_OUTPUT:-$(pwd)/outputs}"

mkdir -p "$RAPID_FIG_OUTPUT"

echo "RAPID_GCS_BASE      = $RAPID_GCS_BASE"
echo "RAPID_MASK_AREA_PATH = $RAPID_MASK_AREA_PATH"
echo "RAPID_OBS_CANTH_MAT   = $RAPID_OBS_CANTH_MAT"
echo "RAPID_FIG_OUTPUT      = $RAPID_FIG_OUTPUT"

# 若环境缺包再安装（LEAP 上通常不需要）
if [[ "${INSTALL_DEPS:-0}" == "1" ]]; then
  pip install -r requirements.txt
fi

python -c "import xarray, gcsfs, matplotlib; print('Dependencies OK')"
