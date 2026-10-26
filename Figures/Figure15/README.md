# Figure 15

Seasonal cycle of C_anth transport across 26.5°N, 2004–2014, CMIP6 against the observations (left) and per component with every member, the ensemble and the CESM and CanESM means (right).

## Data

- `data/RAPID_Figure15_climatology.csv`: `component`, `series`, `month`, `mean`, `std`. `cmip6_within_member` is shaded by the mean within-member monthly standard deviation, `cmip6_across_member` by the spread of the member climatologies, and `obs` by the standard deviation across years (ddof = 1). `CESM` and `CanESM` are means only.
- `data/RAPID_Figure15_member_climatology.csv`: `component`, `member`, `month`, `value`

Run `python plot.py` from this folder. It reads only `data/` and writes `RAPID_Figure15.png`. The data files are written by `analysis/export_figure_data.py` from the output of `analysis/compute.py`.
