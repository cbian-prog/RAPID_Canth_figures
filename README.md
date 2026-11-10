# RAPID C_anth transport — analysis code, figures and plotted data

Anthropogenic carbon (C_anth) transport across the RAPID section at 26.5°N in
CMIP6, historical and SSP1-2.6 / SSP2-4.5 / SSP5-8.5, compared with the
RAPID-based observational estimate for 2004–2014.

## Layout

```
analysis/    the code that computes every diagnostic from CMIP6 output
Figures/     one folder per figure: plot script, plotted data, figure
tests/       a synthetic stand-in for compute.py's output, used by the check below
```

```
Figures/Figure04/
    plot.py                        numpy, pandas, matplotlib — nothing else
    data/RAPID_Figure04_data.csv   every curve as plotted
    RAPID_Figure04.png
    README.md
```

The pipeline has three steps:

```bash
cd analysis
python compute.py                # CMIP6 on GCS -> outputs/data/  (run on LEAP)
python export_figure_data.py     # outputs/data/ -> ../Figures/FigureNN/data/
bash ../Figures/run_all.sh       # redraw every figure
```

Once `data/` is filled, any figure redraws on its own:

```bash
pip install -r Figures/requirements.txt
cd Figures/Figure04 && python plot.py
```

The figure folders share no code, so any one of them can be copied out on its
own and still redraw its figure. See `analysis/README.md` for the methods and
the environment variables `compute.py` needs.

| Folder in `Figures/` | Figure |
|---|---|
| `Figure01/` | Overturning and horizontal C_anth transport, annual and monthly |
| `Figure02/` | Vertical profiles of C_anth transport, volume transport and concentration, 2004–2014 |
| `Figure03/` | Along-section C_anth transport, volume transport and inventory, 2004–2014 |
| `Figure04/` | Annual C_anth transport, 1850–2100 |
| `Figure05/` | Annual AMOC strength, 1850–2100 |
| `Figure06/` | Annual net volume transport, 1850–2100 |
| `Figure07/` | Area-weighted mean C_anth concentration, 1850–2100 |
| `Figure08/` | C_anth transport with its time of emergence |
| `Figure09/` | Net volume transport with its time of emergence |
| `Figure10/` | AMOC strength with its time of emergence |
| `Figure11/` | Volume transport, annual against monthly mean |
| `Figure12/` | Regional and contribution split of the projected C_anth transport |
| `Figure13/` | Contribution split within the western boundary current and the interior 0–700 m |
| `Figure14/` | CMIP6 against observed C_anth transport, 2004–2014 |
| `Figure15/` | Seasonal cycle, CMIP6 against observations, 2004–2014 |

The numbering follows the original notebooks (`analysis/SOURCES.md`).

## Reproducibility

The figure scripts reproduce the drawing code of the original single plotting
program. Drawn from the same data, all 26 images match the original output
pixel for pixel, except for about 20 antialiased pixels in Figure 9 that come
from the last digit of the CSV round trip.

The data files hold ensemble-level quantities. Members appear only where a
panel draws them (Figures 14 and 15).

A GitHub Actions check runs at every push. It writes synthetic data in
compute.py's output layout (`tests/make_synthetic_outputs.py`), exports it and
draws all 26 images, so a change that breaks the path from compute output to
figure fails visibly before any real data are involved. Once the exported
`data/` folders are committed, the same check also redraws the figures from
them.

## Licence and citation

Code under the MIT Licence; data files and figures under CC BY 4.0. See
`LICENSE` and `CITATION.cff`.
