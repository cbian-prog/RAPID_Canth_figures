"""Load and concatenate historical + SSP RAPID-section datasets."""

from __future__ import annotations

import numpy as np
import xarray as xr

from .config import EXPERIMENTS, GCS_BASE_PATH, SSP_EXPERIMENTS
from .io import get_fs, load_mask_and_area, open_rapid_zarr


def concat_historical_with_ssp_annual(hist_ds: xr.Dataset, ssp_ds: xr.Dataset) -> tuple[xr.Dataset, np.ndarray]:
    hist_members = hist_ds["member"].values
    ssp_members = ssp_ds["member"].values
    common_members = np.intersect1d(hist_members, ssp_members)
    if len(common_members) == 0:
        raise ValueError("No common members between historical and SSP annual dataset.")

    hist_sel = hist_ds.sel(member=common_members).sortby("year")
    ssp_sel = ssp_ds.sel(member=common_members).sortby("year")
    ds_concat = xr.concat([hist_sel, ssp_sel], dim="year")

    _, unique_idx = np.unique(ds_concat["year"].values, return_index=True)
    ds_concat = ds_concat.isel(year=np.sort(unique_idx))
    return ds_concat, common_members


def concat_historical_with_ssp_monthly(hist_ds: xr.Dataset, ssp_ds: xr.Dataset) -> tuple[xr.Dataset, np.ndarray]:
    hist_members = hist_ds["member"].values
    ssp_members = ssp_ds["member"].values
    common_members = np.intersect1d(hist_members, ssp_members)
    if len(common_members) == 0:
        raise ValueError("No common members between historical and SSP monthly dataset.")

    hist_sel = hist_ds.sel(member=common_members)
    ssp_sel = ssp_ds.sel(member=common_members)

    n_hist = hist_sel.sizes["time"]
    hist_year = np.repeat(np.arange(1850, 2015), 12)
    hist_month = np.tile(np.arange(1, 13), 2015 - 1850)
    if len(hist_year) != n_hist:
        raise ValueError(f"Historical monthly length mismatch: expected {len(hist_year)}, got {n_hist}")

    hist_sel = hist_sel.assign_coords(
        time=np.arange(n_hist),
        year=("time", hist_year),
        month=("time", hist_month),
    )

    n_ssp = ssp_sel.sizes["time"]
    ssp_year = np.repeat(np.arange(2015, 2101), 12)
    ssp_month = np.tile(np.arange(1, 13), 2101 - 2015)
    if len(ssp_year) != n_ssp:
        raise ValueError(f"SSP monthly length mismatch: expected {len(ssp_year)}, got {n_ssp}")

    ssp_sel = ssp_sel.assign_coords(
        time=np.arange(n_hist, n_hist + n_ssp),
        year=("time", ssp_year),
        month=("time", ssp_month),
    )

    ds_concat = xr.concat([hist_sel, ssp_sel], dim="time")
    return ds_concat, common_members


def _apply_mask(ds: xr.Dataset, mask: xr.DataArray) -> xr.Dataset:
    mask_like = xr.DataArray(
        mask.data,
        dims=("lev", "lon"),
        coords={"lev": ds["lev"], "lon": ds["lon"]},
        name="mask",
    )
    return ds.where(mask_like.notnull())


def build_masked_concat_dicts() -> tuple[dict[str, xr.Dataset], dict[str, xr.Dataset], xr.DataArray]:
    """Return annual dict, monthly dict, and area_like for SSP experiments."""
    annual_dict = {exp: open_rapid_zarr(exp, "annual") for exp in EXPERIMENTS}
    monthly_dict = {exp: open_rapid_zarr(exp, "monthly") for exp in EXPERIMENTS}
    mask, area = load_mask_and_area()

    hist_annual = annual_dict["historical"]
    hist_monthly = monthly_dict["historical"]

    masked_annual: dict[str, xr.Dataset] = {}
    masked_monthly: dict[str, xr.Dataset] = {}

    for exp in SSP_EXPERIMENTS:
        ds_a, _ = concat_historical_with_ssp_annual(hist_annual, annual_dict[exp])
        ds_m, _ = concat_historical_with_ssp_monthly(hist_monthly, monthly_dict[exp])
        masked_annual[exp] = _apply_mask(ds_a, mask)
        masked_monthly[exp] = _apply_mask(ds_m, mask)

    ref_ds = masked_annual[SSP_EXPERIMENTS[-1]]
    area_like = xr.DataArray(
        area.data,
        dims=("lev", "lon"),
        coords={"lev": ref_ds["lev"], "lon": ref_ds["lon"]},
        name="area",
    )
    return masked_annual, masked_monthly, area_like
