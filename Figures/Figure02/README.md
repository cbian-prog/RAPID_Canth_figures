# Figure 2

Vertical profiles at 26.5°N averaged over 2004–2014: C_anth transport and volume transport accumulated from the surface down, and the zonal-mean C_anth concentration, for each scenario.

## Data

- `data/RAPID_Figure02_data.csv`: `scenario`, `depth_m`, `canth_transport_PgC_yr`, `volume_transport_Sv`, `canth_concentration_mol_m3`, `period`

Run `python plot.py` from this folder. It reads only `data/` and writes `RAPID_Figure02.png`. The data files are written by `analysis/export_figure_data.py` from the output of `analysis/compute.py`.
