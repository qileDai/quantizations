import redis
import socket
import time


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
            pool = redis.ConnectionPool(host='192.168.4.179', password='sHZQ4zLB6LasF8ox', port=6379, db=0)
            print("connected success.")
        except:
            print("could not connect to redis.")
        self.conn = redis.Redis(connection_pool=pool)
        myname = socket.getfqdn(socket.gethostname())
        myaddr = socket.gethostbyname(myname)
        self.ip = myaddr

    def send_msg(self):
        for item in self.warning_account:
            msg = dict()
            msg['contact'] = item
            msg['ip'] = self.ip
            # "yyyy/MM/dd HH:mm:ss"
            msg['date'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
            msg['userName'] = item
            msg['sendNum'] = 1
            msg['cont'] = '%s策略的%s交易对当前价格已低于您的预警价，请即时前往处理!' % (self.strategy, self.transaction_pair)
            self.conn.lpush("sms", msg)





















