
import os
import glob
import hashlib
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
    get_uploaded_files,
    get_file_info,
    get_data_summary,
    delete_uploaded_file,
)
from services.ai_agent import ask_ai
# Optional PDF/Excel exports
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False

st.set_page_config(
    page_title="Automated Utility Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
    .main { background: #f6f8fb; }
    .block-container { padding-top: 1rem; }
    .metric-card {
        background: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e6eaf0;
        box-shadow: 0 2px 8px rgba(0,0,0,.04);
    }
    .metric-title { color: #64748b; font-size: 13px; }
    .metric-value { color: #0f2f5f; font-size: 27px; font-weight: 700; }
    .metric-delta { font-size: 12px; }
    .critical { color:#b91c1c; font-weight:700; }
    .high { color:#ea580c; font-weight:700; }
    .medium { color:#ca8a04; font-weight:700; }
    .low { color:#16a34a; font-weight:700; }
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
# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("⚡ Utility Intelligence")
st.sidebar.caption("Automated Utility Intelligence & Daily Report System")

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
        "Data Upload",
        "Data Sources",
        "AI Assistant",
    ],
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
    m = energy[energy["location"].str.lower().str.contains(keyword.lower(), na=False)]
    return float(m["daily_kwh"].sum()) if not m.empty else np.nan

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
st.title("Automated Utility Intelligence & Daily Report System")
st.caption("Ingest → Store → Analyze → Visualize → Alert → Report → Insights")

# -----------------------------
# Command Center
# -----------------------------
if page == "Command Center":
    st.subheader("Command Center — Today")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Grid Energy", f"{grid:,.0f} kWh" if pd.notna(grid) else "N/A")
    c2.metric("Solar Generation", f"{solar_total:,.0f} kWh" if pd.notna(solar_total) else "N/A")
    c3.metric("Transformer Consumption", f"{transformer_total:,.0f} kWh" if pd.notna(transformer_total) else "N/A")
    c4.metric("Active Alerts", len(alerts_df))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Hexa Consumption", f"{hexa:,.0f} kWh" if pd.notna(hexa) else "N/A")
    c6.metric("Vega Consumption", f"{vega:,.0f} kWh" if pd.notna(vega) else "N/A")
    c7.metric("Compressed Air", f"{air_total:,.0f} m³" if pd.notna(air_total) else "N/A")
    c8.metric("Data Sources", len(data["sources"]))

    st.divider()

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("### Energy Overview")
        overview = pd.DataFrame({
            "Metric": ["Grid", "Solar", "Transformer", "Hexa", "Vega"],
            "Daily Value": [grid, solar_total, transformer_total, hexa, vega],
            "Unit": ["kWh", "kWh", "kWh", "kWh", "kWh"]
        }).dropna()
        st.bar_chart(overview.set_index("Metric")["Daily Value"])

    with right:
        st.markdown("### Top Consumers")
        if not tr_df.empty:
            top = tr_df.sort_values("daily_kwh", ascending=False).head(5)
            st.dataframe(top, use_container_width=True, hide_index=True)

    st.markdown("### Intelligent Operational Status")
    if alerts_df.empty:
        st.success("No major anomalies detected in the imported dataset.")
    else:
        for _, a in alerts_df.head(8).iterrows():
            icon = "🔴" if a["severity"] == "High" else "🟠"
            st.write(f"{icon} **{a['title']}** — {a['description']}")

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

# -----------------------------
# Data Upload
# -----------------------------
# ---------------------------------------------------------
# DATA UPLOAD
# ---------------------------------------------------------

elif page == "Data Upload":

    st.subheader("Data Ingestion & Validation")

    st.write(
        "Upload your utility data in CSV or Excel format. "
        "The system will validate, clean and permanently store the data."
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
                # LOAD
                # -------------------------------------------------

                df = load_file(file)

                st.success(
                    f"File loaded successfully: {file.name}"
                )

                # -------------------------------------------------
                # CLEAN
                # -------------------------------------------------

                cleaned_df = clean_data(df)

                # -------------------------------------------------
                # SUMMARY
                # -------------------------------------------------

                summary = get_data_summary(cleaned_df)

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
                # PREVIEW
                # -------------------------------------------------

                st.write("#### Data Preview")

                st.dataframe(
                    cleaned_df.head(20),
                    width="stretch"
                )

                # -------------------------------------------------
                # VALIDATION
                # -------------------------------------------------

                errors, warnings = validate_data(cleaned_df)

                if errors:

                    for error in errors:
                        st.error(error)

                if warnings:

                    st.warning("Data validation warnings:")

                    for warning in warnings:
                        st.write(f"• {warning}")

                if not errors:

                    st.success(
                        "Data validation completed successfully."
                    )

                    # -------------------------------------------------
                    # SAVE
                    # -------------------------------------------------

                    if st.button(
                        f"💾 Save {file.name}",
                        key=f"save_{file.name}"
                    ):

                        try:

                            saved_path = save_uploaded_data(
                                cleaned_df,
                                file.name
                            )

                            st.success(
                                f"Data saved successfully!"
                            )

                            st.info(
                                f"Stored as: {saved_path.name}"
                            )

                            st.session_state[
                                "uploaded_data"
                            ] = cleaned_df

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

    st.subheader("Saved Data Files")

    try:

        saved_files = get_uploaded_files()

        if not saved_files:

            st.info(
                "No uploaded files have been permanently stored yet."
            )

        else:

            for filename in saved_files:

                col1, col2 = st.columns([4, 1])

                col1.write(f"📄 {filename}")

                if col2.button(
                    "Delete",
                    key=f"delete_{filename}"
                ):

                    try:

                        delete_uploaded_file(filename)

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

    question = st.text_input(
        "Ask your question",
        placeholder="Example: Which location has the highest energy consumption?"
    )

    if question:

        with st.spinner("Analyzing your utility data..."):

            project_data = load_project_data()

            context_parts = []

            for name, df in project_data.items():

                if isinstance(df, pd.DataFrame) and not df.empty:

                    context_parts.append(
                        f"\n--- {name.upper()} DATA ---\n"
                    )

                    # Limit rows for now
                    context_parts.append(
                        df.head(100).to_string(index=False)
                    )

            data_context = "\n".join(context_parts)

            answer = ask_ai(
                question,
                data_context
            )

        st.markdown("### 🤖 AI Answer")
        st.write(answer)