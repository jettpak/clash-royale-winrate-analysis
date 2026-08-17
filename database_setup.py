import sqlite3

DB_NAME = "clash_data.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS timeinfo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT UNIQUE,
            day_of_week TEXT,
            hour INTEGER,
            timezone TEXT
        );
    """)

    # ... your Clash Royale tables here ...

    conn.commit()
    conn.close()
