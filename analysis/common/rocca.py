"""ROCCA figure 1: CMIP6 vs RAPID observations (2004–2014).

Loads pre-computed Canth budget time series from GCS
(``cmip6_NA_Canth_budget_time/*RAPID_20042014.zarr``) and RAPID obs from a
``.mat`` file for plotting in ``plot.py``.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import scipy.io
import xarray as xr

from .config import GCS_BASE_PATH, OBS_CANTH_MAT_PATH, ROCCA_YEAR_END, ROCCA_YEAR_START
from .io import get_fs, save_dataset

ROCCA_VARS = [
    "total_trans_time_seri",
    "overturning_transport_time_seri",
    "horizontal_transport_time_seri",
]
ROCCA_OBS_VARS = ["total", "overturning", "horizontal"]
ROCCA_N_MONTHS = 132


def rocca_time_axis() -> np.ndarray:
    """Monthly decimal-year axis, 2004-2014: the middle of each month.

    Months are 1/12 yr apart.  (The notebook spread 132 points evenly from
    2004.0 to 2015.0, i.e. 11/131 yr apart, which put the model up to a month
    behind the observations by 2014.)
    """
    n = 12 * (ROCCA_YEAR_END - ROCCA_YEAR_START + 1)
    if n != ROCCA_N_MONTHS:
        raise ValueError(f"{ROCCA_YEAR_START}-{ROCCA_YEAR_END} is {n} months, "
                         f"but the budget files hold {ROCCA_N_MONTHS}")
    return ROCCA_YEAR_START + (np.arange(n) + 0.5) / 12.0


def list_budget_time_files(keyword: str = "RAPID_20042014") -> list[str]:
    fs = get_fs()
    bucket = f"{GCS_BASE_PATH}/cmip6_NA_Canth_budget_time"
    return sorted(path for path in fs.ls(bucket) if keyword in path)


def _gcs_mapper(path: str):
    fs = get_fs()
    if path.startswith("gs://"):
        return fs.get_mapper(path)
    return fs.get_mapper(f"gs://{path}")


def _member_name(path: str) -> str:
    return Path(path).name.replace(".zarr", "")


def load_member_series(files: list[str]) -> xr.Dataset | None:
    """Load CMIP6 member time series into Dataset(member, time)."""
    if not files:
        return None

    time_axis = rocca_time_axis()
    members: list[str] = []
    stacks: dict[str, list[np.ndarray]] = {var: [] for var in ROCCA_VARS}

    for file in files:
        try:
            ds = xr.open_zarr(_gcs_mapper(file), consolidated=True)
            members.append(_member_name(file))
            for var in ROCCA_VARS:
                if var not in ds:
                    raise KeyError(var)
                values = np.asarray(ds[var].squeeze().values, dtype=float)
                if values.size < ROCCA_N_MONTHS:
                    raise ValueError(f"{file}: expected >= {ROCCA_N_MONTHS} points, got {values.size}")
                stacks[var].append(values[:ROCCA_N_MONTHS])
        except Exception as exc:
            print(f"Warning: skip {file}: {exc}")

    if not members:
        return None

    data_vars = {}
    for var in ROCCA_VARS:
        if stacks[var]:
            data_vars[var] = xr.DataArray(
                np.stack(stacks[var]),
                dims=("member", "time"),
                coords={"member": members[: len(stacks[var])], "time": time_axis},
            )

    return xr.Dataset(data_vars) if data_vars else None


def load_obs(mat_path: Path | None = None) -> xr.Dataset:
    path = mat_path or OBS_CANTH_MAT_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"RAPID obs file not found: {path}\n"
            "Set RAPID_OBS_CANTH_MAT to the path of RAPID_Canth_20042014.mat"
        )

    data = scipy.io.loadmat(str(path))
    time_obs = np.squeeze(data["time"]).astype(float)
    return xr.Dataset(
        {
            "total": ("time_obs", np.squeeze(data["total"]).astype(float)),
            "overturning": ("time_obs", np.squeeze(data["overturning"]).astype(float)),
            "horizontal": ("time_obs", np.squeeze(data["horizontal"]).astype(float)),
            "time_obs": time_obs,
        }
    )


def build_rocca_datasets(mat_path: Path | None = None) -> dict[str, xr.Dataset]:
    all_files = list_budget_time_files()
    if not all_files:
        raise FileNotFoundError(
            f"No RAPID_20042014 zarr files under {GCS_BASE_PATH}/cmip6_NA_Canth_budget_time"
        )

    cmip6_all = load_member_series(all_files)
    if cmip6_all is None:
        raise RuntimeError("Failed to load any CMIP6 RAPID_20042014 member files")

    cesm2 = load_member_series([f for f in all_files if "CESM2" in f])
    canesm5 = load_member_series([f for f in all_files if "CanESM5" in f])
    obs = load_obs(mat_path)

    out = {"cmip6_all": cmip6_all, "obs": obs}
    if cesm2 is not None:
        out["cesm2"] = cesm2
    if canesm5 is not None:
        out["canesm5"] = canesm5
    return out


def save_rocca_datasets(datasets: dict[str, xr.Dataset], out_dir: Path) -> None:
    rocca_dir = out_dir / "rocca"
    rocca_dir.mkdir(parents=True, exist_ok=True)
    for name, ds in datasets.items():
        save_dataset(ds, rocca_dir / f"{name}.nc")
