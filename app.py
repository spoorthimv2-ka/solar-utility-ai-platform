
import os
import glob
import hashlib
import io
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
from services.data_service import (
    load_file,
    clean_data,
    validate_data,
    save_uploaded_data,
    load_saved_data,
    get_uploaded_files,
    get_file_info,
    get_data_summary,
    delete_uploaded_file,
    load_excel_sheets,
    save_uploaded_workbook,
    load_saved_workbook,
)
from services.ai_agent import ask_ai
from database import (
    get_question_history,
    get_previous_answer,
    save_question_history,
    clear_question_history,
)
import hashlib
# Optional PDF/Excel exports
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False
from services.config_service import (
    get_app_config,
    update_config,
)
st.set_page_config(
    page_title="Automated Utility Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>

/* =========================================================
   UTILITY INTELLIGENCE — ENTERPRISE VISUAL SYSTEM
   ========================================================= */

:root {
    --ui-navy: #12355B;
    --ui-blue: #2563EB;
    --ui-cyan: #0891B2;
    --ui-teal: #0F766E;
    --ui-green: #16A34A;
    --ui-purple: #7C3AED;
    --ui-orange: #F59E0B;
    --ui-red: #DC2626;
    --ui-bg: #F4F7FB;
    --ui-card: #FFFFFF;
    --ui-border: #E2E8F0;
    --ui-text: #172033;
    --ui-muted: #64748B;
}

/* ---------------------------------------------------------
   MAIN APPLICATION
   --------------------------------------------------------- */

.stApp {
    background: var(--ui-bg);
    color: var(--ui-text);
}

/* Main content width */

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

/* ---------------------------------------------------------
   HEADINGS
   --------------------------------------------------------- */

h1 {
    color: var(--ui-navy) !important;
    font-weight: 750 !important;
    letter-spacing: -0.5px;
}

h2 {
    color: var(--ui-navy) !important;
    font-weight: 700 !important;
}

h3 {
    color: #1E3A5F !important;
    font-weight: 650 !important;
}

/* ---------------------------------------------------------
   SIDEBAR
   --------------------------------------------------------- */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #102A43 0%,
        #12355B 48%,
        #164E63 100%
    );
}

section[data-testid="stSidebar"] * {
    color: #F8FAFC;
}

/* Sidebar radio */

section[data-testid="stSidebar"]
div[role="radiogroup"] {
    gap: 5px;
}

/* Navigation options */

section[data-testid="stSidebar"]
div[role="radiogroup"] label {
    border-radius: 10px;
    padding: 8px 10px;
    transition: all 0.18s ease;
}

/* Navigation hover */

section[data-testid="stSidebar"]
div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.10);
}

/* Selected navigation */

section[data-testid="stSidebar"]
div[role="radiogroup"]
label[data-checked="true"] {
    background: rgba(37,99,235,0.55);
    border-left: 4px solid #67E8F9;
}

/* Sidebar divider */

section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.16);
}

/* ---------------------------------------------------------
   METRIC CARDS
   --------------------------------------------------------- */

div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #D9E2EC;
    border-radius: 14px;
    padding: 16px 18px;
    min-height: 105px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    position: relative;
    overflow: hidden;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.10);
}


div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 7px 18px rgba(15, 23, 42, 0.10);
}

div[data-testid="stMetricLabel"] {
    color: #334155 !important;
    opacity: 1 !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
}

div[data-testid="stMetricLabel"] * {
    color: #334155 !important;
    opacity: 1 !important;
}

div[data-testid="stMetricValue"] {
    color: #12355B !important;
    opacity: 1 !important;
    font-weight: 750 !important;
}

div[data-testid="stMetricValue"] * {
    color: #12355B !important;
    opacity: 1 !important;
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p {
    color: #F8FAFC !important;
}

section[data-testid="stSidebar"] label {
    color: #F8FAFC !important;
}

/* ---------------------------------------------------------
   CONTAINERS / CARDS
   --------------------------------------------------------- */

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px;
}

/* ---------------------------------------------------------
   BUTTONS
   --------------------------------------------------------- */

.stButton > button {
    border-radius: 9px;
    border: 1px solid #CBD5E1;
    font-weight: 600;
    transition: all 0.18s ease;
}

.stButton > button:hover {
    border-color: var(--ui-blue);
    color: var(--ui-blue);
    transform: translateY(-1px);
}

/* ---------------------------------------------------------
   DOWNLOAD BUTTONS
   --------------------------------------------------------- */

.stDownloadButton > button {
    border-radius: 9px;
    font-weight: 600;
}

/* ---------------------------------------------------------
   DATAFRAMES
   --------------------------------------------------------- */

div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--ui-border);
}

/* ---------------------------------------------------------
   INPUTS
   --------------------------------------------------------- */

.stTextInput input,
.stNumberInput input,
.stSelectbox,
.stMultiSelect {
    border-radius: 9px;
}

/* ---------------------------------------------------------
   ALERT / STATUS COLORS
   --------------------------------------------------------- */

div[data-testid="stAlert"] {
    border-radius: 11px;
}

/* ---------------------------------------------------------
   EXPANDERS
   --------------------------------------------------------- */

details {
    border-radius: 11px !important;
    border: 1px solid var(--ui-border) !important;
}

/* ---------------------------------------------------------
   LINKS
   --------------------------------------------------------- */

a {
    color: var(--ui-blue);
}

/* ---------------------------------------------------------
   SMALL SCREEN POLISH
   --------------------------------------------------------- */

@media (max-width: 900px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

}

