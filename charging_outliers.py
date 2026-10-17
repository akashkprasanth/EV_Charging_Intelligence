
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

# Step 3: Remove missing energy values
energy_data = df["kWhDelivered"].dropna()

# Step 4: Calculate quartiles
Q1 = energy_data.quantile(0.25)
Q3 = energy_data.quantile(0.75)

# Step 5: Calculate the interquartile range
IQR = Q3 - Q1

# Step 6: Calculate outlier boundaries
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Step 7: Identify potential outliers
outliers = df[
    (df["kWhDelivered"] < lower_bound)
    | (df["kWhDelivered"] > upper_bound)
]

print("\n--- Energy Outlier Analysis ---")
print(f"Q1: {Q1:.2f} kWh")
print(f"Q3: {Q3:.2f} kWh")
print(f"IQR: {IQR:.2f} kWh")
print(f"Lower boundary: {lower_bound:.2f} kWh")
print(f"Upper boundary: {upper_bound:.2f} kWh")

print("\nNumber of potential outlier sessions:", len(outliers))

print("\n--- First 10 Potential Outliers ---")
print(
    outliers[
        ["sessionID", "stationID", "kWhDelivered"]
    ].head(10).to_string(index=False)
)

# Step 8: Save the potential outliers
outliers.to_csv("charging_energy_outliers.csv", index=False)

print("\nResults saved to charging_energy_outliers.csv")
