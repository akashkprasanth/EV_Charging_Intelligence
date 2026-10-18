import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="EV Demand Analysis",
    page_icon="📈",
    layout="wide"
)

st.title("📈 EV Charging Demand Analysis")
st.markdown("Analyze charging demand by hour, day, month, and station.")

# --------------------------------------------------
# LOAD DATA FROM CSV
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("ev_charging_cleaned.csv")

    column_mapping = {
        "_id": "record_id",
        "clusterID": "cluster_id",
        "connectionTime": "connection_time",
        "disconnectTime": "disconnect_time",
        "doneChargingTime": "done_charging_time",
        "kWhDelivered": "energy_kwh",
        "sessionID": "session_id",
        "siteID": "site_id",
        "spaceID": "space_id",
        "stationID": "station_id",
        "userID": "user_id",
        "userInputs": "user_inputs"
    }

    df = df.rename(columns=column_mapping)

    required_columns = [
        "session_id",
        "connection_time",
        "energy_kwh",
        "station_id"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Parse timestamps as UTC
    for column in [
        "connection_time",
        "disconnect_time",
        "done_charging_time"
    ]:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce",
                utc=True
            )

    df["energy_kwh"] = pd.to_numeric(
        df["energy_kwh"],
        errors="coerce"
    )

    # Convert connection time to Los Angeles local time
    df["connection_local"] = (
        df["connection_time"]
        .dt.tz_convert("America/Los_Angeles")
    )

    df["hour"] = df["connection_local"].dt.hour
    df["day_name"] = df["connection_local"].dt.day_name()
    df["day_number"] = df["connection_local"].dt.dayofweek
    df["month"] = df["connection_local"].dt.strftime("%Y-%m")
    df["date"] = df["connection_local"].dt.date

    return df


try:
    df = load_data()
except Exception as error:
    st.error(f"Unable to load the dataset: {error}")
    st.stop()


# --------------------------------------------------
# FILTERS
# --------------------------------------------------

st.sidebar.header("🔎 Demand Filters")

stations = sorted(
    df["station_id"].dropna().astype(str).unique().tolist()
)

selected_stations = st.sidebar.multiselect(
    "Select Charging Stations",
    options=stations,
    default=stations
)

filtered_df = df[
    df["station_id"].astype(str).isin(selected_stations)
].copy()

if filtered_df.empty:
    st.warning("No data available for the selected stations.")
    st.stop()


# --------------------------------------------------
# KEY PERFORMANCE INDICATORS
# --------------------------------------------------

total_sessions = len(filtered_df)

total_energy = filtered_df["energy_kwh"].sum()

average_energy = filtered_df["energy_kwh"].mean()

busiest_hour = (
    filtered_df["hour"].value_counts().idxmax()
    if filtered_df["hour"].notna().any()
    else None
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Charging Sessions",
    f"{total_sessions:,}"
)

col2.metric(
    "Total Energy Delivered",
    f"{total_energy:,.2f} kWh"
)

col3.metric(
    "Average Energy per Session",
    f"{average_energy:,.2f} kWh"
    if pd.notna(average_energy)
    else "N/A"
)

col4.metric(
    "Busiest Connection Hour",
    f"{int(busiest_hour):02d}:00"
    if busiest_hour is not None
    else "N/A"
)

st.divider()


# --------------------------------------------------
# HOURLY DEMAND
# --------------------------------------------------

st.subheader("⏰ Charging Demand by Hour")

hourly_demand = (
    filtered_df.groupby("hour", dropna=True)
    .size()
    .reindex(range(24), fill_value=0)
    .reset_index(name="sessions")
)

hourly_demand["hour"] = hourly_demand["hour"].astype(int)

fig_hourly = px.bar(
    hourly_demand,
    x="hour",
    y="sessions",
    title="Charging Sessions by Hour (Los Angeles Local Time)",
    labels={
        "hour": "Hour of Day",
        "sessions": "Number of Sessions"
    },
    text="sessions"
)

fig_hourly.update_layout(
    xaxis=dict(
        tickmode="linear",
        dtick=1
    )
)

st.plotly_chart(fig_hourly, use_container_width=True)


# --------------------------------------------------
# DAILY DEMAND
# --------------------------------------------------

st.subheader("📅 Charging Demand by Day of Week")

