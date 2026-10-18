import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Station Performance",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 EV Charging Station Performance")
st.markdown(
    "Compare charging stations by session volume, "
    "energy delivery, and charging efficiency."
)


# --------------------------------------------------
# LOAD DATA
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

    required = [
        "session_id",
        "station_id",
        "connection_time",
        "disconnect_time",
        "energy_kwh"
    ]

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    for col in [
        "connection_time",
        "disconnect_time",
        "done_charging_time"
    ]:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                errors="coerce",
                utc=True
            )

    df["energy_kwh"] = pd.to_numeric(
        df["energy_kwh"],
        errors="coerce"
    )

    # Calculate how long the vehicle remained connected.
    df["connection_duration_hours"] = (
        df["disconnect_time"] - df["connection_time"]
    ).dt.total_seconds() / 3600

    # Calculate actual charging duration when available.
    df["charging_duration_hours"] = (
        df["done_charging_time"] - df["connection_time"]
    ).dt.total_seconds() / 3600

    # Ignore negative or invalid duration values.
    df.loc[
        df["connection_duration_hours"] < 0,
        "connection_duration_hours"
    ] = float("nan")

    df.loc[
        df["charging_duration_hours"] < 0,
        "charging_duration_hours"
    ] = float("nan")

    return df


try:
    df = load_data()
except Exception as error:
    st.error(f"Unable to load station data: {error}")
    st.stop()


# --------------------------------------------------
# FILTERS
# --------------------------------------------------

st.sidebar.header("🔎 Station Filters")

stations = sorted(
    df["station_id"].dropna().astype(str).unique().tolist()
)

selected_stations = st.sidebar.multiselect(
    "Select Stations",
    options=stations,
    default=stations
)

df["station_id"] = df["station_id"].astype(str)

filtered_df = df[
    df["station_id"].isin(selected_stations)
].copy()

if filtered_df.empty:
    st.warning("No data available for the selected stations.")
    st.stop()


# --------------------------------------------------
# STATION SUMMARY
# --------------------------------------------------

station_summary = (
    filtered_df.groupby("station_id")
    .agg(
        total_sessions=("session_id", "count"),
        total_energy_kwh=("energy_kwh", "sum"),
        average_energy_kwh=("energy_kwh", "mean"),
        average_connection_hours=(
            "connection_duration_hours", "mean"
        ),
        average_charging_hours=(
            "charging_duration_hours", "mean"
        ),
        maximum_energy_kwh=("energy_kwh", "max")
    )
    .reset_index()
)

station_summary["total_energy_kwh"] = (
    station_summary["total_energy_kwh"].round(2)
)

station_summary["average_energy_kwh"] = (
    station_summary["average_energy_kwh"].round(2)
)

station_summary["average_connection_hours"] = (
    station_summary["average_connection_hours"].round(2)
)

station_summary["average_charging_hours"] = (
    station_summary["average_charging_hours"].round(2)
)

station_summary["maximum_energy_kwh"] = (
    station_summary["maximum_energy_kwh"].round(2)
)

station_summary = station_summary.sort_values(
    "total_energy_kwh",
    ascending=False
)


# --------------------------------------------------
# KEY METRICS
# --------------------------------------------------

total_stations = filtered_df["station_id"].nunique()
total_sessions = len(filtered_df)
total_energy = filtered_df["energy_kwh"].sum()

top_station = (
    station_summary.iloc[0]["station_id"]
    if not station_summary.empty
    else "N/A"
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Charging Stations", f"{total_stations:,}")
c2.metric("Total Sessions", f"{total_sessions:,}")
c3.metric("Total Energy", f"{total_energy:,.2f} kWh")
c4.metric("Top Station by Energy", top_station)

st.divider()


# --------------------------------------------------
# TOP STATIONS BY SESSION COUNT
# --------------------------------------------------

st.subheader("📊 Top Stations by Charging Sessions")

top_sessions = (
    station_summary
    .sort_values("total_sessions", ascending=False)
    .head(10)
)

fig_sessions = px.bar(
    top_sessions,
    x="station_id",
    y="total_sessions",
    title="Top 10 Stations by Number of Sessions",
    labels={
        "station_id": "Charging Station",
        "total_sessions": "Total Sessions"
    },
    text="total_sessions"
)

fig_sessions.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig_sessions, use_container_width=True)


# --------------------------------------------------
# TOP STATIONS BY ENERGY
# --------------------------------------------------

st.subheader("⚡ Top Stations by Energy Delivered")

top_energy = (
    station_summary
    .sort_values("total_energy_kwh", ascending=False)
    .head(10)
)

fig_energy = px.bar(
    top_energy,
    x="station_id",
    y="total_energy_kwh",
    title="Top 10 Stations by Total Energy Delivered",
    labels={
        "station_id": "Charging Station",
        "total_energy_kwh": "Energy Delivered (kWh)"
    },
    text="total_energy_kwh"
)

