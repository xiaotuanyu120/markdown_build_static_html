# coding=utf-8

import os
import json

from flask import Flask, render_template, redirect, request, url_for
from flask import send_from_directory

from config import Config

# get config file
CONF_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = Config(os.path.join(CONF_DIR, 'conf'), 'blog.ini').conf('blog')

# config variables
with open(BLOG['topics_json'], 'r') as json_file:
    TOPIC_DICT = json.load(json_file)

with open(BLOG['index_json_file'], 'r') as json_file:
    INDEX_JSON = json.load(json_file)

CAT_DICT = {}
for i in INDEX_JSON:
    base_cat = INDEX_JSON[i]["base_cat"]
    if not base_cat in CAT_DICT.keys():
        CAT_DICT[base_cat] = []
    sub_cat = INDEX_JSON[i]["sub_cat"]
    if not sub_cat in CAT_DICT[base_cat]:
        CAT_DICT[base_cat].append(sub_cat)

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template("base/home.html",
                            TOPIC_DICT=TOPIC_DICT)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='images/favicon.ico')


@app.route('/<cat>')
def cat(cat):
    sub_cats = CAT_DICT[cat]
    return render_template("base/categories_base.html",
                           TOPIC_DICT=TOPIC_DICT,
                           cat=cat,
                           sub_cats=sub_cats)


@app.route('/<cat1>/<cat2>')
def sub_content(cat1, cat2):
    sub_cats = CAT_DICT[cat1]
    return render_template("base/sub_categories_base.html",
                           TOPIC_DICT=TOPIC_DICT,
                           uri_subcat=cat2,
                           cat=cat1,
                           sub_cats=sub_cats)


@app.route('/<cat1>/<cat2>/<topic>.html')
def content(cat1, cat2, topic):
    topic = topic + ".html"
    page = '/'.join([cat1, cat2, topic])
    sub_cats = CAT_DICT[cat1]
    return render_template(page,
                           TOPIC_DICT=TOPIC_DICT,
                           uri_subcat=cat2,
                           cat=cat1,
                           sub_cats=sub_cats)


@app.route('/contact')
def contact():
    return render_template("base/contact.html",
                           TOPIC_DICT=TOPIC_DICT)
