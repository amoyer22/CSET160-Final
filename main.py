from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:cset155@localhost/testsdb"
engine = create_engine(conn_str)
conn = engine.connect()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

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

@app.route('/tests')
def testshome():
    return render_template('tests_home.html')

@app.route('/tests/create')
def testscreate():
    return render_template('tests_create.html')

@app.route('/tests/edit')
def testsedit():
    return render_template('tests_edit.html')

@app.route('/tests/delete')
def testsdelete():
    return render_template('tests_delete.html')

if __name__ == '__main__':
    app.run(debug=True)