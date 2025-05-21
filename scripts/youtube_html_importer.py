import os
import psycopg2
from bs4 import BeautifulSoup
from datetime import datetime
import re

html_path = "/app/data/watch-history.html"

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="0.0.0.0",
    port=3000,
    dbname="life_logger",
    user="postgres",
    password="password"
)
conn.autocommit = False
cursor = conn.cursor()

new_count = 0

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    content_divs = soup.find_all("div", class_="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")
    content_divs = content_divs[:50]  # ⬅️ Only process the first 50 entries for testing

    for div in content_divs:
        try:
            if not div.text.strip().startswith("Watched"):
                continue

            video_links = div.find_all("a")
            if len(video_links) < 2:
                continue

            video_tag = video_links[0]
            title = video_tag.text.strip()
            url = video_tag["href"]
            video_id_match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
            video_id = video_id_match.group(1) if video_id_match else None

            if not video_id:
                continue

            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

            channel_tag = video_links[1]
            channel = channel_tag.text.strip()

            lines = div.get_text(separator="|").split("|")
            raw_time = lines[-1].strip()
            watched_at = datetime.strptime(raw_time, "%d %b %Y, %H:%M:%S GMT%z").isoformat()

            full_title = f"{title} ({channel})"

            try:
                cursor.execute("""
                    INSERT INTO youtube_history (title, channel, url, watched_at, thumbnail, source)
                    VALUES (%s, %s, %s, %s, %s, 'YouTube')
                    ON CONFLICT DO NOTHING;
                """, (full_title, channel, url, watched_at, thumbnail_url))
                conn.commit()
                if cursor.rowcount > 0:
                    new_count += 1
            except Exception as insert_error:
                conn.rollback()
                print(f"⚠️ Insert failed: {insert_error}")

        except Exception as e:
            print(f"⚠️ Skipped entry due to error: {e}")

    print(f"✅ Imported {new_count} new YouTube entries.")
else:
    print(f"❌ File not found: {html_path}")

conn.close()
