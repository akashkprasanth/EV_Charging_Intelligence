
import json
import pandas as pd

# Step 1: Load the dataset
with open("acndata_sessions.json", "r") as file:
    data = json.load(file)

df = pd.DataFrame(data["_items"])

# Step 2: Prepare energy data
df["kWhDelivered"] = pd.to_numeric(
    df["kWhDelivered"],
    errors="coerce"
)

# Step 3: Create station_usage
station_usage = (
    df.groupby("stationID")
    .agg(
        total_sessions=("sessionID", "count"),
        total_energy_kwh=("kWhDelivered", "sum"),
        average_energy_kwh=("kWhDelivered", "mean")
    )
)

# Step 4: Calculate total energy
total_energy = station_usage["total_energy_kwh"].sum()

# Step 5: Calculate each station's energy contribution
station_usage["energy_share_percent"] = (
    station_usage["total_energy_kwh"] / total_energy
) * 100

# Step 6: Sort stations by energy contribution
top_energy_share = station_usage.sort_values(
    "energy_share_percent",
    ascending=False
)

# Step 7: Display the top 10 stations
print("\n--- Top 10 Stations by Energy Contribution ---")

print(
    top_energy_share[
        [
            "total_sessions",
            "total_energy_kwh",
            "energy_share_percent"
        ]
    ].head(10).round(2)
)

# Step 8: Save results to CSV
top_energy_share.to_csv("station_energy_share.csv")

print("\nTotal energy delivered:", round(total_energy, 2), "kWh")
print("Results saved to station_energy_share.csv")

