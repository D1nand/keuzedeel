from config import host, user, password, database
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import check_password_hash
import mysql.connector

DB_CONFIG = {
    'host': host,
    'user': user,
    'password': password,
    'database': database
}

app = Flask(__name__)

def authenticate_user(username, password):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Fetch hashed password from the database
            query = f"SELECT * FROM users WHERE username = '{username}'"
            cursor.execute(query)
            user_data = cursor.fetchone()

            if user_data and check_password_hash(user_data['password'], password):
                return True

    except mysql.connector.Error as e:
        print(f"Error: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if authenticate_user(username, password):
            # Redirect to a dashboard or home page on successful login
            return redirect(url_for('quiz_menu'))
        else:
            # Provide an error message on unsuccessful login
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

# ... (previous code)

@app.route('/quiz_menu')
def quiz_menu():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Fetch quiz data from the database
            query = "SELECT * FROM quiz"
            cursor.execute(query)
            quiz = cursor.fetchall()

            return render_template('quiz_menu.html', quizzes=quiz)

    except mysql.connector.Error as e:
        print(f"Error: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return render_template('quiz_menu.html', quizzes=None)
# ... (previous code)

@app.route('/quiz_task/<int:quiz_id>')
def quiz_task(quiz_id):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Fetch the first question for the given quiz_id
            query = f"SELECT * FROM quiztask WHERE quiz_id = {quiz_id} ORDER BY id LIMIT 1"
            cursor.execute(query)
            first_question = cursor.fetchone()

            return render_template('quiz_task.html', quiz_task_details=[first_question])

    except mysql.connector.Error as e:
        print(f"Error: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return render_template('quiz_task.html', quiz_task_details=None)

@app.route('/quiz_task/<int:quiz_id>/<int:question_id>')
def quiz_task_detail(quiz_id, question_id):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Fetch the current question details
            query = f"SELECT * FROM quiztask WHERE quiz_id = {quiz_id} AND id = {question_id}"
            cursor.execute(query)
            current_question = cursor.fetchone()

            # Check if the current question has been answered
            current_question['answered'] = request.args.get('answered') == 'True'

            return render_template('quiz_task.html', quiz_task_details=[current_question])

    except mysql.connector.Error as e:
        print(f"Error: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return render_template('quiz_task.html', quiz_task_details=None)



if __name__ == '__main__':
    app.run(debug=True)
