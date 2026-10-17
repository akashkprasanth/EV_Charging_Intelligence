
import json
import pandas as pd
import mysql.connector

# 1. Load the cleaned CSV
df = pd.read_csv("ev_charging_cleaned.csv")

# 2. Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password=input("Enter your MySQL root password: "),
    database="ev_charging_db"
)

cursor = conn.cursor()

# 3. Prepare the INSERT statement
sql = """
INSERT INTO charging_sessions (
    session_id,
    record_id,
    cluster_id,
    connection_time,
    disconnect_time,
    done_charging_time,
    energy_kwh,
    site_id,
    space_id,
    station_id,
    timezone,
    user_id,
    user_inputs
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# 4. Convert missing values and timestamps
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

df = df.astype(object).where(pd.notna(df), None)

# 5. Map CSV columns to MySQL columns
records = []

for _, row in df.iterrows():
    user_inputs = row["userInputs"]

    if user_inputs is not None:
        if isinstance(user_inputs, str):
            try:
                user_inputs = json.loads(user_inputs)
            except json.JSONDecodeError:
                pass

        user_inputs = json.dumps(user_inputs)

    records.append((
        str(row["sessionID"]),
        str(row["_id"]),
        str(row["clusterID"]),
        row["connectionTime"].to_pydatetime().replace(tzinfo=None)
        if row["connectionTime"] is not None else None,
        row["disconnectTime"].to_pydatetime().replace(tzinfo=None)
        if row["disconnectTime"] is not None else None,
        row["doneChargingTime"].to_pydatetime().replace(tzinfo=None)
        if row["doneChargingTime"] is not None else None,
        float(row["kWhDelivered"])
        if row["kWhDelivered"] is not None else None,
        str(row["siteID"]),
        str(row["spaceID"]),
        str(row["stationID"]),
        str(row["timezone"]),
        str(row["userID"]) if row["userID"] is not None else None,
        user_inputs
    ))

# 6. Import records
try:
    cursor.executemany(sql, records)
    conn.commit()

    print("\nImport completed successfully!")
    print("Rows submitted:", len(records))

    # 7. Verify the total record count
    cursor.execute("SELECT COUNT(*) FROM charging_sessions")
    count = cursor.fetchone()[0]

    print("Total records in MySQL:", count)

except mysql.connector.Error as error:
    conn.rollback()
    print("\nMySQL import failed:")
    print(error)

finally:
    cursor.close()
    conn.close()
