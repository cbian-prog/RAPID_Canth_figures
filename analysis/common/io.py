"""I/O helpers: load mask/area, save and load intermediate results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import gcsfs
import numpy as np
import xarray as xr

from .config import GCS_BASE_PATH, MASK_AREA_PATH


def get_fs() -> gcsfs.GCSFileSystem:
    return gcsfs.GCSFileSystem()


def load_mask_and_area(mask_path: Path | None = None) -> tuple[xr.DataArray, xr.DataArray]:
    """Load RAPID section mask and area.

    Tries local NetCDF first, then falls back to GCS area zarr (mask = area > 0).
    """
    path = mask_path or MASK_AREA_PATH
    if path.exists():
        ds_aux = xr.open_dataset(path)
        return ds_aux["mask"], ds_aux["area"]

    fs = get_fs()
    area = xr.open_zarr(
        fs.get_mapper(f"{GCS_BASE_PATH}/RAPID_section_area.zarr"),
        consolidated=True,
    )["area"]
    mask = xr.where(area > 0, 1.0, np.nan)
    mask.name = "mask"
    return mask, area


def open_rapid_zarr(experiment: str, temporal: str) -> xr.Dataset:
    """Open ``{experiment}_{temporal}_vars_RAPID.zarr`` from GCS."""
    if temporal not in {"annual", "monthly"}:
        raise ValueError("temporal must be 'annual' or 'monthly'")
    fs = get_fs()
    path = f"{GCS_BASE_PATH}/{experiment}_{temporal}_vars_RAPID.zarr"
    return xr.open_zarr(fs.get_mapper(path), consolidated=True)


def save_dataset(ds: xr.Dataset, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ds.to_netcdf(path)


def load_dataset(path: Path) -> xr.Dataset:
    return xr.open_dataset(path)


def save_dict_of_datasets(data: dict[str, xr.Dataset], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for key, ds in data.items():
        save_dataset(ds, directory / f"{key}.nc")


def load_dict_of_datasets(directory: Path, keys: list[str]) -> dict[str, xr.Dataset]:
    return {key: load_dataset(directory / f"{key}.nc") for key in keys}


def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str)
