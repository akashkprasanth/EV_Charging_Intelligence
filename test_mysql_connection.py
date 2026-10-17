import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=input("Enter your MySQL root password: "),
        database="ev_charging_db"
    )

    if connection.is_connected():
        print("Successfully connected to MySQL!")

        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM charging_sessions"
        )

        total_sessions = cursor.fetchone()[0]

        print(f"Total charging sessions: {total_sessions}")

        cursor.close()
        connection.close()

except mysql.connector.Error as error:
    print(f"MySQL connection failed: {error}")