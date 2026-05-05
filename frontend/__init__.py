from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/reader/<int:book_id>')
def reader(book_id):
    return render_template('reader.html', book_id=book_id)
