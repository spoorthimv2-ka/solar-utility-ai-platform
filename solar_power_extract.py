import sqlite3
import pandas as pd
import os

# CONFIGURATION

DB_FILE = "solar_power/solar_power_sense.db"
EXCEL_FILE = "solar_daily_data.xlsx"

# EXCEL SHEET -> LOCATION

SOLAR_LOCATIONS = {
    "60KW Solar ( Above ATS)": {
        "location_id": 1,
        "location_name": "60KW Solar (Above ATS)"
    },
    "20KW Solar (Above Canteen )": {
        "location_id": 2,
        "location_name": "20KW Solar (Above Canteen)"
    },
    "110KW Solar (Above LT Room)": {
        "location_id": 3,
        "location_name": "110KW Solar (Above LT Room)"
    },
    "230Kw Solar kit( chiller area 3": {
        "location_id": 4,
        "location_name": "230KW Solar Kit (Chiller Area 3 to 6)"
    },
    "40 kW Solar (PECVD Pump Room)": {
        "location_id": 5,
        "location_name": "40KW Solar (PECVD Pump Room)"
    },
    "180kw Solar (hexa AHU area)": {
        "location_id": 6,
        "location_name": "180KW Solar (Hexa AHU Area)"
    },
    "Solar Near STP": {
        "location_id": 7,
        "location_name": "Solar Near STP"
    },
    "Solar Near Gate-1 Pathway Stair": {
        "location_id": 8,
        "location_name": "Solar Near Gate-1 Pathway Staircase"
    },
    "Solar Near Parking Area": {
        "location_id": 9,
        "location_name": "Solar Near Parking Area"
    }
}

# DATABASE CONNECTION

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# CREATE TABLES

