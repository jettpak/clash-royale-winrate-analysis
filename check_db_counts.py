import sqlite3

DB_NAME = "clash_data.db"

TABLES = ["cards", "battles", "battle_cards", "timeinfo"]

def table_exists(cur, table_name):
    cur.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name=?;
    """, (table_name,))
    return cur.fetchone() is not None

def main():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    for table in TABLES:
        if table_exists(cur, table):
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            count = cur.fetchone()[0]
            print(f"{table}: {count} rows")
        else:
            print(f"{table}: MISSING TABLE")

    conn.close()

if __name__ == "__main__":
    main()
