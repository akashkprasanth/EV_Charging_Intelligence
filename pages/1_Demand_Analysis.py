import streamlit as st
import pandas as pd
import mysql.connector

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="EV Charging - Demand Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Charging Demand Analysis")
st.caption(
    "Understand charging patterns by hour, weekday, and month."
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
                energy_kwh,
                station_id
            FROM charging_sessions
            WHERE connection_time IS NOT NULL
        """

        df = pd.read_sql(query, connection)

    finally:
        connection.close()

    # Database timestamps were imported as UTC values
    # without timezone information. Convert UTC to local time.
    df["connection_time"] = (
        pd.to_datetime(df["connection_time"], utc=True)
        .dt.tz_convert("America/Los_Angeles")
    )

    df["energy_kwh"] = pd.to_numeric(
        df["energy_kwh"], errors="coerce"
    )

    # Extract demand dimensions using local time
    df["hour"] = df["connection_time"].dt.hour
    df["weekday_number"] = df["connection_time"].dt.dayofweek
    df["weekday"] = df["connection_time"].dt.day_name()
    df["month"] = df["connection_time"].dt.strftime("%Y-%m")

    df["day_type"] = df["weekday_number"].apply(
        lambda day: "Weekend" if day >= 5 else "Weekday"
    )

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

st.sidebar.header("Demand Filters")

stations = sorted(
    df["station_id"].dropna().unique().tolist()
)

selected_stations = st.sidebar.multiselect(
    "Select Charging Stations",
    options=stations,
    default=stations
)

filtered_df = df[
    df["station_id"].isin(selected_stations)
].copy()

if filtered_df.empty:
    st.warning("Please select at least one charging station.")
    st.stop()


# ==================================================
# KPI METRICS
# ==================================================

hourly_counts = (
    filtered_df.groupby("hour")
    .size()
    .reindex(range(24), fill_value=0)
)

busiest_hour = int(hourly_counts.idxmax())
busiest_hour_sessions = int(hourly_counts.max())

weekday_sessions = int(
    (filtered_df["day_type"] == "Weekday").sum()
)

weekend_sessions = int(
    (filtered_df["day_type"] == "Weekend").sum()
)

total_energy = filtered_df["energy_kwh"].sum()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric(
    "Total Sessions",
    f"{len(filtered_df):,}"
)

kpi2.metric(
    "Busiest Hour",
    f"{busiest_hour:02d}:00"
)

kpi3.metric(
    "Weekday Sessions",
    f"{weekday_sessions:,}"
)

kpi4.metric(
    "Energy Delivered",
    f"{total_energy:,.2f} kWh"
)

st.divider()


# ==================================================
# HOURLY DEMAND
# ==================================================

st.subheader("⏰ Charging Sessions by Hour")

st.caption(
    "Hours are shown in America/Los_Angeles local time."
)

st.bar_chart(
    hourly_counts,
    x_label="Hour of Day",
    y_label="Number of Sessions"
)


# ==================================================
# WEEKDAY VS WEEKEND
# ==================================================

st.subheader("📅 Weekday vs Weekend")

day_type_counts = (
    filtered_df["day_type"]
    .value_counts()
    .reindex(["Weekday", "Weekend"], fill_value=0)
)

col1, col2 = st.columns(2)

with col1:
    st.bar_chart(
        day_type_counts,
        x_label="Day Type",
        y_label="Number of Sessions"
    )

with col2:
    st.metric(
        "Weekend Share",
        f"{weekend_sessions / len(filtered_df) * 100:.1f}%"
    )

    st.metric(
        "Weekday Share",
        f"{weekday_sessions / len(filtered_df) * 100:.1f}%"
    )


# ==================================================
# DAILY DEMAND
# ==================================================

st.subheader("📆 Charging Sessions by Day of Week")

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

daily_demand = (
    filtered_df["weekday"]
    .value_counts()
    .reindex(weekday_order, fill_value=0)
)

st.bar_chart(
    daily_demand,
    x_label="Day of Week",
    y_label="Number of Sessions"
)


# ==================================================
# MONTHLY DEMAND
# ==================================================

st.subheader("📈 Monthly Charging Demand")

monthly_demand = (
    filtered_df.groupby("month")
    .agg(
        sessions=("session_id", "count"),
        energy_kwh=("energy_kwh", "sum")
    )
    .sort_index()
)

col1, col2 = st.columns(2)

with col1:
    st.write("Monthly Sessions")

    st.bar_chart(
        monthly_demand["sessions"],
        x_label="Month",
        y_label="Sessions"
    )

with col2:
    st.write("Monthly Energy Delivered")

    st.bar_chart(
        monthly_demand["energy_kwh"],
        x_label="Month",
        y_label="Energy (kWh)"
    )


# ==================================================
# ENERGY BY HOUR
# ==================================================

st.subheader("⚡ Energy Delivered by Hour")

hourly_energy = (
    filtered_df.groupby("hour")["energy_kwh"]
    .sum()
    .reindex(range(24), fill_value=0)
)

st.line_chart(
    hourly_energy,
    x_label="Hour of Day",
    y_label="Energy (kWh)"
)


# ==================================================
# BUSINESS INSIGHTS
# ==================================================

st.divider()

st.subheader("💡 Business Insights")

busiest_day = daily_demand.idxmax()
busiest_day_sessions = int(daily_demand.max())

quietest_hour = int(hourly_counts.idxmin())

st.success(
    f"The busiest connection-start hour is {busiest_hour:02d}:00, "
    f"with {busiest_hour_sessions:,} sessions."
)

st.info(
    f"{busiest_day} is the busiest day, with "
    f"{busiest_day_sessions:,} sessions."
)

st.write(
    f"**Quietest connection-start hour:** {quietest_hour:02d}:00."
)

st.write(
    f"**Weekday sessions:** {weekday_sessions:,}."
)

st.write(
    f"**Weekend sessions:** {weekend_sessions:,}."
)

st.warning(
    "The dataset covers January 1 through September 13, 2021. "
    "September is a partial month. Session starts measure demand "
    "by connection time, not simultaneous charger occupancy."
)

st.caption(
    "Data source: ev_charging_db | "
    "Technology: Python, Pandas, MySQL and Streamlit"
)