</style>
""", unsafe_allow_html=True)

DATA_DIR = Path("data")

# -----------------------------
# Helpers
# -----------------------------
def clean_name(x):
    return str(x).strip().lower().replace("\n", " ").replace("_", " ")

def find_file(patterns):
    for p in patterns:
        matches = glob.glob(str(DATA_DIR / p))
        if matches:
            return matches[0]
    return None

def read_sheet(path, sheet, header=None):
    try:
        df = pd.read_excel(
            path,
            sheet_name=sheet,
            header=header
        )

        # Remove completely empty columns
        df = df.dropna(axis=1, how="all")

        # Remove Excel-generated empty columns
        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed")
        ]

        # Remove completely empty rows
        df = df.dropna(how="all")

        # Clean mixed object columns
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].apply(
                    lambda x: str(x).strip()
                    if pd.notna(x)
                    else None
                )

        return df

    except Exception as e:
        print(f"Could not read sheet {sheet}: {e}")
        return pd.DataFrame()

def numeric(v):
    try:
        return float(v)
    except Exception:
        return np.nan

def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def discover_files():
    return sorted(glob.glob(str(DATA_DIR / "*.xlsx")) + glob.glob(str(DATA_DIR / "*.csv")))

# -----------------------------
# Load real project data
# -----------------------------
@st.cache_data(show_spinner=False)
def load_project_data():
    result = {
        "energy": pd.DataFrame(),
        "transformers": pd.DataFrame(),
        "solar": pd.DataFrame(),
        "air": pd.DataFrame(),
        "environment": pd.DataFrame(),
        "pf": pd.DataFrame(),
        "sources": [],
    }

    files = discover_files()

    # ---------- Tata Power daily ----------
    tata = find_file(["Daily_Tata_Power_Systems_LTD_17-Aug-26.xlsx"])
    if tata:
        try:
            df = read_sheet(tata, "Formulas_Overview", header=None)
            rows = []
            for i in range(4, len(df)):
                loc = df.iloc[i, 1] if df.shape[1] > 1 else None
                daily = numeric(df.iloc[i, 3]) if df.shape[1] > 3 else np.nan
                mtd = numeric(df.iloc[i, 4]) if df.shape[1] > 4 else np.nan
                if pd.notna(loc) and pd.notna(daily):
                    rows.append({"location": str(loc).strip(), "daily_kwh": daily, "mtd_kwh": mtd})
            result["energy"] = pd.DataFrame(rows)

            # Progressive daily history
            prog = read_sheet(tata, "Formulas_Progressive Report", header=None)
            if not prog.empty and prog.shape[1] > 3:
                headers = list(prog.iloc[3])
                loc_col = 2
                date_cols = []
                for j in range(3, prog.shape[1]):
                    if pd.notna(prog.iloc[3, j]):
                        try:
                            d = pd.to_datetime(prog.iloc[3, j])
                            date_cols.append((j, d))
                        except Exception:
                            pass
                hist = []
                for i in range(4, len(prog)):
                    loc = prog.iloc[i, loc_col]
                    if pd.isna(loc):
                        continue
                    for j, d in date_cols:
                        v = numeric(prog.iloc[i, j])
                        if pd.notna(v):
                            hist.append({"date": d, "location": str(loc).strip(), "kwh": v})
                if hist:
                    result["energy_history"] = pd.DataFrame(hist)
                else:
                    result["energy_history"] = pd.DataFrame()
            else:
                result["energy_history"] = pd.DataFrame()

            result["sources"].append(("Tata Power Daily", tata))
        except Exception:
            result["energy_history"] = pd.DataFrame()
    else:
        result["energy_history"] = pd.DataFrame()

    # ---------- Hexa / Vega ----------
    hv = find_file(["Daily_Hexa_and_Vega_power_consumption_17-Aug-26.xlsx"])
    if hv:
        try:
            df = read_sheet(hv, "Daily Sheet", header=None)
            rows = []
            if not df.empty:
                # Row 1 contains date headers; row 2 onward contains locations.
                for i in range(2, len(df)):
                    loc = df.iloc[i, 0]
                    if pd.isna(loc):
                        continue
                    # Latest available daily column is normally the last date column.
                    vals = []
                    for j in range(3, df.shape[1]):
                        v = numeric(df.iloc[i, j])
                        if pd.notna(v):
                            vals.append(v)
                    if vals:
                        rows.append({"location": str(loc).strip(), "daily_kwh": vals[-1], "mtd_kwh": np.nan})
            hv_df = pd.DataFrame(rows)
            if not hv_df.empty:
                # Prefer the dedicated main-sheet daily/MTD values for headline figures.
                main = read_sheet(hv, "Main Sheet", header=None)
                main_rows = []
                for i in range(4, len(main)):
                    loc = main.iloc[i, 1] if main.shape[1] > 1 else None
                    daily = numeric(main.iloc[i, 4]) if main.shape[1] > 4 else np.nan
                    mtd = numeric(main.iloc[i, 5]) if main.shape[1] > 5 else np.nan
                    if pd.notna(loc) and pd.notna(daily):
                        main_rows.append({"location": str(loc).strip(), "daily_kwh": daily, "mtd_kwh": mtd})
                if main_rows:
                    hv_df = pd.DataFrame(main_rows)

            # Transformer records from Main Sheet
            if not main.empty:
                trs = []
                for i in range(4, len(main)):
                    loc = str(main.iloc[i, 1]).strip() if main.shape[1] > 1 and pd.notna(main.iloc[i,1]) else ""
                    if "transformer" in loc.lower():
                        daily = numeric(main.iloc[i, 4])
                        mtd = numeric(main.iloc[i, 5])
                        sensor = main.iloc[i, 3] if main.shape[1] > 3 else None
                        if pd.notna(daily):
                            trs.append({"transformer": loc, "sensor_id": sensor, "daily_kwh": daily, "mtd_kwh": mtd})
                result["transformers"] = pd.DataFrame(trs)

            # Add Hexa/Vega into energy table.
            if not hv_df.empty:
                result["energy"] = pd.concat([result["energy"], hv_df], ignore_index=True).drop_duplicates(
                    subset=["location"], keep="last"
                )
            result["sources"].append(("Hexa & Vega", hv))
        except Exception:
            pass

    # ---------- Solar ----------
    solar = find_file([
        "Solar_Generation_-_U2_17-Aug-26.xlsx",
        "Solar_Generation_-_U2_17-Aug-26 (1).xlsx",
    ])
    if solar:
        try:
            df = read_sheet(solar, "Solar daily sheet", header=None)
            rows = []
            for i in range(4, len(df)):
                loc = df.iloc[i, 1] if df.shape[1] > 1 else None
                daily = numeric(df.iloc[i, 3]) if df.shape[1] > 3 else np.nan
                mtd = numeric(df.iloc[i, 4]) if df.shape[1] > 4 else np.nan
                if pd.notna(loc) and pd.notna(daily):
                    rows.append({"source": str(loc).strip(), "daily_kwh": daily, "mtd_kwh": mtd})
            result["solar"] = pd.DataFrame(rows)
            result["sources"].append(("Solar Generation", solar))
        except Exception:
            pass

    # ---------- Air / utilities ----------
    air = find_file(["Tata_Power_Air_Report_-_U2_17-Aug-26.xlsx"])
    if air:
        try:
            df = read_sheet(air, "Summary Report", header=None)
            rows = []
            for i in range(4, len(df)):
                loc = df.iloc[i, 2] if df.shape[1] > 2 else None
                avg_flow = numeric(df.iloc[i, 3]) if df.shape[1] > 3 else np.nan
                total = numeric(df.iloc[i, 4]) if df.shape[1] > 4 else np.nan
                if pd.notna(loc):
                    rows.append({"utility": str(loc).strip(), "avg_flow_m3_hr": avg_flow, "total_m3": total})
            result["air"] = pd.DataFrame(rows)
            result["sources"].append(("Air / Utilities", air))
        except Exception:
            pass

    # ---------- Environment ----------
    env = find_file(["Tata_Power_Solar_Systems_Ltd_Humidity___Temperature_-_U2_17-Aug-26.xlsx"])
    if env:
        try:
            hum = read_sheet(env, "Humidity", header=None)
            temp = read_sheet(env, "Temperature", header=None)

            # Columns begin at row 2; timestamp at column 1.
            env_rows = []
            if not hum.empty:
                locations = list(hum.iloc[2])
                for j in range(2, hum.shape[1]):
                    loc = hum.iloc[2, j] if j < len(locations) else None
                    if pd.isna(loc) or str(loc).strip() == "nan":
                        continue
                    vals = pd.to_numeric(hum.iloc[3:, j], errors="coerce").dropna()
                    tvals = pd.to_numeric(temp.iloc[3:, j], errors="coerce").dropna() if not temp.empty and j < temp.shape[1] else pd.Series(dtype=float)
                    if len(vals):
                        env_rows.append({
                            "location": str(loc).strip(),
                            "humidity_avg": float(vals.mean()),
                            "humidity_max": float(vals.max()),
                            "temperature_avg": float(tvals.mean()) if len(tvals) else np.nan,
                            "temperature_max": float(tvals.max()) if len(tvals) else np.nan,
                            "humidity_target": 60.0,
                            "temperature_target": 30.0,
                        })
            result["environment"] = pd.DataFrame(env_rows)
            result["sources"].append(("Humidity & Temperature", env))
        except Exception:
            pass

    # ---------- Unit 1 / 5 PF & Demand ----------
    unit = find_file(["Unit_-1_and_5_daily_Tata_Power_Systems_LTD_17-Aug-26.xlsx"])
    if unit:
        try:
            pf = read_sheet(unit, "PF & Demand", header=None)
            # Search all cells for the known PF / demand columns and collect numeric time-series rows.
            records = []
            for i in range(4, len(pf)):
                row = pf.iloc[i]
                for j, value in enumerate(row):
                    if isinstance(value, (int, float, np.number)) and pd.notna(value):
                        # Store raw numeric values for a simple technical view.
                        records.append({"row": i, "column": j, "value": float(value)})
            result["pf"] = pd.DataFrame(records)
            result["sources"].append(("Unit 1 & Unit 5", unit))
        except Exception:
            pass

    return result
def load_uploaded_master_data():
    """
    Load the most recently uploaded Excel workbook and map
    its worksheets into the application's existing data model.
    """

    result = {
        "energy": pd.DataFrame(),
        "transformers": pd.DataFrame(),
        "solar": pd.DataFrame(),
        "air": pd.DataFrame(),
        "environment": pd.DataFrame(),
        "pf": pd.DataFrame(),
        "sources": [],
        "energy_history": pd.DataFrame(),
    }

    uploaded_files = get_uploaded_files()

    excel_files = [
        filename
        for filename in uploaded_files
        if str(filename).lower().endswith(
            (".xlsx", ".xls")
        )
    ]

    if not excel_files:
        return None

    active_workbook = st.session_state.get(
        "active_workbook"
    )

    if not active_workbook:
        active_file_path = DATA_DIR / "active_workbook.txt"

        if active_file_path.exists():
            active_workbook = (
                active_file_path
                .read_text()
                .strip()
            )

    if active_workbook in excel_files:
        filename = active_workbook
    else:
        filename = excel_files[-1]

    try:

        workbook = load_saved_workbook(
            filename
        )

    except Exception as e:

        st.error(
            f"MASTER WORKBOOK ERROR: "
            f"{type(e).__name__}: {e}"
        )

        return None

    if not workbook:
        return None
    # =========================================================
    # ELECTRICAL METERS → ENERGY
    # =========================================================

    electrical = workbook.get("Electrical_Meters")

    if (
        isinstance(electrical, pd.DataFrame)
        and not electrical.empty
    ):

        electrical = electrical.copy()

        if "date" in electrical.columns:
            electrical["date"] = pd.to_datetime(
                electrical["date"],
                errors="coerce"
            )

        if "kwh" in electrical.columns:
            electrical["kwh"] = pd.to_numeric(
                electrical["kwh"],
                errors="coerce"
            )

        if (
            "date" in electrical.columns
            and "location" in electrical.columns
            and "kwh" in electrical.columns
        ):

            valid = electrical.dropna(
                subset=[
                    "date",
                    "location",
                    "kwh"
                ]
            ).copy()

            if not valid.empty:

                latest_date = valid["date"].max()

                latest = valid[
                    valid["date"] == latest_date
                ].copy()

                energy_rows = (
                    latest[
                        [
                            "location",
                            "kwh"
                        ]
                    ]
                    .groupby(
                        "location",
                        as_index=False
                    )
                    .sum()
                )

                energy_rows = energy_rows.rename(
                    columns={
                        "kwh": "daily_kwh"
                    }
                )

                energy_rows["mtd_kwh"] = np.nan

                result["energy"] = energy_rows

                # -------------------------------------------------
                # DAILY ENERGY HISTORY
                # -------------------------------------------------

                history = (
                    valid[
                        [
                            "date",
                            "location",
                            "kwh"
                        ]
                    ]
                    .groupby(
                        [
                            "date",
                            "location"
                        ],
                        as_index=False
                    )
                    .sum()
                )

                history = history.rename(
                    columns={
                        "kwh": "kwh"
                    }
                )

                result["energy_history"] = history

    # =========================================================
    # SOLAR
    # =========================================================

    solar = workbook.get("Solar")

    if (
        isinstance(solar, pd.DataFrame)
        and not solar.empty
    ):

        solar = solar.copy()

        if "date" in solar.columns:
            solar["date"] = pd.to_datetime(
                solar["date"],
                errors="coerce"
            )

        if "daily_kwh" in solar.columns:
            solar["daily_kwh"] = pd.to_numeric(
                solar["daily_kwh"],
                errors="coerce"
            )

        required = [
            "date",
            "source",
            "daily_kwh"
        ]

        if all(
            column in solar.columns
            for column in required
        ):

            valid_solar = solar.dropna(
                subset=required
            ).copy()

            if not valid_solar.empty:

                latest_date = valid_solar["date"].max()

                latest_solar = valid_solar[
                    valid_solar["date"] == latest_date
                ].copy()

                solar_rows = (
                    latest_solar[
                        [
                            "source",
                            "daily_kwh"
                        ]
                    ]
                    .groupby(
                        "source",
                        as_index=False
                    )
                    .sum()
                )

                solar_rows["mtd_kwh"] = np.nan

                result["solar"] = solar_rows

    # =========================================================
    # TRANSFORMERS
    # =========================================================

    transformers = workbook.get("Transformers")

    if (
        isinstance(transformers, pd.DataFrame)
        and not transformers.empty
    ):

        transformers = transformers.copy()

        if "date" in transformers.columns:
            transformers["date"] = pd.to_datetime(
                transformers["date"],
                errors="coerce"
            )

        if "daily_kwh" in transformers.columns:
            transformers["daily_kwh"] = pd.to_numeric(
                transformers["daily_kwh"],
                errors="coerce"
            )

        if (
            "date" in transformers.columns
            and "transformer" in transformers.columns
            and "daily_kwh" in transformers.columns
        ):

            valid_tr = transformers.dropna(
                subset=[
                    "date",
                    "transformer",
                    "daily_kwh"
                ]
            ).copy()

            if not valid_tr.empty:

                latest_date = valid_tr["date"].max()

                latest_tr = valid_tr[
                    valid_tr["date"] == latest_date
                ].copy()

                tr_rows = latest_tr[
                    [
                        "transformer",
                        "sensor_id",
                        "daily_kwh"
                    ]
                ].copy()

                if "loading_percent" in latest_tr.columns:
                    tr_rows["loading_percent"] = (
                        pd.to_numeric(
                            latest_tr[
                                "loading_percent"
                            ],
                            errors="coerce"
                        )
                    )
                else:
                    tr_rows["loading_percent"] = np.nan

                if "health_indicator" in latest_tr.columns:
                    tr_rows["health_indicator"] = (
                        pd.to_numeric(
                            latest_tr[
                                "health_indicator"
                            ],
                            errors="coerce"
                        )
                    )
                else:
                    tr_rows["health_indicator"] = np.nan

                tr_rows["mtd_kwh"] = np.nan

                result["transformers"] = tr_rows

    # =========================================================
    # COMPRESSED AIR → UTILITIES
    # =========================================================

    air = workbook.get("Compressed_Air")

    if (
        isinstance(air, pd.DataFrame)
        and not air.empty
    ):

        air = air.copy()

        if "date" in air.columns:
            air["date"] = pd.to_datetime(
                air["date"],
                errors="coerce"
            )

        if "date" in air.columns:

            latest_date = air["date"].max()

            latest_air = air[
                air["date"] == latest_date
            ].copy()

            if not latest_air.empty:

                utility_rows = []

                for column in [
                    "pure_air_m3",
                    "fad___module_line_m3",
                    "fad___cell_line_m3",
                ]:

                    if column not in latest_air.columns:
                        continue

                    value = pd.to_numeric(
                        latest_air[column],
                        errors="coerce"
                    ).sum()

                    utility_rows.append(
                        {
                            "utility": column,
                            "avg_flow_m3_hr": np.nan,
                            "total_m3": value,
                        }
                    )

                result["air"] = pd.DataFrame(
                    utility_rows
                )

    # =========================================================
    # ENVIRONMENT
    # =========================================================

    environment = workbook.get("Environment")

    if (
        isinstance(environment, pd.DataFrame)
        and not environment.empty
    ):

        environment = environment.copy()

        if "timestamp" in environment.columns:
            environment["timestamp"] = pd.to_datetime(
                environment["timestamp"],
                errors="coerce"
            )

        if "humidity_percent" in environment.columns:
            environment["humidity_percent"] = pd.to_numeric(
                environment["humidity_percent"],
                errors="coerce"
            )

        if "temperature_c" in environment.columns:
            environment["temperature_c"] = pd.to_numeric(
                environment["temperature_c"],
                errors="coerce"
            )

        if "location" in environment.columns:

            grouped_rows = []

            for location, group in environment.groupby(
                "location"
            ):

                grouped_rows.append(
                    {
                        "location": str(location),

                        "humidity_avg": (
                            float(
                                group[
                                    "humidity_percent"
                                ].mean()
                            )
                            if "humidity_percent"
                            in group.columns
                            else np.nan
                        ),

                        "humidity_max": (
                            float(
                                group[
                                    "humidity_percent"
                                ].max()
                            )
                            if "humidity_percent"
                            in group.columns
                            else np.nan
                        ),

                        "temperature_avg": (
                            float(
                                group[
                                    "temperature_c"
                                ].mean()
                            )
                            if "temperature_c"
                            in group.columns
                            else np.nan
                        ),

                        "temperature_max": (
                            float(
                                group[
                                    "temperature_c"
                                ].max()
                            )
                            if "temperature_c"
                            in group.columns
                            else np.nan
                        ),

                        "humidity_target": 60.0,
                        "temperature_target": 30.0,
                    }
                )

            result["environment"] = pd.DataFrame(
                grouped_rows
            )

    # =========================================================
    # SOURCE INFORMATION
    # =========================================================

    result["sources"].append(
        (
            "Uploaded Master Workbook",
            filename
        )
    )

    return result

uploaded_master_data = load_uploaded_master_data()

if uploaded_master_data is not None:
    data = uploaded_master_data
else:
    data = load_project_data()

# -----------------------------
# Login System
# -----------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None


# Demo users
DEMO_USERS = {
    "admin@utility.com": {
        "password": "admin123",
        "role": "Admin"
    },

    "management@utility.com": {
        "password": "management123",
        "role": "Management"
    },
    "planthead@utility.com": {
        "password": "planthead123",
        "role": "Plant Head"
    },
    "engineer@utility.com": {
        "password": "engineer123",
        "role": "Engineer"
    }
}


# Login page
if not st.session_state.logged_in:

    st.markdown(
        """
        <style>

        .login-title {
            text-align: center;
            font-size: 42px;
            font-weight: 700;
            margin-top: 80px;
        }

        .login-subtitle {
            text-align: center;
            color: #888888;
            font-size: 18px;
            margin-bottom: 40px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-title">⚡ Utility Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-subtitle">'
        'Automated Utility Intelligence & Daily Report System'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        with st.form("login_form"):

            email = st.text_input(
                "Email",
                placeholder="Enter your email"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password"
            )

            login_button = st.form_submit_button(
                "🔐 Login",
                use_container_width=True
            )

            if login_button:

                if (
                    email in DEMO_USERS
                    and password == DEMO_USERS[email]["password"]
                ):

                    st.session_state.logged_in = True
                    st.session_state.user_role = DEMO_USERS[email]["role"]

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )

        st.info(
            """
            **Demo Login**

            **Management**
            `management@utility.com`
            Password: `management123`

            **Plant Head**
            `planthead@utility.com`
            Password: `planthead123`

            **Engineer**
            `engineer@utility.com`
            Password: `engineer123`
            """
        )

    st.stop()
    # ============================================================
