"""Longitude-section diagnostics."""

from __future__ import annotations

import numpy as np
import xarray as xr

from .constants import UNI_PGCYR


def layer_thickness(ds: xr.Dataset) -> xr.DataArray:
    """Thickness of each model level in metres.

    Taken from `lev_bnds` when the store carries it, otherwise from the level
    centres: interfaces half-way between centres, the top at the sea surface,
    the last layer as thick again below its centre as above it.  Partial
    bottom cells are not represented, so the deepest wet cell of a column is
    counted at its nominal thickness.  `lev` in centimetres (CESM2 publishes
    it so) is converted.
    """
    lev = ds["lev"]
    units = str(lev.attrs.get("units", "m")).lower()
    scale = 0.01 if units in ("cm", "centimeters", "centimetres") else 1.0
    if "lev_bnds" in ds:
        b = ds["lev_bnds"]
        bnd = [d for d in b.dims if d != "lev"][-1]           # the (lower, upper) axis
        b = b.isel({d: 0 for d in b.dims if d not in ("lev", bnd)})
        dz = (b.isel({bnd: 1}) - b.isel({bnd: 0})).values * scale
    else:
        z = np.asarray(lev.values, float) * scale
        edges = np.concatenate([[0.0], 0.5 * (z[1:] + z[:-1])])
        edges = np.append(edges, z[-1] + (z[-1] - edges[-1]))
        dz = np.diff(edges)
    return xr.DataArray(np.abs(dz), dims=("lev",), coords={"lev": lev}, name="dz",
                        attrs={"units": "m"})


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

    # C_anth inventory of each column, mol m-2: concentration (mol m-3) times
    # layer thickness (m), summed down the column.
    canth_cum_concentration_lon = (canth * layer_thickness(ds)).sum("lev", skipna=True)
    canth_cum_concentration_lon.attrs["units"] = "mol m-2"

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
