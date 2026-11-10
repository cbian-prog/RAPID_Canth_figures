"""Shared configuration for RAPID figure scripts."""

from __future__ import annotations

import os
from pathlib import Path

# Repository layout
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_ROOT = Path(os.environ.get("RAPID_FIG_OUTPUT", PACKAGE_ROOT / "outputs"))

# GCS data
GCS_BASE_PATH = os.environ.get(
    "RAPID_GCS_BASE", "gs://leap-persistent/cbian-prog"
)

# Local mask/area file (LEAP JupyterHub default)
MASK_AREA_PATH = Path(
    os.environ.get("RAPID_MASK_AREA_PATH", "/home/jovyan/RAPID_mask_area.nc")
)

EXPERIMENTS = ["historical", "ssp126", "ssp245", "ssp585"]
SSP_EXPERIMENTS = ["ssp126", "ssp245", "ssp585"]
SSP_START_YEAR = int(os.environ.get("RAPID_SSP_START", "2015"))

# ROCCA figure 1 (CMIP6 vs RAPID obs, 2004–2014)
ROCCA_YEAR_START = int(os.environ.get("RAPID_ROCCA_YEAR_START", "2004"))
ROCCA_YEAR_END = int(os.environ.get("RAPID_ROCCA_YEAR_END", "2014"))
OBS_CANTH_MAT_PATH = Path(
    os.environ.get(
        "RAPID_OBS_CANTH_MAT",
        "/home/jovyan/RAPID_Canth_20042014.mat",
    )
)

# Analysis defaults
PROFILE_YEAR_START = int(os.environ.get("RAPID_PROFILE_START", "2004"))
PROFILE_YEAR_END = int(os.environ.get("RAPID_PROFILE_END", "2014"))

TOE_START_YEAR = int(os.environ.get("RAPID_TOE_START", "2004"))
TOE_STEP_YEARS = int(os.environ.get("RAPID_TOE_STEP", "5"))
TOE_THRESHOLD = float(os.environ.get("RAPID_TOE_THRESHOLD", "2.0"))

TREND_START_1 = int(os.environ.get("RAPID_TREND_START_1", "2004"))
TREND_END_1 = int(os.environ.get("RAPID_TREND_END_1", "2050"))
TREND_START_2 = int(os.environ.get("RAPID_TREND_START_2", "2050"))
TREND_END_2 = int(os.environ.get("RAPID_TREND_END_2", "2100"))


def data_dir() -> Path:
    out = OUTPUT_ROOT / "data"
    out.mkdir(parents=True, exist_ok=True)
    return out
