#!/usr/bin/env python3
"""
RAPID 图表 — 绘图程序（只绘图，不计算）

读取 compute.py 生成的 outputs/data/，输出全部 PNG 到 outputs/figures/。

用法:
    python plot.py
    RAPID_FIG_OUTPUT=/path/to/out python plot.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common.config import SSP_EXPERIMENTS, data_dir, figures_dir  # noqa: E402
from common.constants import (  # noqa: E402
    BUDGET_DECOMP_META,
    BUDGET_NONWBC_DECOMP_META,
    BUDGET_REGION_META,
    BUDGET_WBC_DECOMP_META,
    COLOR_DICT,
    LABEL_DICT,
    ROCCA_COLORS,
    ROCCA_LABELS,
    ROCCA_MID_COLORS,
    TOE_PLOT_META,
    TRANSPORT_PLOT_META,
)
from common.io import load_dict_of_datasets, load_json  # noqa: E402
from common.rocca import ROCCA_OBS_VARS, ROCCA_VARS, load_rocca_datasets  # noqa: E402


def _require_data(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}\nRun compute.py first:  python compute.py"
        )


def _load_all(data: Path) -> dict:
    _require_data(data / "meta.json")
    exps = list(SSP_EXPERIMENTS)
    payload = {
        "annual_transport": load_dict_of_datasets(data / "annual_transport", exps),
        "monthly_transport": load_dict_of_datasets(data / "monthly_transport", exps),
        "annual_decomp": load_dict_of_datasets(data / "annual_decomp", exps),
        "monthly_decomp": load_dict_of_datasets(data / "monthly_decomp", exps),
        "profiles": load_dict_of_datasets(data / "profiles", exps),
        "sections": load_dict_of_datasets(data / "sections", exps),
        "toe_dict": load_json(data / "toe_dict.json"),
        "meta": json.loads((data / "meta.json").read_text(encoding="utf-8")),
    }
    budget_keys = ("budget_decomp", "regional_canth", "subregion_decomp")
    for freq in ("annual", "monthly"):
        for key in budget_keys:
            path = data / f"{freq}_{key}"
            if path.exists():
                payload[f"{freq}_{key}"] = load_dict_of_datasets(path, exps)
    return payload


# ---------------------------------------------------------------------------
# Figure 1: annual + monthly Canth decomposition
# ---------------------------------------------------------------------------
def plot_canth_decomp(annual_decomp, monthly_decomp, figdir: Path) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(12, 9))
    for exp in SSP_EXPERIMENTS:
        ds = annual_decomp[exp]
        x = ds["year"].values
        color = COLOR_DICT[exp]
        label = LABEL_DICT[exp]
        over = ds["overturning_transport_time_seri"]
        hori = ds["horizontal_transport_time_seri"]
        axes[0].plot(x, over.mean("member"), color=color, ls="-", lw=2, label=f"{label} Overturning")
        axes[0].fill_between(x, over.mean("member") - over.std("member"), over.mean("member") + over.std("member"), color=color, alpha=0.15)
        axes[0].plot(x, hori.mean("member"), color=color, ls="--", lw=2, label=f"{label} Horizontal")
        axes[0].fill_between(x, hori.mean("member") - hori.std("member"), hori.mean("member") + hori.std("member"), color=color, alpha=0.15)

    axes[0].set_ylabel("Canth Transport (PgC/yr)")
    axes[0].set_xlim(2014, 2101)
    axes[0].legend(fontsize=12, ncol=3)
    axes[0].text(-0.1, 1.1, "a", transform=axes[0].transAxes, fontsize=22, fontweight="bold", va="top")

    for exp in SSP_EXPERIMENTS:
        ds = monthly_decomp[exp]
        x = ds["year"].values + (ds["month"].values - 1) / 12.0
        color = COLOR_DICT[exp]
        over = ds["overturning_transport_time_seri"]
        hori = ds["horizontal_transport_time_seri"]
        axes[1].plot(x, over.mean("member"), color=color, ls="-", lw=2)
        axes[1].fill_between(x, over.mean("member") - over.std("member"), over.mean("member") + over.std("member"), color=color, alpha=0.15)
        axes[1].plot(x, hori.mean("member"), color=color, ls="--", lw=2)
        axes[1].fill_between(x, hori.mean("member") - hori.std("member"), hori.mean("member") + hori.std("member"), color=color, alpha=0.15)

    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Canth Transport (PgC/yr)")
    axes[1].set_xlim(2014, 2101)
    axes[1].text(-0.1, 1.1, "b", transform=axes[1].transAxes, fontsize=22, fontweight="bold", va="top")

    plt.tight_layout()
    path = figdir / "01_annual_monthly_decomp.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Figure 2: vertical profiles
# ---------------------------------------------------------------------------
def plot_vertical_profiles(profiles, meta, figdir: Path) -> Path:
    y0, y1 = meta["profile_start"], meta["profile_end"]
    fig, axes = plt.subplots(1, 3, figsize=(14, 6), sharey=True)
    var_list = [
        "canth_transport_profile_top_to_bottom",
        "volume_transport_profile_top_to_bottom",
        "canth_mean_concentration_profile",
    ]
    titles = ["Canth transport", "Volume transport", "Mean Canth concentration"]
    xlabels = ["(PgC/yr)", "(Sv)", "(mol m$^{-3}$)"]

    for exp in SSP_EXPERIMENTS:
        ds = profiles[exp]
        lev = ds["lev"]
        for ax, var, title, xlab in zip(axes, var_list, titles, xlabels):
            ax.plot(ds[var], lev, color=COLOR_DICT[exp], label=LABEL_DICT[exp], linewidth=2)
            ax.set_title(title, fontsize=16)
            ax.set_xlabel(xlab, fontsize=16)
            ax.set_ylabel("Depth (m)", fontsize=16)
            ax.grid(True, alpha=0.3)

    axes[0].invert_yaxis()
    axes[0].legend(frameon=False, fontsize=16)
    plt.tight_layout()
    path = figdir / f"02_vertical_profiles_{y0}_{y1}.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Figure 3: longitude sections
# ---------------------------------------------------------------------------
def plot_lon_sections(sections, meta, figdir: Path) -> Path:
    y0, y1 = meta["profile_start"], meta["profile_end"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharex=True)
    var_list = ["canth_transport_lon", "volume_transport_lon", "canth_cum_concentration_lon"]
    titles = [
        "Canth transport at each location",
        "Volume transport at each location",
        "Canth amount at each location",
    ]
    ylabels = ["(PgC/yr)", "(Sv)", "(mol m$^{-2}$)"]

    for exp in SSP_EXPERIMENTS:
        ds = sections[exp]
        lon = ds["lon"]
        lon_w = xr.where(lon > 180, 360 - lon, -lon) - 0.5
        sort_idx = np.argsort(lon_w.values)
        lon_sorted = lon_w.values[sort_idx]
        for ax, var, title, ylab in zip(axes, var_list, titles, ylabels):
            ax.plot(lon_sorted, ds[var].isel(lon=sort_idx), color=COLOR_DICT[exp], label=LABEL_DICT[exp], lw=2)
            ax.set_title(title)
            ax.set_xlabel("Longitude")
            ax.set_ylabel(ylab)
            ax.grid(True, alpha=0.3)

    lon0 = sections[SSP_EXPERIMENTS[0]]["lon"]
    lon0_w = xr.where(lon0 > 180, 360 - lon0, -lon0) + 0.5
    lon_sorted0 = np.sort(lon0_w.values)
    ticks = np.arange(int(lon_sorted0.min() // 20 * 20), int(lon_sorted0.max() // 20 * 20 + 21), 20)
    for ax in axes:
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"{x}°W" for x in ticks])
        ax.set_xlim(lon_sorted0.max(), lon_sorted0.min())
    axes[0].legend(frameon=False)
    plt.tight_layout()
    path = figdir / f"03_lon_sections_{y0}_{y1}.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Figures 4–7: annual transport time series
# ---------------------------------------------------------------------------
def plot_transport_ts(annual_transport, varname: str, figdir: Path, ylim=None, figsize=(10, 4)) -> Path:
    meta = TRANSPORT_PLOT_META[varname]
    plt.figure(figsize=figsize)
    for exp in SSP_EXPERIMENTS:
        da = annual_transport[exp][varname]
        m = da.mean("member") if "member" in da.dims else da
        s = da.std("member") if "member" in da.dims else None
        x, y = m["year"].values, m.values
        plt.plot(x, y, color=COLOR_DICT[exp], lw=2, label=LABEL_DICT[exp])
        if s is not None:
            plt.fill_between(x, y - s.values, y + s.values, color=COLOR_DICT[exp], alpha=0.18, lw=0)
    plt.xlim(1850, 2100)
    if ylim:
        plt.ylim(*ylim)
    plt.xlabel("Year")
    plt.ylabel(meta["ylabel"])
    plt.title(meta["title"])
    plt.tight_layout()
    path = figdir / f"04_{varname}.png"
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


# ---------------------------------------------------------------------------
# Figures 8–10: ToE time series
# ---------------------------------------------------------------------------
def plot_toe_ts(annual_transport, toe_dict, varname: str, figdir: Path, ylim=None) -> Path:
    meta = TOE_PLOT_META.get(varname, {"ylabel": varname, "title": varname})
    plt.figure(figsize=(10, 5))
    for exp in SSP_EXPERIMENTS:
        da = annual_transport[exp][varname]
        m = da.mean("member", skipna=True) if "member" in da.dims else da
        s = da.std("member", skipna=True) if "member" in da.dims else None
        years = m["year"].values.astype(int)
        plt.plot(years, m.values, color=COLOR_DICT[exp], lw=2, label=f"{LABEL_DICT[exp]} mean")
        if s is not None:
            plt.fill_between(years, (m - s).values, (m + s).values, color=COLOR_DICT[exp], alpha=0.15)

    plt.xlim(2002, 2102)
    if ylim:
        plt.ylim(*ylim)
    ymin, ymax = plt.ylim()
    for exp in SSP_EXPERIMENTS:
        raw = toe_dict.get(exp, {}).get(varname)
        toe = raw.get("toe_year") if isinstance(raw, dict) else raw
        if toe is None:
            continue
        plt.vlines(toe, ymin, ymax, colors=COLOR_DICT[exp], linestyles="--", lw=1)
        plt.text(toe + 0.3, ymin + 0.05 * (ymax - ymin), f"ToE={toe}", color=COLOR_DICT[exp], rotation=90, va="bottom")

    plt.xlabel("Year")
    plt.ylabel(meta["ylabel"])
    plt.title(meta["title"])
    plt.legend(loc="upper right", ncol=3)
    plt.tight_layout()
    idx = {"canth_transport": "08", "volume_transport": "09", "amoc_strength": "10"}[varname]
    path = figdir / f"{idx}_ToE_{varname}.png"
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


# ---------------------------------------------------------------------------
# Figure 11: annual vs monthly volume transport
# ---------------------------------------------------------------------------
def plot_annual_vs_monthly(annual_transport, monthly_transport, figdir: Path, exp: str = "ssp585") -> Path:
    da_a = annual_transport[exp]["volume_transport"].mean("member")
    da_m = monthly_transport[exp]["volume_transport"].mean("member")
    plt.figure(figsize=(10, 4))
    plt.plot(da_a["year"].values, da_a.values, color=COLOR_DICT[exp], lw=2, label=f"{LABEL_DICT[exp]} annual")
    x_m = da_m["year"].values + (da_m["month"].values - 1) / 12.0
    plt.plot(x_m, da_m.values, color=COLOR_DICT[exp], lw=1, alpha=0.6, ls=":", label=f"{LABEL_DICT[exp]} monthly")
    plt.xlim(1850, 2100)
    plt.xlabel("Year")
    plt.ylabel("Volume Transport at 26N (Sv)")
    plt.title(f"Volume Transport: {LABEL_DICT[exp]} annual vs monthly")
    plt.legend()
    plt.tight_layout()
    path = figdir / f"11_annual_vs_monthly_volume_{exp}.png"
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


# ---------------------------------------------------------------------------
# ROCCA figure 1 (ROCCA_figure1-Copy1.ipynb)
# ---------------------------------------------------------------------------
def _decimal_year_to_datetime(dy: float) -> pd.Timestamp:
    year = int(dy)
    rem = dy - year
    days_in_year = 366 if pd.Timestamp(f"{year}-12-31").is_leap_year else 365
    return pd.Timestamp(f"{year}-01-01") + pd.to_timedelta(rem * days_in_year, unit="D")


def _obs_dates(obs: xr.Dataset) -> pd.DatetimeIndex:
    return pd.to_datetime([_decimal_year_to_datetime(t) for t in obs["time_obs"].values])


def _member_monthly_climatologies(da: xr.DataArray) -> np.ndarray:
    nyear = da.sizes["time"] // 12
    clims = []
    for member in da["member"].values:
        data = da.sel(member=member).values[: nyear * 12]
        clims.append(data.reshape((nyear, 12)).mean(axis=0))
    return np.array(clims)


def plot_rocca_transport_combined(rocca: dict[str, xr.Dataset], figdir: Path) -> Path:
    """Multi-panel CMIP6 vs RAPID obs time series (Canth_Transport_Combined.png)."""
    cmip6 = rocca["cmip6_all"]
    obs = rocca["obs"]
    time_axis = cmip6["time"].values

    fig = plt.figure(figsize=(16, 10))
    outer_gs = gridspec.GridSpec(2, 2, width_ratios=[5, 4], height_ratios=[1, 1], wspace=0.15)
    ax_main = fig.add_subplot(outer_gs[0, 0])
    ax_bottom = fig.add_subplot(outer_gs[1, 0])
    right_gs = gridspec.GridSpecFromSubplotSpec(3, 1, subplot_spec=outer_gs[:, 1], hspace=0.3)
    axes_right = [fig.add_subplot(right_gs[i]) for i in range(3)]

    for var, mid_color, obs_var, color, label in zip(
        ROCCA_VARS, ROCCA_MID_COLORS, ROCCA_OBS_VARS, ROCCA_COLORS, ROCCA_LABELS
    ):
        da = cmip6[var]
        for member in da["member"].values:
            ax_main.plot(time_axis, da.sel(member=member), color=mid_color, linewidth=1, alpha=0.5)
        ax_main.plot(obs["time_obs"], obs[obs_var], color=color, linewidth=1, label=f"{label} (Obs)")

        mean_var = da.mean("member")
        std_var = da.std("member")
        ax_bottom.plot(time_axis, mean_var, color=mid_color, linewidth=1.5, label=f"{label} (CMIP6)")
        ax_bottom.fill_between(time_axis, mean_var - std_var, mean_var + std_var, color=mid_color, alpha=0.3)
        ax_bottom.plot(obs["time_obs"], obs[obs_var], color=color, linewidth=1)

    ax_main.set_title(r"C$_{anth}$ Transport", fontsize=14, fontweight="bold")
    ax_main.set_xlabel("Year", fontsize=12)
    ax_main.set_ylabel("(PgC/yr)", fontsize=12)
    ax_main.set_xlim(2004, 2013)
    ax_main.legend(loc="upper left", fontsize=10)
    ax_main.grid(True, linestyle="--", alpha=0.5)

    ax_bottom.set_title(r"C$_{anth}$ ensemble mean", fontsize=14, fontweight="bold")
    ax_bottom.set_xlabel("Year", fontsize=12)
    ax_bottom.set_ylabel("(PgC/yr)", fontsize=12)
    ax_bottom.set_xlim(2004, 2013)
    ax_bottom.legend(loc="upper left", fontsize=10)
    ax_bottom.grid(True, linestyle="--", alpha=0.5)

    for ax, var, mid_color, obs_var, color, label in zip(
        axes_right, ROCCA_VARS, ROCCA_MID_COLORS, ROCCA_OBS_VARS, ROCCA_COLORS, ROCCA_LABELS
    ):
        da = cmip6[var]
        for member in da["member"].values:
            ax.plot(time_axis, da.sel(member=member), color=mid_color, linewidth=1, alpha=0.7)
        ax.plot(obs["time_obs"], obs[obs_var], color=color, linewidth=1)
        ax.set_title(fr"{label} C$_{{anth}}$ Transport", fontsize=13, fontweight="bold")
        ax.set_ylabel("(PgC/yr)", fontsize=11)
        ax.set_xlim(2004, 2013)
        ax.grid(True, linestyle="--", alpha=0.5)

    axes_right[-1].set_xlabel("Year", fontsize=11)
    plt.tight_layout()
    path = figdir / "14_rocca_canth_transport_combined.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_rocca_seasonal_combined(rocca: dict[str, xr.Dataset], figdir: Path) -> Path:
    """Seasonal climatology CMIP6 vs obs (Canth_Seasonal_Combined_*.png)."""
    cmip6 = rocca["cmip6_all"]
    obs = rocca["obs"]
    dates = _obs_dates(obs)
    months = np.arange(1, 13)

    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(3, 2, width_ratios=[1.2, 1], height_ratios=[1, 1, 1], wspace=0.25, hspace=0.3)
    ax_left = fig.add_subplot(gs[:, 0])
    axes_right = [fig.add_subplot(gs[i, 1]) for i in range(3)]

    overlay_models = []
    if "cesm2" in rocca:
        overlay_models.append({"data": rocca["cesm2"], "label": "CESM"})
    if "canesm5" in rocca:
        overlay_models.append({"data": rocca["canesm5"], "label": "CanESM"})

    for var, obs_var, color, mid_color, label in zip(
        ROCCA_VARS, ROCCA_OBS_VARS, ROCCA_COLORS, ROCCA_MID_COLORS, ROCCA_LABELS
    ):
        da = cmip6[var]
        all_clims = _member_monthly_climatologies(da)
        clim_mean = all_clims.mean(axis=0)
        clim_std = np.mean(
            [da.sel(member=m).values[: (da.sizes["time"] // 12) * 12].reshape(-1, 12).std(axis=0)
             for m in da["member"].values],
            axis=0,
        )

        ax_left.plot(months, clim_mean, color=color, linewidth=2, linestyle="--", marker="o", label=f"{label} (CMIP6)")
        ax_left.fill_between(months, clim_mean - clim_std, clim_mean + clim_std, color=mid_color, alpha=0.4)

        obs_df = pd.DataFrame({"date": dates, "value": obs[obs_var].values})
        obs_df["month"] = obs_df["date"].dt.month
        clim_obs = obs_df.groupby("month")["value"].mean().reindex(months)
        std_obs = obs_df.groupby("month")["value"].std().reindex(months)
        ax_left.plot(months, clim_obs, color=color, linewidth=2, linestyle="-", marker="o", label=f"{label} (Obs)")
        ax_left.fill_between(months, clim_obs - std_obs, clim_obs + std_obs, color=color, alpha=0.3)

    ax_left.set_title("Seasonal Climatology", fontsize=14, fontweight="bold")
    ax_left.set_xlabel("Month", fontsize=12)
    ax_left.set_ylabel("(PgC yr$^{-1}$)", fontsize=12)
    ax_left.set_xticks(months)
    ax_left.grid(True)
    ax_left.legend(fontsize=10, loc="lower left")

    for ax, var, color, label in zip(axes_right, ROCCA_VARS, ROCCA_COLORS, ROCCA_LABELS):
        da = cmip6[var]
        all_clims = _member_monthly_climatologies(da)
        for clim in all_clims:
            ax.plot(months, clim, color=color, alpha=0.3, linewidth=1)

        clim_mean = all_clims.mean(axis=0)
        clim_std = all_clims.std(axis=0)
        ax.plot(months, clim_mean, color=color, linewidth=2, marker="o")
        ax.fill_between(months, clim_mean - clim_std, clim_mean + clim_std, color=color, alpha=0.2)
        ax.text(months[-1] + 0.2, clim_mean[-1], "CMIP6", fontsize=10, color=color, va="center", ha="left", fontstyle="italic")

        for model in overlay_models:
            model_da = model["data"][var]
            model_clims = _member_monthly_climatologies(model_da)
            model_mean = model_clims.mean(axis=0)
            ax.plot(months, model_mean, linestyle="--", marker="o", color=color, linewidth=1.5)
            ax.text(
                months[-1] + 0.2, model_mean[-1], model["label"],
                fontsize=10, color=color, va="center", ha="left", fontstyle="italic",
            )

        ax.set_title(f"{label} – Seasonal Climatology", fontsize=13)
        ax.set_ylabel("(PgC yr$^{-1}$)", fontsize=11)
        ax.grid(True)

    axes_right[-1].set_xlabel("Month", fontsize=11)
    plt.tight_layout()
    path = figdir / "15_rocca_canth_seasonal_combined.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Budget figures (Test_budget.ipynb)
# ---------------------------------------------------------------------------
def _budget_time_axis(ds: xr.Dataset, freq: str) -> np.ndarray:
    if freq == "monthly":
        if "time" in ds.dims and "year" in ds.coords and "month" in ds.coords:
            return ds["year"].values + (ds["month"].values - 0.5) / 12.0
        return ds["time"].dt.year + (ds["time"].dt.month - 0.5) / 12.0
    return ds["year"].values


def _plot_mean_std_panel(ax, x, ds_mean, ds_std, plot_meta, ylabel, title, panel_label):
    for var, meta in plot_meta.items():
        y_mean = ds_mean[var].values
        y_std = ds_std[var].values
        ax.plot(x, y_mean, color=meta["color"], linewidth=1.6, label=meta["label"])
        ax.fill_between(x, y_mean - y_std, y_mean + y_std, color=meta["color"], alpha=0.18)

    ax.text(
        -0.1, 1.1, panel_label,
        transform=ax.transAxes,
        fontsize=24,
        fontweight="bold",
        va="top",
        ha="left",
    )
    ax.set_xlabel("Year", fontsize=15)
    ax.set_ylabel(ylabel, fontsize=15)
    ax.set_title(title, fontsize=16, loc="center", pad=10)
    ax.tick_params(axis="both", labelsize=14)
    ax.grid(alpha=0.3)
    ax.set_xlim(2013, 2102)


def plot_budget_combined(
    budget_decomp: dict,
    regional_canth: dict,
    exp: str,
    freq: str,
    figdir: Path,
) -> Path:
    decomp_ds = budget_decomp[exp]
    regional_ds = regional_canth[exp]
    x = _budget_time_axis(decomp_ds, freq)

    decomp_mean = decomp_ds.mean(dim="member")
    decomp_std = decomp_ds.std(dim="member")
    regional_mean = regional_ds.mean(dim="member")
    regional_std = regional_ds.std(dim="member")

    label = LABEL_DICT[exp]
    freq_label = "monthly" if freq == "monthly" else "yearly"

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=False)
    _plot_mean_std_panel(
        axes[0], x, regional_mean, regional_std, BUDGET_REGION_META,
        "(PgC yr$^{-1}$)",
        f"Regional Decomposition of Canth Transport ({label}, {freq_label})",
        "a",
    )
    _plot_mean_std_panel(
        axes[1], x, decomp_mean, decomp_std, BUDGET_DECOMP_META,
        "(PgC yr$^{-1}$)",
        f"Contributor-based Decomposition of Canth Transport ({label}, {freq_label})",
        "b",
    )
    axes[0].legend(loc="lower left", fontsize=13, frameon=False, ncol=4)
    axes[1].legend(loc="lower left", fontsize=13, frameon=False, ncol=4)
    plt.tight_layout()
    path = figdir / f"12_{exp}_{freq_label}_combined.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def _subregion_dataset(subregion_ds: xr.Dataset, prefix: str) -> xr.Dataset:
    vars_map = {
        "total_change": f"{prefix}_total_change",
        "v0_dC": f"{prefix}_v0_dC",
        "C0_dV": f"{prefix}_C0_dV",
        "dV_dC": f"{prefix}_dV_dC",
    }
    return xr.Dataset({k: subregion_ds[v] for k, v in vars_map.items()})


def plot_budget_subregion_decomp(
    subregion_decomp: dict,
    exp: str,
    freq: str,
    figdir: Path,
) -> Path:
    ds = subregion_decomp[exp]
    x = _budget_time_axis(ds, freq)
    freq_label = "monthly" if freq == "monthly" else "yearly"

    wbc_ds = _subregion_dataset(ds, "wbc")
    nonwbc_ds = _subregion_dataset(ds, "nonwbc_upper")

    wbc_mean = wbc_ds.mean(dim="member")
    wbc_std = wbc_ds.std(dim="member")
    nonwbc_mean = nonwbc_ds.mean(dim="member")
    nonwbc_std = nonwbc_ds.std(dim="member")

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=False)
    _plot_mean_std_panel(
        axes[0], x, wbc_mean, wbc_std, BUDGET_WBC_DECOMP_META,
        "(PgC yr$^{-1}$)",
        "Decomposition of Canth Transport in WBC",
        "c",
    )
    _plot_mean_std_panel(
        axes[1], x, nonwbc_mean, nonwbc_std, BUDGET_NONWBC_DECOMP_META,
        "(PgC yr$^{-1}$)",
        "Decomposition of Canth Transport in Non-WBC (0-700m)",
        "d",
    )
    axes[0].legend(loc="lower left", frameon=False, ncol=4)
    axes[1].legend(loc="lower left", frameon=False, ncol=4)
    plt.tight_layout()
    path = figdir / f"13_{exp}_{freq_label}_decomposition_WBC_NonWBC_0_700m.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run() -> Path:
    data = data_dir()
    figdir = figures_dir()
    _require_data(data / "annual_transport" / "ssp585.nc")

    print(f"=== RAPID plot started ===")
    print(f"Reading:  {data}")
    print(f"Figures:  {figdir}")

    d = _load_all(data)
    saved = []

    saved.append(plot_canth_decomp(d["annual_decomp"], d["monthly_decomp"], figdir))
    saved.append(plot_vertical_profiles(d["profiles"], d["meta"], figdir))
    saved.append(plot_lon_sections(d["sections"], d["meta"], figdir))

    for var in ("canth_transport", "amoc_strength", "volume_transport"):
        saved.append(plot_transport_ts(d["annual_transport"], var, figdir))

    saved.append(plot_transport_ts(
        d["annual_transport"], "canth_mean_concentration", figdir,
        ylim=(0, 0.04), figsize=(5, 2.5),
    ))

    for var in ("canth_transport", "volume_transport", "amoc_strength"):
        saved.append(plot_toe_ts(d["annual_transport"], d["toe_dict"], var, figdir))

    for exp in ("ssp585", "ssp245"):
        saved.append(plot_annual_vs_monthly(d["annual_transport"], d["monthly_transport"], figdir, exp))

    if "annual_budget_decomp" in d:
        for exp in SSP_EXPERIMENTS:
            for freq in ("yearly", "monthly"):
                prefix = "annual" if freq == "yearly" else "monthly"
                saved.append(plot_budget_combined(
                    d[f"{prefix}_budget_decomp"],
                    d[f"{prefix}_regional_canth"],
                    exp,
                    freq,
                    figdir,
                ))
                saved.append(plot_budget_subregion_decomp(
                    d[f"{prefix}_subregion_decomp"],
                    exp,
                    freq,
                    figdir,
                ))

    rocca = load_rocca_datasets(data)
    if "cmip6_all" in rocca and "obs" in rocca:
        saved.append(plot_rocca_transport_combined(rocca, figdir))
        saved.append(plot_rocca_seasonal_combined(rocca, figdir))
    else:
        print("\nWarning: ROCCA data not found — skipping figures 14–15.")
        print("Ensure RAPID_Canth_20042014.mat is available and re-run compute.py step 8.")

    # trends: print summary (no figure)
    trends_files = list(data.glob("trends_*.csv"))
    if trends_files:
        print("\n--- Linear trends ---")
        for tf in sorted(trends_files):
            print(f"\n{tf.name}:")
            print(pd.read_csv(tf).to_string(index=False))

    print(f"\n=== Done. {len(saved)} figures saved to {figdir} ===")
    for p in saved:
        print(f"  {p.name}")
    return figdir


if __name__ == "__main__":
    run()
