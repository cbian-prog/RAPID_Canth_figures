# Figure 1

C_anth transport across 26.5°N split into its overturning and horizontal components, annual (a) and monthly (b), 2015–2100, ensemble mean ± 1 standard deviation under SSP1-2.6, SSP2-4.5 and SSP5-8.5.

## Data

- `data/RAPID_Figure01_data.csv`: `scenario`, `resolution` (annual/monthly), `component` (overturning/horizontal), `time` (decimal year), `mean`, `std` (PgC yr⁻¹)

Run `python plot.py` from this folder. It reads only `data/` and writes `RAPID_Figure01.png`. The data files are written by `analysis/export_figure_data.py` from the output of `analysis/compute.py`.
