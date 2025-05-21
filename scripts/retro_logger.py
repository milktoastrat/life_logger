import requests
import json
import psycopg2
from datetime import datetime, timezone

# Load credentials
with open("config/retro_config.json", "r") as f:
    config = json.load(f)

USERNAME = config["username"]
API_KEY = config["api_key"]

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="10.0.0.0",  # or 10.0.0.187 if that’s more stable
    port=3000,
    dbname="life_logger",
    user="postgres",
    password="password"
)
cursor = conn.cursor()

# ---------------------------------------------
# Step 1: Log new RetroAchievements game sessions
# ---------------------------------------------

url = f"https://retroachievements.org/API/API_GetUserRecentlyPlayedGames.php?z={USERNAME}&y={API_KEY}&u={USERNAME}"
response = requests.get(url)

if response.status_code != 200:
    print(f"❌ API Error: {response.status_code}")
    conn.close()
    exit()

games = response.json()

# Get the most recent logged timestamp
cursor.execute("SELECT MAX(last_played) FROM retro_sessions WHERE username = %s", (USERNAME,))
row = cursor.fetchone()
latest_logged = row[0].isoformat() if row and row[0] else "2000-01-01T00:00:00Z"
latest_logged_dt = datetime.fromisoformat(latest_logged.replace("Z", "+00:00")).astimezone(timezone.utc)

new_count = 0

for game in games:
    game_title = game["Title"]
    console = game["ConsoleName"]
    last_played = game["LastPlayed"]
    game_id = game["GameID"]

    try:
        dt = datetime.strptime(last_played, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        print(f"⚠️ Skipping invalid date: {last_played}")
        continue

    if dt <= latest_logged_dt:
        continue

    iso_timestamp = dt.isoformat()

    cursor.execute('''
        INSERT INTO retro_sessions (username, game_title, console_name, last_played, source, game_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (USERNAME, game_title, console, iso_timestamp, 'RetroAchievements', game_id))

    new_count += 1

conn.commit()
print(f"✅ Logged {new_count} new game sessions from RetroAchievements.")

# ---------------------------------------------
# Step 2: Backfill missing thumbnails
# ---------------------------------------------

cursor.execute("""
    SELECT DISTINCT game_title, game_id
    FROM retro_sessions
    WHERE thumbnail IS NULL AND game_id IS NOT NULL
""")
games = cursor.fetchall()

updated = 0

for game_title, game_id in games:
    try:
        info_url = f"https://retroachievements.org/API/API_GetGame.php?z={USERNAME}&y={API_KEY}&i={game_id}"
        info_resp = requests.get(info_url)

        if info_resp.status_code == 200:
            game_data = info_resp.json()
            image_path = game_data.get("ImageIcon")

            if image_path:
                thumbnail_url = f"https://retroachievements.org{image_path}"

                cursor.execute("""
                    UPDATE retro_sessions
                    SET thumbnail = %s
                    WHERE game_id = %s
                """, (thumbnail_url, game_id))
                updated += cursor.rowcount
                conn.commit()
                print(f"🖼️ Added thumbnail for: {game_title}")
            else:
                print(f"⚠️ No image path for: {game_title}")
        else:
            print(f"❌ Failed to fetch game info for {game_title} (GameID {game_id})")

    except Exception as e:
        conn.rollback()
        print(f"⚠️ Error updating {game_title}: {e}")

conn.close()
print(f"🎉 Finished: {new_count} new sessions logged, {updated} thumbnails updated.")
