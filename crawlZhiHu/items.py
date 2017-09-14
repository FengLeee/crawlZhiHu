# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join
import re

def getNums(value):
    value = value.encode('utf-8')
    matchobj = re.match('.*?(\d+).*?', value)
    if matchobj:
        return int(matchobj.group(1))


class MyItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

class ZhihuAnswerItem(scrapy.Item):
    answer_id = scrapy.Field()
    answer_url = scrapy.Field()
    question_id = scrapy.Field()
    author_url = scrapy.Field()
    praise_nums = scrapy.Field()
    comments_nums = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()
    content = scrapy.Field()

    def getsql(self):
        sql = '''insert into ZhihuAnswer (answer_id, answer_url, question_id, 
        author_url, praise_nums, comments_nums, create_time, update_time, crawl_time, crawl_update_time, content)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)ON DUPLICATE KEY UPDATE praise_nums=VALUES (praise_nums),
        comments_nums=VALUES (comments_nums), update_time=VALUES (update_time), crawl_update_time=VALUES (crawl_update_time),
        content=VALUES (content)'''
        params = (self['answer_id'], self['answer_url'], self['question_id'], self['author_url'], self.get('praise_nums',0),
                  self.get('comments_nums', 0),self['create_time'], self['update_time'], self.get('crawl_time',self['crawl_update_time']), self['crawl_update_time'],
                  self['content'],)
        return (sql, params)

class ZhihuQuestionItem(scrapy.Item):
    question_id = scrapy.Field()
    topics = scrapy.Field(
        input_processor = Join(',')
    )
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_nums = scrapy.Field(
        input_processor = MapCompose(getNums)
    )
    comments_nums = scrapy.Field(
        input_processor = MapCompose(getNums)
    )
    click_nums = scrapy.Field()
    follow_user_nums = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def getsql(self):
        sql = '''insert into ZhihuQuestion(question_id, topics, url, title, content,
                  answer_nums, comments_nums, click_nums, follow_user_nums, crawl_time, crawl_update_time)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)ON DUPLICATE KEY UPDATE topics=VALUES (topics),
                  title=VALUES (title), content=VALUES (content), answer_nums=VALUES (answer_nums),
                  comments_nums=VALUES (comments_nums), click_nums=VALUES (click_nums), 
                  follow_user_nums=VALUES (follow_user_nums), crawl_update_time=VALUES (crawl_update_time)'''
        params = (self['question_id'], self['topics'], self['url'], self['title'],
                  self['content'],self.get('answer_nums',0), self.get('comments_nums',0), self.get('click_nums',0),
                  self.get('follow_user_nums',0),self.get('crawl_time',self['crawl_update_time']), self['crawl_update_time'])
        return (sql,params)