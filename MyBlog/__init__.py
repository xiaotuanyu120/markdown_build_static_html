from flask import Flask, render_template, redirect
from topics import topics

TOPIC_DICT = topics()
CAT_DICT = {"linux":["basic", "commonly_services"],
            "python":["basic", "advance"],
            "javascript":["node.js"],
            "django":["basic", "devops"],
}

app = Flask(__name__)


@app.route('/')
def index():
    return redirect('/home', code=302)

@app.route('/home')
def homepage():
    return render_template("home.html", TOPIC_DICT = TOPIC_DICT)


@app.route('/<cat>')
def cat(cat):
    return render_template("categories_base.html", TOPIC_DICT = TOPIC_DICT, CAT_DICT = CAT_DICT)


@app.route('/html/<cat1>/<cat2>/<topic>')
def content(cat1, cat2, topic):
    page = '/'.join(['/html', cat1, cat2, topic])
    return render_template(page, TOPIC_DICT = TOPIC_DICT)


@app.route('/contact')
def contact():
    return render_template("contact.html", TOPIC_DICT = TOPIC_DICT)
