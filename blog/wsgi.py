# coding=utf-8

import os
import sys
from config import Config

CONF_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = Config(os.path.join(CONF_DIR, 'conf'), 'blog.ini').conf('blog')
sys.path.insert(0, BLOG["base_dir"])

from blog import app

if __name__ == "__main__":
    app.run()
