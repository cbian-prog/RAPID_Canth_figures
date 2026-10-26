"""Linear trend statistics."""

from __future__ import annotations

import pandas as pd
import xarray as xr


def compute_trend_stats_for_var(da: xr.DataArray, start_year: int, end_year: int) -> dict:
    da_sel = da.sel(year=slice(start_year, end_year))
    fit = da_sel.polyfit(dim="year", deg=1)
    trend = fit["polyfit_coefficients"].sel(degree=1)
    trend.name = f"{da.name}_trend"

    if "member" in trend.dims:
        trend_mean = trend.mean(dim="member")
        trend_std = trend.std(dim="member")
    else:
        trend_mean = trend
        trend_std = xr.full_like(trend_mean, float("nan"))

    return {
        "trend_each_member": trend,
        "trend_mean": trend_mean,
        "trend_std": trend_std,
    }


def compute_trends_all_vars(
    transport_dict: dict[str, xr.Dataset],
    var_list: list[str],
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    rows = []
    for exp, ds in transport_dict.items():
        for var in var_list:
            out = compute_trend_stats_for_var(ds[var], start_year, end_year)
            rows.append(
                {
                    "experiment": exp,
                    "variable": var,
                    "start_year": start_year,
                    "end_year": end_year,
                    "trend_mean": float(out["trend_mean"].values),
                    "trend_std": float(out["trend_std"].values),
                }
            )
    return pd.DataFrame(rows)
