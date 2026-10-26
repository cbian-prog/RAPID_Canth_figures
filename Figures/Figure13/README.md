# Figure 13

The contribution split of Figure 12b repeated within the western boundary current (c) and the interior above about 700 m (d). One image per scenario and time resolution (six in all).

## Data

- `data/RAPID_Figure13_data.csv`: `scenario`, `frequency`, `region` (wbc/nonwbc_upper), `series`, `time`, `mean`, `std` (PgC yr⁻¹)

Run `python plot.py` from this folder. It reads only `data/` and writes `RAPID_Figure13_<scenario>_<yearly|monthly>.png`. The data files are written by `analysis/export_figure_data.py` from the output of `analysis/compute.py`.
