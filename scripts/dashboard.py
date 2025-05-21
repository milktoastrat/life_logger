import streamlit as st
import psycopg2
import pandas as pd
from pytz import timezone

st.set_page_config(
    page_title="Life Logger",
    page_icon="assets/favicon.png",
    layout="wide"
)

# Timezone setup
utc = timezone('UTC')

# Source icon map
def get_source_icon(source):
    return {
        "YouTube": "▶️",
        "Trakt": "📺",
        "RetroAchievements": "🎮",
        "Strava": "🏋️",
        "GoodReads": "📖"
    }.get(source, "🗂️")

# Load data
@st.cache_data(ttl=300)
def load_data():
    conn = psycopg2.connect(
        host="0.0.0.0",
        port=3000,
        dbname="life_logger",
        user="postgres",
        password="password"
    )
    df = pd.read_sql("SELECT * FROM unified_timeline ORDER BY timestamp DESC", conn)
    conn.close()
    return df

df = load_data()
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
df["timestamp"] = df["timestamp"].dt.tz_convert(UTC)
df = df.sort_values("timestamp", ascending=False)
df["date"] = df["timestamp"].dt.date

# ========== SIDEBAR ========== #
with st.sidebar:
    st.markdown("""
    <h1 style='font-size: 2.4rem; font-weight: 300; margin-bottom: 0.5rem;'>📅 Life Logger</h1>
    """, unsafe_allow_html=True)

    # Nav links
    st.markdown("""
    <div style='margin-top: -10px;'>
        <a href="#timeline" style="display: block; margin: 8px 0; text-decoration: none; font-weight: 500;">🕒 Timeline</a>
        <a href="#stats" style="display: block; margin: 8px 0; text-decoration: none; font-weight: 500;">📈 Stats</a>
        <a href="#settings" style="display: block; margin: 8px 0; text-decoration: none; font-weight: 500;">⚙️ Settings</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔍 Filters")

    # Exclude sources
    all_sources = df["source"].unique().tolist()
    excluded_sources = st.multiselect("Hide sources", all_sources, default=[])

    # Date range
    st.markdown("**Date Range**")
    min_date = df["timestamp"].min().date()
    max_date = df["timestamp"].max().date()
    start_date, end_date = st.date_input("Filter by date", [min_date, max_date], min_value=min_date, max_value=max_date)

    # Max entries
    max_rows = st.slider("Max entries to show", min_value=50, max_value=1000, value=250, step=50)

    # Optional thumbnail toggle
    show_thumbs = st.checkbox("Show thumbnails", value=True)

    st.markdown("---")
    st.subheader("📊 Quick Stats")

    # Source counts
    for source, count in df["source"].value_counts().items():
        st.markdown(f"{get_source_icon(source)} **{source}**: {count}")

    # Most active hour
    active_hour = df["timestamp"].dt.hour.value_counts().idxmax()
    st.markdown(f"🕒 Most active hour: **{active_hour}:00**")

    st.markdown("---")
    st.subheader("💾 Quick Export")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", data=csv, file_name="life_logger.csv", mime="text/csv")

# Apply filters
filtered_df = df[
    (~df["source"].isin(excluded_sources)) &
    (df["timestamp"].dt.date >= start_date) &
    (df["timestamp"].dt.date <= end_date)
].head(max_rows)

# ========== TIMELINE ========== #
st.markdown('<a name="timeline"></a>', unsafe_allow_html=True)
st.header("🕒 Timeline")

for date, group in filtered_df.groupby("date", sort=False):
    display_date = group.iloc[0]["timestamp"].strftime("%A, %B %d %Y")
    st.subheader(f"{display_date}")

    for _, row in group.iterrows():
        with st.container():
            if show_thumbs and row.get("thumbnail"):
                if row["source"] == "YouTube":
                    image_html = (
                        f'<img src="{row["thumbnail"]}" '
                        f'style="height:72px; width:128px; border-radius:8px; margin-right:16px; object-fit:cover;" />'
                    )
                else:
                    image_html = (
                        f'<img src="{row["thumbnail"]}" width="120" '
                        f'style="border-radius:8px; margin-right:16px;" />'
                    )
            else:
                image_html = ""

            icon = get_source_icon(row["source"])
            title_html = f'{icon} <b>{row["title"]}</b>'
            if row.get("url"):
                title_html = f'{icon} <a href="{row["url"]}" target="_blank"><b>{row["title"]}</b></a>'

            local_time = row["timestamp"]
            html_block = (
                '<div style="display:flex; align-items:center; margin-bottom:20px;">'
                f'{image_html}'
                '<div style="line-height: 1.4;">'
                f'<div style="font-size:1.05em;">{title_html}</div>'
                f'<div style="color:gray; font-style:italic;">{row["source"]} • {local_time.strftime("%I:%M %p")}</div>'
                '</div>'
                '</div>'
            )

            st.markdown(html_block, unsafe_allow_html=True)

st.success(f"Grouped and displayed {len(filtered_df)} entries.")

# ========== STATS ========== #
st.markdown('<a name="stats"></a>', unsafe_allow_html=True)
st.header("📈 Stats")

source_counts = df["source"].value_counts()
most_active_day = df["date"].value_counts().idxmax()
most_active_count = df["date"].value_counts().max()

st.markdown(f"""
- **Total entries:** {len(df):,}  
- **Most active day:** {most_active_day.strftime('%A, %B %d, %Y')} ({most_active_count} entries)  
- **Most frequent source:** {source_counts.idxmax()} ({source_counts.max()} entries)
""")

st.subheader("Entries per Source")
st.bar_chart(source_counts)

st.subheader("Daily Activity (Last 30 Days)")
daily_counts = df["date"].value_counts().sort_index().tail(30)
st.line_chart(daily_counts)

# ========== SETTINGS ========== #
st.markdown('<a name="settings"></a>', unsafe_allow_html=True)
st.header("⚙️ Settings")

with st.expander("Customize Display Options"):
    st.markdown("Change how data is displayed in your timeline view.")

    default_limit = st.number_input(
        "Default number of timeline entries to show",
        min_value=50, max_value=1000, value=max_rows, step=50
    )

    selected_defaults = st.multiselect("Default sources", all_sources, default=all_sources)

    st.markdown("**These settings are temporary and will reset on page reload.**")

with st.expander("Export Options"):
    st.markdown("Download a CSV export of your timeline data.")
    export_df = df.copy()
    csv = export_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", data=csv, file_name="life_logger_timeline.csv", mime="text/csv")
