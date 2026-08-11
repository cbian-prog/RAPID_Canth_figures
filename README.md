# rapid_figures

CMIP6 diagnostics and figure-generation workflow for the RAPID section at 26.5°N. The pipeline can be run independently on [LEAP JupyterHub](https://leap.2i2c.cloud/) or in a local environment.

This repository was refactored from `Timeseri_RAPID_figure.ipynb`, `Test_budget.ipynb`, and `ROCCA_figure1-Copy1.ipynb` into two main programs:

| File             | Purpose                                                                     |
| ---------------- | --------------------------------------------------------------------------- |
| **`compute.py`** | Performs all computations and writes results to `outputs/data/`             |
| **`plot.py`**    | Generates figures from `outputs/data/` and saves them to `outputs/figures/` |

The `common/` directory contains internal utility modules. See `docs/SOURCES.md` for the mapping between the original notebooks and the refactored code.

---

## Directory Structure

```text
rapid_figures/
├── compute.py          # Main computation program (8 steps)
├── plot.py             # Main plotting program (15 figure categories)
├── requirements.txt
├── pack_for_cluster.sh # Package the repository for LEAP / cluster deployment
├── common/             # Data loading, diagnostics, budget analysis, ROCCA utilities, etc.
├── cluster/            # LEAP / Slurm execution scripts
├── docs/
│   └── SOURCES.md      # Documentation of notebook sources
└── outputs/            # Runtime outputs (ignored by git)
    ├── data/
    └── figures/
```

---

## Quick Start

```bash
git clone <your-repo-url>
cd rapid_figures

pip install -r requirements.txt

# 1. Run computations (requires GCS access)
python compute.py

# 2. Generate figures
# This step can be rerun without repeating the computations
python plot.py
```

---

## Environment Variables

| Variable                  | Default                                 | Description                                         |
| ------------------------- | --------------------------------------- | --------------------------------------------------- |
| `RAPID_GCS_BASE`          | `gs://leap-persistent/cbian-prog`       | Root path of the CMIP6 zarr datasets                |
| `RAPID_MASK_AREA_PATH`    | `/home/jovyan/RAPID_mask_area.nc`       | RAPID mask and grid-cell area file                  |
| `RAPID_OBS_CANTH_MAT`     | `/home/jovyan/RAPID_Canth_20042014.mat` | ROCCA observational dataset used for Figures 14–15  |
| `RAPID_FIG_OUTPUT`        | `./outputs`                             | Root output directory                               |
| `RAPID_PROFILE_START/END` | `2004` / `2014`                         | Averaging period for profiles and sections          |
| `RAPID_SSP_START`         | `2015`                                  | Starting year for the SSP analysis in `Test_budget` |

Example:

```bash
export RAPID_GCS_BASE="gs://leap-persistent/cbian-prog"
export RAPID_MASK_AREA_PATH="/home/jovyan/RAPID_mask_area.nc"
export RAPID_OBS_CANTH_MAT="/home/jovyan/RAPID_Canth_20042014.mat"
export RAPID_FIG_OUTPUT="/home/jovyan/rapid_outputs"   # optional
```

---

## `compute.py` Workflow

`compute.py` performs the analysis in eight steps:

| Step | Description                                                                             |
| ---- | --------------------------------------------------------------------------------------- |
| 1    | Load and mask GCS datasets for historical and SSP1-2.6 / SSP2-4.5 / SSP5-8.5            |
| 2    | Calculate volume transport, AMOC strength, and anthropogenic carbon transport           |
| 3    | Decompose anthropogenic carbon transport into overturning and horizontal components     |
| 4    | Calculate vertical profiles and longitude-depth sections averaged over 2004–2014        |
| 5    | Calculate Time of Emergence (ToE)                                                       |
| 6    | Calculate linear trends and save them as CSV files                                      |
| 7    | Run `Test_budget`: contribution, regional, and subregional decompositions               |
| 8    | Run ROCCA diagnostics comparing CMIP6 simulations with RAPID observations for 2004–2014 |

The main outputs are written to `outputs/data/` as NetCDF, JSON, CSV, and `meta.json` files.

A detailed output list is provided below.

---

## `plot.py` Outputs

Figures are written to `outputs/figures/`.

| Figure                                                           | Description                                                                                                |
| ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `01_annual_monthly_decomp.png`                                   | Annual and monthly anthropogenic carbon transport decomposition into overturning and horizontal components |
| `02_vertical_profiles_2004_2014.png`                             | Three-panel vertical profile figure                                                                        |
| `03_lon_sections_2004_2014.png`                                  | Three-panel longitude-depth section figure                                                                 |
| `04_canth_transport.png`                                         | Anthropogenic carbon transport time series                                                                 |
| `04_amoc_strength.png`                                           | AMOC strength time series                                                                                  |
| `04_volume_transport.png`                                        | Volume transport time series                                                                               |
| `04_canth_mean_concentration.png`                                | Section-mean anthropogenic carbon concentration time series                                                |
| `08_ToE_canth_transport.png`                                     | Anthropogenic carbon transport with Time of Emergence                                                      |
| `09_ToE_volume_transport.png`                                    | Volume transport with Time of Emergence                                                                    |
| `10_ToE_amoc_strength.png`                                       | AMOC strength with Time of Emergence                                                                       |
| `11_annual_vs_monthly_volume_{ssp}.png`                          | Comparison of annual and monthly volume transport for SSP5-8.5 and SSP2-4.5                                |
| `12_{ssp}_{yearly\|monthly}_combined.png`                        | `Test_budget` regional and contribution-term decomposition                                                 |
| `13_{ssp}_{yearly\|monthly}_decomposition_WBC_NonWBC_0_700m.png` | WBC / Non-WBC subregional decomposition                                                                    |
| `14_rocca_canth_transport_combined.png`                          | CMIP6 versus RAPID observational anthropogenic carbon transport time series                                |
| `15_rocca_canth_seasonal_combined.png`                           | CMIP6 versus observational seasonal climatology of anthropogenic carbon transport                          |

Linear trend tables are printed directly to the terminal when `plot.py` is executed and are not saved as figures.

---

## Data Outputs

All processed data are stored under `outputs/data/`.

| Path                                                    | Contents                                                                          |
| ------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `annual_transport/{ssp}.nc`                             | Annual transport diagnostics                                                      |
| `monthly_transport/{ssp}.nc`                            | Monthly transport diagnostics                                                     |
| `annual_decomp/`, `monthly_decomp/`                     | Overturning and horizontal decomposition                                          |
| `profiles/`, `sections/`                                | Vertical profiles and longitude-depth sections                                    |
| `toe_dict.json`                                         | Time of Emergence results                                                         |
| `trends_*.csv`                                          | Linear trend results                                                              |
| `annual_budget_decomp/`, `monthly_budget_decomp/`       | `Test_budget` contribution-term decomposition                                     |
| `annual_regional_canth/`, `monthly_regional_canth/`     | WBC / Non-WBC regional anthropogenic carbon transport                             |
| `annual_subregion_decomp/`, `monthly_subregion_decomp/` | Subregional decomposition                                                         |
| `rocca/`                                                | Cached CMIP6 ensemble-member and observational data used by the ROCCA diagnostics |

### GCS Input Variables

The workflow uses the following CMIP6 variables:

```text
vo
dissic
dissicnat
```

The required datasets include historical and SSP1-2.6 / SSP2-4.5 / SSP5-8.5 simulations at both annual and monthly temporal resolution.

---

## LEAP / Cluster Deployment

Package the repository:

```bash
bash pack_for_cluster.sh
```

Upload `rapid_figures_*.tar.gz` to the Hub or cluster, then extract and enter the repository:

```bash
tar -xzf rapid_figures_*.tar.gz
cd rapid_figures
```

Set up the environment:

```bash
bash cluster/setup.sh
```

Run the computations:

```bash
python compute.py
```

or:

```bash
bash cluster/run_compute.sh
```

Generate the figures:

```bash
python plot.py
```

or:

```bash
bash cluster/run_plot.sh
```

An example Slurm submission script is available at:

```text
cluster/slurm_example.sh
```

---

## Uploading to GitHub

This directory is designed to function as an **independent git repository** and is separate from any git repository that may exist under `~/`.

For the first push:

```bash
cd rapid_figures

git init
git add .
git commit -m "Initial commit: RAPID figure pipeline"
git branch -M main
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

The following runtime and data products are excluded through `.gitignore` and will not be uploaded to GitHub:

```text
outputs/
*.mat
*.nc
*.tar.gz
```
