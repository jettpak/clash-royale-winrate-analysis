# analyze_data.py

import sqlite3

DB_NAME = "clash_data.db"
OUTPUT_FILE = "analysis_output.txt"


def fetch_winrate_by_deck(conn):
    query = """
    SELECT
        deck_key_card AS deck_type,
        COUNT(*) AS games_played,
        SUM(CASE WHEN result='win' THEN 1 ELSE 0 END) AS wins,
        SUM(CASE WHEN result='loss' THEN 1 ELSE 0 END) AS losses,
        ROUND(AVG(CASE WHEN result='win' THEN 1.0 ELSE 0.0 END), 3) AS winrate,
        ROUND(AVG(crowns_for), 2) AS avg_crowns_for
    FROM battles
    WHERE deck_key_card IS NOT NULL
      AND TRIM(deck_key_card) != ''
    GROUP BY deck_key_card
    HAVING COUNT(*) >= 3
    ORDER BY winrate DESC, games_played DESC;
    """
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchall()


def fetch_winrate_by_time_of_day(conn):
    query = """
    SELECT
        time_of_day,
        COUNT(*) AS games_played,
        ROUND(AVG(CASE WHEN result='win' THEN 1.0 ELSE 0.0 END), 3) AS winrate
    FROM battles
    WHERE time_of_day IS NOT NULL
      AND TRIM(time_of_day) != ''
    GROUP BY time_of_day
    ORDER BY games_played DESC;
    """
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchall()


def fetch_top_cards_used_join(conn, limit=10):
    # JOIN requirement: battle_cards -> cards
    query = """
    SELECT
        c.name AS card_name,
        COUNT(*) AS uses
    FROM battle_cards bc
    JOIN cards c ON bc.card_id = c.id
    WHERE bc.side = 'player'
    GROUP BY c.name
    ORDER BY uses DESC
    LIMIT ?;
    """
    cur = conn.cursor()
    cur.execute(query, (limit,))
    return cur.fetchall()


def main():
    conn = sqlite3.connect(DB_NAME)

    deck_stats = fetch_winrate_by_deck(conn)
    tod_stats = fetch_winrate_by_time_of_day(conn)
    top_cards = fetch_top_cards_used_join(conn, limit=10)

    with open(OUTPUT_FILE, "w") as f:
        f.write("=== Winrate by Deck Type (deck_key_card) ===\n")
        if not deck_stats:
            f.write("No non-empty deck_key_card values found in battles.\n")
            f.write("Tip: your insert script may not be populating deck_key_card.\n")
        else:
            for deck_type, games, wins, losses, winrate, avg_crowns in deck_stats:
                f.write(
                    f"{deck_type}: games={games}, wins={wins}, losses={losses}, "
                    f"winrate={winrate}, avg_crowns_for={avg_crowns}\n"
                )

        f.write("\n=== Winrate by Time of Day ===\n")
        if not tod_stats:
            f.write("No time_of_day values found in battles.\n")
        else:
            for tod, games, winrate in tod_stats:
                f.write(f"{tod}: games={games}, winrate={winrate}\n")

        f.write("\n=== Top 10 Most-Used Cards Across Player Decks (JOIN: battle_cards → cards) ===\n")
        if not top_cards:
            f.write("No battle_cards data found to join.\n")
        else:
            for card_name, uses in top_cards:
                f.write(f"{card_name}: {uses} uses\n")

    conn.close()
    print("Analysis complete. Results written to analysis_output.txt")


if __name__ == "__main__":
    main()
