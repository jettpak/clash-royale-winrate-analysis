# clash_data.py
"""
- Set ROYALE_API_KEY in your environment before running.
"""

import os
import sqlite3
import requests
import argparse
import json
from datetime import datetime
from typing import List, Dict

DB_PATH = "clash_data.db"
# --- FIX 1: Using the Official Supercell API URL ---
ROYALE_BASE = "https://api.clashroyale.com/v1"
MAX_ITEMS_PER_RUN = 25

KEY_CARDS_PRIORITY = [
    "Golem", "Hog Rider", "Royal Giant", "X-Bow", "Mortar", "Miner",
    "Balloon", "P.E.K.K.A", "Giant", "Lava Hound", "Graveyard", "Sparky"
]

def get_headers():
    token = os.getenv("ROYALE_API_KEY")
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def normalize_name(name: str) -> str:
    if not name:
        return ""
    return name.strip()

def time_of_day_from_hour(h: int) -> str:
    if h is None:
        return None
    if 5 <= h < 12:
        return "morning"
    if 12 <= h < 17:
        return "afternoon"
    if 17 <= h < 22:
        return "evening"
    return "late_night"

def create_tables_if_needed(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cards (
      id INTEGER PRIMARY KEY,
      api_card_id INTEGER UNIQUE,
      name TEXT NOT NULL,
      rarity TEXT,
      elixir_cost INTEGER
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS battles (
      id INTEGER PRIMARY KEY,
      battle_time TEXT NOT NULL,
      battle_timestamp TEXT UNIQUE NOT NULL,
      result TEXT,
      crowns_for INTEGER,
      crowns_against INTEGER,
      deck_key_card TEXT,
      weekday TEXT,
      hour INTEGER,
      time_of_day TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS battle_cards (
      id INTEGER PRIMARY KEY,
      battle_id INTEGER NOT NULL,
      card_id INTEGER NOT NULL,
      side TEXT CHECK(side IN ('player','opponent')),
      FOREIGN KEY(battle_id) REFERENCES battles(id),
      FOREIGN KEY(card_id) REFERENCES cards(id),
      UNIQUE(battle_id, card_id, side)
    );
    """)
    conn.commit()

def fetch_cards_from_api() -> List[Dict]:
    # This will now correctly resolve to https://api.clashroyale.com/v1/cards
    url = f"{ROYALE_BASE}/cards"
    resp = requests.get(url, headers=get_headers(), timeout=15)
    resp.raise_for_status()
    # The official API returns card data in a "items" list
    data = resp.json()
    return data.get("items", [])

def insert_cards(conn: sqlite3.Connection, cards: List[Dict]) -> int:
    cur = conn.cursor()
    inserted = 0
    for c in cards:
        # The official API uses 'id' and 'name' at the top level
        api_id = c.get("id")
        name = c.get("name")
        if not name:
            continue
        # Extract rarity and elixir cost (using keys from official API documentation)
        rarity = c.get("rarity")
        elixir = c.get("elixirCost") # key is 'elixirCost' in official API
        
        try:
            cur.execute("""
            INSERT INTO cards (api_card_id, name, rarity, elixir_cost)
            VALUES (?, ?, ?, ?)
            """, (int(api_id) if api_id is not None else None, normalize_name(name), rarity, elixir))
            inserted += 1
        except sqlite3.IntegrityError:
            continue
    conn.commit()
    print(f"Inserted {inserted} new cards")
    return inserted

def fetch_battlelog(player_tag: str) -> List[Dict]:
    tag = player_tag.strip()
    if tag.startswith("#"):
        tag = tag[1:]
    
    # --- FIX 2: Correct URL structure for Supercell API, including tag encoding ---
    # The official API uses /players/%23{tag}/battlelog
    url = f"{ROYALE_BASE}/players/%23{tag}/battlelog"
    resp = requests.get(url, headers=get_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()

def detect_deck_key_card(card_names: List[str]) -> str:
    names_set = set(normalize_name(n) for n in card_names if n)
    for key in KEY_CARDS_PRIORITY:
        if key in names_set:
            return key
    return "other"

def insert_battles_and_cards(conn: sqlite3.Connection, battles: List[Dict], limit_per_run: int = MAX_ITEMS_PER_RUN, debug=False) -> int:
    cur = conn.cursor()
    inserted_battles = 0
    for b in battles:
        if inserted_battles >= limit_per_run:
            break

        battle_time = b.get("battleTime") # Official API uses 'battleTime'
        battle_timestamp = str(b.get("battleId") or battle_time)

        if debug:
            print("SAMPLE BATTLE JSON:")
            print(json.dumps(b, indent=2))
            return 0

        # --- Data Extraction Logic (Fixed in previous step) ---
        crowns_for = None
        crowns_against = None
        result = None
        
        team_data = b.get("team")
        opponent_data = b.get("opponent")
        
        player_entry = team_data[0] if team_data and isinstance(team_data, list) and team_data else None
        opponent_entry = opponent_data[0] if opponent_data and isinstance(opponent_data, list) and opponent_data else None

        # 1. Get Crowns and Determine Result
        if player_entry:
            crowns_for = player_entry.get("crowns")
        if opponent_entry:
            crowns_against = opponent_entry.get("crowns")
            
        if crowns_for is not None and crowns_against is not None:
            if crowns_for > crowns_against:
                result = "win"
            elif crowns_for < crowns_against:
                result = "loss"
            else:
                result = "draw"

        # 2. Get Deck Cards and Key Card
        deck_cards = []
        if player_entry:
            # The 'cards' key is the standard location for the deck in a battlelog entry
            deck_cards = player_entry.get("cards") or player_entry.get("deck") or player_entry.get("cardsUsed") or [] 

        card_names = []
        for cd in deck_cards:
            if isinstance(cd, dict):
                # Official API uses 'name' for the card name
                name = cd.get("name")
            else:
                name = cd
            if name:
                card_names.append(normalize_name(name))
        
        deck_key_card = detect_deck_key_card(card_names)
        # --- End of Data Extraction Logic ---

        try:
            # Remove the 'Z' and add the standard UTC offset for python's datetime
            dt = datetime.fromisoformat(battle_time.replace("Z", "+00:00")) 
            weekday = dt.strftime("%A")
            hour = dt.hour
            tod = time_of_day_from_hour(hour)
        except Exception:
            weekday = None
            hour = None
            tod = None

        if result is None:
            print(f"Skipping battle at {battle_time} due to missing player/opponent data.")
            continue

        try:
            cur.execute("""
            INSERT INTO battles (battle_time, battle_timestamp, result, crowns_for, crowns_against, deck_key_card, weekday, hour, time_of_day)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (battle_time, battle_timestamp, result, crowns_for, crowns_against, deck_key_card, weekday, hour, tod))
            battle_row_id = cur.lastrowid
            inserted_battles += 1
        except sqlite3.IntegrityError:
            continue

        # Insert cards used in the battle (player side)
        for name in card_names:
            cur.execute("SELECT id FROM cards WHERE name = ? COLLATE NOCASE LIMIT 1", (name,))
            row = cur.fetchone()
            if row:
                card_id = row[0]
            else:
                # Fallback insert if card was missed during main card insert (e.g. new card)
                try:
                    cur.execute("INSERT INTO cards (api_card_id, name) VALUES (?, ?)", (None, name))
                    card_id = cur.lastrowid
                except sqlite3.IntegrityError:
                    cur.execute("SELECT id FROM cards WHERE name = ? COLLATE NOCASE LIMIT 1", (name,))
                    r2 = cur.fetchone()
                    card_id = r2[0] if r2 else None
            
            if card_id:
                try:
                    cur.execute("""
                    INSERT INTO battle_cards (battle_id, card_id, side)
                    VALUES (?, ?, ?)
                    """, (battle_row_id, card_id, "player"))
                except sqlite3.IntegrityError:
                    continue

    conn.commit()
    print(f"Inserted {inserted_battles} new battles (max per run: {limit_per_run})")
    return inserted_battles

def main_cards():
    conn = sqlite3.connect(DB_PATH)
    create_tables_if_needed(conn)
    try:
        cards = fetch_cards_from_api()
        insert_cards(conn, cards)
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching cards: {e}")
        print("Please ensure your API Key is set correctly in the environment variable $env:ROYALE_API_KEY and linked to your IP address on the developer portal.")
    conn.close()

def main_battles(player_tag: str, limit_per_run: int = MAX_ITEMS_PER_RUN, debug=False):
    conn = sqlite3.connect(DB_PATH)
    create_tables_if_needed(conn)
    try:
        battles = fetch_battlelog(player_tag)
        insert_battles_and_cards(conn, battles, limit_per_run=limit_per_run, debug=debug)
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching battle log: {e}")
        print("Please ensure your API Key is set correctly and linked to your IP address.")
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["cards", "battles"], required=True)
    parser.add_argument("--player_tag", help="Player tag for battlelog (include # or not)")
    parser.add_argument("--limit", type=int, default=MAX_ITEMS_PER_RUN)
    parser.add_argument("--debug", action="store_true", help="Print one sample battle JSON and exit")
    args = parser.parse_args()
    if args.mode == "cards":
        main_cards()
    elif args.mode == "battles":
        if not args.player_tag:
            print("Error: --player_tag is required for battles mode")
        else:
            main_battles(args.player_tag, limit_per_run=args.limit, debug=args.debug)