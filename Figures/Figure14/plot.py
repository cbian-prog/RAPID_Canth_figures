#!/usr/bin/env python3
"""Figure 14: C_anth transport at 26.5N, CMIP6 against the RAPID-based
observational estimate, 2004-2014: every member and the observations (top
left), ensemble mean +/- 1 std and the observations (bottom left), and the
total, overturning and horizontal components separately (right).

Reads data/RAPID_Figure14_{members,ensemble,obs}.csv; writes RAPID_Figure14.png.
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

mem = pd.read_csv(HERE / "data" / "RAPID_Figure14_members.csv")
ens = pd.read_csv(HERE / "data" / "RAPID_Figure14_ensemble.csv")
obs = pd.read_csv(HERE / "data" / "RAPID_Figure14_obs.csv")

fig = plt.figure(figsize=(16, 10))
outer = gridspec.GridSpec(2, 2, width_ratios=[5, 4], height_ratios=[1, 1], wspace=0.15)
ax_main = fig.add_subplot(outer[0, 0])
ax_bottom = fig.add_subplot(outer[1, 0])
right = gridspec.GridSpecFromSubplotSpec(3, 1, subplot_spec=outer[:, 1], hspace=0.3)
axes_right = [fig.add_subplot(right[i]) for i in range(3)]

for comp, mid, color, label in zip(COMPONENTS, MID, COLORS, LABELS):
    m, o, e = mem[mem.component == comp], obs[obs.component == comp], ens[ens.component == comp]
    for _, g in m.groupby("member", sort=False):
        ax_main.plot(g.time, g.value, color=mid, linewidth=1, alpha=0.5)
    ax_main.plot(o.time, o.value, color=color, linewidth=1, label=f"{label} (Obs)")
    ax_bottom.plot(e.time, e["mean"], color=mid, linewidth=1.5, label=f"{label} (CMIP6)")
    ax_bottom.fill_between(e.time, e["mean"] - e["std"], e["mean"] + e["std"], color=mid, alpha=0.3)
    ax_bottom.plot(o.time, o.value, color=color, linewidth=1)

for ax, title in ((ax_main, r"C$_{anth}$ Transport"), (ax_bottom, r"C$_{anth}$ ensemble mean")):
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("(PgC/yr)", fontsize=12)
    ax.set_xlim(2004, 2013)
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)

for ax, comp, mid, color, label in zip(axes_right, COMPONENTS, MID, COLORS, LABELS):
    for _, g in mem[mem.component == comp].groupby("member", sort=False):
        ax.plot(g.time, g.value, color=mid, linewidth=1, alpha=0.7)
    o = obs[obs.component == comp]
    ax.plot(o.time, o.value, color=color, linewidth=1)
    ax.set_title(fr"{label} C$_{{anth}}$ Transport", fontsize=13, fontweight="bold")
    ax.set_ylabel("(PgC/yr)", fontsize=11)
    ax.set_xlim(2004, 2013)
    ax.grid(True, linestyle="--", alpha=0.5)
axes_right[-1].set_xlabel("Year", fontsize=11)
plt.tight_layout()
fig.savefig(HERE / "RAPID_Figure14.png", dpi=300, bbox_inches="tight")
