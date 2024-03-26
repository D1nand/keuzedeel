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
            return redirect(url_for('quiz_menu'))
        else:
            # Provide an error message on unsuccessful login
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/quiz_menu')
def quiz_menu():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Fetch quiz data from the database
            query = "SELECT * FROM quiz"
            cursor.execute(query)
            quizzes = cursor.fetchall()

            # Fetch only the first quiz task for each quiz and store it in the dictionary
            quiz_tasks_dict = {}
            for quiz in quizzes:
                quiz_id = quiz['id']
                query2 = f"SELECT * FROM quiztask WHERE quiz_id = {quiz_id} LIMIT 1"
                cursor.execute(query2)
                first_question = cursor.fetchone()
                quiz_tasks_dict[quiz_id] = first_question

            return render_template('quiz_menu.html', quizzes=quizzes, quiz_tasks_dict=quiz_tasks_dict)

    except mysql.connector.Error as e:
        print(f"Error: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return render_template('quiz_menu.html', quizzes=None, quiz_tasks_dict=None)


# ... (other imports and configurations)

@app.route('/add_quiz', methods=['GET', 'POST'])
def add_quiz():
    if request.method == 'POST':
        quizname = request.form['quizname']
        tasks = request.form.getlist('tasks[]')
        correct_answers = request.form.getlist('correctAnswers[]')
        
        # Retrieve answers for each task
        answers = []
        for task_index, task in enumerate(tasks, start=1):
            answer_list = []
            for answer_index in range(1, 5):
                answer = request.form.get(f'answers[{task_index}][{answer_index}]', '')
                answer_list.append(answer.strip())  # Remove leading/trailing whitespaces
            answers.append(answer_list)

        try:
            connection = mysql.connector.connect(**DB_CONFIG)

            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)

                # Insert the new quiz into the database
                query_insert_quiz = "INSERT INTO quiz (quizname) VALUES (%s)"
                cursor.execute(query_insert_quiz, (quizname,))
                connection.commit()

                # Fetch the last inserted quiz_id
                cursor.execute("SELECT LAST_INSERT_ID() as quiz_id")
                quiz_id = cursor.fetchone()['quiz_id']

                # Insert tasks and answers into the quiztask table
                for task_index, task in enumerate(tasks, start=1):
                    answer_list = answers[task_index - 1]

                    # Ensure that answer_list has at least four elements, filling any missing elements with an empty string
                    while len(answer_list) < 4:
                        answer_list.append('')

                    answer1, answer2, answer3, answer4 = answer_list[:4]

                    # Get the correct answer index
                    correct_answer_index = int(correct_answers[task_index - 1])

                    query_insert_task = "INSERT INTO quiztask (quiz_id, question, Answer1, Answer2, Answer3, Answer4, correctAnswer) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(query_insert_task, (quiz_id, task, answer1, answer2, answer3, answer4, correct_answer_index))
                    connection.commit()

                # Redirect to the quiz menu or wherever you want
                return redirect(url_for('quiz_menu'))

        except mysql.connector.Error as e:
            print(f"Error: {e}")

        finally:
            if 'connection' in locals() and connection.is_connected():
                connection.close()

    return render_template('add_quiz.html')
@app.route('/quiz_task/<int:quiz_id>/<int:question_id>', methods=['GET', 'POST'])
def quiz_task_detail(quiz_id, question_id):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            if request.method == 'POST':
                # Logic to handle the Next button click
                query = f"SELECT * FROM quiztask WHERE quiz_id = {quiz_id} AND id > {question_id} ORDER BY id ASC LIMIT 1"
                cursor.execute(query)
                next_question = cursor.fetchone()

                if next_question:
                    next_question_id = next_question['id']
                    print(f"Next Question ID (POST): {next_question_id}")
                    return render_template('quiz_task.html', quiz_task_details=[next_question, quiz_id, next_question_id])
                else:
                    # No more questions, redirect to a page indicating all questions are answered
                    return redirect(url_for('all_questions_answered'))

            # Fetch the current question details for GET request
            query = f"SELECT * FROM quiztask WHERE quiz_id = {quiz_id} AND id = {question_id}"
            cursor.execute(query)
            current_question = cursor.fetchone()

            # Check if the current question has been answered
            current_question['answered'] = request.args.get('answered') == 'True'

            print(f"Current Question ID: {question_id}")

            # Check if there are no more questions left for the quiz
            query_remaining = f"SELECT COUNT(*) AS remaining FROM quiztask WHERE quiz_id = {quiz_id} AND id > {question_id}"
            cursor.execute(query_remaining)
            remaining_questions = cursor.fetchone()['remaining']

            if remaining_questions == 0:
                # No more questions, redirect to a page indicating all questions are answered
                return redirect(url_for('all_questions_answered'))

            return render_template('quiz_task.html', quiz_task_details=[current_question, quiz_id, question_id])

    except mysql.connector.Error as e:
        print(f"Error: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return render_template('quiz_task.html', quiz_task_details=None)

# New route for when all questions are answered
@app.route('/all_questions_answered')
def all_questions_answered():
    return render_template('all_questions_answered.html')

if __name__ == '__main__':
    app.run(debug=True)
