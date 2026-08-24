import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        dbname=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
    )


def get_locations(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                location_id,
                location_name
            FROM solar_locations
            ORDER BY location_id;
        """)

        return cur.fetchall()


def get_daily_generation(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                s.log_date,
                l.location_name,
                s.generation_kwh
            FROM solar_daily_summary s
            JOIN solar_locations l
                ON s.location_id = l.location_id
            ORDER BY s.log_date DESC, l.location_id
            LIMIT 100;
        """)

        return cur.fetchall()


def get_telemetry(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                t.log_date,
                t.log_timestamp,
                l.location_name,
                t.kwh,
                t.kvah,
                t.kvar,
                t.kva,
                t.current,
                t.power_factor
            FROM solar_time_logs t
            JOIN solar_locations l
                ON t.location_id = l.location_id
            ORDER BY t.log_date DESC, t.log_timestamp DESC
            LIMIT 100;
        """)

        return cur.fetchall()


def main():
    print("Connecting to Solar Utility database...")

    conn = None

    try:
        conn = get_connection()

        print("\nSolar Locations:")
        locations = get_locations(conn)

        for location_id, location_name in locations:
            print(f"{location_id}: {location_name}")

        print("\nDaily Generation:")
        daily_generation = get_daily_generation(conn)

        for log_date, location_name, generation_kwh in daily_generation:
            print(
                f"{log_date} | "
                f"{location_name} | "
                f"{generation_kwh} kWh"
            )

        print("\n15-Minute Telemetry:")
        telemetry = get_telemetry(conn)

        for (
            log_date,
            log_timestamp,
            location_name,
            kwh,
            kvah,
            kvar,
            kva,
            current,
            power_factor,
        ) in telemetry:

            print(
                f"{log_date} {log_timestamp} | "
                f"{location_name} | "
                f"kWh: {kwh} | "
                f"kVAh: {kvah} | "
                f"kVAr: {kvar} | "
                f"kVA: {kva} | "
                f"Current: {current} | "
                f"PF: {power_factor}"
            )

    except Exception as e:
        print(f"\nDatabase error: {e}")

    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed")


if __name__ == "__main__":
    main()