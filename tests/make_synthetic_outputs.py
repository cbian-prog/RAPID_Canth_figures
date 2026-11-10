#!/usr/bin/env python3
"""
Write a small synthetic stand-in for compute.py's output (outputs/data/).

It has the layout, variable names, dimensions and coordinates compute.py
writes, filled with made-up numbers, so that export_figure_data.py and every
figure script can be exercised without GCS access.  The numbers mean nothing
and must never be plotted as results.

    python tests/make_synthetic_outputs.py /tmp/synth/data
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

out = Path(sys.argv[1])
rng = np.random.default_rng(0)
SCEN = ["ssp126", "ssp245", "ssp585"]
MEM = [f"r{i}i1p1f1" for i in range(1, 6)]
YRS = np.arange(1850, 2101)
NM = len(YRS) * 12
MY, MM = np.repeat(YRS, 12), np.tile(np.arange(1, 13), len(YRS))


def save(ds: xr.Dataset, p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    ds.to_netcdf(p)


for k, exp in enumerate(SCEN):
    f = 1 + 0.5 * k

    def ann(base, slope):
        y = base + slope * f * (YRS - 1850)[None] / 250 \
            + rng.normal(0, 0.05 * abs(base) + 1e-3, (len(MEM), len(YRS)))
        return xr.DataArray(y, dims=("member", "year"), coords={"member": MEM, "year": YRS})

    def mon(base, slope):
        y = base + slope * f * (MY - 1850)[None] / 250 \
            + np.sin(2 * np.pi * MM / 12)[None] * 0.1 * abs(base) \
            + rng.normal(0, 0.05 * abs(base) + 1e-3, (len(MEM), NM))
        return xr.DataArray(y, dims=("member", "time"),
                            coords={"member": MEM, "time": np.arange(NM),
                                    "year": ("time", MY), "month": ("time", MM)})

    save(xr.Dataset({"canth_transport": ann(0.1, 0.3), "amoc_strength": ann(18, -6),
                     "volume_transport": ann(-1.0, 0.2),
                     "canth_mean_concentration": ann(0.005, 0.03)}),
         out / "annual_transport" / f"{exp}.nc")
    save(xr.Dataset({"volume_transport": mon(-1.0, 0.2)}), out / "monthly_transport" / f"{exp}.nc")
    save(xr.Dataset({"total_trans_time_seri": ann(0.1, 0.3),
                     "overturning_transport_time_seri": ann(0.15, 0.2),
                     "horizontal_transport_time_seri": ann(-0.05, 0.1)}),
         out / "annual_decomp" / f"{exp}.nc")
    save(xr.Dataset({"total_trans_time_seri": mon(0.1, 0.3),
                     "overturning_transport_time_seri": mon(0.15, 0.2),
                     "horizontal_transport_time_seri": mon(-0.05, 0.1)}),
         out / "monthly_decomp" / f"{exp}.nc")

    lev = np.array([5, 15, 50, 100, 200, 400, 700, 1000, 1500, 2000, 3000, 4000, 5000.])
    save(xr.Dataset({
        "canth_transport_profile_top_to_bottom": ("lev", np.cumsum(rng.normal(0.01 * f, 0.01, lev.size))),
        "volume_transport_profile_top_to_bottom": ("lev", np.cumsum(rng.normal(0, 3, lev.size))),
        "canth_mean_concentration_profile": ("lev", 0.05 * f * np.exp(-lev / 800))},
        coords={"lev": lev}), out / "profiles" / f"{exp}.nc")
    lon = np.arange(280.5, 346, 1.0)
    save(xr.Dataset({
        "canth_transport_lon": ("lon", rng.normal(0, 0.01 * f, lon.size)),
        "volume_transport_lon": ("lon", rng.normal(0, 1, lon.size)),
        "canth_cum_concentration_lon": ("lon", rng.uniform(0, 100 * f, lon.size))},
        coords={"lon": lon}), out / "sections" / f"{exp}.nc")

    for freq in ("annual", "monthly"):
        if freq == "annual":
            y = np.arange(2015, 2101)
            crd = {"member": MEM, "year": y}
            dims = ("member", "year")
        else:
            y = np.repeat(np.arange(2015, 2101), 12)
            crd = {"member": MEM, "time": np.arange(y.size), "year": ("time", y),
                   "month": ("time", np.tile(np.arange(1, 13), 86))}
            dims = ("member", "time")

        def b(base):
            v = base * np.linspace(0, 1, y.size)[None] * f + rng.normal(0, 0.01, (len(MEM), y.size))
            return xr.DataArray(v, dims=dims, coords=crd)

        save(xr.Dataset({"total_change": b(0.1), "v0_dC": b(0.15), "C0_dV": b(-0.06), "dV_dC": b(0.01)}),
             out / f"{freq}_budget_decomp" / f"{exp}.nc")
        save(xr.Dataset({"total_canth_transport": b(0.2), "WBC": b(0.5),
                         "NonWBC_0_700m": b(-0.2), "NonWBC_700m_bottom": b(-0.1)}),
             out / f"{freq}_regional_canth" / f"{exp}.nc")
        save(xr.Dataset({f"{r}_{v}": b(s) for r in ("wbc", "nonwbc_upper")
                         for v, s in (("total_change", 0.1), ("v0_dC", 0.12),
                                      ("C0_dV", -0.03), ("dV_dC", 0.01))}),
             out / f"{freq}_subregion_decomp" / f"{exp}.nc")

toe = {exp: {"canth_transport": {"toe_index": 2, "toe_year": 2014 + 5 * k},
             "volume_transport": None,
             "amoc_strength": {"toe_index": 6, "toe_year": 2040 + 3 * k},
             "canth_mean_concentration": 2009}
       for k, exp in enumerate(SCEN)}
(out / "toe_dict.json").write_text(json.dumps(toe))
(out / "meta.json").write_text(json.dumps({"profile_start": 2004, "profile_end": 2014}))

t = 2004 + (np.arange(132) + 0.5) / 12
m12 = np.tile(np.arange(12), 11)


def rc(n):
    v = 0.4 + 0.1 * np.sin(2 * np.pi * m12 / 12)[None] + rng.normal(0, 0.05, (n, 132))
    return xr.DataArray(v, dims=("member", "time"),
                        coords={"member": [f"M{i}" for i in range(n)], "time": t})


for name, n in (("cmip6_all", 8), ("cesm2", 3), ("canesm5", 5)):
    save(xr.Dataset({"total_trans_time_seri": rc(n), "overturning_transport_time_seri": rc(n) * 1.2,
                     "horizontal_transport_time_seri": rc(n) * -0.2}),
         out / "rocca" / f"{name}.nc")
t_obs = np.arange(2004.04, 2014.0, 1 / 24)
save(xr.Dataset({v: ("time_obs", 0.4 * s + 0.1 * np.sin(2 * np.pi * t_obs) + rng.normal(0, 0.05, t_obs.size))
                 for v, s in (("total", 1), ("overturning", 1.2), ("horizontal", -0.2))},
                coords={"time_obs": t_obs}), out / "rocca" / "obs.nc")
pd.DataFrame({"var": ["canth_transport"], "slope": [0.01]}).to_csv(out / "trends_2004_2050.csv", index=False)
print(f"synthetic compute output written to {out}")