fig_energy.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig_energy, use_container_width=True)


# --------------------------------------------------
# AVERAGE ENERGY PER SESSION
# --------------------------------------------------

st.subheader("🔋 Average Energy per Session")

average_energy_stations = station_summary.sort_values(
    "average_energy_kwh",
    ascending=False
).head(10)

fig_average = px.bar(
    average_energy_stations,
    x="station_id",
    y="average_energy_kwh",
    title="Top 10 Stations by Average Energy per Session",
    labels={
        "station_id": "Charging Station",
        "average_energy_kwh": "Average Energy (kWh)"
    },
    text="average_energy_kwh"
)

fig_average.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig_average, use_container_width=True)


# --------------------------------------------------
# ENERGY CONTRIBUTION
# --------------------------------------------------

st.subheader("🌍 Station Energy Contribution")

energy_share = station_summary[
    ["station_id", "total_energy_kwh"]
].copy()

total_station_energy = energy_share["total_energy_kwh"].sum()

if total_station_energy > 0:
    energy_share["energy_share_percent"] = (
        energy_share["total_energy_kwh"]
        / total_station_energy
        * 100
    )

    pie_data = energy_share.head(10).copy()

    if len(energy_share) > 10:
        other_energy = energy_share.iloc[10:]["total_energy_kwh"].sum()

        if other_energy > 0:
            pie_data = pd.concat(
                [
                    pie_data,
                    pd.DataFrame(
                        [{
                            "station_id": "Other Stations",
                            "total_energy_kwh": other_energy
                        }]
                    )
                ],
                ignore_index=True
            )

    fig_share = px.pie(
        pie_data,
        names="station_id",
        values="total_energy_kwh",
        title="Share of Total Energy Delivered"
    )

    st.plotly_chart(fig_share, use_container_width=True)


# --------------------------------------------------
# DURATION COMPARISON
# --------------------------------------------------

st.subheader("⏱️ Station Connection vs Charging Duration")

duration_data = station_summary[
    [
        "station_id",
        "average_connection_hours",
        "average_charging_hours"
    ]
].copy()

duration_data = duration_data.dropna(
    subset=[
        "average_connection_hours",
        "average_charging_hours"
    ]
)

if not duration_data.empty:
    duration_long = duration_data.melt(
        id_vars="station_id",
        value_vars=[
            "average_connection_hours",
            "average_charging_hours"
        ],
        var_name="duration_type",
        value_name="hours"
    )

    duration_long["duration_type"] = duration_long[
        "duration_type"
    ].map({
        "average_connection_hours": "Connection Duration",
        "average_charging_hours": "Charging Duration"
    })

    fig_duration = px.bar(
        duration_long,
        x="station_id",
        y="hours",
        color="duration_type",
        barmode="group",
        title="Average Connection and Charging Duration",
        labels={
            "station_id": "Charging Station",
            "hours": "Average Hours",
            "duration_type": "Duration Type"
        }
    )

    fig_duration.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig_duration, use_container_width=True)

    st.caption(
        "Connection duration measures how long a vehicle remains connected. "
        "Charging duration is calculated only when a charging completion "
        "timestamp is available. The two measurements are not equivalent."
    )
else:
    st.info("Not enough valid duration data to display this comparison.")


# --------------------------------------------------
# STATION PERFORMANCE TABLE
# --------------------------------------------------

st.subheader("📋 Station Performance Summary")

st.dataframe(
    station_summary,
    use_container_width=True,
    hide_index=True
)

st.download_button(
    label="📥 Download Station Performance CSV",
    data=station_summary.to_csv(index=False).encode("utf-8"),
    file_name="station_performance_summary.csv",
    mime="text/csv"
)


# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------

st.subheader("💡 Business Insights")

if not station_summary.empty:
    top_row = station_summary.iloc[0]

    best_session_station = station_summary.sort_values(
        "total_sessions",
        ascending=False
    ).iloc[0]

    insight1, insight2, insight3 = st.columns(3)

    with insight1:
        st.info(
            f"**Highest Energy Contribution**\n\n"
            f"Station `{top_row['station_id']}` delivered "
            f"{top_row['total_energy_kwh']:,.2f} kWh."
        )

    with insight2:
        st.info(
            f"**Most Frequently Used Station**\n\n"
            f"Station `{best_session_station['station_id']}` "
            f"recorded {int(best_session_station['total_sessions']):,} sessions."
        )

    with insight3:
        highest_average = station_summary.sort_values(
            "average_energy_kwh",
            ascending=False
        ).iloc[0]

        st.info(
            f"**Highest Average Energy per Session**\n\n"
            f"Station `{highest_average['station_id']}` averaged "
            f"{highest_average['average_energy_kwh']:.2f} kWh per session."
        )

st.caption(
    "Data source: EV Charging Sessions dataset. "
    "Duration metrics are calculated from available timestamps."
)