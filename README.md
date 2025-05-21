# Life Logger

**Life Logger** is a personal automation project that collects, logs, and visualizes your daily activity from multiple sources — all stored in a PostgreSQL database and rendered via a custom Streamlit dashboard.

---

## 🧠 What It Tracks

- 🎬 **Trakt.tv** — watched TV and movies  
- 🎮 **RetroAchievements** — emulated retro game sessions  
- 🚴‍♂️ **Strava** — logged workouts  
- 📺 **YouTube** — watch history and channel info  
- 📚 **Books** — currently tracking books read  
- 🕹 **Steam** — in progress (not yet timestamp-accurate)  

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
    ```

2. Install dependencies (for local testing):

    ```bash
    pip install -r requirements.txt
    ```

3. Copy and configure your API credentials:

    ```bash
    cp config/retro_config.example.json config/retro_config.json
    cp config/strava_config.example.json config/strava_config.json
    ```

    Fill in the real values from your API dashboards.

4. Build and run in Docker (optional):

    ```bash
    docker build -t life_logger .
    docker run -p 8501:8501 -v $PWD:/app life_logger
    ```

5. Open the dashboard:

    Visit [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

## 🏷 GitHub Topics

life-logger
strava
trakt
streamlit
personal-dashboard
postgresql
retroachievements
youtube-api
tmdb
docker


