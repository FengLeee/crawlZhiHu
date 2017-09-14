# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import json
from DBUtils.PooledDB import PooledDB

class MyPyMysqlPipeline(object):

    def __init__(self, settings):
        mysqlconf_dict = settings['MYSQL']
        self.host = mysqlconf_dict['host']
        self.user = mysqlconf_dict['user']
        self.password = mysqlconf_dict['password']
        self.database = mysqlconf_dict['database']
        self.charset = mysqlconf_dict['charset']
        self.use_unicode = mysqlconf_dict['use_unicode']
        self.db = pymysql.connect(host=self.host, user=self.user, password=self.password,
                        database=self.database, charset=self.charset, use_unicode=self.use_unicode)
        self.cursor = self.db.cursor()

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)



    def process_item(self, item, spider):
        try:
            sql, params = item.getsql()
            self.cursor.execute(sql, params)
            self.db.commit()
            return item
        except Exception as e:
            error_info = str(e)
            if 'ZhihuAnswerItem' == item.__class__.__name__:
                error_rul = item['answer_url']
            if 'ZhihuQuestionItem' == item.__class__.__name__:
                error_rul = item['url']
            spider.logger.error(u'数据插入出错： '+error_info+':'+error_rul)
            spider.filehandler.flush()
            return item

    def close_spider(self, spider):
        self.cursor.close()
        self.db.close()

class MyPyMysqlPoolPipeline(object):
    def __init__(self, settings):
        mysqlconf_dict = settings['MYSQL']
        self.host = mysqlconf_dict['host']
        self.user = mysqlconf_dict['user']
        self.password = mysqlconf_dict['password']
        self.database = mysqlconf_dict['database']
        self.charset = mysqlconf_dict['charset']
        self.use_unicode = mysqlconf_dict['use_unicode']

        self.pool = PooledDB(pymysql,mincached=5,host=self.host,user=self.user,
                 password=self.password,database=self.database,
                 charset=self.charset,use_unicode=True)
        self.conn = self.pool.connection()
        self.cursor = self.conn.cursor()

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def process_item(self, item, spider):
        try:
            sql,params = item.getsql()
            self.cursor.execute(sql,params)
            self.conn.commit()
            return item
        except Exception as e:
            error_info = str(e)
            if 'ZhihuAnswerItem' == item.__class__.__name__:
                error_rul = item['answer_url']
            if 'ZhihuQuestionItem' == item.__class__.__name__:
                error_rul = item['url']
            spider.logger.error(u'数据插入出错： ' + error_info + ':' + error_rul)
            spider.filehandler.flush()
            return item