from flask import Flask, render_template, redirect
from topics import topics

TOPIC_DICT = topics()
CAT_DICT = {
    "linux": {"linux": ["basic", "advance", "service", "lnmp", "shell"]},
    "python": {"python": ["advance", "django", "flask"]},
    "java_env": {"linux": ["java_env"]},
    "javascript": {"javascript": ["basic", "jquery", "node.js"]},
    "database": {"database": ["mysql", "oracle"]},
    "devops": {"devops": ["vagrant"]},
    }

app = Flask(__name__)


@app.route('/')
def index():
    return redirect('/home', code=302)


@app.route('/home')
def homepage():
    return render_template("base/home.html", TOPIC_DICT=TOPIC_DICT)


@app.route('/<cat>')
def cat(cat):
    return render_template("base/categories_base.html",
                           TOPIC_DICT=TOPIC_DICT,
                           CAT_DICT=CAT_DICT)


@app.route('/<cat1>/<cat2>/<topic>.html')
def content(cat1, cat2, topic):
    topic = topic + ".html"
    page = '/'.join([cat1, cat2, topic])
    return render_template(page, TOPIC_DICT=TOPIC_DICT)


@app.route('/contact')
def contact():
    return render_template("base/contact.html", TOPIC_DICT=TOPIC_DICT)
