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
        # md_dir: for store markdown file
        # html_dir: for store generated html file
        # md_info: for store md file's information, such as "path","categories" etc.
        # topics_file: for store {categories:generated_html_path}

        base_dir = os.path.dirname(os.path.abspath(__file__))
        # <<<<<<<<<<<<<<<<<<<<<<
        # set md_dir or default md_dir
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

        # >>>>>>>>>>>>>>>>>>>>>>
        # if not md_dir:
        #     self.md_dir = base_dir + "/MyBlog/post"
        # else:
        #     if os.path.isdir(md_dir):
        #         self.md_dir = md_dir
        #     else:
        #         print "content path doesn't exist!"
        #################################

        # <<<<<<<<<<<<<<<<<<<<<<
        # set html_dir or default html_dir
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
        # >>>>>>>>>>>>>>>>>>>>>>
        # if not html_dir:
        #     self.html_dir = base_dir + "/MyBlog/templates/html"
        # else:
        #     if os.path.isdir(html_dir):
        #         self.html_dir = html_dir
        #     else:
        #         os.makedirs(html_dir)
        #################################

        self.md_info = {}
        self.topics_file = base_dir + '/MyBlog/topics.py'

    def collect_md_info(self):
        '''
        get *.md file list
        '''
        # <<<<<<<<<<<<<<<<<<
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


        # >>>>>>>>>>>>>>>>>>
        # files = os.listdir(md_dir)
        # md_files = [x for x in files if x.split('.')[-1] == 'md']
        # return md_files_info
        ######################

    def _header_parse(self, md_complete_name):
        with open(md_complete_name, 'r') as f:
            # headers totally is 4
            # first "---" means start
            # second "---" means end
            row_num = 0
            header_list = ['title', 'date', 'categories', 'tags']
            result = {}
            error = ""
            # content = []
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
                        # <<<<<<<<<<<<<<<<
                        result = {}
                        error = "Missing header start tag: '---'!"
                        continue
                        # >>>>>>>>>>>>>>>>
                        # print md_file + "(Missing header start tag: '---'!)"
                        # return
                elif 1 < row_num < 6:
                    if not ":" in row:
                        # <<<<<<<<<<<<<<<<
                        result = {}
                        error = "Missing header seperate tag: ':'!"
                        continue
                        # >>>>>>>>>>>>>>>>
                        # print md_file + "(Missing header seperate tag: ':'!)"
                        # return
                    key, value = row.strip().split(":", 1)
                    header_key = key.strip()
                    header_value = value.strip()
                    if not header_key in header_list:
                        # <<<<<<<<<<<<<<<<
                        result = {}
                        error = "Invaild header(%s)!" % header_key
                        continue
                        # >>>>>>>>>>>>>>>>
                        # print md_file + "(Invaild header!)"
                        # return
                    else:
                        result[header_key] = header_value
                        header_list.remove(header_key)
                elif row_num == 6:
                    if not row.strip() == "---":
                        # <<<<<<<<<<<<<<<<
                        result = {}
                        error = "Missing header end tag: '---'!"
                        continue
                        # >>>>>>>>>>>>>>>>
                        # print md_file + "(Missing header end tag: '---'!)"
                        # return
                    else:
                        # <<<<<<<<<<<<<<<<
                        error = ""
                        break
                        # >>>>>>>>>>>>>>>>
                        # return result
                else:
                    print "The end of the world!"
                    break
            self.md_info[md_complete_name]['headers'] = result
            self.md_info[md_complete_name]['header_error'] = error

    def _categories_check(self, md_complete_name, categories):
        error = ""
        if categories == '':
            error = "Categories should not be blank!"
            # print md_file + "(Categories should not be blank!)"
            # return
        if not len(categories.split('/')) == 2:
            error = "Wrong categories syntax! should be 2 level!"
            # print md_file + "(Wrong categories syntax! should be 2 level!)"
            # return
        self.md_info[md_complete_name]['categories_error'] = error

    def _get_md_content(self, md_complete_name):
        with open(md_complete_name, 'r') as f:
            row_num = 0
            content = []
            for line in f.readlines():
                # skip space line
                if line.strip() == "":
                    # content.append(line)
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
        #except (UnicodeDecodeError, TypeError) as e:
        except TypeError as e:
            self.md_info[md_complete_name]["generate_error"] = str(e)
            # print "STOP PROCESSING: " + str(e)
            return
        return html_content

    def md_generate(self):
        md_complete_names = self.md_info.keys()
        for md_complete_name in md_complete_names:

            # parse and check header
            self._header_parse(md_complete_name)


            # <<<<<<<<<<<<<<<<<<
            if self.md_info[md_complete_name]['header_error']:
            # >>>>>>>>>>>>>>>>>>
            # if not md_header:
                continue

            # check categories's syntax and prepare categories folder
            # <<<<<<<<<<<<<<<<<<
            categories = self.md_info[md_complete_name]['headers']['categories']
            # >>>>>>>>>>>>>>>>>>
            # categories = md_header['categories']

            # <<<<<<<<<<<<<<<<<<
            self._categories_check(md_complete_name, categories)
            if self.md_info[md_complete_name]["categories_error"]:
            # >>>>>>>>>>>>>>>>>>
            # if not self._categories_check(md_file_fullpath, categories):
                continue
            # get the path html should stored in
            self.md_info[md_complete_name]["html_path_name"] = self.html_dir + '/' + categories
            html_path_name = self.md_info[md_complete_name]["html_path_name"]
            html_file_name = self.md_info[md_complete_name]["html_file_name"]
            self.md_info[md_complete_name]['html_complete_name'] = html_path_name + "/" + html_file_name
            html_complete_name = self.md_info[md_complete_name]["html_complete_name"]
            if not os.path.isdir(html_path_name):
                os.makedirs(html_path_name)

            # html_file = categories_path + '/' + html_file_name

            # store filename:headerinfo into content_info dict
            # self.md_info[md_file_fullpath] = md_header
            # store filename:html_relative_path into content_info dict
            # self.md_info[md_file_fullpath]['html_file'] = html_file.split(self.html_dir)[1]

            # if html_file exist and newer than md file, skip generate it
            if os.path.isfile(html_complete_name):
                html_mtime = os.path.getmtime(html_complete_name)
                md_mtime = os.path.getmtime(md_complete_name)
                mtime_compare = md_mtime - html_mtime
                if mtime_compare <= 0:
                    continue

            md_content = self._get_md_content(md_complete_name)
            # md_content = self._md_content(md_file_fullpath)
            renderer = HighlightRenderer()
            content = self._generate_html(md_content, renderer)
            if content:
                with codecs.open(html_complete_name, 'w', encoding='utf8') as f:
                    # extend_file = '_'.join(categories.split('/')) + '.html'
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

        # for html_name in html_info.keys():
        #     title = unicode(html_info[html_name]['title'], 'utf-8')
        #     html_file = html_info[html_name]['html_file']
        #     cat_base, cat_child = html_file.split('/')[1:-1]
        #
        #     html_path = unicode('/html' + html_file, 'utf-8')
        #     if not cat_base in index.keys():
        #         index[cat_base] = {}
        #     if not cat_child in index[cat_base].keys():
        #         index[cat_base][cat_child] = []
        #     index[cat_base][cat_child].append([title, html_path])
        #     # index[cat_base][cat_child] = sorted(index[cat_base][cat_child], key=lambda name: name[1])
        #     index[cat_base][cat_child].sort(key = self._sort_key)
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
