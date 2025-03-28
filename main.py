from flask import Flask, render_template, request, redirect
from sqlalchemy import create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:cset155@localhost/testsdb"
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
            user_type = result[3]
            if result:
                if user_type == 'teacher':
                    return redirect('/home/teachers')
                elif user_type == 'student':
                    return redirect('/home/students')
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

@app.route('/home/teachers')
def teacherhome():
    return render_template('teacher_home.html')

@app.route('/home/students')
def studenthome():
    return render_template('student_home.html')

@app.route('/accounts')
def accounts():
    result = conn.execute(text("SELECT * FROM users")).all()
    return render_template('acc.html', users=result)

@app.route('/tests/create')
def testscreate():
    return render_template('tests_create.html')

if __name__ == '__main__':
    app.run(debug=True)