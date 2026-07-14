"""Physical constants and plotting styles."""

UNI_PGCYR = 12.011 * 365 * 24 * 3600 / 1e15
SEC_PER_YR = 365.25 * 24 * 3600
UNI_PGCYR_ALT = 12.0 * 1e-15 * SEC_PER_YR

COLOR_DICT = {
    "ssp126": "orange",
    "ssp245": "green",
    "ssp585": "purple",
}

LABEL_DICT = {
    "ssp126": "SSP1-2.6",
    "ssp245": "SSP2-4.5",
    "ssp585": "SSP5-8.5",
}

TRANSPORT_PLOT_META = {
    "volume_transport": {
        "title": "Net Volume Transport at 26N: annual mean SSP comparison",
        "ylabel": "(Sv)",
    },
    "amoc_strength": {
        "title": "AMOC Strength at 26N: annual mean SSP comparison",
        "ylabel": "(Sv)",
    },
    "amoc_depth": {
        "title": "AMOC Core Depth at 26N: annual mean SSP comparison",
        "ylabel": "(m)",
    },
    "canth_transport": {
        "title": "Canth Transport at 26N: annual mean SSP comparison",
        "ylabel": "(PgC/yr)",
    },
    "dissic_transport": {
        "title": "DIC Transport at 26N: annual mean SSP comparison",
        "ylabel": "(PgC/yr)",
    },
    "dissicnat_transport": {
        "title": "Natural DIC Transport at 26N: annual mean SSP comparison",
        "ylabel": "(PgC/yr)",
    },
    "canth_mean_concentration": {
        "title": "Area-weighted Mean Canth Concentration at 26N",
        "ylabel": "(mol m$^{-3}$)",
    },
}

BUDGET_DECOMP_META = {
    "total_change": {"color": "black", "label": r"$\Delta(C_{(t)} \times V_{(t)})$"},
    "v0_dC": {"color": "purple", "label": r"$V_{(t0)} \cdot \Delta C_{(t)}$"},
    "C0_dV": {"color": "orange", "label": r"$C_{(t0)} \cdot \Delta V_{(t)}$"},
    "dV_dC": {"color": "dodgerblue", "label": r"$\Delta V_{(t)} \cdot \Delta C_{(t)}$"},
}

BUDGET_REGION_META = {
    "total_canth_transport": {"color": "black", "label": "Total"},
    "WBC": {"color": "red", "label": "WBC"},
    "NonWBC_0_700m": {"color": "blue", "label": "Non-WBC (0–700m)"},
    "NonWBC_700m_bottom": {"color": "gray", "label": "Non-WBC (700m–bottom)"},
}

ROCCA_COLORS = ["black", "blue", "red"]
ROCCA_MID_COLORS = [(0.5, 0.5, 0.5), (0.5, 0.7, 1), (1, 0.5, 0.5)]
ROCCA_LABELS = ["Total", "Overturning", "Horizontal"]

BUDGET_WBC_DECOMP_META = {
    "total_change": {"color": "red", "label": r"$\Delta(C_{(t)} \times v_{(t)})$"},
    "v0_dC": {"color": "purple", "label": r"$v_{(t0)} \cdot \Delta C_{(t)}$"},
    "C0_dV": {"color": "orange", "label": r"$C_{(t0)} \cdot \Delta V_{(t)}$"},
    "dV_dC": {"color": "dodgerblue", "label": r"$\Delta V_{(t)} \cdot \Delta C_{(t)}$"},
}

BUDGET_NONWBC_DECOMP_META = {
    "total_change": {"color": "blue", "label": r"$\Delta(C_{(t)} \times v_{(t)})$"},
    "v0_dC": {"color": "purple", "label": r"$v_{(t0)} \cdot \Delta C_{(t)}$"},
    "C0_dV": {"color": "orange", "label": r"$C_{(t0)} \cdot \Delta V_{(t)}$"},
    "dV_dC": {"color": "dodgerblue", "label": r"$\Delta V_{(t)} \cdot \Delta C_{(t)}$"},
}

TOE_PLOT_META = {
    "volume_transport": {"ylabel": "Net Volume Transport (Sv)", "title": ""},
    "amoc_strength": {"ylabel": "AMOC Strength (Sv)", "title": ""},
    "canth_transport": {"ylabel": "Canth Transport (PgC/yr)", "title": ""},
    "canth_mean_concentration": {
        "ylabel": "Mean Canth Concentration (mol m$^{-3}$)",
        "title": "",
    },
}
