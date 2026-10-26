#!/usr/bin/env python3
"""
Reduce what compute.py wrote to exactly what each figure draws.

compute.py writes member-resolved NetCDF to outputs/data/.  This script reads
it and writes, for every figure, the curves as plotted (ensemble means,
spreads, the individual members where a panel draws them, the observed
series, emergence years) as CSV into ../Figures/FigureNN/data/.  After this,
each Figures/FigureNN/plot.py redraws its figure with numpy, pandas and
matplotlib alone.

The reductions are the ones the original plot.py made: spreads are the
population standard deviation over members (xarray's default, ddof=0), except
the observed monthly climatology in Figure 15, which uses pandas' sample
standard deviation (ddof=1), as before.

Usage:
    python export_figure_data.py                       # outputs/data -> ../Figures
    RAPID_FIG_OUTPUT=/path/to/out python export_figure_data.py
    python export_figure_data.py --figures-dir /elsewhere/Figures
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common.config import SSP_EXPERIMENTS, data_dir  # noqa: E402

ROCCA_VARS = ["total_trans_time_seri", "overturning_transport_time_seri",
              "horizontal_transport_time_seri"]
ROCCA_OBS_VARS = ["total", "overturning", "horizontal"]
ROCCA_COMPONENTS = ["total", "overturning", "horizontal"]
REGION_VARS = ["total_canth_transport", "WBC", "NonWBC_0_700m", "NonWBC_700m_bottom"]
DECOMP_VARS = ["total_change", "v0_dC", "C0_dV", "dV_dC"]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _open(path: Path) -> xr.Dataset:
    if not path.exists():
        raise FileNotFoundError(f"missing {path} -- run compute.py first")
    return xr.open_dataset(path)


def _dict(data: Path, sub: str) -> dict[str, xr.Dataset]:
    return {exp: _open(data / sub / f"{exp}.nc") for exp in SSP_EXPERIMENTS}


def _mean_std(da: xr.DataArray, skipna: bool | None = None):
    if "member" in da.dims:
        return da.mean("member", skipna=skipna), da.std("member", skipna=skipna)
    return da, None


def _monthly_x(ds: xr.Dataset | xr.DataArray) -> np.ndarray:
    """Decimal year at the start of each month, as Figures 1 and 11 drew it."""
    return ds["year"].values + (ds["month"].values - 1) / 12.0


def _budget_x(ds: xr.Dataset, freq: str) -> np.ndarray:
    """Time axis of Figures 12 and 13 (mid-month for monthly)."""
    if freq == "monthly":
        if "time" in ds.dims and "year" in ds.coords and "month" in ds.coords:
            return ds["year"].values + (ds["month"].values - 0.5) / 12.0
        return np.asarray(ds["time"].dt.year + (ds["time"].dt.month - 0.5) / 12.0)
    return ds["year"].values


def _write(df: pd.DataFrame, fig_dir: Path, name: str) -> None:
    out = fig_dir / "data"
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / name, index=False)
    print(f"  {out / name}  ({len(df)} rows)")


# ---------------------------------------------------------------------------
# one function per figure
# ---------------------------------------------------------------------------
def fig01(data: Path, figs: Path) -> None:
    rows = []
    for res, sub in (("annual", "annual_decomp"), ("monthly", "monthly_decomp")):
        d = _dict(data, sub)
        for exp in SSP_EXPERIMENTS:
            ds = d[exp]
            x = ds["year"].values if res == "annual" else _monthly_x(ds)
            for comp, var in (("overturning", "overturning_transport_time_seri"),
                              ("horizontal", "horizontal_transport_time_seri")):
                m, s = ds[var].mean("member"), ds[var].std("member")
                rows.append(pd.DataFrame({"scenario": exp, "resolution": res,
                                          "component": comp, "time": x,
                                          "mean": m.values, "std": s.values}))
    _write(pd.concat(rows, ignore_index=True), figs / "Figure01", "RAPID_Figure01_data.csv")


def fig02(data: Path, figs: Path, meta: dict) -> None:
    d = _dict(data, "profiles")
    rows = []
    for exp in SSP_EXPERIMENTS:
        ds = d[exp]
        rows.append(pd.DataFrame({
            "scenario": exp,
            "depth_m": ds["lev"].values,
            "canth_transport_PgC_yr": ds["canth_transport_profile_top_to_bottom"].values,
            "volume_transport_Sv": ds["volume_transport_profile_top_to_bottom"].values,
            "canth_concentration_mol_m3": ds["canth_mean_concentration_profile"].values,
            "period": f"{meta['profile_start']}-{meta['profile_end']}"}))
    _write(pd.concat(rows, ignore_index=True), figs / "Figure02", "RAPID_Figure02_data.csv")


def fig03(data: Path, figs: Path, meta: dict) -> None:
    d = _dict(data, "sections")
    rows = []
    for exp in SSP_EXPERIMENTS:
        ds = d[exp]
        rows.append(pd.DataFrame({
            "scenario": exp,
            "lon": ds["lon"].values,
            "canth_transport_PgC_yr": ds["canth_transport_lon"].values,
            "volume_transport_Sv": ds["volume_transport_lon"].values,
            "canth_amount_mol_m2": ds["canth_cum_concentration_lon"].values,
            "period": f"{meta['profile_start']}-{meta['profile_end']}"}))
    _write(pd.concat(rows, ignore_index=True), figs / "Figure03", "RAPID_Figure03_data.csv")


def _annual_series(d: dict[str, xr.Dataset], var: str, skipna=None) -> pd.DataFrame:
    rows = []
    for exp in SSP_EXPERIMENTS:
        m, s = _mean_std(d[exp][var], skipna=skipna)
        rows.append(pd.DataFrame({"scenario": exp, "year": m["year"].values,
                                  "mean": m.values,
                                  "std": s.values if s is not None else np.nan}))
    return pd.concat(rows, ignore_index=True)


def fig04_to_10(data: Path, figs: Path) -> None:
    d = _dict(data, "annual_transport")
    for n, var in (("04", "canth_transport"), ("05", "amoc_strength"),
                   ("06", "volume_transport"), ("07", "canth_mean_concentration")):
        _write(_annual_series(d, var), figs / f"Figure{n}", f"RAPID_Figure{n}_data.csv")

    toe = json.loads((data / "toe_dict.json").read_text(encoding="utf-8"))
    for n, var in (("08", "canth_transport"), ("09", "volume_transport"),
                   ("10", "amoc_strength")):
        _write(_annual_series(d, var, skipna=True), figs / f"Figure{n}",
               f"RAPID_Figure{n}_data.csv")
        t = []
        for exp in SSP_EXPERIMENTS:
            raw = toe.get(exp, {}).get(var)
            year = raw.get("toe_year") if isinstance(raw, dict) else raw
            t.append({"scenario": exp, "toe_year": year})
        _write(pd.DataFrame(t), figs / f"Figure{n}", f"RAPID_Figure{n}_toe.csv")


def fig11(data: Path, figs: Path) -> None:
    da_ = _dict(data, "annual_transport")
    dm_ = _dict(data, "monthly_transport")
    rows = []
    for exp in ("ssp585", "ssp245"):
        a = da_[exp]["volume_transport"].mean("member")
        m = dm_[exp]["volume_transport"].mean("member")
        rows.append(pd.DataFrame({"scenario": exp, "resolution": "annual",
                                  "time": a["year"].values, "mean": a.values}))
        rows.append(pd.DataFrame({"scenario": exp, "resolution": "monthly",
                                  "time": _monthly_x(m), "mean": m.values}))
    _write(pd.concat(rows, ignore_index=True), figs / "Figure11", "RAPID_Figure11_data.csv")


def fig12_13(data: Path, figs: Path) -> None:
    if not (data / "annual_budget_decomp").exists():
        print("  budget output missing -- Figures 12 and 13 skipped")
        return
    r12, r13 = [], []
    for freq, prefix in (("yearly", "annual"), ("monthly", "monthly")):
        dec = _dict(data, f"{prefix}_budget_decomp")
        reg = _dict(data, f"{prefix}_regional_canth")
        sub = _dict(data, f"{prefix}_subregion_decomp")
        for exp in SSP_EXPERIMENTS:
            for panel, ds, names in (("regional", reg[exp], REGION_VARS),
                                     ("contribution", dec[exp], DECOMP_VARS)):
                x = _budget_x(dec[exp], freq)      # the original used the decomposition's axis for both
                mean, std = ds.mean(dim="member"), ds.std(dim="member")
                for v in names:
                    r12.append(pd.DataFrame({"scenario": exp, "frequency": freq,
                                             "panel": panel, "series": v, "time": x,
                                             "mean": mean[v].values, "std": std[v].values}))
            ds = sub[exp]
            x = _budget_x(ds, freq)
            for region in ("wbc", "nonwbc_upper"):
                part = xr.Dataset({v: ds[f"{region}_{v}"] for v in DECOMP_VARS})
                mean, std = part.mean(dim="member"), part.std(dim="member")
                for v in DECOMP_VARS:
                    r13.append(pd.DataFrame({"scenario": exp, "frequency": freq,
                                             "region": region, "series": v, "time": x,
                                             "mean": mean[v].values, "std": std[v].values}))
    _write(pd.concat(r12, ignore_index=True), figs / "Figure12", "RAPID_Figure12_data.csv")
    _write(pd.concat(r13, ignore_index=True), figs / "Figure13", "RAPID_Figure13_data.csv")


def _member_clims(da: xr.DataArray) -> np.ndarray:
    nyear = da.sizes["time"] // 12
    return np.array([da.sel(member=m).values[: nyear * 12].reshape((nyear, 12)).mean(axis=0)
                     for m in da["member"].values])


def _decimal_year_to_datetime(dy: float) -> pd.Timestamp:
    year = int(dy)
    rem = dy - year
    days = 366 if pd.Timestamp(f"{year}-12-31").is_leap_year else 365
    return pd.Timestamp(f"{year}-01-01") + pd.to_timedelta(rem * days, unit="D")


def fig14_15(data: Path, figs: Path) -> None:
    rdir = data / "rocca"
    if not (rdir / "cmip6_all.nc").exists() or not (rdir / "obs.nc").exists():
        print("  ROCCA output missing -- Figures 14 and 15 skipped")
        return
    cmip6 = xr.open_dataset(rdir / "cmip6_all.nc")
    obs = xr.open_dataset(rdir / "obs.nc")
    overlay = [(lab, xr.open_dataset(rdir / f"{key}.nc")) for key, lab in
               (("cesm2", "CESM"), ("canesm5", "CanESM")) if (rdir / f"{key}.nc").exists()]
    t = cmip6["time"].values
    t_obs = obs["time_obs"].values
    dates = pd.to_datetime([_decimal_year_to_datetime(v) for v in t_obs])
    months = np.arange(1, 13)

    members, ens, obs_rows, mclim, clim = [], [], [], [], []
    for comp, var, ovar in zip(ROCCA_COMPONENTS, ROCCA_VARS, ROCCA_OBS_VARS):
        da = cmip6[var]
        for mem in da["member"].values:
            members.append(pd.DataFrame({"component": comp, "member": str(mem), "time": t,
                                         "value": da.sel(member=mem).values}))
        ens.append(pd.DataFrame({"component": comp, "time": t,
                                 "mean": da.mean("member").values,
                                 "std": da.std("member").values}))
        obs_rows.append(pd.DataFrame({"component": comp, "time": t_obs,
                                      "value": obs[ovar].values}))

        clims = _member_clims(da)
        for mem, c in zip(da["member"].values, clims):
            mclim.append(pd.DataFrame({"component": comp, "member": str(mem),
                                       "month": months, "value": c}))
        n12 = (da.sizes["time"] // 12) * 12
        within = np.mean([da.sel(member=m).values[:n12].reshape(-1, 12).std(axis=0)
                          for m in da["member"].values], axis=0)
        clim.append(pd.DataFrame({"component": comp, "series": "cmip6_within_member",
                                  "month": months, "mean": clims.mean(axis=0), "std": within}))
        clim.append(pd.DataFrame({"component": comp, "series": "cmip6_across_member",
                                  "month": months, "mean": clims.mean(axis=0),
                                  "std": clims.std(axis=0)}))
        df = pd.DataFrame({"month": dates.month, "value": obs[ovar].values})
        g = df.groupby("month")["value"]
        clim.append(pd.DataFrame({"component": comp, "series": "obs", "month": months,
                                  "mean": g.mean().reindex(months).values,
                                  "std": g.std().reindex(months).values}))
        for lab, ds in overlay:
            clim.append(pd.DataFrame({"component": comp, "series": lab, "month": months,
                                      "mean": _member_clims(ds[var]).mean(axis=0),
                                      "std": np.nan}))

    f14, f15 = figs / "Figure14", figs / "Figure15"
    _write(pd.concat(members, ignore_index=True), f14, "RAPID_Figure14_members.csv")
    _write(pd.concat(ens, ignore_index=True), f14, "RAPID_Figure14_ensemble.csv")
    _write(pd.concat(obs_rows, ignore_index=True), f14, "RAPID_Figure14_obs.csv")
    _write(pd.concat(mclim, ignore_index=True), f15, "RAPID_Figure15_member_climatology.csv")
    _write(pd.concat(clim, ignore_index=True), f15, "RAPID_Figure15_climatology.csv")


def trends(data: Path, figs: Path) -> None:
    """Linear-trend tables: numbers quoted in the text, not drawn."""
    out = figs / "Figure04" / "data"
    for f in sorted(data.glob("trends_*.csv")):
        out.mkdir(parents=True, exist_ok=True)
        pd.read_csv(f).to_csv(out / f"RAPID_{f.name}", index=False)
        print(f"  {out / ('RAPID_' + f.name)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--data-dir", default=None, help="compute.py output (default outputs/data)")
    ap.add_argument("--figures-dir", default=str(ROOT.parent / "Figures"))
    a = ap.parse_args()
    data = Path(a.data_dir) if a.data_dir else data_dir()
    figs = Path(a.figures_dir)
    meta = json.loads((data / "meta.json").read_text(encoding="utf-8"))
    print(f"reading {data}\nwriting {figs}/FigureNN/data/")
    fig01(data, figs)
    fig02(data, figs, meta)
    fig03(data, figs, meta)
    fig04_to_10(data, figs)
    fig11(data, figs)
    fig12_13(data, figs)
    fig14_15(data, figs)
    trends(data, figs)


if __name__ == "__main__":
    main()
