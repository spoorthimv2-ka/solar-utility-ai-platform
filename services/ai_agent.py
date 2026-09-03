import requests
import re
import pandas as pd

from services.config_service import is_enabled


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.2"


# =========================================================
# BASIC HELPERS
# =========================================================

def _clean_text(value):
    return str(value).strip().lower()


def _find_column(df, keywords):

    if df is None or df.empty:
        return None

    for column in df.columns:

        name = _clean_text(column)

        for keyword in keywords:

            if keyword in name:
                return column

    return None


# =========================================================
# EXTRACT DATASET FROM CONTEXT
#
# IMPORTANT:
# Uploaded data is placed FIRST in priority.
# This prevents the original project data from
# overriding the user's uploaded CSV/Excel data.
# =========================================================

def _extract_best_dataframe(data_context):

    if not data_context:
        return None

    try:

        lines = [
            line.rstrip()
            for line in data_context.splitlines()
            if line.strip()
        ]

        # -------------------------------------------------
        # FIRST PRIORITY:
        # Find the LAST uploaded file section.
        #
        # This is important because app.py adds uploaded
        # files after the original project data.
        # -------------------------------------------------

        uploaded_starts = []

        for i, line in enumerate(lines):

            if "UPLOADED FILE:" in line.upper():
                uploaded_starts.append(i)

        candidate_starts = uploaded_starts

        # -------------------------------------------------
        # FALLBACK:
        # If there is no uploaded file, use project data.
        # -------------------------------------------------

        if not candidate_starts:

            candidate_starts = [
                i
                for i, line in enumerate(lines)
                if line.startswith("---")
            ]

        # -------------------------------------------------
        # Search sections from newest/last to oldest.
        # -------------------------------------------------

        for start_index in reversed(candidate_starts):

            section_lines = []

            for line in lines[start_index + 1:]:

                if line.startswith("---"):
                    break

                section_lines.append(line)

            if not section_lines:
                continue

            # -------------------------------------------------
            # Find a line that looks like a dataframe header.
            # -------------------------------------------------

            for header_index, line in enumerate(section_lines):

                parts = re.split(
                    r"\s{2,}|\t+",
                    line.strip()
                )

                parts = [
                    p.strip()
                    for p in parts
                    if p.strip()
                ]

                if len(parts) < 2:
                    continue

                joined = " ".join(parts).lower()

                useful_columns = [
                    "energy_consumption",
                    "energy consumption",
                    "water_consumption",
                    "water consumption",
                    "solar_generation",
                    "solar generation",
                    "temperature",
                    "unit",
                    "location"
                ]

                if not any(
                    keyword in joined
                    for keyword in useful_columns
                ):
                    continue

                header = parts
                rows = []

                for row_line in section_lines[
                    header_index + 1:
                ]:

                    row_parts = re.split(
                        r"\s{2,}|\t+",
                        row_line.strip()
                    )

                    row_parts = [
                        p.strip()
                        for p in row_parts
                        if p.strip()
                    ]

                    if len(row_parts) >= len(header):

                        rows.append(
                            row_parts[:len(header)]
                        )

                if not rows:
                    continue

                df = pd.DataFrame(
                    rows,
                    columns=header
                )

                df.columns = [
                    str(c).strip().lower()
                    for c in df.columns
                ]

                return df

    except Exception:
        return None

    return None


# =========================================================
# NUMERIC COLUMN CLEANING
# =========================================================

def _clean_numeric_column(df, column):

    if column is None:
        return

    df[column] = (
        df[column]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(
            r"(-?\d+(?:\.\d+)?)",
            expand=False
        )
    )

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# =========================================================
# DETERMINISTIC ANSWERS
#
# Exact calculations are handled by Python.
# Ollama is NOT used for arithmetic.
# =========================================================

