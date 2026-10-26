#!/usr/bin/env bash
# Set up the environment on a cluster or LEAP (run from inside rapid_figures/analysis)
set -euo pipefail

cd "$(dirname "$0")/.."

# ---------- edit as needed ----------
# LEAP JupyterHub usually provides a notebook environment already; the conda line can stay commented out
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

# Install dependencies only if the environment lacks them (usually not needed on LEAP)
if [[ "${INSTALL_DEPS:-0}" == "1" ]]; then
  pip install -r requirements.txt
fi

python -c "import xarray, gcsfs, matplotlib; print('Dependencies OK')"
