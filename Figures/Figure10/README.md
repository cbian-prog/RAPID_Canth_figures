# Figure 10

As Figure 8, for AMOC strength.

## Data

- `data/RAPID_Figure10_data.csv`: `scenario`, `year`, `mean`, `std` (Sv)
- `data/RAPID_Figure10_toe.csv`: `scenario`, `toe_year`

Run `python plot.py` from this folder. It reads only `data/` and writes `RAPID_Figure10.png`. The data files are written by `analysis/export_figure_data.py` from the output of `analysis/compute.py`.
