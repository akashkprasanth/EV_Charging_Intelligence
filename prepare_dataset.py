
import json
import pandas as pd

# 1. Load the original JSON dataset
with open("acndata_sessions.json", "r") as file:
    data = json.load(file)

df = pd.DataFrame(data["_items"])

print("\n--- Original Dataset ---")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# 2. Remove duplicate records using the session identifier
df = df.drop_duplicates(subset=["sessionID"])

# 3. Convert timestamp columns to datetime
date_columns = [
    "connectionTime",
    "disconnectTime",
    "doneChargingTime"
]

for column in date_columns:
    df[column] = pd.to_datetime(
        df[column],
        errors="coerce",
        utc=True
    )

# 4. Convert energy delivered to numeric
df["kWhDelivered"] = pd.to_numeric(
    df["kWhDelivered"],
    errors="coerce"
)

# 5. Check for missing and invalid values
print("\n--- Data Quality Checks ---")
print("Rows after duplicate check:", len(df))
print("Duplicate session IDs:", df["sessionID"].duplicated().sum())
print("Missing connection times:", df["connectionTime"].isna().sum())
print("Missing energy values:", df["kWhDelivered"].isna().sum())
print("Negative energy values:", (df["kWhDelivered"] < 0).sum())

# 6. Save the processed dataset
df.to_csv(
    "ev_charging_cleaned.csv",
    index=False
)

print("\nCleaned dataset saved as ev_charging_cleaned.csv")
print("Final shape:", df.shape)
