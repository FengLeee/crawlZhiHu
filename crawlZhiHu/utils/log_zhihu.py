# encoding=utf-8
__author__ = "yaoo"
__version__ = "1.0.1"
__email__ = "1711602280@qq.com"
import logging

level_dict = {
    1:logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s'), #debug
    2:logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s'), #info
    3:logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s'), #waring
    4:logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s'), #error
    5:logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s') #critical
}


class Logger(object):
    '''
    自定义log模块 写入zhihu.log模块
    '''
    def __init__(self,name, logginglevel=1):
        '''

        :param logginglevel: 定义log的级别
        '''
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logginglevel)

        self.fh = logging.FileHandler('zhihu.log', encoding='utf-8')
        self.fh.setLevel(logginglevel)
        self.fh.setFormatter(level_dict[logginglevel])

        self.sh = logging.StreamHandler()
        self.sh.setLevel(logginglevel)
        self.sh.setFormatter(level_dict[logginglevel])

        self.logger.addHandler(self.fh)
        self.logger.addHandler(self.sh)

    def getLogger(self):
        return self.logger

    def getFileHandler(self):
        return self.sh
if __name__ == '__main__':
    logger_obj = Logger(logginglevel=1)
    logger = logger_obj.getLogger()
    fh = logger_obj.fh
    logger.error(u'匿名用户:你好')
    fh.flush()
