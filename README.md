# rapid_figures

RAPID 断面（26.5°N）CMIP6 诊断与出图流程，可在 [LEAP JupyterHub](https://leap.2i2c.cloud/) 或本地独立运行。

由 `Timeseri_RAPID_figure.ipynb`、`Test_budget.ipynb`、`ROCCA_figure1-Copy1.ipynb` 重构为两个主程序：

| 文件 | 作用 |
|------|------|
| **`compute.py`** | 只计算，输出到 `outputs/data/` |
| **`plot.py`** | 只绘图，读取 `outputs/data/`，输出到 `outputs/figures/` |

`common/` 为内部工具库。来源对照见 [`docs/SOURCES.md`](docs/SOURCES.md)。

---

## 目录结构

```
rapid_figures/
├── compute.py          # 计算主程序（8 步）
├── plot.py             # 绘图主程序（15 类图）
├── requirements.txt
├── pack_for_cluster.sh # 打包上传 LEAP / 集群
├── common/             # 数据加载、诊断、预算、ROCCA 等
├── cluster/            # LEAP / Slurm 运行脚本
├── docs/
│   └── SOURCES.md      # notebook 来源说明
└── outputs/            # 运行产物（git 忽略）
    ├── data/
    └── figures/
```

---

## 快速开始

```bash
git clone <your-repo-url>
cd rapid_figures

pip install -r requirements.txt

# 1. 计算（需要 GCS 访问权限）
python compute.py

# 2. 绘图（可反复运行，无需重算）
python plot.py
```

---

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `RAPID_GCS_BASE` | `gs://leap-persistent/cbian-prog` | CMIP6 zarr 根路径 |
| `RAPID_MASK_AREA_PATH` | `/home/jovyan/RAPID_mask_area.nc` | RAPID mask/area |
| `RAPID_OBS_CANTH_MAT` | `/home/jovyan/RAPID_Canth_20042014.mat` | ROCCA 观测（图 14–15） |
| `RAPID_FIG_OUTPUT` | `./outputs` | 输出根目录 |
| `RAPID_PROFILE_START/END` | `2004` / `2014` | 剖面/断面平均时段 |
| `RAPID_SSP_START` | `2015` | Test_budget 的 SSP 起始年 |

```bash
export RAPID_GCS_BASE="gs://leap-persistent/cbian-prog"
export RAPID_MASK_AREA_PATH="/home/jovyan/RAPID_mask_area.nc"
export RAPID_OBS_CANTH_MAT="/home/jovyan/RAPID_Canth_20042014.mat"
export RAPID_FIG_OUTPUT="/home/jovyan/rapid_outputs"   # 可选
```

---

## compute.py（8 步）

| 步骤 | 内容 |
|------|------|
| 1 | 加载并 mask GCS 数据（historical + ssp126/245/585） |
| 2 | 体积 / AMOC / Canth 输送 |
| 3 | Canth 分解（overturning + horizontal） |
| 4 | 垂直剖面 + 经向断面（2004–2014） |
| 5 | Time of Emergence (ToE) |
| 6 | 线性趋势 CSV |
| 7 | Test_budget：贡献项 / 区域 / 子区域分解 |
| 8 | ROCCA：CMIP6 vs RAPID 观测（2004–2014） |

主要输出目录：`outputs/data/`（NetCDF、JSON、CSV、`meta.json`）。完整清单见下方表格。

---

## plot.py 输出（`outputs/figures/`）

| 图片 | 说明 |
|------|------|
| `01_annual_monthly_decomp.png` | Canth overturning / horizontal，年+月 |
| `02_vertical_profiles_2004_2014.png` | 三面板垂直剖面 |
| `03_lon_sections_2004_2014.png` | 三面板经向断面 |
| `04_canth_transport.png` | Canth 输送时间序列 |
| `04_amoc_strength.png` | AMOC 强度时间序列 |
| `04_volume_transport.png` | 体积输送时间序列 |
| `04_canth_mean_concentration.png` | 断面平均 Canth 浓度 |
| `08_ToE_canth_transport.png` | Canth 输送 + ToE |
| `09_ToE_volume_transport.png` | 体积输送 + ToE |
| `10_ToE_amoc_strength.png` | AMOC + ToE |
| `11_annual_vs_monthly_volume_{ssp}.png` | 年 vs 月体积输送（ssp585, ssp245） |
| `12_{ssp}_{yearly\|monthly}_combined.png` | Test_budget 区域 + 贡献项分解 |
| `13_{ssp}_{yearly\|monthly}_decomposition_WBC_NonWBC_0_700m.png` | WBC / Non-WBC 子区域分解 |
| `14_rocca_canth_transport_combined.png` | CMIP6 vs RAPID 观测时间序列 |
| `15_rocca_canth_seasonal_combined.png` | CMIP6 vs 观测季节气候态 |

趋势表在 `plot.py` 运行时打印到终端（不生成图片）。

---

## 数据输出（`outputs/data/`）

| 路径 | 内容 |
|------|------|
| `annual_transport/{ssp}.nc` | 年尺度输送 |
| `monthly_transport/{ssp}.nc` | 月尺度输送 |
| `annual_decomp/`, `monthly_decomp/` | overturning / horizontal 分解 |
| `profiles/`, `sections/` | 剖面与断面 |
| `toe_dict.json` | ToE 结果 |
| `trends_*.csv` | 线性趋势 |
| `annual_budget_decomp/`, `monthly_budget_decomp/` | Test_budget 贡献项 |
| `annual_regional_canth/`, `monthly_regional_canth/` | WBC / Non-WBC 区域输送 |
| `annual_subregion_decomp/`, `monthly_subregion_decomp/` | 子区域分解 |
| `rocca/` | ROCCA CMIP6 成员与观测缓存 |

**GCS 输入变量：** `vo`, `dissic`, `dissicnat`（historical + ssp126/245/585，annual & monthly zarr）

---

## LEAP / 集群部署

```bash
bash pack_for_cluster.sh
# 上传 rapid_figures_*.tar.gz 到 Hub 后：
tar -xzf rapid_figures_*.tar.gz && cd rapid_figures
bash cluster/setup.sh
python compute.py    # 或: bash cluster/run_compute.sh
python plot.py       # 或: bash cluster/run_plot.sh
```

Slurm 示例见 `cluster/slurm_example.sh`。

---

## 上传到 GitHub

本目录为**独立 git 仓库**（与 `~/` 下的 git 无关）：

```bash
cd rapid_figures

# 首次推送
git init
git add .
git commit -m "Initial commit: RAPID figure pipeline"
git branch -M main
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

`outputs/`、`.mat`、`.nc`、打包的 `.tar.gz` 已在 `.gitignore` 中排除，不会上传运行产物。
