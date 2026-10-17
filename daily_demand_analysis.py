
import json
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load the dataset
with open("acndata_sessions.json", "r") as file:
    data = json.load(file)

df = pd.DataFrame(data["_items"])

# Step 2: Convert connection time to datetime
df["connectionTime"] = pd.to_datetime(
    df["connectionTime"],
    errors="coerce",
    utc=True
)

# Step 3: Convert to Los Angeles local time
df["local_connection_time"] = (
    df["connectionTime"]
    .dt.tz_convert("America/Los_Angeles")
)

# Step 4: Extract the local day of the week
df["day_of_week"] = (
    df["local_connection_time"]
    .dt.day_name()
)

# Step 5: Count sessions by day
day_order = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
]

daily_demand = (
    df["day_of_week"]
    .value_counts()
    .reindex(day_order, fill_value=0)
)

print("\n--- Charging Sessions by Day of Week ---")
print(daily_demand)

# Step 6: Find the busiest day
print("\nBusiest day:", daily_demand.idxmax())
print("Sessions:", daily_demand.max())

# Step 7: Create a bar chart
plt.figure(figsize=(10, 6))

plt.bar(daily_demand.index, daily_demand.values)

plt.title("EV Charging Demand by Day of Week")
plt.xlabel("Day of Week")
plt.ylabel("Number of Charging Sessions")
plt.xticks(rotation=30, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("daily_charging_demand.png", dpi=150)
plt.show()

# Step 8: Save results
daily_demand.to_csv("daily_charging_demand.csv", header=["sessions"])

print("\nChart saved as daily_charging_demand.png")
print("Results saved as daily_charging_demand.csv")
