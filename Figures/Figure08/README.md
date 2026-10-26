# Figure 8

Annual C_anth transport across 26.5°N, 2002–2102, with the year its forced trend emerges from internal variability (dashed line) in each scenario.

## Data

- `data/RAPID_Figure08_data.csv`: `scenario`, `year`, `mean`, `std` (PgC yr⁻¹)
- `data/RAPID_Figure08_toe.csv`: `scenario`, `toe_year` (empty where the signal never emerges)

Run `python plot.py` from this folder. It reads only `data/` and writes `RAPID_Figure08.png`. The data files are written by `analysis/export_figure_data.py` from the output of `analysis/compute.py`.
