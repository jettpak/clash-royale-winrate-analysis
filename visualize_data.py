# visualize_data.py

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_NAME = "clash_data.db"


def fetch_deck_stats(conn):
    query = """
    SELECT
        deck_key_card AS deck_type,
        COUNT(*) AS games,
        SUM(CASE WHEN result='win' THEN 1 ELSE 0 END) AS wins,
        SUM(CASE WHEN result='loss' THEN 1 ELSE 0 END) AS losses,
        AVG(CASE WHEN result='win' THEN 1.0 ELSE 0.0 END) AS winrate
    FROM battles
    WHERE deck_key_card IS NOT NULL
      AND TRIM(deck_key_card) != ''
    GROUP BY deck_key_card
    HAVING COUNT(*) >= 3
    ORDER BY games DESC;
    """
    return pd.read_sql_query(query, conn)


def fetch_time_of_day_stats(conn):
    query = """
    SELECT
        time_of_day,
        AVG(CASE WHEN result='win' THEN 1.0 ELSE 0.0 END) AS winrate,
        COUNT(*) AS games
    FROM battles
    WHERE time_of_day IS NOT NULL
      AND TRIM(time_of_day) != ''
    GROUP BY time_of_day;
    """
    return pd.read_sql_query(query, conn)


def plot_winrate_by_deck(df):
    # Keep chart readable: show top 8 by games
    df = df.sort_values("games", ascending=False).head(8)

    plt.figure(figsize=(9, 5))
    plt.bar(df["deck_type"], df["winrate"])
    plt.title("Winrate by Deck Type (Top Decks by Games Played)")
    plt.xlabel("Deck Type (deck_key_card)")
    plt.ylabel("Winrate")
    plt.ylim(0, 1)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.show()


def plot_wins_losses_stacked(df):
    df = df.sort_values("games", ascending=False).head(8)

    plt.figure(figsize=(9, 5))
    plt.bar(df["deck_type"], df["wins"], label="Wins")
    plt.bar(df["deck_type"], df["losses"], bottom=df["wins"], label="Losses")
    plt.title("Wins vs Losses by Deck Type (Stacked, Top Decks)")
    plt.xlabel("Deck Type (deck_key_card)")
    plt.ylabel("Number of Games")
    plt.xticks(rotation=30, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_winrate_by_time_of_day(df):
    order = ["morning", "afternoon", "evening", "late_night"]
    df["time_of_day"] = pd.Categorical(df["time_of_day"], categories=order, ordered=True)
    df = df.sort_values("time_of_day")

    plt.figure(figsize=(7, 4))
    plt.bar(df["time_of_day"], df["winrate"])
    plt.title("Winrate by Time of Day")
    plt.xlabel("Time of Day")
    plt.ylabel("Winrate")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.show()


def main():
    conn = sqlite3.connect(DB_NAME)

    deck_df = fetch_deck_stats(conn)
    tod_df = fetch_time_of_day_stats(conn)

    conn.close()

    if deck_df.empty:
        print("No usable deck_key_card data found to plot.")
        print("This usually means deck_key_card is NULL/blank for your battles.")
        return

    plot_winrate_by_deck(deck_df)
    plot_wins_losses_stacked(deck_df)

    if not tod_df.empty:
        plot_winrate_by_time_of_day(tod_df)
    else:
        print("No time_of_day data found to plot.")


if __name__ == "__main__":
    main()
