import json
import psycopg2
import requests
import time
from datetime import datetime

# Load config
with open("config/strava_config.json", "r") as f:
    config = json.load(f)

client_id = config["client_id"]
client_secret = config["client_secret"]
access_token = config["access_token"]
refresh_token = config["refresh_token"]
expires_at = config["expires_at"]

# Refresh token if expired
if time.time() > expires_at:
    print("🔄 Refreshing access token...")
    response = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    })

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens["access_token"]
        config["access_token"] = access_token
        config["refresh_token"] = tokens["refresh_token"]
        config["expires_at"] = tokens["expires_at"]
        with open("strava_config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("✅ Access token refreshed.")
    else:
        print("❌ Failed to refresh token:", response.text)
        exit()

# Get recent activities
headers = {"Authorization": f"Bearer {access_token}"}
params = {"per_page": 50}
response = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers, params=params)

if response.status_code != 200:
    print("❌ Error fetching activities:", response.text)
    exit()

activities = response.json()

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="0.0.0.0",
    port=3000,
    dbname="life_logger",
    user="postgres",
    password="password"
)
cursor = conn.cursor()

# Insert new activities
new_count = 0
for activity in activities:
    activity_id = activity["id"]
    name = activity.get("name", "")
    type_ = activity.get("type", "")
    start = activity.get("start_date", "")
    duration = round(activity.get("elapsed_time", 0) / 60, 2)  # seconds to minutes
    distance = round(activity.get("distance", 0) / 1000, 2)     # meters to km
    calories = activity.get("calories", None)

    # Skip if ID already exists
    cursor.execute("SELECT 1 FROM strava_workouts WHERE id = %s", (activity_id,))
    if cursor.fetchone():
        continue

    cursor.execute("""
        INSERT INTO strava_workouts (id, name, type, start_date, duration, distance, calories, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'Strava')
    """, (activity_id, name, type_, start, duration, distance, calories))
    new_count += 1

conn.commit()
conn.close()
print(f"✅ Logged {new_count} new Strava workouts.")
