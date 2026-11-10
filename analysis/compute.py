#!/usr/bin/env python3
"""
RAPID figures: computation program (computes only, draws no figures).

Reads the CMIP6 RAPID-section data from GCS, computes every diagnostic, and
saves the data the figures need to outputs/data/.

Usage:
    python compute.py
    RAPID_FIG_OUTPUT=/path/to/out python compute.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common.config import (  # noqa: E402
    PROFILE_YEAR_END,
    PROFILE_YEAR_START,
    SSP_EXPERIMENTS,
    TOE_START_YEAR,
    TOE_STEP_YEARS,
    TOE_THRESHOLD,
    TREND_END_1,
    TREND_END_2,
    TREND_START_1,
    TREND_START_2,
    data_dir,
)
from common.budget import compute_budget_dicts  # noqa: E402
from common.data_pipeline import build_masked_concat_dicts  # noqa: E402
from common.decomp import compute_decomp_dict  # noqa: E402
from common.io import save_dataset, save_dict_of_datasets, save_json  # noqa: E402
from common.profiles import compute_profiles_for_all_ssps  # noqa: E402
from common.rocca import build_rocca_datasets, save_rocca_datasets  # noqa: E402
from common.sections import compute_lon_sections_for_all_ssps  # noqa: E402
from common.toe import compute_toe_for_all_variables  # noqa: E402
from common.trends import compute_trends_all_vars  # noqa: E402
from common.transports import build_transport_dicts  # noqa: E402

TREND_VARS = [
    "canth_transport",
    "volume_transport",
    "amoc_strength",
    "canth_mean_concentration",
]


def run() -> Path:
    out = data_dir()
    print("=== RAPID compute started ===")
    print(f"Output data directory: {out}")

    # ------------------------------------------------------------------
    # 1. Load masked annual/monthly fields + RAPID area
    # ------------------------------------------------------------------
    print("\n[1/8] Loading and masking GCS data ...")
    masked_annual, masked_monthly, area_like = build_masked_concat_dicts()
    save_dataset(area_like.to_dataset(), out / "area_like.nc")

    # ------------------------------------------------------------------
    # 2. Volume / AMOC / carbon transports
    # ------------------------------------------------------------------
    print("[2/8] Computing transports ...")
    annual_transport, monthly_transport = build_transport_dicts(
        masked_annual, masked_monthly, area_like
    )
    save_dict_of_datasets(annual_transport, out / "annual_transport")
    save_dict_of_datasets(monthly_transport, out / "monthly_transport")

    # ------------------------------------------------------------------
    # 3. Canth decomposition (overturning + horizontal)
    # ------------------------------------------------------------------
    print("[3/8] Computing Canth decomposition ...")
    save_dict_of_datasets(
        compute_decomp_dict(masked_annual, area_like), out / "annual_decomp"
    )
    save_dict_of_datasets(
        compute_decomp_dict(masked_monthly, area_like), out / "monthly_decomp"
    )

    # ------------------------------------------------------------------
    # 4. Vertical profiles & longitude sections (2004–2014 mean)
    # ------------------------------------------------------------------
    print(f"[4/8] Computing profiles & sections ({PROFILE_YEAR_START}-{PROFILE_YEAR_END}) ...")
    save_dict_of_datasets(
        compute_profiles_for_all_ssps(
            masked_annual,
            area_like,
            PROFILE_YEAR_START,
            PROFILE_YEAR_END,
            tuple(SSP_EXPERIMENTS),
        ),
        out / "profiles",
    )
    save_dict_of_datasets(
        compute_lon_sections_for_all_ssps(
            masked_annual,
            area_like,
            PROFILE_YEAR_START,
            PROFILE_YEAR_END,
            tuple(SSP_EXPERIMENTS),
        ),
        out / "sections",
    )

    # ------------------------------------------------------------------
    # 5. Time of Emergence (ToE)
    # ------------------------------------------------------------------
    print("[5/8] Computing ToE ...")
    toe_dict, _ = compute_toe_for_all_variables(
        annual_transport,
        start_year=TOE_START_YEAR,
        step_years=TOE_STEP_YEARS,
        threshold=TOE_THRESHOLD,
    )
    save_json(toe_dict, out / "toe_dict.json")

    # ------------------------------------------------------------------
    # 6. Linear trends
    # ------------------------------------------------------------------
    print("[6/8] Computing linear trends ...")
    df1 = compute_trends_all_vars(annual_transport, TREND_VARS, TREND_START_1, TREND_END_1)
    df2 = compute_trends_all_vars(annual_transport, TREND_VARS, TREND_START_2, TREND_END_2)
    p1 = out / f"trends_{TREND_START_1}_{TREND_END_1}.csv"
    p2 = out / f"trends_{TREND_START_2}_{TREND_END_2}.csv"
    df1.to_csv(p1, index=False)
    df2.to_csv(p2, index=False)

    # ------------------------------------------------------------------
    # 7. Canth budget diagnostics (Test_budget.ipynb)
    # ------------------------------------------------------------------
    print("[7/8] Computing Canth budget diagnostics ...")
    annual_budget, monthly_budget = compute_budget_dicts(
        masked_annual, masked_monthly, area_like
    )
    for key in ("budget_decomp", "regional_canth", "subregion_decomp"):
        save_dict_of_datasets(
            {exp: d[key] for exp, d in annual_budget.items()},
            out / f"annual_{key}",
        )
        save_dict_of_datasets(
            {exp: d[key] for exp, d in monthly_budget.items()},
            out / f"monthly_{key}",
        )

    # ------------------------------------------------------------------
    # 8. ROCCA figure 1 data (CMIP6 vs RAPID obs, 2004–2014)
    # ------------------------------------------------------------------
    print("[8/8] Loading ROCCA CMIP6 vs obs data ...")
    try:
        rocca = build_rocca_datasets()
        save_rocca_datasets(rocca, out)
        rocca_ok = True
    except FileNotFoundError as exc:
        print(f"Warning: ROCCA data skipped — {exc}")
        rocca_ok = False

    meta = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "profile_start": PROFILE_YEAR_START,
        "profile_end": PROFILE_YEAR_END,
        "toe_start": TOE_START_YEAR,
        "toe_step_years": TOE_STEP_YEARS,
        "toe_threshold": TOE_THRESHOLD,
        "experiments": list(SSP_EXPERIMENTS),
        "files": {
            "annual_transport": "annual_transport/{ssp}.nc",
            "monthly_transport": "monthly_transport/{ssp}.nc",
            "annual_decomp": "annual_decomp/{ssp}.nc",
            "monthly_decomp": "monthly_decomp/{ssp}.nc",
            "profiles": "profiles/{ssp}.nc",
            "sections": "sections/{ssp}.nc",
            "toe": "toe_dict.json",
            "trends_early": p1.name,
            "trends_late": p2.name,
            "annual_budget_decomp": "annual_budget_decomp/{ssp}.nc",
            "monthly_budget_decomp": "monthly_budget_decomp/{ssp}.nc",
            "annual_regional_canth": "annual_regional_canth/{ssp}.nc",
            "monthly_regional_canth": "monthly_regional_canth/{ssp}.nc",
            "annual_subregion_decomp": "annual_subregion_decomp/{ssp}.nc",
            "monthly_subregion_decomp": "monthly_subregion_decomp/{ssp}.nc",
            "rocca": "rocca/{name}.nc",
        },
        "rocca_loaded": rocca_ok,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"\n=== Done. Plot data saved to {out} ===")
    print("Next: python plot.py")
    return out


if __name__ == "__main__":
    run()
