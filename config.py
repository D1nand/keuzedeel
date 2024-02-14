import mysql.connector

# Replace these values with your MySQL server details
host = 'localhost'
user = 'root'
password = ""
database = 'keuzedeel'

# Establish a connection
try:
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    if connection.is_connected():
        print("Connected to the MySQL database")

    # Your database operations go here

except mysql.connector.Error as e:
    print(f"Error: {e}")

finally:
    # Close the connection in a finally block to ensure it's always closed
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("Connection closed")
