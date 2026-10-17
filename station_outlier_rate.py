
import json
import pandas as pd

# Step 1: Load the dataset
with open("acndata_sessions.json", "r") as file:
    data = json.load(file)

df = pd.DataFrame(data["_items"])

# Step 2: Convert energy values to numeric
df["kWhDelivered"] = pd.to_numeric(
    df["kWhDelivered"],
    errors="coerce"
)

# Step 3: Calculate the dataset-wide IQR threshold
energy = df["kWhDelivered"].dropna()

Q1 = energy.quantile(0.25)
Q3 = energy.quantile(0.75)
IQR = Q3 - Q1

upper_bound = Q3 + 1.5 * IQR

# Step 4: Keep sessions with recorded energy
valid_df = df.dropna(subset=["kWhDelivered"]).copy()

# Step 5: Flag high-energy outliers
valid_df["is_outlier"] = (
    valid_df["kWhDelivered"] > upper_bound
)

# Step 6: Calculate station-level statistics
station_analysis = (
    valid_df.groupby("stationID")
    .agg(
        total_sessions=("sessionID", "count"),
        outlier_sessions=("is_outlier", "sum"),
        average_energy_kwh=("kWhDelivered", "mean")
    )
)

# Step 7: Calculate outlier percentage per station
station_analysis["outlier_rate_percent"] = (
    station_analysis["outlier_sessions"]
    / station_analysis["total_sessions"]
) * 100

# Step 8: Sort by outlier rate
station_analysis = station_analysis.sort_values(
    "outlier_rate_percent",
    ascending=False
)

print("\n--- Stations with the Highest Outlier Rates ---")
print(station_analysis.head(10).round(2))

# Step 9: Save the results
station_analysis.to_csv("station_outlier_rates.csv")

print("\nResults saved to station_outlier_rates.csv")
