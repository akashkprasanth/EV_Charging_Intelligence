
import json
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load the JSON dataset
with open("acndata_sessions.json", "r") as file:
    data = json.load(file)

df = pd.DataFrame(data["_items"])

# Step 2: Convert connection time to datetime
df["connectionTime"] = pd.to_datetime(
    df["connectionTime"],
    errors="coerce",
    utc=True
)

# Step 3: Extract the connection hour in UTC
df["connection_hour"] = df["connectionTime"].dt.hour

# Step 4: Count sessions for every hour (including hours with zero sessions)
hourly_demand = (
    df["connection_hour"]
    .value_counts()
    .reindex(range(24), fill_value=0)
    .sort_index()
)

print("\n--- Charging Sessions by Hour (UTC) ---")
print(hourly_demand)

print("\n--- Busiest Connection Hour (UTC) ---")
print(f"Hour: {hourly_demand.idxmax()}:00 UTC")
print(f"Number of sessions: {hourly_demand.max()}")

# Step 5: Create a bar chart
plt.figure(figsize=(12, 6))
plt.bar(hourly_demand.index, hourly_demand.values)

plt.title("EV Charging Demand by Hour (UTC)")
plt.xlabel("Hour of Day (UTC)")
plt.ylabel("Number of Charging Sessions")
plt.xticks(range(24))
plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("hourly_charging_demand.png", dpi=150)
plt.show()


# Step 6: Convert UTC connection times to local time
df["connectionTime_local"] = (
    df["connectionTime"]
    .dt.tz_convert("America/Los_Angeles")
)

# Step 7: Extract the local connection hour
df["local_connection_hour"] = (
    df["connectionTime_local"].dt.hour
)

# Step 8: Count sessions by local hour
local_hourly_demand = (
    df["local_connection_hour"]
    .value_counts()
    .reindex(range(24), fill_value=0)
    .sort_index()
)

print("\n--- Charging Sessions by Hour (Los Angeles Local Time) ---")
print(local_hourly_demand)

# Step 9: Find the busiest local hour
busiest_local_hour = local_hourly_demand.idxmax()
busiest_local_count = local_hourly_demand.max()

print("\n--- Busiest Local Connection Hour ---")
print(f"Hour: {busiest_local_hour}:00")
print(f"Number of sessions: {busiest_local_count}")

# Step 10: Plot local-time demand
plt.figure(figsize=(12, 6))
plt.bar(local_hourly_demand.index, local_hourly_demand.values)

plt.title("EV Charging Demand by Hour (Los Angeles Local Time)")
plt.xlabel("Local Hour")
plt.ylabel("Number of Charging Sessions")
plt.xticks(range(24))
plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("local_hourly_charging_demand.png", dpi=150)
plt.show()