def _deterministic_answer(
    question,
    data_context,
    dataframe=None
):

    q = _clean_text(question)

    # -----------------------------------------------------
    # USE THE ACTUAL DATAFRAME FROM APP
    # -----------------------------------------------------

    if (
        isinstance(dataframe, pd.DataFrame)
        and not dataframe.empty
    ):
        df = dataframe.copy()

    else:
        df = None

    
    # -----------------------------------------------------
    # IDENTIFY COLUMNS
    # -----------------------------------------------------

    unit_col = _find_column(
        df,
        [
            "unit",
            "location",
            "site"
        ]
    )

    energy_col = _find_column(
        df,
        [
            "energy_consumption",
            "energy consumption",
            "daily_kwh",
            "kwh",
            "energy"
        ]
    )

    water_col = _find_column(
        df,
        [
            "water_consumption",
            "water consumption",
            "water",
            "liters"
        ]
    )

    solar_col = _find_column(
        df,
        [
            "solar_generation",
            "solar generation",
            "solar"
        ]
    )

    temperature_col = _find_column(
        df,
        [
            "temperature_c",
            "temperature"
        ]
    )

    # -----------------------------------------------------
    # CLEAN NUMERIC COLUMNS
    # -----------------------------------------------------

    for column in [
        energy_col,
        water_col,
        solar_col,
        temperature_col
    ]:

        _clean_numeric_column(
            df,
            column
        )

    # =====================================================
    # ENERGY
    # =====================================================

    if energy_col:

        # -------------------------------------------------
        # TOTAL ENERGY
        # -------------------------------------------------

        if (
            "energy" in q
            and (
                "total" in q
                or "overall" in q
            )
            and (
                "consumption" in q
                or "consumed" in q
            )
        ):

            total = df[energy_col].sum()

            return (
                f"The total energy consumption is "
                f"{total:,.0f} kWh."
            )

        # -------------------------------------------------
        # MOST ENERGY
        # -------------------------------------------------

        if (
            "energy" in q
            and (
                "most" in q
                or "highest" in q
                or "maximum" in q
            )
        ):

            idx = df[energy_col].idxmax()

            value = df.loc[
                idx,
                energy_col
            ]

            if unit_col:

                unit = df.loc[
                    idx,
                    unit_col
                ]

                return (
                    f"{unit} consumed the most energy, "
                    f"with {value:,.0f} kWh."
                )

            return (
                f"The highest energy consumption was "
                f"{value:,.0f} kWh."
            )

        # -------------------------------------------------
        # LEAST ENERGY
        # -------------------------------------------------

        if (
            "energy" in q
            and (
                "least" in q
                or "lowest" in q
                or "minimum" in q
            )
        ):

            idx = df[energy_col].idxmin()

            value = df.loc[
                idx,
                energy_col
            ]

            if unit_col:

                unit = df.loc[
                    idx,
                    unit_col
                ]

                return (
                    f"{unit} consumed the least energy, "
                    f"with {value:,.0f} kWh."
                )

            return (
                f"The lowest energy consumption was "
                f"{value:,.0f} kWh."
            )

    # =====================================================
    # WATER
    # =====================================================

    if water_col:

        # -------------------------------------------------
        # TOTAL WATER
        # -------------------------------------------------

        if (
            "water" in q
            and (
                "total" in q
                or "overall" in q
            )
        ):

            total = df[water_col].sum()

            return (
                f"The total water consumption is "
                f"{total:,.0f} liters."
            )

        # -------------------------------------------------
        # MOST WATER
        # -------------------------------------------------

        if (
            "water" in q
            and (
                "most" in q
                or "highest" in q
                or "maximum" in q
            )
        ):

            idx = df[water_col].idxmax()

            value = df.loc[
                idx,
                water_col
            ]

            if unit_col:

                unit = df.loc[
                    idx,
                    unit_col
                ]

                return (
                    f"{unit} had the highest water "
                    f"consumption, at "
                    f"{value:,.0f} liters."
                )

    # =====================================================
    # SOLAR
    # =====================================================

    if solar_col:

        # -------------------------------------------------
        # TOTAL SOLAR
        # -------------------------------------------------

        if (
            "solar" in q
            and (
                "total" in q
                or "overall" in q
            )
        ):

            total = df[solar_col].sum()

            return (
                f"The total solar generation is "
                f"{total:,.0f} kWh."
            )

        # -------------------------------------------------
        # MOST SOLAR
        # -------------------------------------------------

        if (
            "solar" in q
            and (
                "most" in q
                or "highest" in q
                or "maximum" in q
            )
        ):

            idx = df[solar_col].idxmax()

            value = df.loc[
                idx,
                solar_col
            ]

            if unit_col:

                unit = df.loc[
                    idx,
                    unit_col
                ]

                return (
                    f"{unit} had the highest solar "
                    f"generation, at "
                    f"{value:,.0f} kWh."
                )

    # =====================================================
    # TEMPERATURE
    # =====================================================

    if temperature_col:

        # -------------------------------------------------
        # HIGHEST TEMPERATURE
        # -------------------------------------------------

        if (
            "temperature" in q
            and (
                "highest" in q
                or "maximum" in q
                or "hottest" in q
            )
        ):

            idx = df[temperature_col].idxmax()

            value = df.loc[
                idx,
                temperature_col
            ]

            if unit_col:

                unit = df.loc[
                    idx,
                    unit_col
                ]

                return (
                    f"{unit} had the highest "
                    f"temperature, at "
                    f"{value:,.1f} °C."
                )

            return (
                f"The highest temperature was "
                f"{value:,.1f} °C."
            )

    return None


# =========================================================
# MAIN AI FUNCTION
# =========================================================

def ask_ai(question, data_context, dataframe=None):

    # -----------------------------------------------------
    # ADMIN AI CHECK
    # -----------------------------------------------------

    if not is_enabled(
        "ai_enabled",
        default=True
    ):

        return (
            "The AI Agent has been disabled "
            "by the administrator."
        )

    # -----------------------------------------------------
    # EXACT NUMERICAL QUESTIONS
    #
    # Python handles these first.
    # -----------------------------------------------------

    deterministic = _deterministic_answer(
        question,
        data_context,
        dataframe
    )

    if deterministic:

        return deterministic

    # -----------------------------------------------------
    # OLLAMA FOR GENERAL QUESTIONS
    # -----------------------------------------------------

    prompt = f"""
You are the Utility Intelligence AI assistant.

Answer ONLY using the utility data supplied below.

STRICT RULES:

1. Answer the exact question asked.
2. Use only the supplied utility data.
3. Never invent numbers.
4. Never invent dates.
5. Never invent locations.
6. Never assume information that is not present.
7. If calculations are required, use the supplied data.
8. If the information is not available, say:
"I could not find this information in the available data."
9. Do not answer a different question.
10. Do not use outside knowledge.

UTILITY DATA:
----------------
{data_context}
----------------

USER QUESTION:
{question}

Return ONLY the answer.
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "seed": 42,
                    "num_ctx": 4096
                }
            },
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        answer = result.get(
            "response",
            ""
        ).strip()

        if not answer:

            return (
                "I could not generate an answer "
                "from the available data."
            )

        return answer

    except requests.exceptions.ConnectionError:

        return (
            "The local AI service is not running. "
            "Please start Ollama with: ollama serve"
        )

    except requests.exceptions.Timeout:

        return (
            "The AI request took too long to complete. "
            "Please try again."
        )

    except Exception as e:

        return f"AI error: {e}"