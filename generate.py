# -*- coding: utf-8 -*-
import os
import re

import mistune
import codecs
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html


class HighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % \
                mistune.escape(code)
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = html.HtmlFormatter()
        return highlight(code, lexer, formatter)


class MdGenerator(object):
    def __init__(self, md_dir=None, html_dir=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_md_dir = base_dir + "/MyBlog/post"
        self.md_dir = md_dir or default_md_dir

        # ensure md_dir is absolute path, if not, make current dir as root dir of md_dir
        self.md_dir = self.md_dir if os.path.isabs(self.md_dir) else '/'.join([base_dir, self.md_dir])

        # ensure md_dir exist and not a file
        if not os.path.isdir(self.md_dir):
            if os.path.isfile(self.md_dir):
                return "md_dir should be dir"
            else:
                os.makedirs(self.md_dir)

        default_html_dir = base_dir + "/MyBlog/templates/html"
        self.html_dir = html_dir or default_html_dir

        # ensure html_dir is absolute path, if not, make current dir as root dir of md_dir
        self.html_dir = self.html_dir if os.path.isabs(self.html_dir) else '/'.join([base_dir, self.html_dir])

        # ensure html_dir exist and not a file
        if not os.path.isdir(self.html_dir):
            if os.path.isfile(self.html_dir):
                return "html_dir should be dir"
            else:
                os.makedirs(self.html_dir)

        self.md_info = {}
        self.topics_file = base_dir + '/MyBlog/topics.py'

    def collect_md_info(self):
        '''
        get *.md file list
        '''
        md_dir = self.md_dir
        for root,sub_dirs,md_file_names in os.walk(md_dir):
            for md_file_name in md_file_names:
                md_name_splits = md_file_name.split('.')
                if len(md_name_splits) > 1 and md_name_splits[-1] == "md":
                    md_complete_name = "%s/%s" % (root, md_file_name)
                    html_file_name = md_file_name.rsplit(".md")[0] + ".html"
                    self.md_info[md_complete_name] = {}
                    self.md_info[md_complete_name]["md_file_name"] = md_file_name
                    self.md_info[md_complete_name]["md_path_name"] = root
                    self.md_info[md_complete_name]['html_file_name'] = html_file_name
                    self.md_info[md_complete_name]["html_path_name"] = ""
                    self.md_info[md_complete_name]["html_complete_name"] = ""
                    self.md_info[md_complete_name]['categories_error'] = ""
                    self.md_info[md_complete_name]['header_error'] = ""
                    self.md_info[md_complete_name]["generate_error"] = ""

    def _header_parse(self, md_complete_name):
        with open(md_complete_name, 'r') as f:
            # headers totally is 4
            # first "---" means start
            # second "---" means end
            row_num = 0
            header_list = ['title', 'date', 'categories', 'tags']
            result = {}
            error = ""
            for row in f.readlines():
                # check stop singnal
                if error:
                    break
                # skip space row
                if row.strip() == "":
                    continue
                row_num += 1
                if row_num == 1:
                    if not row.strip() == "---":
                        result = {}
                        error = "Missing header start tag: '---'!"
                        continue
                elif 1 < row_num < 6:
                    if not ":" in row:
                        result = {}
                        error = "Missing header seperate tag: ':'!"
                        continue
                    key, value = row.strip().split(":", 1)
                    header_key = key.strip()
                    header_value = value.strip()
                    if not header_key in header_list:
                        result = {}
                        error = "Invaild header(%s)!" % header_key
                        continue
                    else:
                        result[header_key] = header_value
                        header_list.remove(header_key)
                elif row_num == 6:
                    if not row.strip() == "---":
                        result = {}
                        error = "Missing header end tag: '---'!"
                        continue
                    else:
                        error = ""
                        break
                else:
                    print "The end of the world!"
                    break
            self.md_info[md_complete_name]['headers'] = result
            self.md_info[md_complete_name]['header_error'] = error

    def _categories_check(self, md_complete_name, categories):
        error = ""
        if categories == '':
            error = "Categories should not be blank!"
        if not len(categories.split('/')) == 2:
            error = "Wrong categories syntax! should be 2 level!"
        self.md_info[md_complete_name]['categories_error'] = error

    def _get_md_content(self, md_complete_name):
        with open(md_complete_name, 'r') as f:
            row_num = 0
            content = []
            for line in f.readlines():
                if line.strip() == "":
                    content.append(line)
                    continue
                row_num += 1
                if row_num > 6:
                    content.append(line)
            result = ''.join(content)
            return result

    def _generate_html(self, md_content, renderer):
        try:
            md_content = unicode(md_content, 'utf-8')
            html_content = mistune.Markdown(renderer=renderer)(md_content)
        except TypeError as e:
            self.md_info[md_complete_name]["generate_error"] = str(e)
            return
        return html_content

    def md_generate(self):
        md_complete_names = self.md_info.keys()
        for md_complete_name in md_complete_names:

            # parse and check header
            self._header_parse(md_complete_name)

            if self.md_info[md_complete_name]['header_error']:
                del self.md_info[md_complete_name]
                continue

            categories = self.md_info[md_complete_name]['headers']['categories']

            self._categories_check(md_complete_name, categories)
            if self.md_info[md_complete_name]["categories_error"]:
                continue

            # get the path html should stored in
            self.md_info[md_complete_name]["html_path_name"] = self.html_dir + '/' + categories
            html_path_name = self.md_info[md_complete_name]["html_path_name"]
            html_file_name = self.md_info[md_complete_name]["html_file_name"]
            self.md_info[md_complete_name]['html_complete_name'] = html_path_name + "/" + html_file_name
            html_complete_name = self.md_info[md_complete_name]["html_complete_name"]
            if not os.path.isdir(html_path_name):
                os.makedirs(html_path_name)

            # if html_file exist and newer than md file, skip generate it
            if os.path.isfile(html_complete_name):
                html_mtime = os.path.getmtime(html_complete_name)
                md_mtime = os.path.getmtime(md_complete_name)
                mtime_compare = md_mtime - html_mtime
                if mtime_compare <= 0:
                    continue

            md_content = self._get_md_content(md_complete_name)
            renderer = HighlightRenderer()
            content = self._generate_html(md_content, renderer)
            if content:
                with codecs.open(html_complete_name, 'w', encoding='utf8') as f:
                    extend_file = 'categories_base.html'
                    begin_template = "{% extends '" + extend_file + "' %}\n{% block md %}\n"
                    end_template = "{% endblock %}"
                    content = begin_template + content + end_template
                    f.write(content)
            else:
                print md_file + "(error to generate)"

    def _tryint(self, input):
        try:
            return int(input)
        except:
            return input

    def _sort_key(self, in_list):
        return [ self._tryint(c) for c in re.split('([0-9]+)', in_list[0]) ]

    def _html_cat_parse(self, md_info):
        index = {}
        for md_complete_name in md_info.keys():
            title = unicode(md_info[md_complete_name]['headers']['title'], 'utf-8')
            categories = md_info[md_complete_name]['headers']['categories']
            html_file_name = md_info[md_complete_name]['html_file_name']
            html_url_name = '/html/%s/%s' % (categories, html_file_name)
            html_path = unicode(html_url_name, 'utf-8')
            root_cat, sub_cat = categories.split('/')
            if not root_cat in index.keys():
                index[root_cat] = {}
            if not sub_cat in index[root_cat].keys():
                index[root_cat][sub_cat] = []
            index[root_cat][sub_cat].append([title, html_path])
            index[root_cat][sub_cat].sort(key = self._sort_key)
        result = str(index).replace(']', ']\n    ')
        return result

    def topic_index(self):
        index = self._html_cat_parse(self.md_info)
        topics_def_temp = "def topics():\n    topics = "
        topics_def_end = "\n    return topics"
        topics_def = topics_def_temp + index + topics_def_end
        with open(self.topics_file, 'w') as f:
            f.write(topics_def)


if __name__ == "__main__":
    markdown_generator = MdGenerator()
    markdown_generator.collect_md_info()
    markdown_generator.md_generate()
    markdown_generator.topic_index()
