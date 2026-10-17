import streamlit as st
import pandas as pd
import mysql.connector

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Station Performance",
    page_icon="🔌",
    layout="wide"
)

st.title("🔌 Charging Station Performance")
st.caption(
    "Compare station utilization, energy delivery, and charging behavior."
)

# ==================================================
# LOAD DATA FROM MYSQL
# ==================================================

@st.cache_data(ttl=60)
def load_data():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=st.secrets["mysql"]["password"],
        database="ev_charging_db"
    )

    try:
        query = """
            SELECT
                session_id,
                connection_time,
                disconnect_time,
                energy_kwh,
                station_id
            FROM charging_sessions
        """

        df = pd.read_sql(query, connection)

    finally:
        connection.close()

    df["connection_time"] = pd.to_datetime(
        df["connection_time"],
        errors="coerce"
    )

    df["disconnect_time"] = pd.to_datetime(
        df["disconnect_time"],
        errors="coerce"
    )

    df["energy_kwh"] = pd.to_numeric(
        df["energy_kwh"],
        errors="coerce"
    )

    # Connection duration in minutes
    df["connection_duration_minutes"] = (
        df["disconnect_time"] - df["connection_time"]
    ).dt.total_seconds() / 60

    return df


try:
    df = load_data()

except Exception as error:
    st.error("Unable to load station data from MySQL.")
    st.code(str(error))
    st.stop()


# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("Station Filters")

stations = sorted(
    df["station_id"].dropna().unique().tolist()
)

selected_stations = st.sidebar.multiselect(
    "Select Stations",
    options=stations,
    default=stations
)

filtered_df = df[
    df["station_id"].isin(selected_stations)
].copy()

if filtered_df.empty:
    st.warning("Please select at least one station.")
    st.stop()


# ==================================================
# STATION PERFORMANCE TABLE
# ==================================================

station_summary = (
    filtered_df.groupby("station_id")
    .agg(
        total_sessions=("session_id", "count"),
        total_energy_kwh=("energy_kwh", "sum"),
        average_energy_kwh=("energy_kwh", "mean"),
        average_connection_minutes=(
            "connection_duration_minutes", "mean"
        ),
        maximum_energy_kwh=("energy_kwh", "max")
    )
    .reset_index()
)

# Calculate energy contribution within selected stations
total_energy = station_summary["total_energy_kwh"].sum()

if total_energy > 0:
    station_summary["energy_share_percent"] = (
        station_summary["total_energy_kwh"]
        / total_energy * 100
    )
else:
    station_summary["energy_share_percent"] = 0

station_summary = station_summary.sort_values(
    "total_energy_kwh",
    ascending=False
)


# ==================================================
# KPI METRICS
# ==================================================

st.subheader("📊 Performance Overview")

top_station = station_summary.iloc[0]

total_sessions = len(filtered_df)
total_stations = filtered_df["station_id"].nunique()

average_energy = filtered_df["energy_kwh"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Charging Stations",
    f"{total_stations:,}"
)

col2.metric(
    "Total Sessions",
    f"{total_sessions:,}"
)

col3.metric(
    "Total Energy Delivered",
    f"{total_energy:,.2f} kWh"
)

col4.metric(
    "Average Energy / Session",
    f"{average_energy:.2f} kWh"
    if pd.notna(average_energy) else "N/A"
)

st.divider()


# ==================================================
# TOP STATIONS BY ENERGY
# ==================================================

st.subheader("🏆 Top 10 Stations by Energy")

top_energy = station_summary.head(10)

chart_col, table_col = st.columns([1, 1.3])

with chart_col:
    st.bar_chart(
        top_energy.set_index("station_id")["total_energy_kwh"],
        x_label="Station",
        y_label="Energy (kWh)"
    )

with table_col:
    st.dataframe(
        top_energy[
            [
                "station_id",
                "total_sessions",
                "total_energy_kwh",
                "average_energy_kwh",
                "energy_share_percent"
            ]
        ].round(2),
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# TOP STATIONS BY SESSION COUNT
# ==================================================

st.divider()

st.subheader("🔌 Top 10 Stations by Charging Sessions")

top_sessions = (
    station_summary
    .sort_values("total_sessions", ascending=False)
    .head(10)
)

st.bar_chart(
    top_sessions.set_index("station_id")["total_sessions"],
    x_label="Station",
    y_label="Number of Sessions"
)


# ==================================================
# AVERAGE ENERGY COMPARISON
# ==================================================

st.divider()

st.subheader("⚡ Average Energy Delivered per Session")

top_average = (
    station_summary[
        station_summary["total_sessions"] >= 10
    ]
    .sort_values("average_energy_kwh", ascending=False)
    .head(10)
)

st.caption(
    "Only stations with at least 10 recorded sessions are included "
    "to reduce the influence of stations with very small samples."
)

if not top_average.empty:
    st.bar_chart(
        top_average.set_index("station_id")["average_energy_kwh"],
        x_label="Station",
        y_label="Average Energy (kWh)"
    )


# ==================================================
# CONNECTION DURATION ANALYSIS
# ==================================================

st.divider()

st.subheader("⏱️ Average Connection Duration by Station")

duration_summary = (
    station_summary[
        station_summary["total_sessions"] >= 10
    ]
    .sort_values("average_connection_minutes", ascending=False)
    .head(10)
)

duration_summary["average_connection_hours"] = (
    duration_summary["average_connection_minutes"] / 60
)

st.dataframe(
    duration_summary[
        [
            "station_id",
            "total_sessions",
            "average_connection_hours"
        ]
    ].round(2),
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Connection duration is the time between connecting and disconnecting "
    "a vehicle. It is not necessarily the same as actual charging time."
)


# ==================================================
# BUSINESS INSIGHTS
# ==================================================

st.divider()

st.subheader("💡 Business Insights")

st.write(
    f"**Highest total energy:** Station `{top_station['station_id']}` "
    f"delivered {top_station['total_energy_kwh']:,.2f} kWh."
)

st.write(
    f"**Energy contribution:** This station accounts for "
    f"{top_station['energy_share_percent']:.2f}% of the energy "
    "delivered by the currently selected stations."
)

if len(station_summary) > 1:

    lowest_station = station_summary.sort_values(
        "total_energy_kwh"
    ).iloc[0]

    st.write(
        f"**Lowest total energy among selected stations:** "
        f"`{lowest_station['station_id']}` delivered "
        f"{lowest_station['total_energy_kwh']:,.2f} kWh."
    )

st.info(
    "Business recommendation: Compare energy delivered, session counts, "
    "and connection durations together before deciding whether a station "
    "is performing well. Low energy may reflect low demand rather than "
    "poor station performance."
)


# ==================================================
# COMPLETE STATION TABLE
# ==================================================

with st.expander("📋 View All Station Performance Results"):

    st.dataframe(
        station_summary.round(2),
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "EV Charging Intelligence | Station Performance Analytics"
)