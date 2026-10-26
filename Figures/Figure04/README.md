# Figure 4

Annual C_anth transport across 26.5°N, 1850–2100, historical run joined to each scenario, ensemble mean ± 1 standard deviation.

## Data

- `data/RAPID_Figure04_data.csv`: `scenario`, `year`, `mean`, `std` (PgC yr⁻¹)
- `data/RAPID_trends_*.csv`: linear trends of the four annual series of Figures 4–7 over 2004–2050 and 2050–2100; numbers quoted in the text, not drawn

Run `python plot.py` from this folder. It reads only `data/` and writes `RAPID_Figure04.png`. The data files are written by `analysis/export_figure_data.py` from the output of `analysis/compute.py`.
