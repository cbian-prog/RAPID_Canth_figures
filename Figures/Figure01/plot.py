#!/usr/bin/env python3
"""Figure 1: overturning and horizontal C_anth transport at 26.5N, annual (a)
and monthly (b), ensemble mean +/- 1 std, three scenarios.

Reads data/RAPID_Figure01_data.csv; writes RAPID_Figure01.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
SCEN = ["ssp126", "ssp245", "ssp585"]
COLOR = {"ssp126": "orange", "ssp245": "green", "ssp585": "purple"}
LABEL = {"ssp126": "SSP1-2.6", "ssp245": "SSP2-4.5", "ssp585": "SSP5-8.5"}
STYLE = {"overturning": ("-", "Overturning"), "horizontal": ("--", "Horizontal")}

d = pd.read_csv(HERE / "data" / "RAPID_Figure01_data.csv")
fig, axes = plt.subplots(2, 1, figsize=(12, 9))
for ax, res in zip(axes, ("annual", "monthly")):
    for exp in SCEN:
        for comp in ("overturning", "horizontal"):
            c = d[(d.scenario == exp) & (d.resolution == res) & (d.component == comp)]
            ls, name = STYLE[comp]
            kw = {"label": f"{LABEL[exp]} {name}"} if res == "annual" else {}
            ax.plot(c.time, c["mean"], color=COLOR[exp], ls=ls, lw=2, **kw)
            ax.fill_between(c.time, c["mean"] - c["std"], c["mean"] + c["std"],
                            color=COLOR[exp], alpha=0.15)
    ax.set_ylabel("Canth Transport (PgC/yr)")
    ax.set_xlim(2014, 2101)
axes[0].legend(fontsize=12, ncol=3)
axes[1].set_xlabel("Year")
for ax, let in zip(axes, "ab"):
    ax.text(-0.1, 1.1, let, transform=ax.transAxes, fontsize=22, fontweight="bold", va="top")
plt.tight_layout()
fig.savefig(HERE / "RAPID_Figure01.png", dpi=300, bbox_inches="tight")
