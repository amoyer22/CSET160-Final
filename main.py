from flask import Flask, render_template, request, redirect
from sqlalchemy import create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:cset155@localhost/tests"
engine = create_engine(conn_str)
conn = engine.connect()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            result = conn.execute(text("SELECT * FROM users WHERE username = :username AND password = :password"),
                                {"username": username, "password": password}).first()
            if result:
                user_type = result[3]
                student_id = result[0]
                if user_type == 'teacher':
                    return redirect(f'/home/teachers?username={username}')
                elif user_type == 'student':
                    return redirect(f'/home/students?student_id={student_id}')
            else:
                message = "ERROR: Invalid entry. Try again."
        except:
            message = "ERROR: Invalid entry. Try again."
    return render_template('login.html', message=message)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['type']
        try:
            conn.execute(text("INSERT INTO users (username, password, type) VALUES (:username, :password, :type)"),
                        {"username": username, "password": password, "type": user_type})
            conn.commit()
            message = "Sign up successful."
        except:
            message = "ERROR: Sign up failed. Try again."
    return render_template('signup.html', message=message)

@app.route('/home/students')
def studenthome():
    student_id = request.args.get('student_id')
    message = request.args.get('message')
    tests = conn.execute(text("""
        SELECT t.*, 
               (SELECT COUNT(*) FROM test_attempts WHERE test_attempts.test_id = t.id) AS student_count,
               EXISTS (SELECT 1 FROM test_attempts WHERE test_attempts.test_id = t.id AND test_attempts.student_id = :student_id) AS has_taken
        FROM tests t
    """), {"student_id": student_id}).all()
    return render_template('student_home.html', tests=tests, student_id=student_id, message=message)

@app.route('/home/students/accounts')
def studentaccounts():
    user_type = request.args.get('type', 'all')
    if user_type == 'students':
        result = conn.execute(text("SELECT * FROM users WHERE type='student'")).all()
    elif user_type == 'teachers':
        result = conn.execute(text("SELECT * FROM users WHERE type='teacher'")).all()
    else:
        result = conn.execute(text("SELECT * FROM users")).all()
    return render_template('student_accs.html', users=result)

@app.route('/home/teachers', methods=['GET', 'POST'])
def teacherhome():
    if request.method == 'POST':
        test_id = request.form.get('delete_test_id')
        if test_id:
            conn.execute(text("DELETE FROM questions WHERE test_id = :test_id"), {"test_id": test_id})
            conn.execute(text("DELETE FROM tests WHERE id = :id"), {"id": test_id})
            conn.commit()
    username = request.args.get('username')
    tests = conn.execute(text("""
        SELECT t.*, 
               (SELECT COUNT(*) FROM test_attempts WHERE test_attempts.test_id = t.id) AS student_count
        FROM tests t
    """)).all()
    return render_template('teacher_home.html', tests=tests, username=username)

@app.route('/home/teachers/accounts')
def teacheraccounts():
    user_type = request.args.get('type', 'all')
    if user_type == 'students':
        result = conn.execute(text("SELECT * FROM users WHERE type='student'")).all()
    elif user_type == 'teachers':
        result = conn.execute(text("SELECT * FROM users WHERE type='teacher'")).all()
    else:
        result = conn.execute(text("SELECT * FROM users")).all()
    return render_template('teacher_accs.html', users=result)

@app.route('/tests/take')
def teststake():
    test_id = request.args.get('id')
    student_id = request.args.get('student_id')
    has_taken = conn.execute(text("""
        SELECT 1 FROM test_attempts WHERE test_id = :test_id AND student_id = :student_id
    """), {"test_id": test_id, "student_id": student_id}).first()
    if has_taken:
        return redirect(f'/home/students?student_id={student_id}&message=already_taken')
    test = conn.execute(text("SELECT * FROM tests WHERE id = :id"), {"id": test_id}).all()
    questions = conn.execute(text("SELECT * FROM questions WHERE test_id = :test_id"), {"test_id": test_id}).all()
    return render_template('tests_take.html', test=test, questions=questions, student_id=student_id)

@app.route('/tests/submit', methods=['POST'])
def testssubmit():
    test_id = request.form.get('test_id')
    student_id = request.args.get('student_id')
    answers = request.form.to_dict(flat=False)
    if not test_id or not student_id:
        return "ERROR: Missing test_id or student_id."
    try:
        for question_id, answer_text in answers.items():
            if question_id.startswith("answers["):
                question_id = question_id[8:-1]
                conn.execute(
                    text("INSERT INTO answers (test_id, question_id, student_id, answer_text) VALUES (:test_id, :question_id, :student_id, :answer_text)"),
                    {"test_id": int(test_id), "question_id": int(question_id), "student_id": int(student_id), "answer_text": answer_text[0]}
                )
        conn.execute(
            text("INSERT INTO test_attempts (test_id, student_id) VALUES (:test_id, :student_id)"),
            {"test_id": int(test_id), "student_id": int(student_id)}
        )
        conn.commit()
        return redirect('/home/students')
    except:
        return "ERROR: Could not submit answers."

@app.route('/tests/create', methods=['GET', 'POST'])
def testscreate():
    message = None
    username = request.args.get('username')
    if request.method == 'POST':
        test_name = request.form['test_name']
        creator = request.form['creator']
        questions = request.form.getlist('questions[]')
        points = request.form.getlist('points[]')
        try:
            existing_test = conn.execute(text("SELECT * FROM tests WHERE name = :name"), {"name": test_name}).first()
            if existing_test:
                message = "ERROR: A test with this name already exists."
            else:
                result = conn.execute(text("INSERT INTO tests (name, creator) VALUES (:name, :creator)"),
                                    {"name": test_name, "creator": creator})
                test_id = result.lastrowid
                for question, point in zip(questions, points):
                    conn.execute(text("INSERT INTO questions (test_id, question_text, points) VALUES (:test_id, :question_text, :points)"),
                                {"test_id": test_id, "question_text": question, "points": point})
                conn.commit()
                message = "Test created successfully."
        except:
            message = "ERROR: Could not create test."
    return render_template('tests_create.html', message=message, username=username)

@app.route('/tests/edit', methods=['GET', 'POST'])
def testsedit():
    test_id = request.args.get('id')
    message = None
    if request.method == 'POST':
        test_name = request.form['test_name']
        questions = request.form.getlist('questions[]')
        points = request.form.getlist('points[]')
        try:
            conn.execute(text("UPDATE tests SET name = :name WHERE id = :id"),
                         {"name": test_name, "id": test_id})
            conn.execute(text("DELETE FROM questions WHERE test_id = :test_id"), {"test_id": test_id})
            for question, point in zip(questions, points):
                conn.execute(text("INSERT INTO questions (test_id, question_text, points) VALUES (:test_id, :question_text, :points)"),
                             {"test_id": test_id, "question_text": question, "points": point})
            conn.commit()
            message = "Test updated successfully."
        except:
            message = "ERROR: Could not update test."
    test = conn.execute(text("SELECT * FROM tests WHERE id = :id"), {"id": test_id}).first()
    questions = conn.execute(text("SELECT * FROM questions WHERE test_id = :test_id"), {"test_id": test_id}).all()
    return render_template('tests_edit.html', test=test, questions=questions, message=message)

@app.route('/tests/grade')
def testsgrade():
    return render_template('tests_grade.html')

if __name__ == '__main__':
    app.run(debug=True)