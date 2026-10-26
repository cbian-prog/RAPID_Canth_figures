#!/usr/bin/env python3
"""Figure 12: projected C_anth transport at 26.5N from 2015, split (a) by
region -- western boundary current (WBC), interior 0-700 m, interior
700 m-bottom -- and (b) by contribution -- change in concentration,
change in velocity, and their product -- relative to the first scenario
time step (2015, or January 2015 for monthly).  One figure per scenario and
time resolution.

Reads data/RAPID_Figure12_data.csv; writes RAPID_Figure12_<ssp>_<yearly|monthly>.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
SCEN = ["ssp126", "ssp245", "ssp585"]
LABEL = {"ssp126": "SSP1-2.6", "ssp245": "SSP2-4.5", "ssp585": "SSP5-8.5"}
REGION = {
    "total_canth_transport": ("black", "Total"),
    "WBC": ("red", "WBC"),
    "NonWBC_0_700m": ("blue", "Non-WBC (0–700m)"),
    "NonWBC_700m_bottom": ("gray", "Non-WBC (700m–bottom)"),
}
DECOMP = {
    "total_change": ("black", r"$\Delta(C_{(t)} \times V_{(t)})$"),
    "v0_dC": ("purple", r"$V_{(t0)} \cdot \Delta C_{(t)}$"),
    "C0_dV": ("orange", r"$C_{(t0)} \cdot \Delta V_{(t)}$"),
    "dV_dC": ("dodgerblue", r"$\Delta V_{(t)} \cdot \Delta C_{(t)}$"),
}


def panel(ax, d, styles, title, letter):
    for v, (color, label) in styles.items():
        c = d[d.series == v]
        ax.plot(c.time, c["mean"], color=color, linewidth=1.6, label=label)
        ax.fill_between(c.time, c["mean"] - c["std"], c["mean"] + c["std"], color=color, alpha=0.18)
    ax.text(-0.1, 1.1, letter, transform=ax.transAxes, fontsize=24, fontweight="bold",
            va="top", ha="left")
    ax.set_xlabel("Year", fontsize=15)
    ax.set_ylabel("(PgC yr$^{-1}$)", fontsize=15)
    ax.set_title(title, fontsize=16, loc="center", pad=10)
    ax.tick_params(axis="both", labelsize=14)
    ax.grid(alpha=0.3)
    ax.set_xlim(2013, 2102)
    ax.legend(loc="lower left", fontsize=13, frameon=False, ncol=4)


d = pd.read_csv(HERE / "data" / "RAPID_Figure12_data.csv")
for exp in SCEN:
    for freq in ("yearly", "monthly"):
        s = d[(d.scenario == exp) & (d.frequency == freq)]
        fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=False)
        panel(axes[0], s[s.panel == "regional"], REGION,
              f"Regional Decomposition of Canth Transport ({LABEL[exp]}, {freq})", "a")
        panel(axes[1], s[s.panel == "contribution"], DECOMP,
              f"Contributor-based Decomposition of Canth Transport ({LABEL[exp]}, {freq})", "b")
        plt.tight_layout()
        fig.savefig(HERE / f"RAPID_Figure12_{exp}_{freq}.png", dpi=300, bbox_inches="tight")
        plt.close(fig)