day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

daily_demand = (
    filtered_df.groupby("day_name", dropna=True)
    .size()
    .reindex(day_order, fill_value=0)
    .reset_index(name="sessions")
)

fig_daily = px.bar(
    daily_demand,
    x="day_name",
    y="sessions",
    title="Charging Sessions by Day of Week",
    labels={
        "day_name": "Day",
        "sessions": "Number of Sessions"
    },
    text="sessions"
)

st.plotly_chart(fig_daily, use_container_width=True)


# --------------------------------------------------
# WEEKDAY VS WEEKEND
# --------------------------------------------------

st.subheader("🗓️ Weekday vs Weekend Demand")

filtered_df["day_type"] = filtered_df["day_number"].apply(
    lambda day: "Weekend" if day >= 5 else "Weekday"
    if pd.notna(day)
    else "Unknown"
)

day_type_demand = (
    filtered_df.groupby("day_type")
    .size()
    .reset_index(name="sessions")
)

fig_day_type = px.pie(
    day_type_demand,
    names="day_type",
    values="sessions",
    title="Share of Charging Sessions"
)

st.plotly_chart(fig_day_type, use_container_width=True)


# --------------------------------------------------
# MONTHLY DEMAND
# --------------------------------------------------

st.subheader("📊 Monthly Charging Demand")

monthly_demand = (
    filtered_df.groupby("month", dropna=True)
    .size()
    .reset_index(name="sessions")
    .sort_values("month")
)

fig_monthly = px.bar(
    monthly_demand,
    x="month",
    y="sessions",
    title="Charging Sessions by Month",
    labels={
        "month": "Month",
        "sessions": "Number of Sessions"
    },
    text="sessions"
)

st.plotly_chart(fig_monthly, use_container_width=True)


# --------------------------------------------------
# ENERGY BY HOUR
# --------------------------------------------------

st.subheader("⚡ Energy Delivered by Hour")

hourly_energy = (
    filtered_df.groupby("hour", dropna=True)["energy_kwh"]
    .sum()
    .reindex(range(24), fill_value=0)
    .reset_index()
)

hourly_energy["hour"] = hourly_energy["hour"].astype(int)

fig_energy = px.line(
    hourly_energy,
    x="hour",
    y="energy_kwh",
    markers=True,
    title="Energy Delivered by Hour",
    labels={
        "hour": "Hour of Day",
        "energy_kwh": "Energy Delivered (kWh)"
    }
)

fig_energy.update_layout(
    xaxis=dict(
        tickmode="linear",
        dtick=1
    )
)

st.plotly_chart(fig_energy, use_container_width=True)


# --------------------------------------------------
# INSIGHTS
# --------------------------------------------------

st.subheader("💡 Demand Insights")

hour_counts = filtered_df["hour"].dropna().value_counts()
day_counts = filtered_df["day_name"].dropna().value_counts()
month_counts = filtered_df["month"].dropna().value_counts()

insight1, insight2, insight3 = st.columns(3)

with insight1:
    if not hour_counts.empty:
        busiest = int(hour_counts.idxmax())
        st.info(
            f"**Peak Hour**\n\n"
            f"{busiest:02d}:00 local time has the most "
            f"charging session starts."
        )

with insight2:
    if not day_counts.empty:
        busiest_day = day_counts.idxmax()
        st.info(
            f"**Busiest Day**\n\n"
            f"{busiest_day} has the most charging sessions."
        )

with insight3:
    if not month_counts.empty:
        busiest_month = month_counts.idxmax()
        st.info(
            f"**Busiest Month**\n\n"
            f"{busiest_month} has the most charging sessions."
        )


# --------------------------------------------------
# DATA TABLE AND DOWNLOAD
# --------------------------------------------------

with st.expander("🔍 View Demand Analysis Data"):
    display_columns = [
        column for column in [
            "session_id",
            "station_id",
            "connection_local",
            "hour",
            "day_name",
            "month",
            "energy_kwh"
        ]
        if column in filtered_df.columns
    ]

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True
    )

st.download_button(
    label="📥 Download Filtered Demand Data",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="ev_demand_analysis.csv",
    mime="text/csv"
)

st.caption(
    "Data source: EV Charging Sessions dataset | "
    "Connection times are displayed in Los Angeles local time."
)