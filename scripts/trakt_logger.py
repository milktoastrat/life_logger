import requests
import json
import psycopg2
from datetime import datetime

# Load Trakt + TMDB config
with open("config/trakt_config.json", "r") as f:
    config = json.load(f)

client_id = config["client_id"]
access_token = config["access_token"]
tmdb_api_key = config["tmdb_api_key"]

def get_tmdb_poster(title, media_type):
    search_type = "tv" if media_type == "TV" else "movie"
    url = f"https://api.themoviedb.org/3/search/{search_type}"
    params = {"api_key": tmdb_api_key, "query": title}
    response = requests.get(url, params=params)
    if response.status_code == 200 and response.json()["results"]:
        poster_path = response.json()["results"][0].get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w342{poster_path}"
    return None

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="0.0.0.0",
    port=3000,
    dbname="life_logger",
    user="postgres",
    password="password"
)
cursor = conn.cursor()

# Get most recent watched_at timestamp
cursor.execute("SELECT watched_at FROM trakt_history ORDER BY watched_at DESC LIMIT 1")
row = cursor.fetchone()
start_at = row[0].isoformat() if row and row[0] else "2000-01-01T00:00:00Z"

# Fetch recent Trakt history
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "trakt-api-version": "2",
    "trakt-api-key": client_id
}
params = {"start_at": start_at, "limit": 50}
response = requests.get("https://api.trakt.tv/sync/history", headers=headers, params=params)

if response.status_code != 200:
    print(f"Error: {response.status_code} - {response.text}")
    exit()

history = response.json()
new_count = 0

for item in history:
    history_id = item.get("id")
    watched_at = item.get("watched_at")
    media_type_raw = item.get("type")

    title = ""
    season = None
    episode = None
    media_type_clean = "Other"
    poster_url = None

    if media_type_raw == "episode":
        show = item["show"]["title"]
        episode_info = item["episode"]
        title = f"{show} - S{episode_info['season']:02d}E{episode_info['number']:02d}"
        season = episode_info["season"]
        episode = episode_info["number"]
        media_type_clean = "TV"
        poster_url = get_tmdb_poster(show, "TV")
    elif media_type_raw == "movie":
        title = item["movie"]["title"]
        media_type_clean = "Movie"
        poster_url = get_tmdb_poster(title, "Movie")

    # Check if already exists
    cursor.execute("SELECT 1 FROM trakt_history WHERE id = %s", (history_id,))
    if cursor.fetchone():
        continue

    cursor.execute("""
        INSERT INTO trakt_history (id, watched_at, type, title, season, episode, poster_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (history_id, watched_at, media_type_clean, title, season, episode, poster_url))
    new_count += 1

conn.commit()
conn.close()

print(f"✅ Logged {new_count} new Trakt items with poster images.")
