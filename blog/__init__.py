# coding=utf-8

import os
import json

from flask import Flask, render_template, redirect, request

from config import Config

CONF_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = Config(os.path.join(CONF_DIR, 'conf'), 'blog.ini').conf('blog')

with open(BLOG['topics_json'], 'r') as json_file:
    TOPIC_DICT = json.load(json_file)

CAT_DICT = {
    "linux": {"linux": ["basic",
                        "advance",
                        "service",
                        "lnmp",
                        "shell",
                        "java_env"]},
    "python": {"python": ["advance",
                          "django",
                          "flask"]},
    "javascript": {"javascript": ["basic",
                                  "jquery",
                                  "node.js"]},
    "database": {"database": ["mysql",
                              "oracle"]},
    "devops": {"devops": ["vagrant",
                          "git",
                          "ansible"]},
    "virtualization": {"virtualization":["docker",
                                         "container",
                                         "kvm"]},
    }
HREF_LIST = [x for x in CAT_DICT]

app = Flask(__name__)


# @app.route('/')
# def index():
#     return redirect('/home',
#                     HREF_LIST=HREF_LIST,
#                     code=302)


# @app.route('/home')
@app.route('/')
def homepage():
    return render_template("base/home.html",
                            TOPIC_DICT=TOPIC_DICT,
                            HREF_LIST=HREF_LIST)


@app.route('/<cat>')
def cat(cat):
    uri_cat = request.full_path.split('/')[1].split('?')[0]
    cat = CAT_DICT[uri_cat].keys()[0]
    sub_cats = CAT_DICT[uri_cat][cat]
    print cat
    return render_template("base/categories_base.html",
                           TOPIC_DICT=TOPIC_DICT,
                           HREF_LIST=HREF_LIST,
                           cat=cat,
                           sub_cats=sub_cats)


@app.route('/<cat1>/<cat2>')
def sub_content(cat1, cat2):
    page = '/'.join([cat1, cat2])
    uri_cat = request.full_path.split('/')[1].split('?')[0]
    uri_subcat = request.full_path.split('/')[2].split('?')[0]
    cat = CAT_DICT[uri_cat].keys()[0]
    sub_cats = CAT_DICT[uri_cat][cat]
    return render_template("base/sub_categories_base.html",
                           TOPIC_DICT=TOPIC_DICT,
                           HREF_LIST=HREF_LIST,
                           uri_subcat=uri_subcat,
                           cat=cat,
                           sub_cats=sub_cats)


@app.route('/<cat1>/<cat2>/<topic>.html')
def content(cat1, cat2, topic):
    topic = topic + ".html"
    page = '/'.join([cat1, cat2, topic])

    uri_cat = request.full_path.split('/')[1].split('?')[0]
    uri_subcat = request.full_path.split('/')[2].split('?')[0]
    cat = CAT_DICT[uri_cat].keys()[0]
    sub_cats = CAT_DICT[uri_cat][cat]
    return render_template(page,
                           TOPIC_DICT=TOPIC_DICT,
                           HREF_LIST=HREF_LIST,
                           uri_subcat=uri_subcat,
                           cat=cat,
                           sub_cats=sub_cats)


@app.route('/contact')
def contact():
    return render_template("base/contact.html",
                           HREF_LIST=HREF_LIST,
                           TOPIC_DICT=TOPIC_DICT)