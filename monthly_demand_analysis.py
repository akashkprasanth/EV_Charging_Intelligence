
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

# Step 4: Extract the month
df["month"] = (
    df["local_connection_time"]
    .dt.to_period("M")
    .astype(str)
)

# Step 5: Count sessions by month
monthly_demand = (
    df.groupby("month")
    .size()
    .sort_index()
)

print("\n--- Charging Sessions by Month ---")
print(monthly_demand)

# Step 6: Identify the busiest month
print("\nBusiest month:", monthly_demand.idxmax())
print("Sessions:", monthly_demand.max())

# Step 7: Plot monthly demand
plt.figure(figsize=(12, 6))

plt.plot(
    monthly_demand.index,
    monthly_demand.values,
    marker="o"
)

plt.title("EV Charging Demand by Month")
plt.xlabel("Month")
plt.ylabel("Number of Charging Sessions")
plt.xticks(rotation=45, ha="right")
plt.grid(True, linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("monthly_charging_demand.png", dpi=150)
plt.show()

# Step 8: Save results
monthly_demand.to_csv(
    "monthly_charging_demand.csv",
    header=["sessions"]
)

print("\nChart saved as monthly_charging_demand.png")
print("Results saved as monthly_charging_demand.csv")