# ADMIN CONFIGURATION
# ============================================================

if st.session_state.user_role == "Management":

    with st.sidebar.expander("⚙️ Admin", expanded=False):

        st.markdown("### Application Settings")

        app_config = get_app_config()

        ai_enabled = st.toggle(
            "Enable AI Agent",
            value=app_config.get("ai_enabled", True),
        )

        daily_reports_enabled = st.toggle(
            "Enable Daily Reports",
            value=app_config.get("daily_reports_enabled", True),
        )

        monthly_reports_enabled = st.toggle(
            "Enable Monthly Reports",
            value=app_config.get("monthly_reports_enabled", True),
        )

        data_upload_enabled = st.toggle(
            "Enable Data Upload",
            value=app_config.get("data_upload_enabled", True),
        )

        user_registration_enabled = st.toggle(
            "Enable User Registration",
            value=app_config.get("user_registration_enabled", True),
        )

        alert_threshold = st.number_input(
            "Alert Threshold",
            min_value=0.0,
            max_value=100.0,
            value=float(app_config.get("alert_threshold", 80.0)),
            step=1.0,
        )

        if st.button(
            "💾 Save Configuration",
            use_container_width=True
        ):

            update_config(
                "ai_enabled",
                str(ai_enabled).lower()
            )

            update_config(
                "daily_reports_enabled",
                str(daily_reports_enabled).lower()
            )

            update_config(
                "monthly_reports_enabled",
                str(monthly_reports_enabled).lower()
            )

            update_config(
                "data_upload_enabled",
                str(data_upload_enabled).lower()
            )

            update_config(
                "user_registration_enabled",
                str(user_registration_enabled).lower()
            )

            update_config(
                "alert_threshold",
                str(alert_threshold)
            )

            st.success(
                "✅ Admin configuration saved successfully."
            )

            st.rerun()


# -----------------------------

# -----------------
# Sidebar
# -----------------------------
# -----------------------------
# ENTERPRISE SIDEBAR
# -----------------------------

st.sidebar.markdown(
    "## ⚡ Utility Intelligence"
)

st.sidebar.caption(
    "Enterprise Utility Operations Platform"
)

st.sidebar.markdown(
    """
    <div style="
        font-size: 10px;
        font-weight: 700;
        color: #94A3B8;
        letter-spacing: 1.2px;
        margin: 8px 0 5px 4px;
    ">
        APPLICATION NAVIGATION
    </div>
    """,
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Command Center",
        "Energy",
        "Solar",
        "Hexa & Vega",
        "Transformers",
        "Utilities",
        "Environment",
        "Electrical Quality",
        "Alerts & Anomalies",
        "Intelligent Insights",
        "Daily Report",
        "Management Reports",
        "Data Upload",
        "Data Sources",
        "AI Assistant",
    ],
    label_visibility="collapsed",
    key="main_navigation"
)

