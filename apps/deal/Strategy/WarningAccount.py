import redis
import socket
import time
import json
import re
from exxTrading import configuration


class WarningAccount(object):
    """
    账户预警
    """

    def __init__(self, warning_account, strategy, transaction_pair):
        self.warning_account = warning_account
        self.strategy = strategy
        self.transaction_pair = transaction_pair
        try:
            # 连接redis
            pool = redis.ConnectionPool(host=configuration.REDIS_HOST, password=configuration.REDIS_PWD, port=6379, db=0)
            print("connected success.")
        except:
            print("could not connect to redis.")
        self.conn = redis.Redis(connection_pool=pool)
        myname = socket.getfqdn(socket.gethostname())
        myaddr = socket.gethostbyname(myname)
        self.ip = myaddr

    def send_msg(self):
        email_pattern = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
        phone_pattern = r'^1[34578]\d{9}$'
        for item in self.warning_account:
            if re.match(phone_pattern, item.phone_number):
                msg = dict()
                msg['contact'] = '+86 ' + item.phone_number
                msg['ip'] = self.ip
                # "yyyy/MM/dd HH:mm:ss"
                msg['date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                msg['userName'] = '+86 ' + item.phone_number
                msg['sendNum'] = 1
                msg['cont'] = '%s策略的%s交易对当前价格已低于您的预警价，请即时前往处理!' % (self.strategy, self.transaction_pair)
                self.conn.lpush("sms", json.dumps(msg))
                # res = self.conn.lrange("sms", 0, -1)
                # print(res)
                print(msg, '发送成功！')
            elif re.match(email_pattern, item.email):
                msg = dict()
                msg['contact'] = item.email
                msg['ip'] = self.ip
                # "yyyy/MM/dd HH:mm:ss"
                msg['date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                msg['userName'] = item.email
                msg['sendNum'] = 1
                msg['cont'] = '%s策略的%s交易对当前价格已低于您的预警价，请即时前往处理!' % (self.strategy, self.transaction_pair)
                self.conn.lpush("sms", json.dumps(msg))
                print(msg, '发送成功！')
            else:
                print("手机或者邮箱格式有误！")





















