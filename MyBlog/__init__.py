from flask import Flask, render_template
from cms import content
from topics import topics

TOPIC_DICT = topics()

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("index.html", TOPIC_DICT = TOPIC_DICT)


@app.route('/linux_basic')
def linux_basic():
    return render_template("linux_basic.html")
