import json
import pandas as pd

# Step 1: Load the dataset
with open("acndata_sessions.json", "r") as file:
    data = json.load(file)

df = pd.DataFrame(data["_items"])

# Step 2: Convert text columns into datetime values
date_columns = [
    "connectionTime",
    "disconnectTime",
    "doneChargingTime"
]

for column in date_columns:
    df[column] = pd.to_datetime(df[column], errors="coerce", utc=True)

# Step 3: Calculate connection duration in minutes
df["connection_duration_minutes"] = (
    df["disconnectTime"] - df["connectionTime"]
).dt.total_seconds() / 60

# Step 4: Calculate charging duration in minutes
df["charging_duration_minutes"] = (
    df["doneChargingTime"] - df["connectionTime"]
).dt.total_seconds() / 60

# Step 5: Display results
print("\n--- Date Column Types ---")
print(df[date_columns].dtypes)

print("\n--- First 5 Sessions ---")
print(
    df[
        [
            "connectionTime",
            "disconnectTime",
            "doneChargingTime",
            "connection_duration_minutes",
            "charging_duration_minutes"
        ]
    ].head()
)

print("\n--- Duration Statistics ---")
print(
    df[
        [
            "connection_duration_minutes",
            "charging_duration_minutes"
        ]
    ].describe().round(2)
)

print("\n--- Missing Charging Durations ---")
print(df["charging_duration_minutes"].isnull().sum())

# Step 6: Investigate unusually long sessions

print("\n--- Sessions With Long Connection Durations ---")

long_sessions = df[
    df["connection_duration_minutes"] > 720
]

print("Sessions connected for more than 12 hours:")
print(len(long_sessions))

print(
    long_sessions[
        [
            "stationID",
            "connectionTime",
            "disconnectTime",
            "connection_duration_minutes",
            "charging_duration_minutes",
            "kWhDelivered"
        ]
    ].head(10).to_string(index=False)
)

print("\n--- Sessions With Long Charging Durations ---")

long_charging = df[
    df["charging_duration_minutes"] > 720
]

print("Sessions charging for more than 12 hours:")
print(len(long_charging))

print(
    long_charging[
        [
            "stationID",
            "connectionTime",
            "doneChargingTime",
            "charging_duration_minutes",
            "kWhDelivered"
        ]
    ].head(10).to_string(index=False)
)