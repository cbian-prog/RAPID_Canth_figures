"""Canth transport budget diagnostics from Test_budget.ipynb.

Contributor decomposition (v0*dC, C0*dV, dV*dC), regional WBC / Non-WBC
transport, and sub-region contributor decompositions. Computed on the SSP
period only (year >= 2015) with baseline = first SSP timestep.
"""

from __future__ import annotations

import xarray as xr

from .constants import UNI_PGCYR
from .config import SSP_START_YEAR

WBC_LON_SLICE = slice(0, 10)
NONWBC_LON_SLICE = slice(10, None)
NONWBC_UPPER_LEV_SLICE = slice(0, 21)
NONWBC_DEEP_LEV_SLICE = slice(21, None)


def _vo_canth(ds: xr.Dataset) -> tuple[xr.DataArray, xr.DataArray]:
    vo = ds["vo"]
    canth = ds["dissic"] - ds["dissicnat"]
    canth.name = "canth"
    return vo, canth


def _time_dim(ds: xr.Dataset) -> str:
    return "time" if "time" in ds.dims else "year"


def slice_ssp_period(ds: xr.Dataset, start_year: int = SSP_START_YEAR) -> xr.Dataset:
    """Keep SSP futures only so budget baseline is the first SSP timestep."""
    if "year" in ds.coords:
        return ds.sel(year=slice(start_year, None))
    raise ValueError("Dataset has no year coordinate for SSP slicing")


def decompose_transport_budget(
    vo: xr.DataArray,
    canth: xr.DataArray,
    area_like: xr.DataArray,
    time_dim: str,
    dims: tuple[str, ...] = ("lev", "lon"),
    baseline: str = "initial",
) -> xr.Dataset:
    """Δ(vC) = v0·ΔC + C0·Δv + Δv·ΔC  (units: PgC yr⁻¹)."""
    area_use = area_like.where(vo.notnull() & canth.notnull())

    if baseline == "initial":
        v0 = vo.isel({time_dim: 0})
        c0 = canth.isel({time_dim: 0})
    elif baseline == "mean":
        v0 = vo.mean(time_dim)
        c0 = canth.mean(time_dim)
    else:
        raise ValueError("baseline must be 'initial' or 'mean'")

    dv = vo - v0
    dc = canth - c0

    total_change = ((vo * canth - v0 * c0) * area_use).sum(dim=dims)
    v0_dc = (v0 * dc * area_use).sum(dim=dims)
    c0_dv = (c0 * dv * area_use).sum(dim=dims)
    dv_dc = (dv * dc * area_use).sum(dim=dims)

    ds_out = xr.Dataset(
        {
            "total_change": total_change,
            "v0_dC": v0_dc,
            "C0_dV": c0_dv,
            "dV_dC": dv_dc,
        }
    )
    for var in ds_out.data_vars:
        ds_out[var] = (ds_out[var] * UNI_PGCYR).astype("float32")
    return ds_out


def compute_regional_canth_transport(
    vo: xr.DataArray,
    canth: xr.DataArray,
    area_like: xr.DataArray,
) -> xr.Dataset:
    """Regional Canth transport: total, WBC, Non-WBC upper/deep (PgC yr⁻¹)."""
    area_use = area_like.where(vo.notnull() & canth.notnull())
    transport = vo * canth * area_use

    total = transport.sum(dim=("lev", "lon"))
    wbc = transport.isel(lon=WBC_LON_SLICE).sum(dim=("lev", "lon"))

    nonwbc = transport.isel(lon=NONWBC_LON_SLICE)
    nonwbc_upper = nonwbc.isel(lev=NONWBC_UPPER_LEV_SLICE).sum(dim=("lev", "lon"))
    nonwbc_deep = nonwbc.isel(lev=NONWBC_DEEP_LEV_SLICE).sum(dim=("lev", "lon"))

    ds_out = xr.Dataset(
        {
            "total_canth_transport": total,
            "WBC": wbc,
            "NonWBC_0_700m": nonwbc_upper,
            "NonWBC_700m_bottom": nonwbc_deep,
        }
    )
    for var in ds_out.data_vars:
        ds_out[var] = (ds_out[var] * UNI_PGCYR).astype("float32")
    return ds_out


def decompose_transport_region(
    vo: xr.DataArray,
    canth: xr.DataArray,
    area_like: xr.DataArray,
    time_dim: str,
    lon_slice: slice | None = None,
    lev_slice: slice | None = None,
    baseline: str = "initial",
) -> xr.Dataset:
    """Contributor decomposition over a lon/lev sub-region."""
    vo_reg = vo
    canth_reg = canth
    area_reg = area_like

    if lon_slice is not None:
        vo_reg = vo_reg.isel(lon=lon_slice)
        canth_reg = canth_reg.isel(lon=lon_slice)
        area_reg = area_reg.isel(lon=lon_slice)

    if lev_slice is not None:
        vo_reg = vo_reg.isel(lev=lev_slice)
        canth_reg = canth_reg.isel(lev=lev_slice)
        area_reg = area_reg.isel(lev=lev_slice)

    return decompose_transport_budget(
        vo_reg, canth_reg, area_reg, time_dim=time_dim, baseline=baseline
    )


def _budget_for_dataset(ds: xr.Dataset, area_like: xr.DataArray) -> dict[str, xr.Dataset]:
    ds_ssp = slice_ssp_period(ds)
    vo, canth = _vo_canth(ds_ssp)
    tdim = _time_dim(ds_ssp)

    budget_decomp = decompose_transport_budget(vo, canth, area_like, time_dim=tdim)
    regional = compute_regional_canth_transport(vo, canth, area_like)

    wbc_decomp = decompose_transport_region(
        vo, canth, area_like, time_dim=tdim, lon_slice=WBC_LON_SLICE
    )
    nonwbc_upper_decomp = decompose_transport_region(
        vo,
        canth,
        area_like,
        time_dim=tdim,
        lon_slice=NONWBC_LON_SLICE,
        lev_slice=NONWBC_UPPER_LEV_SLICE,
    )

    subregion = xr.Dataset()
    for var in wbc_decomp.data_vars:
        subregion[f"wbc_{var}"] = wbc_decomp[var]
    for var in nonwbc_upper_decomp.data_vars:
        subregion[f"nonwbc_upper_{var}"] = nonwbc_upper_decomp[var]

    return {
        "budget_decomp": budget_decomp,
        "regional_canth": regional,
        "subregion_decomp": subregion,
    }


def compute_budget_dicts(
    masked_annual: dict[str, xr.Dataset],
    masked_monthly: dict[str, xr.Dataset],
    area_like: xr.DataArray,
) -> tuple[dict[str, dict[str, xr.Dataset]], dict[str, dict[str, xr.Dataset]]]:
    """Return annual and monthly budget diagnostic dicts keyed by experiment."""
    annual: dict[str, dict[str, xr.Dataset]] = {}
    monthly: dict[str, dict[str, xr.Dataset]] = {}
    for exp, ds in masked_annual.items():
        annual[exp] = _budget_for_dataset(ds, area_like)
    for exp, ds in masked_monthly.items():
        monthly[exp] = _budget_for_dataset(ds, area_like)
    return annual, monthly
