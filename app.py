import streamlit as st
import pandas as pd
import mysql.connector

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="EV Charging Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# CUSTOM CSS - KEEP DEFAULT THEME
# ==================================================

st.markdown("""
<style>
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }

    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .sub-header {
        font-size: 1rem;
        opacity: 0.75;
        margin-bottom: 1.5rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128, 128, 128, 0.25);
        padding: 18px;
        border-radius: 12px;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.95rem;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.7rem;
        font-weight: 700;
    }

    .section-header {
        font-size: 1.35rem;
        font-weight: 650;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


# ==================================================
# DATABASE CONNECTION
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
                station_id,
                site_id,
                user_id
            FROM charging_sessions
        """

        df = pd.read_sql(query, connection)

    finally:
        connection.close()

    df["connection_time"] = pd.to_datetime(
        df["connection_time"], errors="coerce"
    )

    df["energy_kwh"] = pd.to_numeric(
        df["energy_kwh"], errors="coerce"
    )

    df["month"] = (
        df["connection_time"]
        .dt.to_period("M")
        .astype("string")
    )

    return df


# ==================================================
# LOAD DATA
# ==================================================

st.markdown(
    '<div class="main-header">⚡ EV Charging Intelligence</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-header">'
    'Electric Vehicle Charging Demand & Station Performance Analytics'
    '</div>',
    unsafe_allow_html=True
)

try:
    df = load_data()

except Exception as error:
    st.error("Unable to load data from MySQL.")
    st.code(str(error))
    st.stop()


# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.title("⚡ EV Analytics")
st.sidebar.caption("Charging Intelligence Platform")
st.sidebar.divider()

st.sidebar.subheader("Dashboard Filters")

# Station filter
stations = sorted(
    df["station_id"].dropna().unique().tolist()
)

selected_stations = st.sidebar.multiselect(
    "Select Charging Stations",
    options=stations,
    default=stations
)

# Date filter
valid_dates = df["connection_time"].dropna()

if not valid_dates.empty:

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    selected_dates = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

else:
    selected_dates = ()

# Apply filters
filtered_df = df[
    df["station_id"].isin(selected_stations)
].copy()

if len(selected_dates) == 2:

    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        filtered_df["connection_time"].dt.date.between(
            start_date,
            end_date
        )
    ]

st.sidebar.divider()

st.sidebar.metric(
    "Filtered Sessions",
    f"{len(filtered_df):,}"
)

st.sidebar.caption(
    "Data source: MySQL | Database: ev_charging_db"
)

# ==================================================
# KPI CARDS
# ==================================================

st.markdown(
    '<div class="section-header">Executive Overview</div>',
    unsafe_allow_html=True
)

total_sessions = len(filtered_df)

total_energy = filtered_df["energy_kwh"].sum()

total_stations = filtered_df["station_id"].nunique()

average_energy = (
    filtered_df["energy_kwh"].mean()
    if not filtered_df["energy_kwh"].isna().all()
    else 0
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric(
    label="🔌 Total Sessions",
    value=f"{total_sessions:,}"
)

kpi2.metric(
    label="⚡ Energy Delivered",
    value=f"{total_energy:,.2f} kWh"
)

kpi3.metric(
    label="🏢 Charging Stations",
    value=f"{total_stations:,}"
)

kpi4.metric(
    label="📊 Average Energy / Session",
    value=f"{average_energy:.2f} kWh"
)

st.caption(
    "Metrics update automatically when you change the station filters."
)

st.divider()


# ==================================================
# MONTHLY DEMAND
# ==================================================

st.markdown(
    '<div class="section-header">📈 Charging Demand Trends</div>',
    unsafe_allow_html=True
)

if filtered_df.empty:

    st.info("Select at least one station to display analytics.")

else:

    monthly_demand = (
        filtered_df.dropna(subset=["month"])
        .groupby("month")
        .agg(
            sessions=("session_id", "count"),
            energy_kwh=("energy_kwh", "sum")
        )
        .sort_index()
    )

    chart1, chart2 = st.columns(2)

    with chart1:
        st.subheader("Monthly Charging Sessions")

        st.bar_chart(
            monthly_demand["sessions"],
            use_container_width=True
        )

    with chart2:
        st.subheader("Monthly Energy Delivered")

        st.bar_chart(
            monthly_demand["energy_kwh"],
            use_container_width=True
        )


# ==================================================
# STATION PERFORMANCE
# ==================================================

st.divider()

st.markdown(
    '<div class="section-header">🏆 Station Performance</div>',
    unsafe_allow_html=True
)

if not filtered_df.empty:

    station_performance = (
        filtered_df.groupby("station_id")
        .agg(
            total_sessions=("session_id", "count"),
            total_energy_kwh=("energy_kwh", "sum"),
            average_energy_kwh=("energy_kwh", "mean")
        )
        .sort_values(
            "total_energy_kwh",
            ascending=False
        )
        .reset_index()
    )

    station_performance["total_energy_kwh"] = (
        station_performance["total_energy_kwh"].round(2)
    )

    station_performance["average_energy_kwh"] = (
        station_performance["average_energy_kwh"].round(2)
    )

    top10 = station_performance.head(10)

    station_chart, station_table = st.columns(
        [1, 1.3]
    )

    with station_chart:

        st.subheader("Top 10 Stations by Energy")

        st.bar_chart(
            top10.set_index("station_id")["total_energy_kwh"],
            use_container_width=True
        )

    with station_table:

        st.subheader("Performance Details")

        st.dataframe(
            top10,
            use_container_width=True,
            hide_index=True
        )


# ==================================================
# DATA QUALITY SUMMARY
# ==================================================

st.divider()

st.markdown(
    '<div class="section-header">🔎 Data Quality</div>',
    unsafe_allow_html=True
)

quality1, quality2, quality3 = st.columns(3)

quality1.metric(
    "Missing Energy Values",
    f"{filtered_df['energy_kwh'].isna().sum():,}"
)

quality2.metric(
    "Missing Connection Times",
    f"{filtered_df['connection_time'].isna().sum():,}"
)

quality3.metric(
    "Missing Charging Completion Times",
    f"{filtered_df['done_charging_time'].isna().sum():,}"
)


# ==================================================
# SESSION DATA PREVIEW
# ==================================================

with st.expander("🔍 Explore Charging Session Records"):

    st.write(
        f"Currently displaying {len(filtered_df):,} sessions."
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

# ==================================================
# DOWNLOAD FILTERED DATA
# ==================================================

st.subheader("📥 Export Filtered Data")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Sessions (CSV)",
    data=csv_data,
    file_name="ev_charging_filtered_sessions.csv",
    mime="text/csv"
)

# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "EV Charging Intelligence | "
    "Built with Python, Pandas, MySQL and Streamlit"
)