def create_tables(conn):
    cursor = conn.cursor()

    # Locations
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solar_locations (
            location_id INTEGER PRIMARY KEY,
            location_name TEXT NOT NULL,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            modified_date TEXT DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT DEFAULT 'system',
            modified_by TEXT DEFAULT 'system'
        )
    """)

    # Daily summary

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solar_daily_summary (
            summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,
            generation_kwh REAL NOT NULL,

            UNIQUE(location_id, log_date),

            FOREIGN KEY(location_id)
                REFERENCES solar_locations(location_id)
        )
    """)

    # Time logs
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solar_time_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,

            location_id INTEGER NOT NULL,

            log_date TEXT NOT NULL,

            log_timestamp TEXT NOT NULL,

            kwh REAL,
            kvah REAL,
            kw REAL,
            kva REAL,
            current REAL,
            power_factor REAL,

            UNIQUE(
                location_id,
                log_date,
                log_timestamp
            ),

            FOREIGN KEY(location_id)
                REFERENCES solar_locations(location_id)
        )
    """)

    conn.commit()



# INSERT LOCATIONS


def insert_locations(conn):

    cursor = conn.cursor()

    for sheet_name, location in SOLAR_LOCATIONS.items():

        cursor.execute("""
            INSERT INTO solar_locations
            (
                location_id,
                location_name
            )
            VALUES (?, ?)

            ON CONFLICT(location_id)
            DO UPDATE SET
                location_name = excluded.location_name,
                modified_date = CURRENT_TIMESTAMP
        """, (
            location["location_id"],
            location["location_name"]
        ))

    conn.commit()

# CLEAN NUMBER

def clean_number(value):

    if value is None:
        return None

    if pd.isna(value):
        return None

    try:

        if isinstance(value, str):

            value = value.strip()

            if value == "":
                return None

            value = value.replace(",", "")

        return float(value)

    except Exception:

        return None

# NORMALIZE TEXT

def normalize_text(value):

    if value is None:
        return ""

    if pd.isna(value):
        return ""

    return str(value).strip().lower()

# FIND DATA HEADER

def find_data_header(df):

    for index in range(len(df)):

        row = df.iloc[index]

        values = [
            normalize_text(value)
            for value in row.values
        ]

        has_timestamp = any(
            "timestamp" in value
            for value in values
        )

        has_kwh = any(
            value == "kwh"
            for value in values
        )

        has_kvah = any(
            value == "kvah"
            for value in values
        )

        if (
            has_timestamp
            and has_kwh
            and has_kvah
        ):

            return index

    return None

# FIND COLUMN

def find_column(columns, names):

    for column in columns:

        normalized = normalize_text(column)

        normalized = (
            normalized
            .replace(".", "")
            .replace(" ", "")
            .replace("_", "")
        )

        for name in names:

            target = (
                name.lower()
                .replace(".", "")
                .replace(" ", "")
                .replace("_", "")
            )

            if normalized == target:

                return column

    return None

# FIND REPORT DATE

def find_report_date(df):

    for row_index in range(min(len(df), 20)):

        row = df.iloc[row_index]

        for col_index, value in enumerate(row):

            text = normalize_text(value)

            if text == "from:":

                # The date is usually next column
                if col_index + 1 < len(row):

                    date_value = row.iloc[
                        col_index + 1
                    ]

                    parsed = pd.to_datetime(
                        date_value,
                        errors="coerce",
                        dayfirst=True
                    )

                    if not pd.isna(parsed):

                        return parsed.strftime(
                            "%Y-%m-%d"
                        )

    return None

# PROCESS ONE SHEET

def process_sheet(
    conn,
    excel_file,
    sheet_name,
    location_id
):

    print()
    print("=" * 80)

    print(
        f"Processing: {sheet_name}"
    )

    print(
        f"Location ID: {location_id}"
    )

    print("=" * 80)

    # Read entire Excel sheet without header
    
    try:

        df = pd.read_excel(
            excel_file,
            sheet_name=sheet_name,
            header=None
        )

    except Exception as e:

        print(
            f"ERROR reading sheet: {e}"
        )

        return 0


    if df.empty:

        print("Sheet is empty.")

        return 0


    print(
        f"Total Excel rows: {len(df)}"
    )
    
    # Find report date

    report_date = find_report_date(df)


    if report_date is None:

        print(
            "WARNING: Could not find report From date."
        )

        return 0


    print(
        f"Report date: {report_date}"
    )

    # Find actual data header
    
    header_row = find_data_header(df)


    if header_row is None:

        print(
            "ERROR: Could not find "
            "Timestamp/kWh/kVAh header."
        )

        return 0


    print(
        f"Data header row: {header_row + 1}"
    )

    # Extract header

    headers = df.iloc[
        header_row
    ].tolist()


    
    # Data starts after header
    

    data = df.iloc[
        header_row + 1:
    ].copy()


    data.columns = headers


    
    # Find columns
    

    timestamp_col = find_column(
        data.columns,
        [
            "Timestamp"
        ]
    )

    kwh_col = find_column(
        data.columns,
        [
            "kWh"
        ]
    )

    kvah_col = find_column(
        data.columns,
        [
            "kVAh"
        ]
    )

    kw_col = find_column(
        data.columns,
        [
            "kW"
        ]
    )

    kva_col = find_column(
        data.columns,
        [
            "kVA"
        ]
    )

    current_col = find_column(
        data.columns,
        [
            "current"
        ]
    )

    pf_col = find_column(
        data.columns,
        [
            "P.F.",
            "PF"
        ]
    )


    print()
    print("Detected columns:")

    print("Timestamp:", timestamp_col)
    print("kWh      :", kwh_col)
    print("kVAh     :", kvah_col)
    print("kW       :", kw_col)
    print("kVA      :", kva_col)
    print("Current  :", current_col)
    print("P.F.     :", pf_col)


    if timestamp_col is None:

        print(
            "ERROR: Timestamp column not found."
        )

        return 0


    
    # Process rows
    

    cursor = conn.cursor()

    inserted = 0
    skipped = 0


    for index, row in data.iterrows():

        try:

            timestamp_value = row[
                timestamp_col
            ]


            # ------------------------------------------------
            # Skip empty timestamp
            # ------------------------------------------------

            if (
                timestamp_value is None
                or pd.isna(timestamp_value)
            ):

                skipped += 1

                continue


            timestamp_text = str(
                timestamp_value
            ).strip()


            # ------------------------------------------------
            # Ignore summary rows
            # ------------------------------------------------

            summary_rows = [
                "maximum",
                "minimum",
                "average",
                "total"
            ]


            if timestamp_text.lower() in summary_rows:

                skipped += 1

                continue


            # ------------------------------------------------
            # Convert timestamp
            # ------------------------------------------------

            parsed_time = pd.to_datetime(
                timestamp_value,
                errors="coerce"
            )


            if pd.isna(parsed_time):

                # Try explicit format

                parsed_time = pd.to_datetime(
                    timestamp_text,
                    format="%I:%M:%S %p",
                    errors="coerce"
                )


            if pd.isna(parsed_time):

                print(
                    f"Skipping invalid time: "
                    f"{timestamp_text}"
                )

                skipped += 1

                continue


            log_timestamp = parsed_time.strftime(
                "%H:%M:%S"
            )


            # ------------------------------------------------
            # Numeric values
            # ------------------------------------------------

            kwh = clean_number(
                row[kwh_col]
            ) if kwh_col else None


            kvah = clean_number(
                row[kvah_col]
            ) if kvah_col else None


            kw = clean_number(
                row[kw_col]
            ) if kw_col else None


            kva = clean_number(
                row[kva_col]
            ) if kva_col else None


            current = clean_number(
                row[current_col]
            ) if current_col else None


            power_factor = clean_number(
                row[pf_col]
            ) if pf_col else None


            # ------------------------------------------------
            # Insert / Update
            # ------------------------------------------------

            cursor.execute("""
                INSERT INTO solar_time_logs
                (
                    location_id,
                    log_date,
                    log_timestamp,
                    kwh,
                    kvah,
                    kw,
                    kva,
                    current,
                    power_factor
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(
                    location_id,
                    log_date,
                    log_timestamp
                )
                DO UPDATE SET

                    kwh = excluded.kwh,
                    kvah = excluded.kvah,
                    kw = excluded.kw,
                    kva = excluded.kva,
                    current = excluded.current,
                    power_factor = excluded.power_factor

            """, (
                location_id,
                report_date,
                log_timestamp,
                kwh,
                kvah,
                kw,
                kva,
                current,
                power_factor
            ))


            inserted += 1


        except Exception as e:

            print(
                f"Error processing row "
                f"{index + 1}: {e}"
            )

            skipped += 1


    conn.commit()


    
    # Update daily summary
    

    update_daily_summary(
        conn,
        location_id,
        report_date
    )


    print()
    print(
        f"Rows processed : {inserted}"
    )

    print(
        f"Rows skipped   : {skipped}"
    )


    return inserted



# DAILY SUMMARY


def update_daily_summary(
    conn,
    location_id,
    log_date
):

    cursor = conn.cursor()


    
    # Get maximum kWh for the day
    

    cursor.execute("""
        SELECT MAX(kwh)

        FROM solar_time_logs

        WHERE location_id = ?
          AND log_date = ?

          AND kwh IS NOT NULL
    """, (
        location_id,
        log_date
    ))


    result = cursor.fetchone()


    if not result:

        return


    generation_kwh = result[0]


    if generation_kwh is None:

        return


    
    # Insert / Update daily summary
    

    cursor.execute("""
        INSERT INTO solar_daily_summary
        (
            location_id,
            log_date,
            generation_kwh
        )
        VALUES (?, ?, ?)

        ON CONFLICT(
            location_id,
            log_date
        )

        DO UPDATE SET

            generation_kwh =
                excluded.generation_kwh
    """, (
        location_id,
        log_date,
        generation_kwh
    ))


    conn.commit()



# MAIN


def main():

    print()
    print("=" * 80)
    print("SOLAR POWER SENSE - EXCEL INGESTION")
    print("=" * 80)


    
    # Check Excel
    

    if not os.path.exists(EXCEL_FILE):

        print()
        print(
            f"ERROR: Excel file not found:"
        )

        print(
            EXCEL_FILE
        )

        return


    
    # Connect DB
    

    conn = get_connection()


    try:

        # ----------------------------------------------------
        # Create tables
        # ----------------------------------------------------

        create_tables(conn)


        # ----------------------------------------------------
        # Insert locations
        # ----------------------------------------------------

        insert_locations(conn)


        # ----------------------------------------------------
        # Get Excel sheets
        # ----------------------------------------------------

        excel = pd.ExcelFile(
            EXCEL_FILE
        )


        print()
        print("Excel sheets found:")

        for sheet in excel.sheet_names:

            print(
                f"  {sheet}"
            )


        total = 0


        # ----------------------------------------------------
        # Process configured sheets
        # ----------------------------------------------------

        for sheet_name, location in SOLAR_LOCATIONS.items():

            print(f"Excel Sheet NameList : {sheet_name}")
            print(f"Excel Sheet Names : {excel.sheet_names}")

            if sheet_name not in excel.sheet_names:

                print()
                print(
                    "WARNING: Sheet not found:"
                )

                print(
                    sheet_name
                )

                continue


            count = process_sheet(
                conn,
                EXCEL_FILE,
                sheet_name,
                location["location_id"]
            )


            total += count


        print()
        print("=" * 80)

        print(
            f"TOTAL RECORDS PROCESSED: {total}"
        )

        print("=" * 80)


    finally:

        conn.close()



# RUN


if __name__ == "__main__":

    main()