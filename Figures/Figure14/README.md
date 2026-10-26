# Figure 14

C_anth transport across 26.5°N in CMIP6 against the RAPID-based observational estimate, 2004–2014: every member with the observations, the ensemble mean ± 1 standard deviation with the observations, and the total, overturning and horizontal components separately.

## Data

- `data/RAPID_Figure14_members.csv`: `component`, `member`, `time` (decimal year), `value` (PgC yr⁻¹); every member is drawn
- `data/RAPID_Figure14_ensemble.csv`: `component`, `time`, `mean`, `std`
- `data/RAPID_Figure14_obs.csv`: `component`, `time`, `value`

Run `python plot.py` from this folder. It reads only `data/` and writes `RAPID_Figure14.png`. The data files are written by `analysis/export_figure_data.py` from the output of `analysis/compute.py`.
