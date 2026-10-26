# Figure 11

Net volume transport across 26.5°N, annual against monthly ensemble mean, for SSP5-8.5 and SSP2-4.5 (one image each).

## Data

- `data/RAPID_Figure11_data.csv`: `scenario`, `resolution`, `time` (decimal year), `mean` (Sv)

Run `python plot.py` from this folder. It reads only `data/` and writes `RAPID_Figure11_ssp585.png`, `RAPID_Figure11_ssp245.png`. The data files are written by `analysis/export_figure_data.py` from the output of `analysis/compute.py`.
