# -*- coding: utf-8 -*-
import scrapy
from crawlZhiHu.utils.login_zhihu import getCookies
import json
import datetime
from crawlZhiHu.items import ZhihuAnswerItem, ZhihuQuestionItem, MyItemLoader
from crawlZhiHu.utils.log_zhihu import Logger



class ZhihuSpider(scrapy.Spider):
    name = 'ZhihuSpider'
    allowed_domains = ['zhihu.com']
    cookies_dict = getCookies('13652331556', '49ba59abbe56e057')
    index_api = 'https://www.zhihu.com/api/v3/feed/topstory?action_feed=True&limit=10&action=down&after_id=0&desktop=true'
    auth_headers = {
        'Authorization': 'Bearer ' + cookies_dict['z_c0'],
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'
    }
    answers_url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data[*].is_normal%2Ccomment_count%2Ccontent%2Cvoteup_count%2Ccreated_time%2Cupdated_time%2Cbadge[%3F(type%3Dbest_answerer)].topics&limit=20&offset=0'
    question_url = 'https://www.zhihu.com/question/{0}'
    # 自定义logging module
    logger_obj = Logger(name=__name__, logginglevel=1)
    logger = logger_obj.getLogger()
    filehandler = logger_obj.getFileHandler()

    def start_requests(self):
        # 调用questions API 基于auth验证 不需要cookies
        yield scrapy.Request(self.index_api, headers=self.auth_headers)


    def parse(self, response):
        '''
        这是url转发中心 通过API调用 获得question ID 通过ID构造question主页 和answer JSON
        :param response:
        :return:
        '''
        # 解析json
        questions = json.loads(response.text)
        for question in questions['data']:
            try:
                question_id = question['target']['question']['id']
                question_url = self.question_url.format(question_id)
                answers_url = self.answers_url.format(question_id)
                # 通过json数据获取到 question的ID  打开question主页进行解析
                yield scrapy.Request(url=question_url, headers=self.headers, callback=self.parse_question,
                                     meta={'question_id': question_id}, priority=20)
                # 通过json数据获取到 question的ID  请求answer的json 进行解析
                yield scrapy.Request(url=answers_url, headers=self.headers,cookies=self.cookies_dict, callback=self.parse_answers)
            except Exception as e:
                # 引入自己写的日志module
                error_info = str(e)
                error_question = json.dumps(question, ensure_ascii=False)
                self.logger.error(u'字段获取错误:' + error_info.decode('utf-8') +':'+error_question )
                self.filehandler.flush()

        if questions['paging']['is_end']:
            # 没有更多question
            print '没有更多question'
            return
        else:
            # 根据next字段 爬取下一个 个人主页推荐的页面
            next_index_api = questions['paging']['next']
            yield scrapy.Request(url=next_index_api, headers=self.auth_headers, priority=50)

    def parse_question(self, response):
        '''
        解析 question主页
        :param response:
        :return:
        '''
        try:
            question_id = response.meta['question_id']
            question_item = MyItemLoader(item=ZhihuQuestionItem(), response=response)
            question_item.add_value('question_id', question_id)
            # topics = ','.join(response.xpath("//div[@class='Tag QuestionTopic']//text()").extract())
            question_item.add_xpath('topics', "//div[@class='Tag QuestionTopic']//text()")
            question_item.add_value('url', response.url)
            question_item.add_xpath('title', "//h1[@class='QuestionHeader-title']/text()")
            content_list = response.xpath("//span[@class='RichText']//text()").extract()
            content_list = [x.encode('utf-8').strip() for x in content_list]
            # 类似问题
            href = response.xpath("//span[@class='RichText']//a/@href").extract()
            href = [x.encode('utf-8').strip() for x in href]
            content = ','.join(content_list) + ','.join(href)
            question_item.add_value('content', content)
            question_item.add_xpath('answer_nums', "//h4[@class='List-headerText']/span/text()")
            question_item.add_xpath('comments_nums',
                                    "//div[@class='QuestionHeader-Comment']/button[@class='Button Button--plain']/text()")
            try:
                follow_user_nums = response.xpath("//div[@class='NumberBoard-item']/div[2]/text()").extract()[0]
                click_nums = response.xpath("//div[@class='NumberBoard-item']/div[2]/text()").extract()[1]
                question_item.add_value('follow_user_nums', follow_user_nums)
                question_item.add_value('click_nums', click_nums)
            except Exception as e:
                self.logger.error('response url: '+response.url+'request url: '+response.request.url+ str(e))
                self.filehandler.flush()

            crawl_time = datetime.datetime.now()
            crawl_update_time = datetime.datetime.now()
            question_item.add_value('crawl_time', crawl_time)
            question_item.add_value('crawl_update_time', crawl_update_time)
            question_item = question_item.load_item()
            try:
                question_item['content']
            except Exception as e:
                question_item['content'] = ''
            yield question_item
        except Exception as e:
            response_url = response.url
            request_url = response.request.url
            info = 'response_url: '+ response_url+' request_url '+request_url+' error_info: '+str(e).decode('utf-8')
            self.logger(info)



    def parse_answers(self, response):
        # 解析answers_json
        try:
            answers = json.loads(response.text)
            for answer in answers['data']:
                # 解析每一个answer
                item = ZhihuAnswerItem()
                answer_id = answer['id']
                question_id = answer['question']['id']
                url = 'https://www.zhihu.com/question/{0}/answer/{1}'
                answer_url = url.format(question_id, answer_id)
                comments_nums = answer['comment_count']
                praise_nums = answer['voteup_count']
                #  这个时间需要转换
                create_time = answer['created_time']
                update_time = answer['updated_time']
                create_time = datetime.datetime.fromtimestamp(create_time)
                update_time = datetime.datetime.fromtimestamp(update_time)
                crawl_time = datetime.datetime.now()
                crawl_update_time = datetime.datetime.now()
                # 知乎做了图片屏蔽  我们手动更改content中内容 str类型才能使用replace方法
                content = answer['content'].encode('utf-8')
                content = content.replace('src="//zhstatic.zhihu.com/assets/zhihu/ztext/whitedot.jpg"', '')
                content = content.replace('data-actualsrc', 'src')
                author_token = answer['author']['url_token']
                if '' == author_token:
                    # 匿名用户
                    author_url = u'匿名用户'
                else:
                    author_url = 'https://www.zhihu.com/people/{0}/answers'.format(author_token)
                item['answer_id'] = answer_id
                item['question_id'] = question_id
                item['answer_url'] = answer_url
                item['comments_nums'] = comments_nums
                item['create_time'] = create_time
                item['update_time'] = update_time
                item['crawl_time'] = crawl_time
                item['crawl_update_time'] = crawl_update_time
                item['content'] = content
                item['praise_nums'] = praise_nums
                item['author_url'] = author_url
                yield item

            if answers['paging']['is_end']:
                # 没有更多的answer
                print '%(asctime)s'+'没有更多answer'
                return
            else:
                next_answers_url = answers['paging']['next']
                yield scrapy.Request(url=next_answers_url, headers=self.headers,cookies=self.cookies_dict, callback=self.parse_answers)
        except Exception as e:
            response_url = response.url
            request_url = response.request.url
            info = 'response_url: '+ response_url+' request_url '+request_url+' error_info: '+str(e).decode('utf-8')
            self.logger(info)
