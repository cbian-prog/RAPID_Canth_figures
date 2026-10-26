"""Longitude-section diagnostics."""

from __future__ import annotations

import xarray as xr

from .constants import UNI_PGCYR


def compute_three_lon_sections(
    ds: xr.Dataset,
    area: xr.DataArray,
    start_year: int,
    end_year: int,
    member_mean: bool = True,
    year_mean: bool = True,
) -> xr.Dataset:
    ds = ds.copy()

    if "year" in ds.dims or "year" in ds.coords:
        ds_sel = ds.sel(year=slice(start_year, end_year))
    elif "time" in ds.dims or "time" in ds.coords:
        ds = ds.assign_coords(year=("time", ds.time.dt.year.data))
        ds_sel = ds.where((ds.year >= start_year) & (ds.year <= end_year), drop=True)
    else:
        raise ValueError("Dataset must contain either 'year' or 'time'.")

    vo = ds_sel["vo"]
    canth = ds_sel["dissic"] - ds_sel["dissicnat"]

    vol_transport_cell = vo * area
    canth_transport_cell = canth * vo * area

    volume_transport_lon = vol_transport_cell.sum("lev", skipna=True) / 1e6
    volume_transport_lon.attrs["units"] = "Sv"

    canth_transport_lon = canth_transport_cell.sum("lev", skipna=True) * UNI_PGCYR
    canth_transport_lon.attrs["units"] = "PgC/yr"

    canth_cum_concentration_lon = canth.sum("lev", skipna=True)

    def maybe_mean(da: xr.DataArray) -> xr.DataArray:
        dims = []
        if year_mean:
            dims.extend([d for d in ("year", "time") if d in da.dims])
        if member_mean and "member" in da.dims:
            dims.append("member")
        return da.mean(dim=dims, skipna=True) if dims else da

    return xr.Dataset(
        {
            "canth_transport_lon": maybe_mean(canth_transport_lon),
            "volume_transport_lon": maybe_mean(volume_transport_lon),
            "canth_cum_concentration_lon": maybe_mean(canth_cum_concentration_lon),
        }
    )


def compute_lon_sections_for_all_ssps(
    ds_dict: dict[str, xr.Dataset],
    area: xr.DataArray,
    start_year: int,
    end_year: int,
    exps: tuple[str, ...] = ("ssp126", "ssp245", "ssp585"),
) -> dict[str, xr.Dataset]:
    return {
        exp: compute_three_lon_sections(ds_dict[exp], area, start_year, end_year)
        for exp in exps
    }
