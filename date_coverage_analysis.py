
import json
import pandas as pd

# Step 1: Load the dataset
with open("acndata_sessions.json", "r") as file:
    data = json.load(file)

df = pd.DataFrame(data["_items"])

# Step 2: Convert connection times to datetime
df["connectionTime"] = pd.to_datetime(
    df["connectionTime"],
    errors="coerce",
    utc=True
)

# Step 3: Convert timestamps to Los Angeles local time
df["local_connection_time"] = (
    df["connectionTime"]
    .dt.tz_convert("America/Los_Angeles")
)

# Step 4: Remove invalid timestamps for this analysis
valid_dates = df["local_connection_time"].dropna()

# Step 5: Find the date range
print("\n--- Dataset Date Coverage ---")

print(
    "First connection:",
    valid_dates.min()
)

print(
    "Last connection:",
    valid_dates.max()
)

print(
    "Total valid timestamps:",
    len(valid_dates)
)

# Step 6: Count distinct calendar dates
print(
    "Distinct calendar dates:",
    valid_dates.dt.date.nunique()
)

# Step 7: Count records by month
monthly_counts = (
    valid_dates.dt.strftime("%Y-%m")
    .value_counts()
    .sort_index()
)

print("\n--- Sessions Recorded per Month ---")
print(monthly_counts)

# Step 8: Save results
monthly_counts.to_csv(
    "monthly_date_coverage.csv",
    header=["sessions"]
)

print("\nResults saved to monthly_date_coverage.csv")
