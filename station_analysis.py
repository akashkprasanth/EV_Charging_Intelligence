
import json
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load the dataset
with open("acndata_sessions.json", "r") as file:
    data = json.load(file)

df = pd.DataFrame(data["_items"])

# Step 2: Convert energy delivered to numeric
df["kWhDelivered"] = pd.to_numeric(
    df["kWhDelivered"],
    errors="coerce"
)

# Step 3: Analyze station usage
station_usage = (
    df.groupby("stationID")
    .agg(
        total_sessions=("sessionID", "count"),
        total_energy_kwh=("kWhDelivered", "sum"),
        average_energy_kwh=("kWhDelivered", "mean")
    )
    .sort_values("total_sessions", ascending=False)
)

print("\n--- Top 10 Charging Stations by Number of Sessions ---")
print(station_usage.head(10).round(2))

# Step 6: Rank stations by total energy delivered
top_energy_stations = station_usage.sort_values(
    "total_energy_kwh",
    ascending=False
)

print("\n--- Top 10 Stations by Total Energy Delivered ---")
print(
    top_energy_stations[
        ["total_sessions", "total_energy_kwh", "average_energy_kwh"]
    ].head(10).round(2)
)

# Step 7: Plot the top 10 energy-delivering stations
top_10_energy = top_energy_stations.head(10)

plt.figure(figsize=(12, 6))

plt.bar(
    top_10_energy.index.astype(str),
    top_10_energy["total_energy_kwh"]
)

plt.title("Top 10 EV Charging Stations by Energy Delivered")
plt.xlabel("Station ID")
plt.ylabel("Total Energy Delivered (kWh)")
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("top_stations_by_energy.png", dpi=150)
plt.show()

print("\nChart saved as top_stations_by_energy.png")

print(station_usage.head(10).round(2))

# Step 4: Visualize the top 10 stations
top_stations = station_usage.head(10)

plt.figure(figsize=(12, 6))
plt.bar(
    top_stations.index.astype(str),
    top_stations["total_sessions"]
)

plt.title("Top 10 EV Charging Stations by Sessions")
plt.xlabel("Station ID")
plt.ylabel("Total Charging Sessions")
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("top_charging_stations.png", dpi=150)
plt.show()

# Step 5: Save the station analysis
station_usage.to_csv("station_performance.csv")

print("\nChart saved as top_charging_stations.png")
print("Results saved as station_performance.csv")
