
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

# Step 3: Calculate IQR boundaries
energy = df["kWhDelivered"].dropna()

Q1 = energy.quantile(0.25)
Q3 = energy.quantile(0.75)
IQR = Q3 - Q1

upper_bound = Q3 + 1.5 * IQR

# Step 4: Select high-energy outlier sessions
outliers = df[
    df["kWhDelivered"] > upper_bound
].copy()

# Step 5: Count outliers for each station
station_outliers = (
    outliers.groupby("stationID")
    .agg(
        high_energy_sessions=("sessionID", "count"),
        average_energy_kwh=("kWhDelivered", "mean"),
        maximum_energy_kwh=("kWhDelivered", "max")
    )
    .sort_values(
        "high_energy_sessions",
        ascending=False
    )
)

# Step 6: Display the top 10 stations
print("\n--- Top 10 Stations by High-Energy Outlier Count ---")
print(station_outliers.head(10).round(2))

# Step 7: Save the results
station_outliers.to_csv("station_outlier_summary.csv")

print("\nTotal high-energy outlier sessions:", len(outliers))
print("Stations with high-energy outliers:", len(station_outliers))
print("Results saved to station_outlier_summary.csv")
