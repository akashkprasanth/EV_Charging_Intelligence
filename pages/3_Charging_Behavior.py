import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Charging Behavior",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 EV Charging Behavior & Anomaly Analysis")

st.markdown(
    "Identify unusual charging sessions, investigate long connections, "
    "and compare charging behavior across stations."
)


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

    # Calculate connection duration in hours.
    df["connection_duration_hours"] = (
        df["disconnect_time"] - df["connection_time"]
    ).dt.total_seconds() / 3600

    # Calculate charging duration when a completion timestamp exists.
    df["charging_duration_hours"] = (
        df["done_charging_time"] - df["connection_time"]
    ).dt.total_seconds() / 3600

    # Remove invalid negative durations.
    df.loc[
        df["connection_duration_hours"] < 0,
        "connection_duration_hours"
    ] = float("nan")

    df.loc[
        df["charging_duration_hours"] < 0,
        "charging_duration_hours"
    ] = float("nan")

    # Flag unusually long connections.
    df["long_connection"] = (
        df["connection_duration_hours"] > 4
    )

    # Identify high-energy outliers using the IQR method.
    valid_energy = df["energy_kwh"].dropna()

    if len(valid_energy) > 0:
        q1 = valid_energy.quantile(0.25)
        q3 = valid_energy.quantile(0.75)
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr
    else:
        upper_bound = float("inf")

    df["high_energy_outlier"] = (
        df["energy_kwh"] > upper_bound
    )

    # Long connection with low energy is an investigation flag,
    # not proof of a faulty charger or abnormal behavior.
    median_energy = df["energy_kwh"].median()

    df["long_connection_low_energy"] = (
        df["long_connection"]
        & (df["energy_kwh"] < median_energy)
    )

    return df, upper_bound


try:
    df, energy_upper_bound = load_data()
except Exception as error:
    st.error(f"Unable to load charging data: {error}")
    st.stop()


# --------------------------------------------------
# FILTERS
# --------------------------------------------------

st.sidebar.header("🔎 Behavior Filters")

stations = sorted(
    df["station_id"].dropna().astype(str).unique().tolist()
)

selected_stations = st.sidebar.multiselect(
    "Select Charging Stations",
    options=stations,
    default=stations
)

connection_threshold = st.sidebar.slider(
    "Long connection threshold (hours)",
    min_value=1,
    max_value=24,
    value=4
)

df["station_id"] = df["station_id"].astype(str)

filtered_df = df[
    df["station_id"].isin(selected_stations)
].copy()

if filtered_df.empty:
    st.warning("No data available for the selected stations.")
    st.stop()

# Apply the selected threshold.
filtered_df["long_connection"] = (
    filtered_df["connection_duration_hours"]
    > connection_threshold
)

filtered_df["long_connection_low_energy"] = (
    filtered_df["long_connection"]
    & (
        filtered_df["energy_kwh"]
        < filtered_df["energy_kwh"].median()
    )
)


# --------------------------------------------------
# KEY METRICS
# --------------------------------------------------

total_sessions = len(filtered_df)

long_connections = int(
    filtered_df["long_connection"].sum()
)

high_energy_outliers = int(
    filtered_df["high_energy_outlier"].sum()
)

missing_completion = int(
    filtered_df["done_charging_time"].isna().sum()
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Sessions",
    f"{total_sessions:,}"
)

c2.metric(
    "Long Connections",
    f"{long_connections:,}",
    help="Connections exceeding your selected threshold."
)

c3.metric(
    "High-Energy Outliers",
    f"{high_energy_outliers:,}"
)

c4.metric(
    "Missing Charging Completion",
    f"{missing_completion:,}"
)

st.divider()


# --------------------------------------------------
# CONNECTION DURATION DISTRIBUTION
# --------------------------------------------------

st.subheader("⏱️ Connection Duration Distribution")

duration_data = filtered_df[
    filtered_df["connection_duration_hours"].notna()
].copy()

if not duration_data.empty:
    fig_duration = px.histogram(
        duration_data,
        x="connection_duration_hours",
        nbins=40,
        title="Distribution of Vehicle Connection Duration",
        labels={
            "connection_duration_hours": "Connection Duration (Hours)",
            "count": "Number of Sessions"
        }
    )

    st.plotly_chart(
        fig_duration,
        use_container_width=True
    )
else:
    st.info("No valid connection-duration data is available.")


# --------------------------------------------------
# ENERGY DISTRIBUTION
# --------------------------------------------------

st.subheader("⚡ Energy Delivered per Session")

energy_data = filtered_df[
    filtered_df["energy_kwh"].notna()
].copy()

if not energy_data.empty:
    fig_energy = px.histogram(
        energy_data,
        x="energy_kwh",
        nbins=40,
        title="Distribution of Energy Delivered",
        labels={
            "energy_kwh": "Energy Delivered (kWh)",
            "count": "Number of Sessions"
        }
    )

    st.plotly_chart(
        fig_energy,
        use_container_width=True
    )


