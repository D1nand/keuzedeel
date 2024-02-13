import mysql.connector

# Replace these with your MySQL server details
db_config = {
    'host': 'your_mysql_host',
    'user': 'your_mysql_user',
    'password': 'your_mysql_password',
    'database': 'your_mysql_database'
}

# Connect to the MySQL database
connection = mysql.connector.connect(**db_config)

# Create a cursor object to execute SQL queries
cursor = connection.cursor()

# Example: Create a table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL
    )
''')

# Commit the changes and close the connection
connection.commit()
connection.close()
