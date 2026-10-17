import json
import pandas as pd

# Step 1: Load the dataset
with open("acndata_sessions.json", "r") as file:
    data = json.load(file)

# Step 2: Convert the records into a DataFrame
df = pd.DataFrame(data["_items"])

# Step 3: Display the dataset information
print("\n--- Dataset Shape ---")
print(df.shape)

print("\n--- Column Names ---")
print(df.columns.tolist())

print("\n--- First 5 Records ---")
print(df.head())

print("\n--- Dataset Information ---")
df.info()

print("\n--- Missing Values ---")
print(df.isnull().sum())

# Step 4: Calculate missing-value percentages

print("\n--- Missing Value Percentages ---")

missing_percentage = (df.isnull().sum() / len(df)) * 100

print(missing_percentage.round(2))

# What did we learn?
#
# You have now learned four important data-analysis concepts:
#
# Dataset shape: How many rows and columns exist.
# Data types: What kind of data each column contains.
# Missing values: Which columns contain incomplete information.
# Missing-value percentage: How much information is missing from each column.
#
# These are fundamental skills for a data analyst.

# Step 5: Check for duplicate records

print("\n--- Duplicate Analysis ---")

# Exclude the nested userInputs column
df_for_duplicates = df.drop(columns=["userInputs"])

# Count duplicate rows using the remaining columns
print(
    "Duplicate rows (excluding userInputs):",
    df_for_duplicates.duplicated().sum()
)

# Check duplicate session IDs
print(
    "Duplicate session IDs:",
    df["sessionID"].duplicated().sum()
)

# Check duplicate record IDs
print(
    "Duplicate record IDs:",
    df["_id"].duplicated().sum()
)