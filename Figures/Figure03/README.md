# Figure 3

Along-section structure at 26.5°N averaged over 2004–2014: depth-integrated C_anth transport, volume transport and C_anth inventory in each grid column, plotted against longitude.

## Data

- `data/RAPID_Figure03_data.csv`: `scenario`, `lon` (model longitude, 0–360; the script converts it to °W), `canth_transport_PgC_yr`, `volume_transport_Sv`, `canth_amount_mol_m2`, `period`

Run `python plot.py` from this folder. It reads only `data/` and writes `RAPID_Figure03.png`. The data files are written by `analysis/export_figure_data.py` from the output of `analysis/compute.py`.
