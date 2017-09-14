# encoding=utf-8
__author__ = "yaoo"
__version__ = "1.0.1"
__email__ = "1711602280@qq.com"

import os
import sys
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(__file__))
execute(['scrapy', 'crawl', 'ZhihuSpider'])