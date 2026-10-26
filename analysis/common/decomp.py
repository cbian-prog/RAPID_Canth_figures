"""Canth transport decomposition: total = overturning + horizontal."""

from __future__ import annotations

import xarray as xr

from .constants import UNI_PGCYR_ALT


def compute_canth_decomp(ds: xr.Dataset, area_like: xr.DataArray) -> xr.Dataset:
    """Decompose Canth transport into overturning and horizontal components."""
    v = ds["vo"]
    c = ds["dissic"] - ds["dissicnat"]
    v, c = xr.align(v, c, join="inner")

    template_dims = {d: 0 for d in v.dims if d not in area_like.dims}
    area = area_like.broadcast_like(v.isel(template_dims, drop=True))
    valid_mask = (
        xr.ufuncs.isfinite(area)
        & xr.ufuncs.isfinite(v).any("time" if "time" in v.dims else "year")
        & xr.ufuncs.isfinite(c).any("time" if "time" in c.dims else "year")
    )
    v = v.where(valid_mask)
    c = c.where(valid_mask)
    area = area.where(valid_mask)

    v_bar = v.mean("lon", skipna=True).broadcast_like(v)
    c_bar = c.mean("lon", skipna=True).broadcast_like(c)

    total = ((v * c) * area).sum(("lev", "lon"), skipna=True) * UNI_PGCYR_ALT
    overturning = ((v_bar * c_bar) * area).sum(("lev", "lon"), skipna=True) * UNI_PGCYR_ALT
    horizontal = total - overturning

    return xr.Dataset(
        {
            "total_trans_time_seri": total.astype("float32"),
            "overturning_transport_time_seri": overturning.astype("float32"),
            "horizontal_transport_time_seri": horizontal.astype("float32"),
        }
    )


def compute_decomp_dict(
    data_dict: dict[str, xr.Dataset],
    area_like: xr.DataArray,
) -> dict[str, xr.Dataset]:
    return {exp: compute_canth_decomp(ds, area_like) for exp, ds in data_dict.items()}
