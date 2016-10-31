from flask import Flask, render_template
from topics import topics

TOPIC_DICT = topics()

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("index.html", TOPIC_DICT = TOPIC_DICT)

@app.route('/html/<cat1>/<cat2>/<topic>')
def content(cat1, cat2, topic):
    page = '/'.join(['/html', cat1, cat2, topic])
    return render_template(page)
