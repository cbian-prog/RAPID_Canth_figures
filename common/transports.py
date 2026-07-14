"""Transport diagnostics on masked RAPID-section datasets."""

from __future__ import annotations

import xarray as xr

from .constants import UNI_PGCYR
from .config import SSP_EXPERIMENTS


def calc_transports(ds: xr.Dataset, area_like: xr.DataArray, carbon_unit: float = UNI_PGCYR) -> xr.Dataset:
    """Compute member-resolved volume, AMOC, and carbon transports."""
    canth = ds["dissic"] - ds["dissicnat"]
    total_area = area_like.sum(dim=("lon", "lev"))

    volume_transport = (ds["vo"] * area_like / 1e6).sum(dim=("lon", "lev"))
    volume_transport.name = "volume_transport"

    transport_z = (ds["vo"] * area_like / 1e6).sum(dim="lon")
    transport_z.name = "transport_z"

    psi = -transport_z.isel(lev=slice(None, None, -1)).cumsum(dim="lev")
    psi = psi.isel(lev=slice(None, None, -1))
    psi.name = "overturning_streamfunction"

    amoc_strength = psi.max(dim="lev")
    amoc_strength.name = "amoc_strength"

    amoc_depth = psi.idxmax(dim="lev")
    amoc_depth.name = "amoc_depth"

    canth_transport = (ds["vo"] * canth * area_like).sum(dim=("lon", "lev")) * carbon_unit
    canth_transport.name = "canth_transport"

    dissic_transport = (ds["vo"] * ds["dissic"] * area_like).sum(dim=("lon", "lev")) * carbon_unit
    dissic_transport.name = "dissic_transport"

    dissicnat_transport = (ds["vo"] * ds["dissicnat"] * area_like).sum(dim=("lon", "lev")) * carbon_unit
    dissicnat_transport.name = "dissicnat_transport"

    canth_mean_concentration = (canth * area_like).sum(dim=("lon", "lev")) / total_area
    canth_mean_concentration.name = "canth_mean_concentration"

    return xr.Dataset(
        {
            "volume_transport": volume_transport,
            "amoc_strength": amoc_strength,
            "amoc_depth": amoc_depth,
            "canth_transport": canth_transport,
            "dissic_transport": dissic_transport,
            "dissicnat_transport": dissicnat_transport,
            "canth_mean_concentration": canth_mean_concentration,
            "transport_z": transport_z,
            "overturning_streamfunction": psi,
        }
    )


def build_transport_dicts(
    masked_annual: dict[str, xr.Dataset],
    masked_monthly: dict[str, xr.Dataset],
    area_like: xr.DataArray,
) -> tuple[dict[str, xr.Dataset], dict[str, xr.Dataset]]:
    annual_transport = {exp: calc_transports(ds, area_like) for exp, ds in masked_annual.items()}
    monthly_transport = {exp: calc_transports(ds, area_like) for exp, ds in masked_monthly.items()}
    return annual_transport, monthly_transport


def ensure_transport_dicts(cache_dir) -> tuple[dict[str, xr.Dataset], dict[str, xr.Dataset]]:
    """Load cached transport dicts or compute and cache them."""
    from pathlib import Path

    from .data_pipeline import build_masked_concat_dicts
    from .io import load_dict_of_datasets, save_dict_of_datasets

    cache_dir = Path(cache_dir)
    annual_dir = cache_dir / "annual_transport"
    monthly_dir = cache_dir / "monthly_transport"
    marker = cache_dir / "transport_ready.txt"

    if marker.exists():
        return (
            load_dict_of_datasets(annual_dir, SSP_EXPERIMENTS),
            load_dict_of_datasets(monthly_dir, SSP_EXPERIMENTS),
        )

    masked_annual, masked_monthly, area_like = build_masked_concat_dicts()
    annual_transport, monthly_transport = build_transport_dicts(
        masked_annual, masked_monthly, area_like
    )
    save_dict_of_datasets(annual_transport, annual_dir)
    save_dict_of_datasets(monthly_transport, monthly_dir)
    marker.write_text("ok\n", encoding="utf-8")
    return annual_transport, monthly_transport
