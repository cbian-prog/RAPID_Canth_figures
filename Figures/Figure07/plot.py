#!/usr/bin/env python3
"""Figure 7: area-weighted mean C_anth concentration at 26.5N, annual mean 1850-2100,
historical joined to each scenario, ensemble mean +/- 1 std.

Reads data/RAPID_Figure07_data.csv; writes RAPID_Figure07.png.
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
YLIM = (0, 0.04)

d = pd.read_csv(HERE / "data" / "RAPID_Figure07_data.csv")
plt.figure(figsize=(5, 2.5))
for exp in SCEN:
    c = d[d.scenario == exp]
    plt.plot(c.year, c["mean"], color=COLOR[exp], lw=2, label=LABEL[exp])
    if c["std"].notna().any():
        plt.fill_between(c.year, c["mean"] - c["std"], c["mean"] + c["std"],
                         color=COLOR[exp], alpha=0.18, lw=0)
plt.xlim(1850, 2100)
if YLIM:
    plt.ylim(*YLIM)
plt.xlabel("Year")
plt.ylabel(r"(mol m$^{-3}$)")
plt.title("Area-weighted Mean Canth Concentration at 26N")
plt.tight_layout()
plt.savefig(HERE / "RAPID_Figure07.png", dpi=300, bbox_inches="tight")