# --------------------------------------------------
# LONG CONNECTION ANALYSIS
# --------------------------------------------------

st.subheader("🚗 Long Connection Analysis")

long_df = filtered_df[
    filtered_df["long_connection"]
].copy()

if not long_df.empty:
    fig_long = px.scatter(
        long_df,
        x="connection_duration_hours",
        y="energy_kwh",
        color="station_id",
        hover_data=["session_id"],
        title="Energy Delivered During Long Connections",
        labels={
            "connection_duration_hours": "Connection Duration (Hours)",
            "energy_kwh": "Energy Delivered (kWh)",
            "station_id": "Charging Station"
        }
    )

    st.plotly_chart(
        fig_long,
        use_container_width=True
    )

    st.caption(
        "Long connection time does not necessarily mean long charging time. "
        "A vehicle may remain connected after charging finishes."
    )
else:
    st.info(
        "No connections exceed the selected duration threshold."
    )


# --------------------------------------------------
# HIGH-ENERGY OUTLIERS
# --------------------------------------------------

st.subheader("⚠️ High-Energy Sessions")

st.write(
    f"The IQR method identifies sessions above "
    f"**{energy_upper_bound:.2f} kWh** as potential high-energy outliers "
    "in the full dataset. These sessions should be investigated, "
    "not automatically treated as errors."
)

outlier_df = filtered_df[
    filtered_df["high_energy_outlier"]
].copy()

if not outlier_df.empty:
    fig_outliers = px.scatter(
        outlier_df,
        x="connection_duration_hours",
        y="energy_kwh",
        color="station_id",
        hover_data=["session_id"],
        title="Potential High-Energy Outliers",
        labels={
            "connection_duration_hours": "Connection Duration (Hours)",
            "energy_kwh": "Energy Delivered (kWh)",
            "station_id": "Charging Station"
        }
    )

    st.plotly_chart(
        fig_outliers,
        use_container_width=True
    )
else:
    st.info("No high-energy outliers were found for these stations.")


# --------------------------------------------------
# LONG CONNECTION + LOW ENERGY
# --------------------------------------------------

st.subheader("🔎 Long Connections with Low Energy")

low_energy_df = filtered_df[
    filtered_df["long_connection_low_energy"]
].copy()

st.write(
    "These sessions combine a long connection with energy below the "
    "median for the currently selected stations. They may warrant review, "
    "but the available data cannot establish the cause."
)

if not low_energy_df.empty:
    st.dataframe(
        low_energy_df[
            [
                "session_id",
                "station_id",
                "connection_duration_hours",
                "charging_duration_hours",
                "energy_kwh"
            ]
        ].sort_values(
            "connection_duration_hours",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )
else:
    st.success(
        "No sessions match both conditions for the current filters."
    )


# --------------------------------------------------
# STATION ANOMALY SUMMARY
# --------------------------------------------------

st.subheader("🏭 Station Behavior Summary")

station_summary = (
    filtered_df.groupby("station_id")
    .agg(
        total_sessions=("session_id", "count"),
        total_energy_kwh=("energy_kwh", "sum"),
        average_energy_kwh=("energy_kwh", "mean"),
        average_connection_hours=(
            "connection_duration_hours", "mean"
        ),
        long_connections=("long_connection", "sum"),
        high_energy_outliers=("high_energy_outlier", "sum"),
        long_connection_low_energy=(
            "long_connection_low_energy", "sum"
        )
    )
    .reset_index()
)

station_summary["long_connection_rate_percent"] = (
    station_summary["long_connections"]
    / station_summary["total_sessions"]
    * 100
)

station_summary = station_summary.sort_values(
    "long_connection_rate_percent",
    ascending=False
)

st.dataframe(
    station_summary.round(2),
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# DOWNLOAD RESULTS
# --------------------------------------------------

st.subheader("📥 Export Analysis")

st.download_button(
    label="Download Filtered Sessions",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="charging_behavior_sessions.csv",
    mime="text/csv"
)

st.download_button(
    label="Download Station Behavior Summary",
    data=station_summary.to_csv(index=False).encode("utf-8"),
    file_name="station_behavior_summary.csv",
    mime="text/csv"
)


# --------------------------------------------------
# BUSINESS NOTES
# --------------------------------------------------

st.subheader("💡 How to Interpret These Flags")

st.markdown(
    """
    - **Long connection:** The vehicle remained connected longer than
      the selected threshold.
    - **High-energy outlier:** The session delivered unusually high energy
      relative to the full dataset, using the IQR method.
    - **Long connection + low energy:** A session may deserve further
      investigation because connection time was high while delivered
      energy was below the selected stations' median.
    - **Missing completion timestamp:** Charging completion time was not
      recorded. This does not necessarily mean the session failed.

    These are analytical investigation flags, not confirmed faults,
    fraud, or equipment failures.
    """
)

st.caption(
    "Data source: EV Charging Sessions dataset."
)