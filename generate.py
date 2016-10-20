import mistune
import os


class MdGenerator(object):
    def __init__(self, content_path=None, html_path=None):
        # you should have a dir named content located in same dir with your generate.py
        # and put all your *.md inside
        # or you indicate it yourself
        if not content_path:
            self.content_path = os.path.dirname(os.path.abspath(__file__)) + "/content"
        else:
            if os.path.isdir(content_path):
                self.content_path = content_path
            else:
                print "content path doesn't exist!"

        if not html_path:
            self.html_path = os.path.dirname(os.path.abspath(__file__)) + "/html"
        else:
            if os.path.isdir(html_path):
                self.html_path = html_path
            else:
                print "html path doesn't exist!"

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
            content = []
            for line in f.readlines():
                print line
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
                                if header[0] not in ['title', 'date', 'categories']:
                                    print md_file + ": Wrong syntax, invaild header!"
                                    return
                                result['header'] = [header[0], header[1]]
                                header_line_num += 1
                        else:
                            print md_file + ": Wrong header syntax, missing ':'!"
            result['content'] = ''.join(content)
            return result

    def md_generate(self):
        content_files = os.listdir(self.content_path)
        content_md = [x for x in content_files if x.split('.')[1] == 'md']
        for md_file in content_md:
            html_file = self.html_path + '/' + md_file.split('.md')[0] + '.html'
            md_file = self.content_path + '/' + md_file
            # if parse faild, md_parsed_file should be None
            md_parsed_file = self._md_parse(md_file)
            if not md_parsed_file:
                break
            with open(html_file, 'w') as f:
                content = self._md_generate(md_parsed_file['content'])
                f.write(content)


if __name__ == "__main__":
    markdown_generator = MdGenerator()
    markdown_generator.md_generate()
