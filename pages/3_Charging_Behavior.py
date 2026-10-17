import streamlit as st
import pandas as pd
import mysql.connector

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Charging Behavior & Anomalies",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Charging Behavior & Anomaly Analysis")

st.caption(
    "Investigate long connection times, high-energy sessions, "
    "and unusual charging behavior."
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
                done_charging_time,
                energy_kwh,
                station_id
            FROM charging_sessions
        """

        df = pd.read_sql(query, connection)

    finally:
        connection.close()

    # Imported database timestamps represent UTC.
    df["connection_time"] = pd.to_datetime(
        df["connection_time"], utc=True, errors="coerce"
    )

    df["disconnect_time"] = pd.to_datetime(
        df["disconnect_time"], utc=True, errors="coerce"
    )

    df["done_charging_time"] = pd.to_datetime(
        df["done_charging_time"], utc=True, errors="coerce"
    )

    df["energy_kwh"] = pd.to_numeric(
        df["energy_kwh"], errors="coerce"
    )

    # Calculate connection duration in hours.
    df["connection_duration_hours"] = (
        df["disconnect_time"] - df["connection_time"]
    ).dt.total_seconds() / 3600

    # Actual charging duration where a completion timestamp exists.
    df["charging_duration_hours"] = (
        df["done_charging_time"] - df["connection_time"]
    ).dt.total_seconds() / 3600

    return df


try:
    df = load_data()

except Exception as error:
    st.error("Unable to load charging data from MySQL.")
    st.code(str(error))
    st.stop()


# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("Analysis Filters")

stations = sorted(
    df["station_id"].dropna().unique().tolist()
)

selected_stations = st.sidebar.multiselect(
    "Select Charging Stations",
    options=stations,
    default=stations
)

duration_threshold = st.sidebar.slider(
    "Long connection threshold (hours)",
    min_value=1,
    max_value=24,
    value=4
)

filtered_df = df[
    df["station_id"].isin(selected_stations)
].copy()

if filtered_df.empty:
    st.warning("Select at least one charging station.")
    st.stop()


# ==================================================
# DEFINE HIGH-ENERGY OUTLIERS
# ==================================================

valid_energy = filtered_df["energy_kwh"].dropna()

if len(valid_energy) >= 4:

    q1 = valid_energy.quantile(0.25)
    q3 = valid_energy.quantile(0.75)
    iqr = q3 - q1

    high_energy_threshold = q3 + (1.5 * iqr)

else:

    q1 = 0
    q3 = 0
    iqr = 0
    high_energy_threshold = float("inf")


filtered_df["high_energy_outlier"] = (
    filtered_df["energy_kwh"] > high_energy_threshold
)

filtered_df["long_connection"] = (
    filtered_df["connection_duration_hours"]
    > duration_threshold
)

filtered_df["long_connection_low_energy"] = (
    filtered_df["long_connection"]
    & (filtered_df["energy_kwh"] < 10)
)


# ==================================================
# KPI SUMMARY
# ==================================================

st.subheader("📊 Behavior Overview")

total_sessions = len(filtered_df)

long_connections = int(
    filtered_df["long_connection"].sum()
)

high_energy_sessions = int(
    filtered_df["high_energy_outlier"].sum()
)

long_low_energy_sessions = int(
    filtered_df["long_connection_low_energy"].sum()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Sessions",
    f"{total_sessions:,}"
)

col2.metric(
    "Long Connections",
    f"{long_connections:,}"
)

col3.metric(
    "High-Energy Outliers",
    f"{high_energy_sessions:,}"
)

col4.metric(
    "Long + Low Energy",
    f"{long_low_energy_sessions:,}"
)

st.divider()


# ==================================================
# EXPLAIN THE RULES
# ==================================================

st.subheader("📖 How Are Unusual Sessions Identified?")

rule1, rule2 = st.columns(2)

with rule1:

    st.markdown("**Long connection**")

    st.write(
        f"A session is flagged when its connection duration exceeds "
        f"{duration_threshold} hours."
    )

with rule2:

    st.markdown("**High-energy outlier**")

    st.write(
        "A session is flagged when its energy exceeds the statistical "
        "upper boundary calculated as Q3 + 1.5 × IQR."
    )

st.info(
    "These are investigation flags, not proof of a fault, fraud, "
    "or abnormal vehicle behavior."
)


# ==================================================
# CONNECTION DURATION DISTRIBUTION
# ==================================================

st.subheader("⏱️ Connection Duration Distribution")

duration_data = filtered_df[
    filtered_df["connection_duration_hours"].notna()
    & (filtered_df["connection_duration_hours"] >= 0)
]

if not duration_data.empty:

    st.bar_chart(
        duration_data["connection_duration_hours"]
        .clip(upper=24)
        .value_counts()
        .sort_index(),
        x_label="Connection Duration (hours, capped at 24)",
        y_label="Number of Sessions"
    )

    st.caption(
        "Durations above 24 hours are capped at 24 for this chart "
        "to make the more common durations easier to inspect."
    )

else:

    st.info("No valid connection durations are available.")


# ==================================================
# ENERGY DISTRIBUTION
# ==================================================

st.divider()

st.subheader("⚡ Energy Delivered per Session")

if not valid_energy.empty:

    st.write(
        f"**Q1:** {q1:.2f} kWh"
    )

    st.write(
        f"**Median:** {valid_energy.median():.2f} kWh"
    )

    st.write(
        f"**Q3:** {q3:.2f} kWh"
    )

    st.write(
        f"**High-energy investigation threshold:** "
        f"{high_energy_threshold:.2f} kWh"
    )

    st.bar_chart(
        filtered_df["energy_kwh"].dropna().clip(upper=40)
        .value_counts()
        .sort_index(),
        x_label="Energy Delivered (kWh, capped at 40)",
        y_label="Number of Sessions"
    )

    st.caption(
        "Energy values above 40 kWh are capped in this chart only. "
        "The underlying records remain unchanged."
    )


# ==================================================
# LONG CONNECTIONS
# ==================================================

st.divider()

st.subheader("🚩 Long Connection Sessions")

long_sessions = (
    filtered_df[
        filtered_df["long_connection"]
    ]
    .sort_values(
        "connection_duration_hours",
        ascending=False
    )
)

st.write(
    f"Found **{len(long_sessions):,}** sessions exceeding "
    f"{duration_threshold} hours with a valid connection duration."
)

if not long_sessions.empty:

    st.dataframe(
        long_sessions[
            [
                "session_id",
                "station_id",
                "connection_time",
                "disconnect_time",
                "connection_duration_hours",
                "energy_kwh"
            ]
        ].round(2),
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# LONG CONNECTIONS WITH LOW ENERGY
# ==================================================

st.divider()

st.subheader("🔎 Long Connections with Less Than 10 kWh")

low_energy_long = (
    filtered_df[
        filtered_df["long_connection_low_energy"]
    ]
    .sort_values(
        "connection_duration_hours",
        ascending=False
    )
)

st.write(
    f"Found **{len(low_energy_long):,}** sessions matching both conditions."
)

if not low_energy_long.empty:

    st.dataframe(
        low_energy_long[
            [
                "session_id",
                "station_id",
                "connection_duration_hours",
                "energy_kwh",
                "done_charging_time"
            ]
        ].round(2),
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "Possible explanations include a vehicle remaining connected "
        "after charging stopped, an interrupted charging session, "
        "or incomplete records. The dataset alone cannot establish "
        "which explanation applies."
    )

else:

    st.success("No sessions match both selected conditions.")


# ==================================================
# STATION ANOMALY SUMMARY
# ==================================================

st.divider()

st.subheader("🏢 Station Investigation Summary")

station_summary = (
    filtered_df.groupby("station_id")
    .agg(
        total_sessions=("session_id", "count"),
        long_connections=("long_connection", "sum"),
        high_energy_outliers=("high_energy_outlier", "sum"),
        average_energy_kwh=("energy_kwh", "mean")
    )
    .reset_index()
)

station_summary["long_connection_rate_percent"] = (
    station_summary["long_connections"]
    / station_summary["total_sessions"] * 100
)

station_summary["high_energy_rate_percent"] = (
    station_summary["high_energy_outliers"]
    / station_summary["total_sessions"] * 100
)

station_summary = station_summary.sort_values(
    "long_connections",
    ascending=False
)

st.dataframe(
    station_summary.round(2),
    use_container_width=True,
    hide_index=True
)


# ==================================================
# EXPORT RESULTS
# ==================================================

st.divider()

st.subheader("📥 Download Analysis Results")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Analyzed Sessions (CSV)",
    data=csv_data,
    file_name="ev_charging_behavior_analysis.csv",
    mime="text/csv"
)


# ==================================================
# BUSINESS RECOMMENDATIONS
# ==================================================

st.divider()

st.subheader("💡 Operational Recommendations")

st.markdown("""
1. **Investigate long connections:** Determine whether extended connection
   times are caused by customer behavior, charging interruptions, or
   operational constraints.

2. **Review high-energy sessions:** Compare flagged sessions with vehicle
   capacity, station characteristics, and available operational records.

3. **Compare stations fairly:** Consider session counts and sample sizes
   before interpreting station-level rates.

4. **Improve data quality:** Investigate missing charging completion
   timestamps before drawing conclusions about actual charging duration.

5. **Avoid premature conclusions:** Statistical outliers are candidates
   for investigation, not confirmed equipment failures or misconduct.
""")

st.caption(
    "EV Charging Intelligence | Charging Behavior & Anomaly Analysis"
)