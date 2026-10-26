# Figure 12

Projected C_anth transport across 26.5°N from 2015, split (a) by region and (b) by contribution, ensemble mean ± 1 standard deviation. The regions are the western boundary current (WBC, the westernmost ten grid columns), the interior above about 700 m (top 21 model levels) and the interior below. The contributions are the change in concentration at the initial velocity, the change in velocity at the initial concentration, and their product, relative to the first scenario time step. One image per scenario and time resolution (six in all).

## Data

- `data/RAPID_Figure12_data.csv`: `scenario`, `frequency` (yearly/monthly), `panel` (regional/contribution), `series`, `time`, `mean`, `std` (PgC yr⁻¹)

Run `python plot.py` from this folder. It reads only `data/` and writes `RAPID_Figure12_<scenario>_<yearly|monthly>.png`. The data files are written by `analysis/export_figure_data.py` from the output of `analysis/compute.py`.
