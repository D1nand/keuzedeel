from config import host, user, password, database
import mysql.connector
from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash

DB_CONFIG = {
    'host': host,
    'user': user,
    'password': password,
    'database': database
}

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # If it's a POST request, process the registration
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Validation code...

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Perform user registration logic here (e.g., store in a database)
        try:
            connection = mysql.connector.connect(**DB_CONFIG)

            with connection.cursor() as cursor:
                # Check if the username already exists
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    return "Username already exists. Choose a different username."

                # Insert user into the database
                cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                               (username, hashed_password, email))

                connection.commit()

                return f"Registration successful! Username: {username}, Email: {email}"

        except mysql.connector.Error as e:
            print(f"Database Error: {e}")
            return f"Error: {e}"

        finally:
            if 'connection' in locals() and connection.is_connected():
                connection.close()
                print("Connection closed")

    # If it's a GET request, render the registration form
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
