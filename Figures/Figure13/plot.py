#!/usr/bin/env python3
"""Figure 13: the contribution split of Figure 12b repeated within (c) the
western boundary current and (d) the interior 0-700 m.  One figure per
scenario and time resolution.

Reads data/RAPID_Figure13_data.csv; writes RAPID_Figure13_<ssp>_<yearly|monthly>.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
SCEN = ["ssp126", "ssp245", "ssp585"]
TERMS = {
    "v0_dC": ("purple", r"$v_{(t0)} \cdot \Delta C_{(t)}$"),
    "C0_dV": ("orange", r"$C_{(t0)} \cdot \Delta V_{(t)}$"),
    "dV_dC": ("dodgerblue", r"$\Delta V_{(t)} \cdot \Delta C_{(t)}$"),
}
TOTAL_LABEL = r"$\Delta(C_{(t)} \times v_{(t)})$"
REGIONS = [("wbc", "red", "Decomposition of Canth Transport in WBC", "c"),
           ("nonwbc_upper", "blue", "Decomposition of Canth Transport in Non-WBC (0-700m)", "d")]


def panel(ax, d, total_color, title, letter):
    styles = {"total_change": (total_color, TOTAL_LABEL), **TERMS}
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
    ax.legend(loc="lower left", frameon=False, ncol=4)


d = pd.read_csv(HERE / "data" / "RAPID_Figure13_data.csv")
for exp in SCEN:
    for freq in ("yearly", "monthly"):
        s = d[(d.scenario == exp) & (d.frequency == freq)]
        fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=False)
        for ax, (region, color, title, letter) in zip(axes, REGIONS):
            panel(ax, s[s.region == region], color, title, letter)
        plt.tight_layout()
        fig.savefig(HERE / f"RAPID_Figure13_{exp}_{freq}.png", dpi=300, bbox_inches="tight")
        plt.close(fig)
