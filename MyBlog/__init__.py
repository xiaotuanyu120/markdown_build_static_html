from flask import Flask, render_template
from cms import content

TOPIC_DICT = content()

app = Flask(__name__)

@app.route('/')
def homepage():
    home_active = "active"
    return render_template("index.html", home_active = home_active)


@app.route('/linux_basic')
def linux_basic():
    linux_active = "active"
    linux_basic = "active"
    return render_template("linux_basic.html",
                            linux_active = linux_active,
                            linux_basic = linux_basic,
                            TOPIC_DICT = TOPIC_DICT)
