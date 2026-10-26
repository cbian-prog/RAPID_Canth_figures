#!/usr/bin/env python3
"""Figure 3: along-section structure at 26.5N, period mean (2004-2014 by
default): depth-integrated C_anth transport, volume transport and C_anth
inventory at each longitude, three scenarios.

Reads data/RAPID_Figure03_data.csv; writes RAPID_Figure03.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SCEN = ["ssp126", "ssp245", "ssp585"]
COLOR = {"ssp126": "orange", "ssp245": "green", "ssp585": "purple"}
LABEL = {"ssp126": "SSP1-2.6", "ssp245": "SSP2-4.5", "ssp585": "SSP5-8.5"}
COLS = ["canth_transport_PgC_yr", "volume_transport_Sv", "canth_amount_mol_m2"]
TITLES = ["Canth transport at each location", "Volume transport at each location",
          "Canth amount at each location"]
YLABELS = ["(PgC/yr)", "(Sv)", "(mol m$^{-2}$)"]


def deg_west(lon, offset):
    """Model longitude (0-360) to degrees west, as the original figure did."""
    lon = np.asarray(lon, float)
    return np.where(lon > 180, 360 - lon, -lon) + offset


d = pd.read_csv(HERE / "data" / "RAPID_Figure03_data.csv")
fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharex=True)
for exp in SCEN:
    c = d[d.scenario == exp]
    lw_ = deg_west(c.lon, -0.5)
    idx = np.argsort(lw_)
    for ax, col, title, ylab in zip(axes, COLS, TITLES, YLABELS):
        ax.plot(lw_[idx], c[col].values[idx], color=COLOR[exp], label=LABEL[exp], lw=2)
        ax.set_title(title)
        ax.set_xlabel("Longitude")
        ax.set_ylabel(ylab)
        ax.grid(True, alpha=0.3)
lon0 = np.sort(deg_west(d[d.scenario == SCEN[0]].lon, +0.5))
ticks = np.arange(int(lon0.min() // 20 * 20), int(lon0.max() // 20 * 20 + 21), 20)
for ax in axes:
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{x}°W" for x in ticks])
    ax.set_xlim(lon0.max(), lon0.min())
axes[0].legend(frameon=False)
plt.tight_layout()
fig.savefig(HERE / "RAPID_Figure03.png", dpi=300, bbox_inches="tight")
