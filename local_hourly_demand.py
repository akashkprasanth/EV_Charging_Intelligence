
import json
import pandas as pd

# 1. Load the dataset
with open("acndata_sessions.json", "r") as file:
    data = json.load(file)

df = pd.DataFrame(data["_items"])

# 2. Convert connection time to datetime
df["connectionTime"] = pd.to_datetime(
    df["connectionTime"],
    errors="coerce",
    utc=True
)

# 3. Convert UTC to Los Angeles local time
df["local_connection_time"] = (
    df["connectionTime"].dt.tz_convert("America/Los_Angeles")
)

# 4. Extract the local hour
df["local_hour"] = df["local_connection_time"].dt.hour

# 5. Count sessions for each hour
hourly_demand = (
    df.groupby("local_hour")
    .size()
    .reindex(range(24), fill_value=0)
)

# 6. Display the results
print("\n--- EV Charging Demand by Local Hour ---")
print(hourly_demand)

# 7. Find the busiest and quietest hours
print("\nBusiest hour:", hourly_demand.idxmax())
print("Sessions during busiest hour:", hourly_demand.max())

print("\nQuietest hour:", hourly_demand.idxmin())
print("Sessions during quietest hour:", hourly_demand.min())

# 8. Save the results
hourly_demand.to_csv(
    "local_hourly_demand.csv",
    header=["sessions"]
)

print("\nResults saved to local_hourly_demand.csv")
