from flask import Flask, render_template
from topics import topics

TOPIC_DICT = topics()

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template("home.html", TOPIC_DICT = TOPIC_DICT)


@app.route('/linux')
def linux():
    return render_template("linux_basic.html", TOPIC_DICT = TOPIC_DICT)


@app.route('/python')
def python():
    return render_template("python_advance.html", TOPIC_DICT = TOPIC_DICT)


@app.route('/django')
def django():
    return render_template("python_django.html", TOPIC_DICT = TOPIC_DICT)


@app.route('/mysql')
def mysql():
    return render_template("linux_mysql.html", TOPIC_DICT = TOPIC_DICT)


@app.route('/html/<cat1>/<cat2>/<topic>')
def content(cat1, cat2, topic):
    page = '/'.join(['/html', cat1, cat2, topic])
    return render_template(page, TOPIC_DICT = TOPIC_DICT)


@app.route('/contact')
def contact():
    return render_template("contact.html", TOPIC_DICT = TOPIC_DICT)
