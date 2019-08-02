# _*_ coding:utf-8 _*_
"""
日志模块处理日志
"""
import logging
from logging.handlers import TimedRotatingFileHandler
import os,time
class MylogHandler(logging.Logger):
    def __init__(self,name,level="DEBUG",stream=True,files=True):
      self.name = name
      self.level = level
      logging.Logger.__init__(self,self.name,level=self.level)
      if stream:
        self.__streamHandler__(self.level)
      if files:
        self.__filesHandler__(self.level)
    def __streamHandler__(self,level=None):
      curretime = time.strftime('%Y%m%d%H%M%S')
      file_path = os.path.abspath('..') + "/logs/"
      filename = file_path + self.name + curretime + ".log"
      if os.path.isdir(file_path):
          os.mkdir(file_path)
      handler = TimedRotatingFileHandler(filename=filename, when='D', interval=1, backupCount=15)
      handler.suffix = '%Y%m%d.log'
      handler.setLevel(level)
      formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
      handler.setFormatter(formatter)
      self.addHandler(handler) #将hander添加到logger上
    def __filesHandler__(self,level=None):
      handler = logging.StreamHandler()
      formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
      handler.setFormatter(formatter)
      handler.setLevel(level)
      self.addHandler(handler)
if __name__ == '__main__':
 log = MylogHandler('test')
 log.info('this is a my log handler')
