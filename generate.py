# -*- coding: utf-8 -*-
import os

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
        # you should have a dir named content located in same dir with your generate.py
        # and put all your *.md inside
        # or you indicate it yourself
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if not md_dir:
            self.md_dir = base_dir + "/MyBlog/post"
        else:
            if os.path.isdir(md_dir):
                self.md_dir = md_dir
            else:
                print "content path doesn't exist!"

        # you should have a dir named html located in same dir with your generate.py
        # all generated html file will been put inside
        if not html_dir:
            self.html_dir = base_dir + "/MyBlog/templates/html"
        else:
            if os.path.isdir(html_dir):
                self.html_dir = html_dir
            else:
                os.makedirs(html_dir)

        self.content_info = {}
        self.topics_file = base_dir + '/MyBlog/topics.py'

    def _md_file_filter(self, dir_path):
        all_files = os.listdir(dir_path)
        md_files = [x for x in all_files if x.split('.')[-1] == 'md']
        return md_files

    def _md_generate(self, content, renderer):
        try:
            content = unicode(content, 'utf-8')
            content = mistune.Markdown(renderer=renderer)(content)
        #except (UnicodeDecodeError, TypeError) as e:
        except TypeError as e:
            print "STOP PROCESSING: " + str(e)
            return
        return content

    def _header_parse(self, md_file):
        with open(md_file, 'r') as f:
            # header must less than 4 rows,
            # first "---" means start
            # second "---" means end
            row_num = 0
            header_list = ['title', 'date', 'categories', 'tags']
            result = {}
            content = []
            for row in f.readlines():
                # skip space row
                if row.strip() == "":
                    continue
                row_num += 1
                if row_num == 1:
                    if not row.strip() == "---":
                        print md_file + "(Missing header start tag: '---'!)"
                        return
                elif 1 < row_num < 6:
                    if not ":" in row:
                        print md_file + "(Missing header seperate tag: ':'!)"
                        return
                    key, value = row.strip().split(":", 1)
                    header_key = key.strip()
                    header_value = value.strip()
                    if not header_key in header_list:
                        print md_file + "(Invaild header!)"
                        return
                    else:
                        result[header_key] = header_value
                        header_list.remove(header_key)
                elif row_num == 6:
                    if not row.strip() == "---":
                        print md_file + "(Missing header end tag: '---'!)"
                        return
                    else:
                        return result
                else:
                    print md_file + "(Header should be 4 rows!)"
                    return

    def _md_content(self, md_file):
        with open(md_file, 'r') as f:
            row_num = 0
            content = []
            for line in f.readlines():
                # skip space line
                if line.strip() == "":
                    content.append(line)
                    continue
                row_num += 1
                if row_num > 6:
                    content.append(line)
            result = ''.join(content)
            return result

    def _categories_check(self, md_file, categories):
        if categories == '':
            print md_file + "(Categories should not be blank!)"
            return
        if not len(categories.split('/')) == 2:
            print md_file + "(Wrong categories syntax! should be 2 level!)"
            return
        return True

    def md_generate(self):
        md_files = self._md_file_filter(self.md_dir)
        for md_file in md_files:
            html_file_name = md_file.split('.md')[0] + '.html'
            md_file_fullpath = self.md_dir + '/' + md_file

            # parse and check header
            md_header = self._header_parse(md_file_fullpath)
            if not md_header:
                continue

            # check categories's syntax and prepare categories folder
            categories = md_header['categories']
            if not self._categories_check(md_file_fullpath, categories):
                continue
            # get the path html should stored in
            categories_path = self.html_dir + '/' + categories
            if not os.path.isdir(categories_path):
                os.makedirs(categories_path)
            html_file = categories_path + '/' + html_file_name

            # store filename:headerinfo into content_info dict
            self.content_info[md_file_fullpath] = md_header
            # store filename:html_relative_path into content_info dict
            self.content_info[md_file_fullpath]['html_file'] = html_file.split(self.html_dir)[1]

            # if html_file exist and newer than md file, skip generate it
            if os.path.isfile(html_file):
                html_mtime = os.path.getmtime(html_file)
                md_mtime = os.path.getmtime(md_file_fullpath)
                mtime_compare = md_mtime - html_mtime
                if mtime_compare <= 0:
                    continue

            md_content = self._md_content(md_file_fullpath)
            renderer = HighlightRenderer()
            content = self._md_generate(md_content, renderer)
            if content:
                with codecs.open(html_file, 'w', encoding='utf8') as f:
                    begin_template = "{% extends 'index.html' %}\n{% block md %}\n"
                    end_template = "{% endblock %}"
                    content = begin_template + content + end_template
                    f.write(content)
            else:
                print md_file + "(error to generate)"

    def _html_cat_parse(self, html_info):
        index = {}
        for html_name in html_info.keys():
            title = unicode(html_info[html_name]['title'], 'utf-8')
            html_file = html_info[html_name]['html_file']
            cat_base, cat_child = html_file.split('/')[1:-1]
            html_path = unicode('/html' + html_file, 'utf-8')
            if not cat_base in index.keys():
                index[cat_base] = {}
            if not cat_child in index[cat_base].keys():
                index[cat_base][cat_child] = []
            index[cat_base][cat_child].append([title, html_path])
            index[cat_base][cat_child] = sorted(index[cat_base][cat_child], key=lambda name: name[1])
        result = str(index).replace(']', ']\n    ')
        return result

    def topic_index(self):
        index = self._html_cat_parse(self.content_info)
        topics_def_temp = "def topics():\n    topics = "
        topics_def_end = "\n    return topics"
        topics_def = topics_def_temp + index + topics_def_end
        with open(self.topics_file, 'w') as f:
            f.write(topics_def)


if __name__ == "__main__":
    markdown_generator = MdGenerator()
    markdown_generator.md_generate()
    markdown_generator.topic_index()
