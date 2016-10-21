import mistune
import os


class MdGenerator(object):
    def __init__(self, content_dir=None, html_dir=None):
        # you should have a dir named content located in same dir with your generate.py
        # and put all your *.md inside
        # or you indicate it yourself
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if not content_dir:
            self.content_dir = base_dir + "/content"
        else:
            if os.path.isdir(content_dir):
                self.content_dir = content_dir
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
                print "html path doesn't exist!"

        self.content_info = {}
        self.topics_file = base_dir + '/topics.py'

    def _md_generate(self, content):
        try:
            content = mistune.Markdown()(content)
        except TypeError as e:
            print "STOP PROCESSING: " + str(e)
            return
        return content

    def _md_parse(self, md_file):
        with open(md_file, 'r') as f:
            # header must less than 3 lines,
            # first "---" means start
            # second "---" means end
            starter = False
            content_starter = False
            header_line_num = 0
            result = {}
            result['header'] = {}
            content = []
            for line in f.readlines():
                # skip space line
                if line.strip() == "":
                    continue
                # seek start line
                if not starter:
                    if line.strip() == "---":
                        starter = True
                    else:
                        # seek body content
                        if content_starter:
                             content.append(line)
                        else:
                            print md_file + ": Wrong syntax, should start with '---'!"
                            return
                else:
                    # seek end line
                    if line.strip() == "---":
                        if header_line_num == 3:
                            starter = False
                            content_starter = True
                        else:
                            print md_file + ": Wrong syntax, header less than 3 lines!"
                    else:
                        if ":" in line:
                            if header_line_num > 2:
                                print md_file + ": Wrong syntax, header more than 3 lines!"
                            else:
                                header = line.strip().split(":", 1)
                                if header[0].strip() not in ['title', 'date', 'categories']:
                                    print md_file + ": Wrong syntax, invaild header!"
                                    return
                                header_key = header[0].strip()
                                header_value = header[1].strip()
                                result['header'][header_key] = header_value
                                header_line_num += 1
                        else:
                            print md_file + ": Wrong header syntax, missing ':'!"
            result['content'] = ''.join(content)
            return result

    def md_generate(self):
        content_files = os.listdir(self.content_dir)
        content_md = [x for x in content_files if x.split('.')[1] == 'md']
        for md_file in content_md:
            html_file_name = md_file.split('.md')[0] + '.html'
            md_file = self.content_dir + '/' + md_file

            # if parse faild, md_parsed_file should be None, so skip it
            md_parsed_file = self._md_parse(md_file)
            if not md_parsed_file:
                continue

            # get the path html should stored in
            html_file_path = self.html_dir + '/' + md_parsed_file['header']['categories']
            if not os.path.isdir(html_file_path):
                os.makedirs(html_file_path)
            html_file = html_file_path + '/' + html_file_name

            # store filename:headerinfo into content_info dict
            self.content_info[md_file] = md_parsed_file['header']
            # store filename:html_relative_path into content_info dict
            self.content_info[md_file]['html_file'] = html_file.split(self.html_dir)[1]

            # if html_file exist and newer than md file, skip generate it
            if os.path.isfile(html_file):
                html_mtime = os.path.getmtime(html_file)
                md_mtime = os.path.getmtime(md_file)
                mtime_compare = md_mtime - html_mtime
                if mtime_compare <= 0:
                    continue

            with open(html_file, 'w') as f:
                content = self._md_generate(md_parsed_file['content'])
                f.write(content)

    def content_index_generate(self):
        # create a dict which key is title and value is html_file's path
        content_index = {}
        topics_def = "def topics():\n    return topics = "
        src = self.content_info
        for md in src.keys():
            content_index[src[md]['title']] = src[md]['html_file']
        topics_def = topics_def + str(content_index)
        with open(self.topics_file, 'w') as f:
            f.write(topics_def)


if __name__ == "__main__":
    markdown_generator = MdGenerator()
    markdown_generator.md_generate()
    markdown_generator.content_index_generate()
