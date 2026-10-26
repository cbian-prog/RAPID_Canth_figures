#!/usr/bin/env python3
"""Figure 15: seasonal cycle of C_anth transport at 26.5N, 2004-2014.
Left: CMIP6 ensemble (mean of member climatologies, shaded by the mean
within-member monthly std) against the observations (shaded by the monthly
std across years).  Right: total, overturning and horizontal, every member's
climatology, the ensemble mean +/- across-member std, and the CESM and
CanESM means.

Reads data/RAPID_Figure15_{climatology,member_climatology}.csv;
writes RAPID_Figure15.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
COMPONENTS = ["total", "overturning", "horizontal"]
COLORS = ["black", "blue", "red"]
MID = [(0.5, 0.5, 0.5), (0.5, 0.7, 1), (1, 0.5, 0.5)]
LABELS = ["Total", "Overturning", "Horizontal"]
OVERLAY = ["CESM", "CanESM"]

clim = pd.read_csv(HERE / "data" / "RAPID_Figure15_climatology.csv")
mclim = pd.read_csv(HERE / "data" / "RAPID_Figure15_member_climatology.csv")

fig = plt.figure(figsize=(16, 10))
gs = gridspec.GridSpec(3, 2, width_ratios=[1.2, 1], height_ratios=[1, 1, 1], wspace=0.25, hspace=0.3)
ax_left = fig.add_subplot(gs[:, 0])
axes_right = [fig.add_subplot(gs[i, 1]) for i in range(3)]


def series(comp, name):
    return clim[(clim.component == comp) & (clim.series == name)]


for comp, color, mid, label in zip(COMPONENTS, COLORS, MID, LABELS):
    c = series(comp, "cmip6_within_member")
    ax_left.plot(c.month, c["mean"], color=color, linewidth=2, linestyle="--", marker="o",
                 label=f"{label} (CMIP6)")
    ax_left.fill_between(c.month, c["mean"] - c["std"], c["mean"] + c["std"], color=mid, alpha=0.4)
    o = series(comp, "obs")
    ax_left.plot(o.month, o["mean"], color=color, linewidth=2, linestyle="-", marker="o",
                 label=f"{label} (Obs)")
    ax_left.fill_between(o.month, o["mean"] - o["std"], o["mean"] + o["std"], color=color, alpha=0.3)
ax_left.set_title("Seasonal Climatology", fontsize=14, fontweight="bold")
ax_left.set_xlabel("Month", fontsize=12)
ax_left.set_ylabel("(PgC yr$^{-1}$)", fontsize=12)
ax_left.set_xticks(range(1, 13))
ax_left.grid(True)
ax_left.legend(fontsize=10, loc="lower left")

for ax, comp, color, label in zip(axes_right, COMPONENTS, COLORS, LABELS):
    for _, g in mclim[mclim.component == comp].groupby("member", sort=False):
        ax.plot(g.month, g.value, color=color, alpha=0.3, linewidth=1)
    c = series(comp, "cmip6_across_member")
    ax.plot(c.month, c["mean"], color=color, linewidth=2, marker="o")
    ax.fill_between(c.month, c["mean"] - c["std"], c["mean"] + c["std"], color=color, alpha=0.2)
    ax.text(12.2, c["mean"].iloc[-1], "CMIP6", fontsize=10, color=color, va="center",
            ha="left", fontstyle="italic")
    for name in OVERLAY:
        o = series(comp, name)
        if o.empty:
            continue
        ax.plot(o.month, o["mean"], linestyle="--", marker="o", color=color, linewidth=1.5)
        ax.text(12.2, o["mean"].iloc[-1], name, fontsize=10, color=color, va="center",
                ha="left", fontstyle="italic")
    ax.set_title(f"{label} – Seasonal Climatology", fontsize=13)
    ax.set_ylabel("(PgC yr$^{-1}$)", fontsize=11)
    ax.grid(True)
axes_right[-1].set_xlabel("Month", fontsize=11)
plt.tight_layout()
fig.savefig(HERE / "RAPID_Figure15.png", dpi=300, bbox_inches="tight")
