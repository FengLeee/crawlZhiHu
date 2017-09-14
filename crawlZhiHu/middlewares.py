# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy.utils import response as res
import random


class HandlerRequestErrorMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def __init__(self, crawler):
        self.crawler = crawler

    def process_response(self, request, response, spider ):
        if response.status >= 400:
            # 自定义优先级在系统自带的retry后面 已经retry多次 直接保存失败的URL
            info = res.response_status_message(response.status)
            spider.logger.error(response.url+'  '+info)
            spider.filehandler.flush()
        return response


class UserAgentMiddleware(object):
    '''
    随机替换UA
    '''
    @classmethod
    def from_settings(cls, settings):
        ua_list = settings['USER_AGETN']
        return cls(ua_list)

    def __init__(self, ua_list):
        self.ua_list = ua_list

    def process_request(self, request, spider):
        index = random.randint(0,len(self.ua_list)-1)
        ua = self.ua_list[index]
        request.headers['User-Agent']=ua
        return