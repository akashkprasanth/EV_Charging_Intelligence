
import json
import pandas as pd

# Step 1: Load the dataset
with open("acndata_sessions.json", "r") as file:
    data = json.load(file)

df = pd.DataFrame(data["_items"])

# Step 2: Convert energy and timestamps
df["kWhDelivered"] = pd.to_numeric(
    df["kWhDelivered"],
    errors="coerce"
)

df["connectionTime"] = pd.to_datetime(
    df["connectionTime"],
    errors="coerce",
    utc=True
)

df["doneChargingTime"] = pd.to_datetime(
    df["doneChargingTime"],
    errors="coerce",
    utc=True
)

# Step 3: Calculate charging duration in minutes
df["charging_duration_minutes"] = (
    df["doneChargingTime"] - df["connectionTime"]
).dt.total_seconds() / 60

# Step 4: Identify high-energy outliers using the IQR method
energy = df["kWhDelivered"].dropna()

Q1 = energy.quantile(0.25)
Q3 = energy.quantile(0.75)
IQR = Q3 - Q1

upper_bound = Q3 + 1.5 * IQR

df["energy_group"] = "Normal"
df.loc[
    df["kWhDelivered"] > upper_bound,
    "energy_group"
] = "High-energy outlier"

# Step 5: Compare both groups
comparison = df.groupby("energy_group").agg(
    session_count=("sessionID", "count"),
    average_energy_kwh=("kWhDelivered", "mean"),
    median_energy_kwh=("kWhDelivered", "median"),
    average_charging_minutes=("charging_duration_minutes", "mean"),
    median_charging_minutes=("charging_duration_minutes", "median")
)

print("\n--- Normal Sessions vs High-Energy Outliers ---")
print(comparison.round(2))

# Step 6: Save the comparison
comparison.to_csv("outlier_duration_comparison.csv")

print("\nResults saved to outlier_duration_comparison.csv")
