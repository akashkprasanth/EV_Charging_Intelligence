import json

# Open the JSON dataset
with open("acndata_sessions.json", "r") as file:
    data = json.load(file)

# Get all charging sessions
sessions = data["_items"]

# Display basic information
print("EV Charging Intelligence Project")

print("Total charging sessions:", len(sessions))

print("\nFirst charging session:")
print(sessions[0])