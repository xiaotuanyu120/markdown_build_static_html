from flask import Flask, render_template, redirect
from topics import topics

TOPIC_DICT = topics()
# CAT_DICT = {"linux":["basic", "advance", "commonly_services"],
#             "python":["basic", "advance"],
#             "javascript":["node.js"],
#             "django":["basic", "devops"],
# }
CAT_DICT = {"linux":{"linux":["basic", "advance", "commonly_services"]},
            "python":{"python":["basic", "advance"]},
            "javaenv":{"linux":["java_env"]},
            "javascript":{"javascript":["node.js"]},
            "django":{"django":["basic", "devops"]},
            "flask":{"python":["flask"]},
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
