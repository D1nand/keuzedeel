from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import check_password_hash
import mysql.connector
from config import host, user, password, database


app = Flask(__name__)

DB_CONFIG = {
    'host': host,
    'user': user,
    'password': password,
    'database': database
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                # Retrieve hashed password from the database
                cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
                result = cursor.fetchone()

                if result:
                    hashed_password_from_db = result[0]
                    # Check if the provided password matches the hashed password from the database
                    if check_password_hash(hashed_password_from_db, password):
                        return redirect(url_for('quiz_menu'))
                    else:
                        return "Incorrect password. Please try again."

                else:
                    return "Username not found. Please register."

        except mysql.connector.Error as e:
            return f"Error: {e}"

        finally:
            if 'connection' in locals() and connection.is_connected():
                connection.close()

    # If it's a GET request, render the login form
    return render_template('login.html')

@app.route('/quiz_menu')
def quiz_menu():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            # Fetch all quizzes from the database
            cursor.execute("SELECT id, title, description FROM quizzes")
            quizzes = cursor.fetchall()

            return render_template('quiz_menu.html', quizzes=quizzes)

    except mysql.connector.Error as e:
        return f"Error: {e}"

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)