st.sidebar.markdown(
    """
    <div style="
        margin-top: 18px;
        padding: 10px 12px;
        border-radius: 10px;
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.10);
        font-size: 11px;
        color: #CBD5E1;
    ">
        <div style="
            color: #67E8F9;
            font-weight: 700;
            margin-bottom: 3px;
        ">
            ● SYSTEM ONLINE
        </div>

        Data → AI → Insights → Reports
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()
# -----------------------------
# Reporting Period
# -----------------------------

import datetime as dt

st.sidebar.subheader("📅 Reporting Period")

period_option = st.sidebar.selectbox(
    "Quick Select",
    [
        "Today",
        "Last 7 Days",
        "Month to Date",
        "Custom"
    ]
)

# Your current dataset ends on Aug 18, 2026
data_end_date = dt.date(2026, 8, 18)

if period_option == "Today":

    start_date = data_end_date
    end_date = data_end_date

elif period_option == "Last 7 Days":

    start_date = data_end_date - dt.timedelta(days=6)
    end_date = data_end_date

elif period_option == "Month to Date":

    start_date = data_end_date.replace(day=1)
    end_date = data_end_date

else:

    start_date = st.sidebar.date_input(
        "Start Date",
        value=dt.date(2026, 8, 1)
    )

    end_date = st.sidebar.date_input(
        "End Date",
        value=data_end_date
    )

if start_date > end_date:
    st.sidebar.error("Start date cannot be after end date.")
else:
    st.sidebar.success(
        f"{start_date.strftime('%d %b %Y')} → "
        f"{end_date.strftime('%d %b %Y')}"
    )
st.sidebar.caption("Real Excel project data is used as the initial dataset.")

# -----------------------------
# Common calculations
# -----------------------------
energy = data["energy"].copy()
solar_df = data["solar"].copy()
tr_df = data["transformers"].copy()
air_df = data["air"].copy()
env_df = data["environment"].copy()

def find_energy_value(keyword):
    if energy.empty:
        return np.nan

    if "location" not in energy.columns:
        return np.nan

    if "daily_kwh" not in energy.columns:
        return np.nan

    m = energy[
        energy["location"]
        .astype(str)
        .str.lower()
        .str.contains(
            keyword.lower(),
            na=False
        )
    ]

    return (
        float(m["daily_kwh"].sum())
        if not m.empty
        else np.nan
    )
grid = find_energy_value("66kv")
hexa = find_energy_value("hexa")
vega = find_energy_value("vega")
transformer_total = float(tr_df["daily_kwh"].sum()) if not tr_df.empty else np.nan
solar_total = float(solar_df["daily_kwh"].sum()) if not solar_df.empty else np.nan
air_total = float(air_df["total_m3"].sum()) if not air_df.empty else np.nan

# Fixed thresholds based on project specification
HUMIDITY_TARGET = 60.0
TEMP_TARGET = 30.0
PF_TARGET = 0.90

def make_alerts():
    alerts = []

    if not env_df.empty:
        for _, r in env_df.iterrows():
            if pd.notna(r.get("humidity_avg")) and r["humidity_avg"] > HUMIDITY_TARGET:
                diff = r["humidity_avg"] - HUMIDITY_TARGET
                sev = "High" if diff >= 10 else "Medium"
                alerts.append({
                    "severity": sev,
                    "type": "Environment",
                    "title": "Humidity Above Target",
                    "location": r["location"],
                    "actual": round(r["humidity_avg"], 2),
                    "target": HUMIDITY_TARGET,
                    "description": f"{r['location']} humidity is {r['humidity_avg']:.2f}% vs {HUMIDITY_TARGET:.0f}% target."
                })
            if pd.notna(r.get("temperature_avg")) and r["temperature_avg"] > TEMP_TARGET:
                alerts.append({
                    "severity": "Medium",
                    "type": "Environment",
                    "title": "Temperature Above Target",
                    "location": r["location"],
                    "actual": round(r["temperature_avg"], 2),
                    "target": TEMP_TARGET,
                    "description": f"{r['location']} temperature is {r['temperature_avg']:.2f}°C vs {TEMP_TARGET:.0f}°C target."
                })

    if not tr_df.empty:
        for _, r in tr_df.iterrows():
            if pd.notna(r["daily_kwh"]):
                # Flag unusually high transformer consumers for attention.
                if r["daily_kwh"] >= tr_df["daily_kwh"].quantile(0.75):
                    alerts.append({
                        "severity": "Medium",
                        "type": "Energy",
                        "title": "High Transformer Consumption",
                        "location": r["transformer"],
                        "actual": round(r["daily_kwh"], 2),
                        "target": None,
                        "description": f"{r['transformer']} is among the highest transformer consumers."
                    })

    return pd.DataFrame(alerts)

alerts_df = make_alerts()

# -----------------------------
# Header
# -----------------------------
st.markdown(
    "## Automated Utility Intelligence"
)

st.caption(
    "Enterprise Utility Operations & Daily Reporting Platform"
)
st.caption("Ingest → Store → Analyze → Visualize → Alert → Report → Insights")

# -----------------------------
# Command Center
# -----------------------------
# -----------------------------
# Command Center
# -----------------------------
if page == "Command Center":

    st.markdown("## ⚡ Command Center")
    st.caption(
        "Real-time overview of utility operations, consumption, "
        "generation and system health."
    )

    # =========================================================
    # KPI CARDS
    # =========================================================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
    "⚡ Grid Energy",
    f"{grid:,.0f} kWh" if pd.notna(grid) else "N/A",
    border=True,
    delta_color="blue",
)

    c2.metric(
    "☀️ Solar Generation",
    f"{solar_total:,.0f} kWh"
    if pd.notna(solar_total)
    else "N/A",
    border=True,
    delta_color="green",
)

    c3.metric(
    "🔌 Transformer Consumption",
    f"{transformer_total:,.0f} kWh"
    if pd.notna(transformer_total)
    else "N/A",
    border=True,
    delta_color="violet",
)
    c4.metric(
        "Active Alerts",
        len(alerts_df),
        icon="⚠️",
        border=True,
    )

    # =========================================================
    # SECOND KPI ROW
    # =========================================================

    c5, c6, c7, c8 = st.columns(4)

    c5.metric(
        "Hexa Consumption",
        f"{hexa:,.0f} kWh" if pd.notna(hexa) else "N/A",
        icon="🏭",
        border=True,
    )

    c6.metric(
        "Vega Consumption",
        f"{vega:,.0f} kWh" if pd.notna(vega) else "N/A",
        icon="🏗️",
        border=True,
    )

    c7.metric(
        "Compressed Air",
        f"{air_total:,.0f} m³"
        if pd.notna(air_total)
        else "N/A",
        icon="💨",
        border=True,
    )

    c8.metric(
        "Data Sources",
        len(data["sources"]),
        icon="📁",
        border=True,
    )

    st.markdown("")

    # =========================================================
    # MAIN ANALYTICS AREA
    # =========================================================

    left, right = st.columns([1.6, 1])

    # ---------------------------------------------------------
    # ENERGY OVERVIEW
    # ---------------------------------------------------------

    with left:

        st.markdown("### 📈 Energy Overview")

        overview = pd.DataFrame({
            "Metric": [
                "Grid",
                "Solar",
                "Transformer",
                "Hexa",
                "Vega",
            ],
            "Daily Value": [
                grid,
                solar_total,
                transformer_total,
                hexa,
                vega,
            ],
        }).dropna()

        if not overview.empty:

            st.bar_chart(
                overview.set_index(
                    "Metric"
                )["Daily Value"],
                height=320,
            )

        else:

            st.info(
                "Energy overview is not available."
            )

    # ---------------------------------------------------------
    # TOP CONSUMERS
    # ---------------------------------------------------------

    with right:

        st.markdown("### 🏆 Top Consumers")

        if (
            not tr_df.empty
            and "daily_kwh" in tr_df.columns
        ):

            top = (
                tr_df
                .sort_values(
                    "daily_kwh",
                    ascending=False
                )
                .head(5)
                .copy()
            )

            st.dataframe(
                top,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No consumer data is available."
            )

    # =========================================================
    # OPERATIONAL STATUS
    # =========================================================

    st.markdown("### 🚦 Intelligent Operational Status")

    if alerts_df.empty:

        st.success(
            "✅ No major anomalies detected in the imported dataset."
        )

    else:

        for _, alert in alerts_df.head(8).iterrows():

            severity = str(
                alert.get("severity", "")
            ).strip().lower()

            if severity == "high":

                st.error(
                    f"🔴 **{alert.get('title', 'Alert')}** — "
                    f"{alert.get('description', '')}"
                )

            elif severity == "medium":

                st.warning(
                    f"🟠 **{alert.get('title', 'Alert')}** — "
                    f"{alert.get('description', '')}"
                )

            else:

                st.info(
                    f"🔵 **{alert.get('title', 'Alert')}** — "
                    f"{alert.get('description', '')}"
                )

    # =========================================================
    # MANAGEMENT SNAPSHOT
    # =========================================================

    st.markdown("### 📋 Management Snapshot")

    snapshot_left, snapshot_right = st.columns(2)

    with snapshot_left:

        st.markdown(
            "**Energy Position**"
        )

        if (
            pd.notna(grid)
            and pd.notna(solar_total)
            and grid > 0
        ):

            solar_share = (
                solar_total / grid
            ) * 100

            st.write(
                f"Solar contribution is approximately "
                f"**{solar_share:.1f}%** of the reported grid-energy figure."
            )

        else:

            st.write(
                "Solar contribution cannot be calculated "
                "from the current dataset."
            )

    with snapshot_right:

        st.markdown(
            "**System Health**"
        )

        if alerts_df.empty:

            st.write(
                "🟢 Operations currently show no major alerts."
            )

        else:

            high_alerts = int(
                (
                    alerts_df["severity"]
                    .astype(str)
                    .str.lower()
                    == "high"
                ).sum()
            )

            st.write(
                f"🔴 **{high_alerts} high-severity alert(s)** "
                f"require attention."
            )

# -----------------------------
# Energy
# -----------------------------
elif page == "Energy":
    st.subheader("Energy Monitoring")
    st.write("Real energy values parsed from the Tata Power and Hexa/Vega workbooks.")

    if energy.empty:
        st.warning("No energy data found. Put the Excel files inside the data folder.")
    else:
        st.dataframe(energy, use_container_width=True, hide_index=True)

        chart = energy[["location", "daily_kwh"]].dropna().sort_values("daily_kwh", ascending=False).head(15)
        st.markdown("### Daily Consumption by Source")
        st.bar_chart(chart.set_index("location"))

        if "energy_history" in data and not data["energy_history"].empty:
            st.markdown("### Historical Energy Trend")
            hist = data["energy_history"].copy()
            locations = st.multiselect(
                "Select sources",
                sorted(hist["location"].unique()),
                default=list(sorted(hist["location"].unique()))[:3]
            )
            if locations:
                h = hist[hist["location"].isin(locations)]
                pivot = h.pivot_table(index="date", columns="location", values="kwh", aggfunc="sum")
                st.line_chart(pivot)

# -----------------------------
# Solar
# -----------------------------
elif page == "Solar":
    st.subheader("Solar Generation")
    if solar_df.empty:
        st.warning("Solar workbook not found.")
    else:
        total_daily = solar_df["daily_kwh"].sum()
        total_mtd = solar_df["mtd_kwh"].sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("Daily Solar", f"{total_daily:,.2f} kWh")
        c2.metric("MTD Solar", f"{total_mtd:,.2f} kWh")
        c3.metric("Solar Sources", len(solar_df))

        st.bar_chart(solar_df.set_index("source")["daily_kwh"])
        st.dataframe(solar_df, use_container_width=True, hide_index=True)

# -----------------------------
# Hexa & Vega
# -----------------------------
elif page == "Hexa & Vega":
    st.subheader("Hexa & Vega Power Consumption")
    rows = energy[energy["location"].str.contains("Hexa|Vega", case=False, na=False)].copy()
    if rows.empty:
        st.warning("Hexa/Vega data not found.")
    else:
        st.bar_chart(rows.set_index("location")["daily_kwh"])
        st.dataframe(rows, use_container_width=True, hide_index=True)

# -----------------------------
# Transformers
# -----------------------------
elif page == "Transformers":
    st.subheader("Transformer Performance")
    if tr_df.empty:
        st.warning("Transformer data not found.")
    else:
        st.bar_chart(tr_df.set_index("transformer")["daily_kwh"])
        st.dataframe(tr_df.sort_values("daily_kwh", ascending=False), use_container_width=True, hide_index=True)

        top = tr_df.sort_values("daily_kwh", ascending=False).iloc[0]
        st.info(
            f"Top transformer consumer: {top['transformer']} — "
            f"{top['daily_kwh']:,.2f} kWh for the selected day."
        )

# -----------------------------
# Utilities
# -----------------------------
elif page == "Utilities":
    st.subheader("Utilities — Air / Water / Flow")
    if air_df.empty:
        st.warning("Air/utility data not found.")
    else:
        st.dataframe(air_df, use_container_width=True, hide_index=True)
        chart = air_df[["utility", "total_m3"]].dropna()
        if not chart.empty:
            st.bar_chart(chart.set_index("utility"))

# -----------------------------
# Environment
# -----------------------------
elif page == "Environment":
    st.subheader("Environment Monitoring")
    if env_df.empty:
        st.warning("Environment workbook not found.")
    else:
        display = env_df.copy()
        display["humidity_status"] = np.where(
            display["humidity_avg"] > HUMIDITY_TARGET, "Above Target", "Within Target"
        )
        display["temperature_status"] = np.where(
            display["temperature_avg"] > TEMP_TARGET, "Above Target", "Within Target"
        )
        st.dataframe(display, use_container_width=True, hide_index=True)

        st.markdown("### Humidity")
        hum = display[["location", "humidity_avg"]].dropna().sort_values("humidity_avg", ascending=False)
        st.bar_chart(hum.set_index("location"))

        st.markdown("### Temperature")
        tmp = display[["location", "temperature_avg"]].dropna()
        st.bar_chart(tmp.set_index("location"))

# -----------------------------
# Electrical Quality
# -----------------------------
elif page == "Electrical Quality":
    st.subheader("Electrical Quality — PF & Demand")
    st.info("The Unit 1 / Unit 5 workbook is connected. Raw PF/Demand numeric records are available below.")
    if data["pf"].empty:
        st.warning("PF & Demand data not found.")
    else:
        st.dataframe(data["pf"].head(1000), use_container_width=True, hide_index=True)

# -----------------------------
# Alerts
# -----------------------------
elif page == "Alerts & Anomalies":
    st.subheader("Exception & Anomaly Detection")
    if alerts_df.empty:
        st.success("No alerts.")
    else:
        counts = alerts_df["severity"].value_counts()
        a,b,c = st.columns(3)
        a.metric("High", int(counts.get("High", 0)))
        b.metric("Medium", int(counts.get("Medium", 0)))
        c.metric("Total", len(alerts_df))

        st.dataframe(alerts_df, use_container_width=True, hide_index=True)

# -----------------------------
# Insights
# -----------------------------
elif page == "Intelligent Insights":
    st.subheader("Intelligent Insights")
    st.caption("Rule-based insights generated from the imported project data.")

    if pd.notna(grid):
        st.write(f"• Grid energy is approximately **{grid:,.2f} kWh** for the selected daily dataset.")
    if pd.notna(solar_total):
        st.write(f"• Solar generation is approximately **{solar_total:,.2f} kWh**.")
    if not tr_df.empty:
        top = tr_df.sort_values("daily_kwh", ascending=False).iloc[0]
        st.write(f"• **{top['transformer']}** is the highest transformer consumer at **{top['daily_kwh']:,.2f} kWh**.")
    if not env_df.empty:
        high_h = env_df.sort_values("humidity_avg", ascending=False).iloc[0]
        st.write(f"• **{high_h['location']}** has the highest average humidity at **{high_h['humidity_avg']:.2f}%**, above the 60% target.")
    if pd.notna(air_total):
        st.write(f"• Compressed-air/utility totalizer data contains approximately **{air_total:,.2f} m³** in the daily summary.")

    st.markdown("### Recommended Actions")
    st.write("1. Investigate high-consumption transformers.")
    st.write("2. Review locations where humidity exceeds the configured target.")
    st.write("3. Review low power-factor intervals from the PF/Demand workbook.")
    st.write("4. Compare solar generation against plant consumption to identify additional savings opportunities.")

# -----------------------------
# Daily Report
# -----------------------------
elif page == "Daily Report":
    st.subheader("Automated Daily Report")

    report_date = st.date_input("Report date", value=datetime(2026, 8, 17).date())

    st.markdown("## Executive Summary")
    summary = pd.DataFrame({
        "Metric": [
            "Grid Energy",
            "Solar Generation",
            "Transformer Consumption",
            "Hexa Consumption",
            "Vega Consumption",
            "Compressed Air",
            "Active Alerts",
        ],
        "Value": [
            f"{grid:,.2f} kWh" if pd.notna(grid) else "N/A",
            f"{solar_total:,.2f} kWh" if pd.notna(solar_total) else "N/A",
            f"{transformer_total:,.2f} kWh" if pd.notna(transformer_total) else "N/A",
            f"{hexa:,.2f} kWh" if pd.notna(hexa) else "N/A",
            f"{vega:,.2f} kWh" if pd.notna(vega) else "N/A",
            f"{air_total:,.2f} m³" if pd.notna(air_total) else "N/A",
            str(len(alerts_df)),
        ],
    })
    st.table(summary)

    st.markdown("## Top Consumers")
    if not tr_df.empty:
        st.dataframe(tr_df.sort_values("daily_kwh", ascending=False).head(5), use_container_width=True, hide_index=True)

    st.markdown("## Alerts")
    if not alerts_df.empty:
        st.dataframe(alerts_df, use_container_width=True, hide_index=True)

    # CSV/Excel export
    report_csv = summary.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Summary CSV",
        report_csv,
        file_name=f"daily_report_{report_date}.csv",
        mime="text/csv",
    )

    if REPORTLAB_OK:
        if st.button("Generate PDF Report"):
            pdf_path = Path(f"daily_report_{report_date}.pdf")
            c = canvas.Canvas(str(pdf_path), pagesize=A4)
            width, height = A4
            y = height - 50
            c.setFont("Helvetica-Bold", 16)
            c.drawString(40, y, "Automated Utility Intelligence")
            y -= 25
            c.setFont("Helvetica", 10)
            c.drawString(40, y, f"Daily Report — {report_date}")
            y -= 35
            for _, row in summary.iterrows():
                c.drawString(50, y, f"{row['Metric']}: {row['Value']}")
                y -= 18
            c.save()
            st.success("PDF generated.")
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "Download PDF",
                    f.read(),
                    file_name=pdf_path.name,
                    mime="application/pdf",
                )
        else:
            st.warning("Install reportlab to enable PDF generation.")


# =========================================================
# DAILY & MONTHLY MANAGEMENT REPORT
# =========================================================

elif page == "Management Reports":

    st.subheader("📊 Daily & Monthly Management Reports")

    st.write(
        "Generate management reports directly from the "
        "uploaded utility data."
    )

    # -----------------------------------------------------
    # LOAD UPLOADED DATA
    # -----------------------------------------------------

    uploaded_files = get_uploaded_files()

    report_dataframes = []

    for filename in uploaded_files:

        try:

            uploaded_df = load_saved_data(filename)

            if (
                isinstance(uploaded_df, pd.DataFrame)
                and not uploaded_df.empty
            ):

                report_dataframes.append(
                    uploaded_df.copy()
                )

        except Exception as e:

            st.warning(
                f"Could not load {filename}: {e}"
            )

    # -----------------------------------------------------
    # CHECK DATA
    # -----------------------------------------------------

    if not report_dataframes:

        st.info(
            "No uploaded utility data is available. "
            "Please upload a CSV or Excel file from "
            "Data Upload."
        )

    else:

        report_df = pd.concat(
            report_dataframes,
            ignore_index=True,
            sort=False
        )

        # -------------------------------------------------
        # CHECK DATE COLUMN
        # -------------------------------------------------

        if "date" not in report_df.columns:

            st.error(
                "The uploaded data does not contain a "
                "'date' column."
            )

        else:

            report_df["date"] = pd.to_datetime(
                report_df["date"],
                errors="coerce"
            )

            report_df = report_df.dropna(
                subset=["date"]
            )

            # -------------------------------------------------
            # REPORT TYPE
            # -------------------------------------------------

            report_type = st.radio(
                "Report Type",
                [
                    "Daily Report",
                    "Monthly Report"
                ],
                horizontal=True,
                key="management_report_type"
            )

            # =================================================
            # DAILY REPORT
            # =================================================

            if report_type == "Daily Report":

                available_dates = sorted(
                    report_df["date"].dt.date.unique()
                )

                if not available_dates:

                    st.warning(
                        "No valid dates are available "
                        "in the uploaded data."
                    )

                else:

                    selected_date = st.selectbox(
                        "Select Report Date",
                        available_dates,
                        index=len(available_dates) - 1,
                        key="management_daily_date"
                    )

                    daily_df = report_df[
                        report_df["date"].dt.date
                        == selected_date
                    ].copy()

                    st.markdown(
                        f"### 📅 Daily Report — {selected_date}"
                    )

                    # -----------------------------------------
                    # NUMERIC COLUMNS
                    # -----------------------------------------

                    energy_total = 0
                    water_total = 0
                    solar_total = 0

                    if (
                        "energy_consumption_kwh"
                        in daily_df.columns
                    ):

                        energy_total = pd.to_numeric(
                            daily_df[
                                "energy_consumption_kwh"
                            ],
                            errors="coerce"
                        ).sum()

                    if (
                        "water_consumption_liters"
                        in daily_df.columns
                    ):

                        water_total = pd.to_numeric(
                            daily_df[
                                "water_consumption_liters"
                            ],
                            errors="coerce"
                        ).sum()

                    if (
                        "solar_generation_kwh"
                        in daily_df.columns
                    ):

                        solar_total = pd.to_numeric(
                            daily_df[
                                "solar_generation_kwh"
                            ],
                            errors="coerce"
                        ).sum()

                    # -----------------------------------------
                    # SUMMARY
                    # -----------------------------------------

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Energy Consumption",
                            f"{energy_total:,.0f} kWh"
                        )

                    with col2:

                        st.metric(
                            "Water Consumption",
                            f"{water_total:,.0f} L"
                        )

                    with col3:

                        st.metric(
                            "Solar Generation",
                            f"{solar_total:,.0f} kWh"
                        )

                    st.markdown("### 🏭 Unit-wise Consumption")

                    if (
                        "unit" in daily_df.columns
                        and
                        "energy_consumption_kwh"
                        in daily_df.columns
                    ):

                        unit_report = (
                            daily_df[
                                [
                                    "unit",
                                    "energy_consumption_kwh"
                                ]
                            ]
                            .copy()
                        )

                        unit_report[
                            "energy_consumption_kwh"
                        ] = pd.to_numeric(
                            unit_report[
                                "energy_consumption_kwh"
                            ],
                            errors="coerce"
                        )

                        unit_report = (
                            unit_report
                            .sort_values(
                                "energy_consumption_kwh",
                                ascending=False
                            )
                            .reset_index(drop=True)
                        )

                        st.dataframe(
                            unit_report,
                            use_container_width=True,
                            hide_index=True
                        )

                    # -----------------------------------------
                    # FULL DAILY DATA
                    # -----------------------------------------

                    with st.expander(
                        "View Daily Data"
                    ):

                        st.dataframe(
                            daily_df,
                            use_container_width=True,
                            hide_index=True
                        )

                                        # -----------------------------------------
                    # DOWNLOAD DAILY REPORTS
                    # -----------------------------------------

                    st.markdown("### 📥 Download Daily Report")

                    # -----------------------------------------
                    # DAILY CSV
                    # -----------------------------------------

                    daily_csv = daily_df.to_csv(
                        index=False
                    ).encode("utf-8")

                    st.download_button(
                        "⬇️ Download Daily Report CSV",
                        daily_csv,
                        file_name=(
                            f"daily_report_"
                            f"{selected_date}.csv"
                        ),
                        mime="text/csv",
                        key="download_daily_management_report"
                    )

                    # -----------------------------------------
                    # DAILY EXCEL
                    # -----------------------------------------

                    daily_excel_buffer = io.BytesIO()

                    with pd.ExcelWriter(
                        daily_excel_buffer,
                        engine="openpyxl"
                    ) as writer:

                        daily_df.to_excel(
                            writer,
                            index=False,
                            sheet_name="Daily Data"
                        )

                        if (
                            "unit" in daily_df.columns
                            and
                            "energy_consumption_kwh"
                            in daily_df.columns
                        ):

                            unit_report.to_excel(
                                writer,
                                index=False,
                                sheet_name="Unit Summary"
                            )

                    daily_excel_buffer.seek(0)

                    st.download_button(
                        "📊 Download Daily Report Excel",
                        daily_excel_buffer.getvalue(),
                        file_name=(
                            f"daily_report_"
                            f"{selected_date}.xlsx"
                        ),
                        mime=(
                            "application/vnd.openxmlformats-"
                            "officedocument.spreadsheetml.sheet"
                        ),
                        key="download_daily_management_excel"
                    )

                    # -----------------------------------------
                    # DAILY PDF
                    # -----------------------------------------

                    if REPORTLAB_OK:

                        daily_pdf_buffer = io.BytesIO()

                        pdf = canvas.Canvas(
                            daily_pdf_buffer,
                            pagesize=A4
                        )

                        width, height = A4

                        y = height - 50

                        pdf.setFont(
                            "Helvetica-Bold",
                            18
                        )

                        pdf.drawString(
                            40,
                            y,
                            "Utility Intelligence"
                        )

                        y -= 28

                        pdf.setFont(
                            "Helvetica",
                            11
                        )

                        pdf.drawString(
                            40,
                            y,
                            f"Daily Management Report — "
                            f"{selected_date}"
                        )

                        y -= 40

                        pdf.setFont(
                            "Helvetica-Bold",
                            12
                        )

                        pdf.drawString(
                            40,
                            y,
                            "Summary"
                        )

                        y -= 25

                        pdf.setFont(
                            "Helvetica",
                            11
                        )

                        pdf.drawString(
                            50,
                            y,
                            f"Energy Consumption: "
                            f"{energy_total:,.0f} kWh"
                        )

                        y -= 20

                        pdf.drawString(
                            50,
                            y,
                            f"Water Consumption: "
                            f"{water_total:,.0f} L"
                        )

                        y -= 20

                        pdf.drawString(
                            50,
                            y,
                            f"Solar Generation: "
                            f"{solar_total:,.0f} kWh"
                        )

                        y -= 35

                        pdf.setFont(
                            "Helvetica-Bold",
                            12
                        )

                        pdf.drawString(
                            40,
                            y,
                            "Unit-wise Energy Consumption"
                        )

                        y -= 25

                        pdf.setFont(
                            "Helvetica",
                            10
                        )

                        if (
                            "unit" in daily_df.columns
                            and
                            "energy_consumption_kwh"
                            in daily_df.columns
                        ):

                            for _, row in unit_report.iterrows():

                                unit = row["unit"]

                                energy = row[
                                    "energy_consumption_kwh"
                                ]

                                pdf.drawString(
                                    50,
                                    y,
                                    f"{unit}: "
                                    f"{energy:,.0f} kWh"
                                )

                                y -= 18

                                if y < 60:

                                    pdf.showPage()

                                    y = height - 50

                                    pdf.setFont(
                                        "Helvetica",
                                        10
                                    )

                        pdf.save()

                        daily_pdf_buffer.seek(0)

                        st.download_button(
                            "📄 Download Daily Report PDF",
                            daily_pdf_buffer.getvalue(),
                            file_name=(
                                f"daily_report_"
                                f"{selected_date}.pdf"
                            ),
                            mime="application/pdf",
                            key="download_daily_management_pdf"
                        )

                    else:

                        st.warning(
                            "PDF download is unavailable "
                            "because ReportLab is not installed."
                        )
            # =================================================
            # MONTHLY REPORT
            # =================================================

            else:

                report_df["month"] = (
                    report_df["date"]
                    .dt.to_period("M")
                    .astype(str)
                )

                available_months = sorted(
                    report_df["month"].unique()
                )

                if not available_months:

                    st.warning(
                        "No valid months are available."
                    )

                else:

                    selected_month = st.selectbox(
                        "Select Report Month",
                        available_months,
                        index=len(available_months) - 1,
                        key="management_month"
                    )

                    monthly_df = report_df[
                        report_df["month"]
                        == selected_month
                    ].copy()

                    st.markdown(
                        f"### 📆 Monthly Report — "
                        f"{selected_month}"
                    )

                    # -----------------------------------------
                    # MONTHLY TOTALS
                    # -----------------------------------------

                    monthly_energy = 0
                    monthly_water = 0
                    monthly_solar = 0

                    if (
                        "energy_consumption_kwh"
                        in monthly_df.columns
                    ):

                        monthly_energy = pd.to_numeric(
                            monthly_df[
                                "energy_consumption_kwh"
                            ],
                            errors="coerce"
                        ).sum()

                    if (
                        "water_consumption_liters"
                        in monthly_df.columns
                    ):

                        monthly_water = pd.to_numeric(
                            monthly_df[
                                "water_consumption_liters"
                            ],
                            errors="coerce"
                        ).sum()

                    if (
                        "solar_generation_kwh"
                        in monthly_df.columns
                    ):

                        monthly_solar = pd.to_numeric(
                            monthly_df[
                                "solar_generation_kwh"
                            ],
                            errors="coerce"
                        ).sum()

                    # -----------------------------------------
                    # SUMMARY METRICS
                    # -----------------------------------------

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Monthly Energy",
                            f"{monthly_energy:,.0f} kWh"
                        )

                    with col2:

                        st.metric(
                            "Monthly Water",
                            f"{monthly_water:,.0f} L"
                        )

                    with col3:

                        st.metric(
                            "Monthly Solar",
                            f"{monthly_solar:,.0f} kWh"
                        )

                    # -----------------------------------------
                    # UNIT RANKING
                    # -----------------------------------------

                    st.markdown(
                        "### 🏆 Top Energy Consumers"
                    )

                    if (
                        "unit" in monthly_df.columns
                        and
                        "energy_consumption_kwh"
                        in monthly_df.columns
                    ):

                        monthly_unit_report = (
                            monthly_df[
                                [
                                    "unit",
                                    "energy_consumption_kwh"
                                ]
                            ]
                            .copy()
                        )

                        monthly_unit_report[
                            "energy_consumption_kwh"
                        ] = pd.to_numeric(
                            monthly_unit_report[
                                "energy_consumption_kwh"
                            ],
                            errors="coerce"
                        )

                        monthly_unit_report = (
                            monthly_unit_report
                            .groupby(
                                "unit",
                                as_index=False
                            )[
                                "energy_consumption_kwh"
                            ]
                            .sum()
                            .sort_values(
                                "energy_consumption_kwh",
                                ascending=False
                            )
                            .reset_index(drop=True)
                        )

                        st.dataframe(
                            monthly_unit_report,
                            use_container_width=True,
                            hide_index=True
                        )

                    # -----------------------------------------
                    # DAILY TREND
                    # -----------------------------------------

                    st.markdown(
                        "### 📈 Daily Energy Trend"
                    )

                    if (
                        "energy_consumption_kwh"
                        in monthly_df.columns
                    ):

                        monthly_daily = (
                            monthly_df
                            .groupby(
                                monthly_df[
                                    "date"
                                ].dt.date
                            )[
                                "energy_consumption_kwh"
                            ]
                            .sum()
                            .reset_index()
                        )

                        monthly_daily.columns = [
                            "date",
                            "energy_consumption_kwh"
                        ]

                        st.line_chart(
                            monthly_daily.set_index(
                                "date"
                            )
                        )

                    # -----------------------------------------
                    # FULL MONTHLY DATA
                    # -----------------------------------------

                    with st.expander(
                        "View Monthly Data"
                    ):

                        st.dataframe(
                            monthly_df.drop(
                                columns=["month"],
                                errors="ignore"
                            ),
                            use_container_width=True,
                            hide_index=True
                        )

                                       # -----------------------------------------
                    # DOWNLOAD MONTHLY REPORTS
                    # -----------------------------------------

                    st.markdown("### 📥 Download Monthly Report")

                    # Remove helper column before exporting
                    monthly_export_df = (
                        monthly_df
                        .drop(
                            columns=["month"],
                            errors="ignore"
                        )
                        .copy()
                    )

                    # -----------------------------------------
                    # MONTHLY CSV
                    # -----------------------------------------

                    monthly_csv = (
                        monthly_export_df
                        .to_csv(index=False)
                        .encode("utf-8")
                    )

                    st.download_button(
                        "⬇️ Download Monthly Report CSV",
                        monthly_csv,
                        file_name=(
                            f"monthly_report_"
                            f"{selected_month}.csv"
                        ),
                        mime="text/csv",
                        key="download_monthly_management_report"
                    )

                    # -----------------------------------------
                    # MONTHLY EXCEL
                    # -----------------------------------------

                    monthly_excel_buffer = io.BytesIO()

                    with pd.ExcelWriter(
                        monthly_excel_buffer,
                        engine="openpyxl"
                    ) as writer:

                        monthly_export_df.to_excel(
                            writer,
                            index=False,
                            sheet_name="Monthly Data"
                        )

                        if (
                            "unit" in monthly_unit_report.columns
                            and
                            "energy_consumption_kwh"
                            in monthly_unit_report.columns
                        ):

                            monthly_unit_report.to_excel(
                                writer,
                                index=False,
                                sheet_name="Unit Summary"
                            )

                        monthly_daily.to_excel(
                            writer,
                            index=False,
                            sheet_name="Daily Trend"
                        )

                    monthly_excel_buffer.seek(0)

                    st.download_button(
                        "📊 Download Monthly Report Excel",
                        monthly_excel_buffer.getvalue(),
                        file_name=(
                            f"monthly_report_"
                            f"{selected_month}.xlsx"
                        ),
                        mime=(
                            "application/vnd.openxmlformats-"
                            "officedocument.spreadsheetml.sheet"
                        ),
                        key="download_monthly_management_excel"
                    )

                    # -----------------------------------------
                    # MONTHLY PDF
                    # -----------------------------------------

                    if REPORTLAB_OK:

                        monthly_pdf_buffer = io.BytesIO()

                        pdf = canvas.Canvas(
                            monthly_pdf_buffer,
                            pagesize=A4
                        )

                        width, height = A4

                        y = height - 50

                        pdf.setFont(
                            "Helvetica-Bold",
                            18
                        )

                        pdf.drawString(
                            40,
                            y,
                            "Utility Intelligence"
                        )

                        y -= 28

                        pdf.setFont(
                            "Helvetica",
                            11
                        )

                        pdf.drawString(
                            40,
                            y,
                            f"Monthly Management Report — "
                            f"{selected_month}"
                        )

                        y -= 40

                        pdf.setFont(
                            "Helvetica-Bold",
                            12
                        )

                        pdf.drawString(
                            40,
                            y,
                            "Monthly Summary"
                        )

                        y -= 25

                        pdf.setFont(
                            "Helvetica",
                            11
                        )

                        pdf.drawString(
                            50,
                            y,
                            f"Energy Consumption: "
                            f"{monthly_energy:,.0f} kWh"
                        )

                        y -= 20

                        pdf.drawString(
                            50,
                            y,
                            f"Water Consumption: "
                            f"{monthly_water:,.0f} L"
                        )

                        y -= 20

                        pdf.drawString(
                            50,
                            y,
                            f"Solar Generation: "
                            f"{monthly_solar:,.0f} kWh"
                        )

                        y -= 35

                        pdf.setFont(
                            "Helvetica-Bold",
                            12
                        )

                        pdf.drawString(
                            40,
                            y,
                            "Top Energy Consumers"
                        )

                        y -= 25

                        pdf.setFont(
                            "Helvetica",
                            10
                        )

                        if (
                            "unit"
                            in monthly_unit_report.columns
                            and
                            "energy_consumption_kwh"
                            in monthly_unit_report.columns
                        ):

                            for _, row in (
                                monthly_unit_report.iterrows()
                            ):

                                unit = row["unit"]

                                energy = row[
                                    "energy_consumption_kwh"
                                ]

                                pdf.drawString(
                                    50,
                                    y,
                                    f"{unit}: "
                                    f"{energy:,.0f} kWh"
                                )

                                y -= 18

                                if y < 60:

                                    pdf.showPage()

                                    y = height - 50

                                    pdf.setFont(
                                        "Helvetica",
                                        10
                                    )

                        y -= 20

                        pdf.setFont(
                            "Helvetica-Bold",
                            12
                        )

                        pdf.drawString(
                            40,
                            y,
                            "Daily Energy Trend"
                        )

                        y -= 25

                        pdf.setFont(
                            "Helvetica",
                            10
                        )

                        for _, row in monthly_daily.iterrows():

                            date_value = row["date"]

                            energy_value = row[
                                "energy_consumption_kwh"
                            ]

                            pdf.drawString(
                                50,
                                y,
                                f"{date_value}: "
                                f"{energy_value:,.0f} kWh"
                            )

                            y -= 16

                            if y < 60:

                                pdf.showPage()

                                y = height - 50

                                pdf.setFont(
                                    "Helvetica",
                                    10
                                )

                        pdf.save()

                        monthly_pdf_buffer.seek(0)

                        st.download_button(
                            "📄 Download Monthly Report PDF",
                            monthly_pdf_buffer.getvalue(),
                            file_name=(
                                f"monthly_report_"
                                f"{selected_month}.pdf"
                            ),
                            mime="application/pdf",
                            key="download_monthly_management_pdf"
                        )

                    else:

                        st.warning(
                            "PDF download is unavailable "
                            "because ReportLab is not installed."
                        )

                    # =================================================
                    # MANAGEMENT INSIGHTS
                    # =================================================

                    st.markdown("## 🧠 Management Insights")

                    # -----------------------------------------
                    # HIGHEST CONSUMING UNIT
                    # -----------------------------------------

                    if (
                        "unit" in monthly_df.columns
                        and
                        "energy_consumption_kwh"
                        in monthly_df.columns
                    ):

                        insight_unit_df = (
                            monthly_df[
                                [
                                    "unit",
                                    "energy_consumption_kwh"
                                ]
                            ]
                            .copy()
                        )

                        insight_unit_df[
                            "energy_consumption_kwh"
                        ] = pd.to_numeric(
                            insight_unit_df[
                                "energy_consumption_kwh"
                            ],
                            errors="coerce"
                        )

                        insight_unit_df = (
                            insight_unit_df
                            .dropna(
                                subset=[
                                    "energy_consumption_kwh"
                                ]
                            )
                            .groupby(
                                "unit",
                                as_index=False
                            )[
                                "energy_consumption_kwh"
                            ]
                            .sum()
                            .sort_values(
                                "energy_consumption_kwh",
                                ascending=False
                            )
                        )

                        if not insight_unit_df.empty:

                            top_unit = insight_unit_df.iloc[0]

                            st.info(
                                f"🏆 **Highest Energy Consumer:** "
                                f"{top_unit['unit']} with "
                                f"{top_unit['energy_consumption_kwh']:,.0f} kWh."
                            )

                    # -----------------------------------------
                    # HIGHEST CONSUMPTION DAY
                    # -----------------------------------------

                    if (
                        "date" in monthly_df.columns
                        and
                        "energy_consumption_kwh"
                        in monthly_df.columns
                    ):

                        daily_insight = (
                            monthly_df
                            .groupby(
                                monthly_df["date"].dt.date
                            )[
                                "energy_consumption_kwh"
                            ]
                            .sum()
                            .sort_values(
                                ascending=False
                            )
                        )

                        if not daily_insight.empty:

                            highest_day = daily_insight.index[0]
                            highest_day_value = daily_insight.iloc[0]

                            st.info(
                                f"📈 **Highest Consumption Day:** "
                                f"{highest_day} with "
                                f"{highest_day_value:,.0f} kWh."
                            )

                    # -----------------------------------------
                    # SOLAR CONTRIBUTION
                    # -----------------------------------------

                    if monthly_energy > 0:

                        solar_percentage = (
                            monthly_solar
                            / monthly_energy
                        ) * 100

                        st.info(
                            f"☀️ **Solar Contribution:** "
                            f"{solar_percentage:.1f}% of total "
                            f"energy consumption."
                        )

                    # -----------------------------------------
                    # MANAGEMENT RECOMMENDATIONS
                    # -----------------------------------------

                    st.markdown(
                        "### 💡 Recommended Management Actions"
                    )

                    recommendations = []

                    if (
                        "unit" in monthly_df.columns
                        and
                        "energy_consumption_kwh"
                        in monthly_df.columns
                        and not insight_unit_df.empty
                    ):

                        recommendations.append(
                            f"Review energy usage at "
                            f"{top_unit['unit']}, the highest "
                            f"consuming unit."
                        )

                    if (
                        monthly_solar > 0
                        and monthly_energy > 0
                    ):

                        recommendations.append(
                            "Continue monitoring solar generation "
                            "against total plant consumption."
                        )

                    if (
                        "water_consumption_liters"
                        in monthly_df.columns
                        and monthly_water > 0
                    ):

                        recommendations.append(
                            "Monitor water consumption trends "
                            "for opportunities to reduce usage."
                        )

                    if not recommendations:

                        recommendations.append(
                            "Continue monitoring utility "
                            "consumption trends."
                        )

                    for recommendation in recommendations:

                        st.write(
                            f"• {recommendation}"
                        )


# -----------------------------
# Data Upload
# -----------------------------

elif page == "Data Upload":

    st.subheader("📁 Data Ingestion & Validation")

    st.write(
        "Upload one utility Excel workbook or a CSV file. "
        "Excel workbooks can contain multiple utility sheets."
    )

    uploaded = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        key="utility_data_uploader"
    )

    if uploaded:

        for file in uploaded:

            st.markdown(f"### 📄 {file.name}")

            try:

                # -------------------------------------------------
                # LOAD FILE
                # -------------------------------------------------

                if file.name.lower().endswith(
                    (".xlsx", ".xls")
                ):

                    workbook_sheets = load_excel_sheets(
                        file
                    )

                    st.success(
                        f"Excel workbook loaded successfully: "
                        f"{file.name}"
                    )

                    # -------------------------------------------------
                    # WORKBOOK SUMMARY
                    # -------------------------------------------------

                    st.markdown(
                        "### 📚 Workbook Sheets"
                    )

                    sheet_summary = []

                    for sheet_name, sheet_df in (
                        workbook_sheets.items()
                    ):

                        sheet_summary.append(
                            {
                                "Sheet": sheet_name,
                                "Rows": len(sheet_df),
                                "Columns": len(sheet_df.columns),
                            }
                        )

                    sheet_summary_df = pd.DataFrame(
                        sheet_summary
                    )

                    st.dataframe(
                        sheet_summary_df,
                        use_container_width=True,
                        hide_index=True
                    )

                    # -------------------------------------------------
                    # SHEET PREVIEW
                    # -------------------------------------------------

                    selected_sheet = st.selectbox(
                        "Preview Sheet",
                        list(workbook_sheets.keys()),
                        key=f"preview_sheet_{file.name}"
                    )

                    df = workbook_sheets[
                        selected_sheet
                    ].copy()

                    st.info(
                        f"Showing sheet: {selected_sheet}"
                    )

                else:

                    df = load_file(file)

                    st.success(
                        f"File loaded successfully: "
                        f"{file.name}"
                    )

                # -------------------------------------------------
                # CLEAN DATA
                # -------------------------------------------------

                cleaned_df = clean_data(
                    df
                )

                # -------------------------------------------------
                # SUMMARY
                # -------------------------------------------------

                summary = get_data_summary(
                    cleaned_df
                )

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Rows",
                    summary["rows"]
                )

                col2.metric(
                    "Columns",
                    summary["columns"]
                )

                col3.metric(
                    "Missing Values",
                    summary["missing_values"]
                )

                col4.metric(
                    "Duplicate Rows",
                    summary["duplicate_rows"]
                )

                # -------------------------------------------------
                # DATA PREVIEW
                # -------------------------------------------------

                st.markdown(
                    "### 🔍 Data Preview"
                )

                st.dataframe(
                    cleaned_df.head(20),
                    use_container_width=True,
                    hide_index=True
                )

                # -------------------------------------------------
                # VALIDATION
                # -------------------------------------------------

                errors, warnings = validate_data(
                    cleaned_df
                )

                if errors:

                    for error in errors:

                        st.error(
                            error
                        )

                if warnings:

                    st.warning(
                        "Data validation warnings:"
                    )

                    for warning in warnings:

                        st.write(
                            f"• {warning}"
                        )

                if not errors:

                    st.success(
                        "✅ Data validation completed successfully."
                    )

                    # -------------------------------------------------
                    # SAVE
                    # -------------------------------------------------

                    if st.button(
                        f"💾 Save {file.name}",
                        key=f"save_{file.name}"
                    ):

                        try:

                            saved_path = save_uploaded_workbook(
                                workbook_sheets,
                                file.name
                            )
                            
                            st.session_state["active_workbook"] = saved_path.name

                            with open(DATA_DIR / "active_workbook.txt", "w") as f:
                                f.write(saved_path.name)

                            st.success(
                                "✅ Data saved successfully!"
                            )

                            st.info(
                                f"Stored as: {saved_path.name}"
                            )

                            

                            st.session_state[
                               "uploaded_data"
                            ] = cleaned_df

                            st.rerun()


                        except Exception as e:

                            st.error(
                                f"Could not save file: {e}"
                            )

            except Exception as e:

                st.error(
                    f"Could not process {file.name}: {e}"
                )

    # ---------------------------------------------------------
    # SAVED FILES
    # ---------------------------------------------------------

    st.divider()

    st.subheader(
        "🗂️ Saved Data Files"
    )

    try:

        saved_files = get_uploaded_files()

        if not saved_files:

            st.info(
                "No uploaded files have been permanently stored yet."
            )

        else:

            for filename in saved_files:

                col1, col2 = st.columns([4, 1])

                col1.write(
                    f"📄 {filename}"
                )

                if col2.button(
                    "Delete",
                    key=f"delete_{filename}"
                ):

                    try:

                        delete_uploaded_file(
                            filename
                        )

                        st.success(
                            f"{filename} deleted successfully."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Could not delete {filename}: {e}"
                        )

    except Exception as e:

        st.error(
            f"Could not read saved files: {e}"
        )


# -----------------------------
# Data Sources
# -----------------------------
elif page == "Data Sources":
    st.subheader("Imported Data Sources")

    files = discover_files()
    if not files:
        st.warning("No files found. Create a data folder and place the Excel files inside it.")
    else:
        records = []
        for f in files:
            p = Path(f)
            try:
                records.append({
                    "File": p.name,
                    "Size (KB)": round(p.stat().st_size / 1024, 1),
                    "SHA256": hash_file(p)[:16] + "...",
                    "Status": "Available",
                })
            except Exception:
                pass
        st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)

    st.markdown("### Expected project files")
    st.write("""
    - Daily_Tata_Power_Systems_LTD_17-Aug-26.xlsx
    - Daily_Hexa_and_Vega_power_consumption_17-Aug-26.xlsx
    - Solar_Generation_-_U2_17-Aug-26.xlsx
    - Tata_Power_Air_Report_-_U2_17-Aug-26.xlsx
    - Tata_Power_Solar_Systems_Ltd_Humidity___Temperature_-_U2_17-Aug-26.xlsx
    - Unit_-1_and_5_daily_Tata_Power_Systems_LTD_17-Aug-26.xlsx
    """)
elif page == "AI Assistant":

    st.subheader("🤖 Utility Intelligence AI")

    st.write(
        "Ask questions about your utility data."
    )

    # ---------------------------------------------------------
    # SESSION STATE
    # ---------------------------------------------------------

    if "selected_question" not in st.session_state:
        st.session_state["selected_question"] = ""

    # ---------------------------------------------------------
    # QUESTION HISTORY
    # ---------------------------------------------------------

    history = get_question_history(20)

    if history:

        st.markdown("### 🕘 Previous Questions")

        # -----------------------------------------------------
        # CLEAR HISTORY
        # -----------------------------------------------------

        if st.button(
            "🗑️ Clear History",
            key="clear_question_history"
        ):

            clear_question_history()

            st.session_state["selected_question"] = ""

            st.rerun()

        # -----------------------------------------------------
        # PREVIOUS QUESTIONS
        # -----------------------------------------------------

        for item in history:

            previous_question = item[1]

            if st.button(
                previous_question,
                key=f"history_{item[0]}"
            ):

                st.session_state["selected_question"] = (
                    previous_question
                )

    # ---------------------------------------------------------
    # QUESTION INPUT
    #
    # IMPORTANT:
    # This stays OUTSIDE "if history"
    # so it remains visible after clearing history.
    # ---------------------------------------------------------

    question = st.text_input(
        "Ask your question",
        value=st.session_state.get(
            "selected_question",
            ""
        ),
        placeholder=(
            "Example: Which location has the highest "
            "energy consumption?"
        ),
        key="ai_question_input"
    )

    # ---------------------------------------------------------
    # ASK AI
    # ---------------------------------------------------------

    if question.strip():

        with st.spinner(
            "Analyzing your utility data..."
        ):

            # -------------------------------------------------
            # LOAD UPLOADED DATA
            # -------------------------------------------------

            uploaded_files = get_uploaded_files()

            uploaded_dataframes = []

            for filename in uploaded_files:

                try:

                    uploaded_df = load_saved_data(
                        filename
                    )

                    if (
                        isinstance(
                            uploaded_df,
                            pd.DataFrame
                        )
                        and not uploaded_df.empty
                    ):

                        uploaded_dataframes.append(
                            uploaded_df.copy()
                        )

                except Exception as e:

                    st.warning(
                        f"Could not load uploaded "
                        f"file {filename}: {e}"
                    )

            # -------------------------------------------------
            # USE UPLOADED DATA IF AVAILABLE
            # -------------------------------------------------

            if uploaded_dataframes:

                ai_dataframe = pd.concat(
                    uploaded_dataframes,
                    ignore_index=True,
                    sort=False
                )

                data_source = "Uploaded Data"

            else:

                # -------------------------------------------------
                # FALL BACK TO ORIGINAL PROJECT DATA
                # -------------------------------------------------

                project_data = load_project_data()

                project_dataframes = []

                for name, dataframe in project_data.items():

                    if (
                        isinstance(
                            dataframe,
                            pd.DataFrame
                        )
                        and not dataframe.empty
                    ):

                        project_dataframes.append(
                            dataframe.copy()
                        )

                if project_dataframes:

                    ai_dataframe = pd.concat(
                        project_dataframes,
                        ignore_index=True,
                        sort=False
                    )

                else:

                    ai_dataframe = pd.DataFrame()

                data_source = "Original Project Data"

            # -------------------------------------------------
            # CHECK DATA
            # -------------------------------------------------

            if ai_dataframe.empty:

                st.warning(
                    "No utility data is available "
                    "for the AI Assistant."
                )

                st.stop()

            # -------------------------------------------------
            # CREATE AI DATA CONTEXT
            # -------------------------------------------------

            data_context = ai_dataframe.to_string(
                index=False
            )

            # -------------------------------------------------
            # CREATE DATA SIGNATURE
            # -------------------------------------------------

            data_signature = hashlib.sha256(
                data_context.encode("utf-8")
            ).hexdigest()

            # -------------------------------------------------
            # CHECK PREVIOUS ANSWER
            # -------------------------------------------------

            previous_answer = get_previous_answer(
                question,
                data_signature
            )

            if previous_answer:

                answer = previous_answer

            else:

                # -------------------------------------------------
                # ASK AI USING CURRENT DATA
                # -------------------------------------------------

                answer = ask_ai(
                    question,
                    data_context,
                    ai_dataframe
                )

                # -------------------------------------------------
                # SAVE QUESTION + ANSWER
                # -------------------------------------------------

                save_question_history(
                    question,
                    answer,
                    data_signature
                )

            # -------------------------------------------------
            # DISPLAY ANSWER
            # -------------------------------------------------

            st.markdown(
                "### 🤖 AI Answer"
            )

            st.write(answer)

            st.caption(
                f"Answer generated from: {data_source}"
            )

    