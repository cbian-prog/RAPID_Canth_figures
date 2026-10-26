#!/usr/bin/env python3
"""Figure 2: vertical profiles at 26.5N, period mean (2004-2014 by default):
cumulative C_anth transport, cumulative volume transport and zonal-mean
C_anth concentration, three scenarios.

Reads data/RAPID_Figure02_data.csv; writes RAPID_Figure02.png.
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
COLS = ["canth_transport_PgC_yr", "volume_transport_Sv", "canth_concentration_mol_m3"]
TITLES = ["Canth transport", "Volume transport", "Mean Canth concentration"]
XLABELS = ["(PgC/yr)", "(Sv)", "(mol m$^{-3}$)"]

d = pd.read_csv(HERE / "data" / "RAPID_Figure02_data.csv")
fig, axes = plt.subplots(1, 3, figsize=(14, 6), sharey=True)
for exp in SCEN:
    c = d[d.scenario == exp]
    for ax, col, title, xlab in zip(axes, COLS, TITLES, XLABELS):
        ax.plot(c[col], c.depth_m, color=COLOR[exp], label=LABEL[exp], linewidth=2)
        ax.set_title(title, fontsize=16)
        ax.set_xlabel(xlab, fontsize=16)
        ax.set_ylabel("Depth (m)", fontsize=16)
        ax.grid(True, alpha=0.3)
axes[0].invert_yaxis()
axes[0].legend(frameon=False, fontsize=16)
plt.tight_layout()
fig.savefig(HERE / "RAPID_Figure02.png", dpi=300, bbox_inches="tight")
