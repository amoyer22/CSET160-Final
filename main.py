from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tests')
def testshome():
    return render_template('tests_home.html')

@app.route('/tests/create')
def testscreate():
    return render_template('tests_create.html')

if __name__ == '__main__':
    app.run(debug=True)