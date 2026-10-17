
import json
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load the dataset
with open("acndata_sessions.json", "r") as file:
    data = json.load(file)

df = pd.DataFrame(data["_items"])

# Step 2: Convert energy values to numeric
df["kWhDelivered"] = pd.to_numeric(
    df["kWhDelivered"],
    errors="coerce"
)

# Step 3: Remove missing energy values for this analysis
energy_data = df["kWhDelivered"].dropna()

# Step 4: Calculate charging statistics
print("\n--- Charging Energy Statistics ---")
print("Valid sessions:", len(energy_data))
print("Average energy:", round(energy_data.mean(), 2), "kWh")
print("Median energy:", round(energy_data.median(), 2), "kWh")
print("Minimum energy:", round(energy_data.min(), 2), "kWh")
print("Maximum energy:", round(energy_data.max(), 2), "kWh")

# Step 5: Calculate energy percentiles
print("\n--- Energy Percentiles ---")
print(energy_data.quantile([0.25, 0.50, 0.75]).round(2))

# Step 6: Create a histogram
plt.figure(figsize=(10, 6))

plt.hist(energy_data, bins=30, edgecolor="black")

plt.title("Distribution of Energy Delivered per Charging Session")
plt.xlabel("Energy Delivered (kWh)")
plt.ylabel("Number of Sessions")
plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("charging_energy_distribution.png", dpi=150)
plt.show()

print("\nChart saved as charging_energy_distribution.png")
