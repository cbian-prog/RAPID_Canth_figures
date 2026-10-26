# analysis — from CMIP6 fields at 26.5°N to the figure data

This folder holds the code that computes everything the figures show: volume
and C_anth transport across the RAPID section, the AMOC strength, the
overturning/horizontal split, profiles and along-section structure, times of
emergence, trends, the budget decomposition of the projected change, and the
comparison with the RAPID-based observational estimate. The figure folders in
`../Figures/` only redraw what this code exports.

## Running

```bash
pip install -r requirements.txt
bash cluster/setup.sh            # sets the paths below; edit for your machine
python compute.py                # CMIP6 on GCS -> outputs/data/   (needs GCS access)
python export_figure_data.py     # outputs/data/ -> ../Figures/FigureNN/data/
bash ../Figures/run_all.sh       # redraw every figure
```

`compute.py` reads `gs://leap-persistent/cbian-prog` and is meant to run on
LEAP JupyterHub, where that bucket is readable; `cluster/slurm_example.sh` and
`pack_for_cluster.sh` cover running it elsewhere. `export_figure_data.py` and
the figure scripts run anywhere.

| Variable | Default | Meaning |
|---|---|---|
| `RAPID_GCS_BASE` | `gs://leap-persistent/cbian-prog` | Root of the CMIP6 section zarr stores |
| `RAPID_MASK_AREA_PATH` | `/home/jovyan/RAPID_mask_area.nc` | Section mask and cell area (falls back to the area zarr on GCS) |
| `RAPID_OBS_CANTH_MAT` | `/home/jovyan/RAPID_Canth_20042014.mat` | Observational C_anth transport, 2004–2014 (Figures 14–15) |
| `RAPID_FIG_OUTPUT` | `./outputs` | Where `compute.py` writes |
| `RAPID_PROFILE_START` / `_END` | `2004` / `2014` | Averaging period of Figures 2–3 |
| `RAPID_SSP_START` | `2015` | Start of the budget decomposition (Figures 12–13) |
| `RAPID_TOE_START`, `RAPID_TOE_STEP`, `RAPID_TOE_THRESHOLD` | `2004`, `5`, `2.0` | Time-of-emergence settings |

## What each step does, and where

| Step in `compute.py` | Module | Figures |
|---|---|---|
| 1. Open the section stores, join historical to each scenario over the members common to both, apply the section mask | `common/io.py`, `common/data_pipeline.py` | all |
| 2. Volume, AMOC and carbon transports | `common/transports.py` | 4–11 |
| 3. Overturning and horizontal C_anth transport | `common/decomp.py` | 1 |
| 4. Vertical profiles and along-section structure | `common/profiles.py`, `common/sections.py` | 2, 3 |
| 5. Time of emergence | `common/toe.py` | 8–10 |
| 6. Linear trends | `common/trends.py` | quoted in the text |
| 7. Budget decomposition of the projected change | `common/budget.py` | 12, 13 |
| 8. CMIP6 against the observational estimate | `common/rocca.py` | 14, 15 |

**Transports** (`calc_transports`). Volume transport is Σ v·A over the section
(Sv). C_anth = `dissic` − `dissicnat`, and its transport is Σ v·C_anth·A
(PgC yr⁻¹). The overturning streamfunction integrates the zonally summed
transport upward from the sea floor, and the AMOC strength is its maximum over
depth. The mean concentration is area-weighted over the section.

**Overturning and horizontal split** (`compute_canth_decomp`). Velocity and
concentration are replaced by their zonal means at each depth; the transport
of those means is the overturning component, and the remainder of the total is
the horizontal (gyre) component. Zonal means are plain averages over the wet
grid columns.

**Time of emergence** (`compute_toe_from_yearly_da`). The linear trend of
each member is fitted over growing windows that all start in 2004 and end in
2008, 2013, 2018 and so on, every five years. The
signal-to-noise ratio is the absolute ensemble-mean trend divided by the
standard deviation of the member trends (ddof = 1). The time of emergence is
the end year of the first window from which that ratio stays above 2.

**Budget decomposition** (`decompose_transport_budget`). From 2015 only, the
change in C_anth transport relative to the first time step is split exactly
into v₀·ΔC, C₀·Δv and Δv·ΔC, summed over the section, the western boundary
current (the westernmost ten grid columns), or the interior above about 700 m
(the top 21 model levels). These index ranges belong to the model grid of the
section stores.

**Observational comparison** (`build_rocca_datasets`). Monthly total,
overturning and horizontal C_anth transport for 2004–2014 from every CMIP6
member in `cmip6_NA_Canth_budget_time`, with the CESM2 and CanESM5 members
also kept separately, against the observational estimate read from the `.mat`
file.

## From outputs to figures

`compute.py` writes member-resolved NetCDF to `outputs/data/` (listed in
`outputs/data/meta.json`). `export_figure_data.py` reduces it to exactly what
each figure draws: ensemble means and spreads (population standard deviation
over members, as the original figures used), the members where a panel draws
them, the observed series, and the emergence years. It writes these as CSV
into `../Figures/FigureNN/data/`.

`SOURCES.md` maps each step back to the notebook it came from.
