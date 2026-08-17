import sqlite3
import requests
from time import sleep

DB_NAME = "clash_data.db"   # keep this the same as the rest of your project
TIME_URL = "http://worldtimeapi.org/api/timezone/America/Detroit"

MAX_NEW_TIME_ROWS_PER_RUN = 25
MAX_ATTEMPTS_PER_CALL = 5


def create_timeinfo_table_if_needed(conn: sqlite3.Connection) -> None:
    """Create the timeinfo table if it does not already exist."""
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS timeinfo (
            id INTEGER PRIMARY KEY,
            datetime TEXT UNIQUE,
            day_of_week TEXT,
            hour INTEGER,
            timezone TEXT
        );
    """)
    conn.commit()


def fetch_and_store_timeinfo(conn: sqlite3.Connection, pause_seconds: float = 1.0) -> int:
    """
    Calls WorldTime API up to MAX_NEW_TIME_ROWS_PER_RUN times and stores each
    datetime/hour/day_of_week/timezone in the timeinfo table.
    Respects UNIQUE(datetime) so no duplicates.
    Returns number of new rows inserted.
    """
    cur = conn.cursor()
    new_rows = 0

    day_map = ["Monday", "Tuesday", "Wednesday",
               "Thursday", "Friday", "Saturday", "Sunday"]

    for i in range(1, MAX_NEW_TIME_ROWS_PER_RUN + 1):
        resp = None

        # retry a few times in case of network hiccups
        for attempt in range(1, MAX_ATTEMPTS_PER_CALL + 1):
            try:
                resp = requests.get(TIME_URL, timeout=10)
                resp.raise_for_status()
                break
            except requests.RequestException as e:
                print(f"[{i}] Request failed (attempt {attempt}), skipping this attempt: {e}")
                resp = None

        if resp is None:
            # give up on this row and move to the next
            continue

        data = resp.json()
        dt = data.get("datetime")          # full ISO string
        day_of_week = data.get("day_of_week")  # 0–6 in API
        timezone = data.get("timezone")
        hour = None
        if dt and len(dt) >= 13:
            try:
                hour = int(dt[11:13])
            except ValueError:
                hour = None

        dow_str = None
        if isinstance(day_of_week, int) and 0 <= day_of_week < len(day_map):
            dow_str = day_map[day_of_week]

        try:
            cur.execute("""
                INSERT INTO timeinfo (datetime, day_of_week, hour, timezone)
                VALUES (?, ?, ?, ?);
            """, (dt, dow_str, hour, timezone))
            new_rows += 1
            print(f"[{i}] Inserted new row at {dt}")
        except sqlite3.IntegrityError:
            # duplicate datetime -> ignore
            print(f"[{i}] Duplicate datetime {dt}, skipping")
            pass

        conn.commit()
        sleep(pause_seconds)

    return new_rows


def main():
    conn = sqlite3.connect(DB_NAME)
    create_timeinfo_table_if_needed(conn)
    new_rows = fetch_and_store_timeinfo(conn)
    print(f"Inserted {new_rows} new time rows this run (max {MAX_NEW_TIME_ROWS_PER_RUN}).")
    conn.close()


if __name__ == "__main__":
    main()
