# Life Logger

**Life Logger** is a personal automation project that collects, logs, and visualizes your daily activity from multiple sources — all stored in a PostgreSQL database and rendered via a custom Streamlit dashboard.

### 🧠 What It Tracks
- 🎬 **Trakt.tv** — watched TV and movies
- 🎮 **RetroAchievements** — emulated retro game sessions
- 🚴‍♂️ **Strava** — logged workouts
- 📺 **YouTube** — watch history and channel info
- 📚 **Books** — currently tracking books read

---

## 🚀 Features

- Unified timeline with images, thumbnails, and metadata
- Auto-refreshing OAuth token handling (Strava)
- TMDB and YouTube thumbnail integration
- Filtered YouTube logging (e.g., 2+ minute videos only)
- Dockerized for portability and hands-off automation
- Full PostgreSQL backend
- Streamlit dashboard frontend

---

## 🛠 Setup

1. Clone the repo:

```bash
git clone https://github.com/milktoastrat/life_logger.git
cd life_logger
