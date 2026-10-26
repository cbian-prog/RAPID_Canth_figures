#!/usr/bin/env python3
"""Figure 8: C_anth transport at 26.5N with its time of emergence (ToE) in each
scenario, ensemble mean +/- 1 std, 2002-2102.

Reads data/RAPID_Figure08_data.csv and data/RAPID_Figure08_toe.csv;
writes RAPID_Figure08.png.
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

d = pd.read_csv(HERE / "data" / "RAPID_Figure08_data.csv")
toe = pd.read_csv(HERE / "data" / "RAPID_Figure08_toe.csv").set_index("scenario")["toe_year"]
plt.figure(figsize=(10, 5))
for exp in SCEN:
    c = d[d.scenario == exp]
    years = c.year.astype(int)
    plt.plot(years, c["mean"], color=COLOR[exp], lw=2, label=f"{LABEL[exp]} mean")
    if c["std"].notna().any():
        plt.fill_between(years, c["mean"] - c["std"], c["mean"] + c["std"],
                         color=COLOR[exp], alpha=0.15)
plt.xlim(2002, 2102)
ymin, ymax = plt.ylim()
for exp in SCEN:
    t = toe.get(exp)
    if pd.isna(t):
        continue
    t = int(t)
    plt.vlines(t, ymin, ymax, colors=COLOR[exp], linestyles="--", lw=1)
    plt.text(t + 0.3, ymin + 0.05 * (ymax - ymin), f"ToE={t}", color=COLOR[exp],
             rotation=90, va="bottom")
plt.xlabel("Year")
plt.ylabel("Canth Transport (PgC/yr)")
plt.title("")
plt.legend(loc="upper right", ncol=3)
plt.tight_layout()
plt.savefig(HERE / "RAPID_Figure08.png", dpi=300, bbox_inches="tight")
