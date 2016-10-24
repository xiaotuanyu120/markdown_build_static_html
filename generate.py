import mistune
import os


class MdGenerator(object):
    def __init__(self, md_dir=None, html_dir=None):
        # you should have a dir named content located in same dir with your generate.py
        # and put all your *.md inside
        # or you indicate it yourself
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if not md_dir:
            self.md_dir = base_dir + "/content"
        else:
            if os.path.isdir(md_dir):
                self.md_dir = md_dir
            else:
                print "content path doesn't exist!"

        # you should have a dir named html located in same dir with your generate.py
        # all generated html file will been put inside
        if not html_dir:
            self.html_dir = base_dir + "/html"
        else:
            if os.path.isdir(html_dir):
                self.html_dir = html_dir
            else:
                os.makedirs(html_dir)

        self.content_info = {}
        self.topics_file = base_dir + '/topics.py'

    def _md_file_filter(self, dir_path):
        all_files = os.listdir(dir_path)
        md_files = [x for x in all_files if x.split('.')[-1] == 'md']
        return md_files

    def _md_generate(self, content):
        renderer = mistune.Renderer(escape=False, hard_wrap=False)
        try:
            content = mistune.Markdown(renderer=renderer)(content)
        except TypeError as e:
            print "STOP PROCESSING: " + str(e)
            return
        return content

    def _parse_header(self, md_file):
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

    def _get_content(self, md_file):
        with open(md_file, 'r') as f:
            row_num = 0
            content = []
            for line in f.readlines():
                # skip space line
                if line.strip() == "":
                    continue
                row_num += 1
                if row_num > 6:
                    content.append(line)
            result = content
            return result

    def _check_categories(self, categories):
        if categories == '':
            print md_file + "(Categories should not be blank!)"
            return
        if len(categories.split('/')) > 2:
            print md_file + "(Wrong categories syntax! at most 2 level!)"
            return
        return True

    def md_generate(self):
        md_files = self._md_file_filter(self.md_dir)
        for md_file in md_files:
            html_file_name = md_file.split('.md')[0] + '.html'
            md_file = self.md_dir + '/' + md_file

            # parse and check header
            md_header = self._parse_header(md_file)
            if not md_header:
                continue

            # check categories's syntax and prepare categories folder
            categories = md_header['categories']
            if not self._check_categories(categories):
                continue
            # get the path html should stored in
            categories_path = self.html_dir + '/' + categories
            if not os.path.isdir(categories_path):
                os.makedirs(categories_path)
            html_file = categories_path + '/' + html_file_name

            # store filename:headerinfo into content_info dict
            self.content_info[md_file] = md_header
            # store filename:html_relative_path into content_info dict
            self.content_info[md_file]['html_file'] = html_file.split(self.html_dir)[1]

            # if html_file exist and newer than md file, skip generate it
            if os.path.isfile(html_file):
                html_mtime = os.path.getmtime(html_file)
                md_mtime = os.path.getmtime(md_file)
                mtime_compare = md_mtime - html_mtime
                if mtime_compare <= 0:
                    continue

            md_content = self._get_content(md_file)
            with open(html_file, 'w') as f:
                content = []
                for i in md_content:
                    # if '> ' in i:
                    #     j = ''
                    content.append(self._md_generate(i))
                content = ''.join(content)
                begin_template = "{% extends 'topic_form.html' %}\n{% block topic %}\n"
                end_template = "\n{% endblock %}"
                content = begin_template + content + end_template
                f.write(content)

    def index_generate(self):
        # create a dict which key is title and value is html_file's path
        index = {}
        topics_def = "def topics():\n    return topics = "
        html_name = self.content_info
        for html_key in html_name.keys():
            title = html_name[html_key]['title']
            html_file = html_name[html_key]['html_file']
            sort = html_file.split('/')
            sort_len = len(sort)
            if sort_len == 3:
                index[sort[1]].append([title, html_file])
            elif sort_len == 4:
                if not sort[1] in index.keys():
                    index[sort[1]] = {}
                if not sort[2] in index[sort[1]].keys():
                    index[sort[1]][sort[2]] = []
                index[sort[1]][sort[2]].append([title, html_file])
        topics_def = topics_def + str(index)
        with open(self.topics_file, 'w') as f:
            f.write(topics_def)


if __name__ == "__main__":
    markdown_generator = MdGenerator()
    markdown_generator.md_generate()
    markdown_generator.index_generate()
