#!/usr/bin/env python3
"""Figure 11: net volume transport at 26.5N, annual against monthly
ensemble mean, one panel per scenario (SSP5-8.5 and SSP2-4.5).

Reads data/RAPID_Figure11_data.csv; writes RAPID_Figure11_ssp585.png and
RAPID_Figure11_ssp245.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
COLOR = {"ssp126": "orange", "ssp245": "green", "ssp585": "purple"}
LABEL = {"ssp126": "SSP1-2.6", "ssp245": "SSP2-4.5", "ssp585": "SSP5-8.5"}

d = pd.read_csv(HERE / "data" / "RAPID_Figure11_data.csv")
for exp in ("ssp585", "ssp245"):
    a = d[(d.scenario == exp) & (d.resolution == "annual")]
    m = d[(d.scenario == exp) & (d.resolution == "monthly")]
    plt.figure(figsize=(10, 4))
    plt.plot(a.time, a["mean"], color=COLOR[exp], lw=2, label=f"{LABEL[exp]} annual")
    plt.plot(m.time, m["mean"], color=COLOR[exp], lw=1, alpha=0.6, ls=":",
             label=f"{LABEL[exp]} monthly")
    plt.xlim(1850, 2100)
    plt.xlabel("Year")
    plt.ylabel("Volume Transport at 26N (Sv)")
    plt.title(f"Volume Transport: {LABEL[exp]} annual vs monthly")
    plt.legend()
    plt.tight_layout()
    plt.savefig(HERE / f"RAPID_Figure11_{exp}.png", dpi=300, bbox_inches="tight")
    plt.close()
