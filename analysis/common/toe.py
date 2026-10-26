"""Time of Emergence (ToE) from annual transport time series."""

from __future__ import annotations

import numpy as np
import xarray as xr


def compute_toe_from_yearly_da(
    da: xr.DataArray,
    start_year: int = 2004,
    step_years: int = 1,
    threshold: float = 2.0,
    require_persistence: bool = True,
) -> tuple[xr.Dataset, dict | None]:
    if "year" not in da.dims:
        raise ValueError("Input DataArray must have dimension 'year'.")
    if step_years < 1:
        raise ValueError("step_years must be >= 1.")

    da = da.where(da["year"] >= start_year, drop=True)
    if da.sizes["year"] < 2:
        raise ValueError("Not enough yearly data after the requested start year.")

    if hasattr(da.data, "chunks"):
        da = da.chunk({"year": -1})

    nyear = da.sizes["year"]
    first_end_idx = max(1, step_years - 1)
    window_end_idx = np.arange(first_end_idx, nyear, step_years)

    slopes = []
    end_years = []

    def _slope_1d(y, x):
        mask = np.isfinite(y) & np.isfinite(x)
        if mask.sum() < 2:
            return np.nan
        return np.polyfit(x[mask], y[mask], 1)[0]

    for end_idx in window_end_idx:
        win = da.isel(year=slice(0, int(end_idx) + 1))
        if hasattr(win.data, "chunks"):
            win = win.chunk({"year": -1})

        t_rel = xr.DataArray(
            np.arange(win.sizes["year"], dtype=float),
            dims="year",
            coords={"year": win["year"]},
        )
        slope = xr.apply_ufunc(
            _slope_1d,
            win,
            t_rel,
            input_core_dims=[["year"], ["year"]],
            output_core_dims=[[]],
            vectorize=True,
            dask="parallelized",
            output_dtypes=[float],
        )
        slopes.append(slope)
        end_years.append(int(win["year"].isel(year=-1).item()))

    slopes = xr.concat(slopes, dim="window_end").assign_coords(
        window_end=np.arange(len(window_end_idx)),
        end_year=("window_end", np.array(end_years)),
    )

    if "member" not in slopes.dims:
        raise ValueError("ToE calculation requires a 'member' dimension.")
    if slopes.sizes["member"] < 2:
        raise ValueError("At least 2 members are required to estimate noise_std.")

    forced_trend = slopes.mean("member", skipna=True)
    noise_std = slopes.std("member", ddof=1, skipna=True)
    snr = xr.where(noise_std > 0, np.abs(forced_trend) / noise_std, np.nan)

    ds_snr = xr.Dataset(
        {
            "forced_trend": forced_trend,
            "noise_std": noise_std,
            "snr": snr,
        }
    ).assign_coords(end_year=("window_end", np.array(end_years)))

    good = np.asarray(ds_snr["snr"] > threshold)
    toe_info = None

    if require_persistence:
        for i in range(len(window_end_idx)):
            if good[i] and np.all(good[i:]):
                toe_info = {"toe_index": int(i), "toe_year": int(end_years[i])}
                break
    else:
        idx = np.where(good)[0]
        if len(idx) > 0:
            i = int(idx[0])
            toe_info = {"toe_index": i, "toe_year": int(end_years[i])}

    return ds_snr, toe_info


def compute_toe_for_all_variables(
    annual_transport_dict: dict[str, xr.Dataset],
    exps: tuple[str, ...] = ("ssp126", "ssp245", "ssp585"),
    varnames: tuple[str, ...] = (
        "volume_transport",
        "amoc_strength",
        "canth_transport",
        "canth_mean_concentration",
    ),
    start_year: int = 2004,
    step_years: int = 5,
    threshold: float = 2.0,
    require_persistence: bool = True,
    skip_if_insufficient_members: bool = True,
) -> tuple[dict, dict]:
    toe_dict: dict = {}
    snr_dict: dict = {}

    for exp in exps:
        toe_dict[exp] = {}
        snr_dict[exp] = {}
        for varname in varnames:
            da = annual_transport_dict[exp][varname]
            if skip_if_insufficient_members and "member" in da.dims and da.sizes["member"] < 2:
                toe_dict[exp][varname] = None
                snr_dict[exp][varname] = None
                continue
            try:
                ds_snr, toe_info = compute_toe_from_yearly_da(
                    da,
                    start_year=start_year,
                    step_years=step_years,
                    threshold=threshold,
                    require_persistence=require_persistence,
                )
                snr_dict[exp][varname] = ds_snr
                toe_dict[exp][varname] = toe_info
            except ValueError:
                toe_dict[exp][varname] = None
                snr_dict[exp][varname] = None

    return toe_dict, snr_dict
