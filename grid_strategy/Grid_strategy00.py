import random
import pymysql
import time
import logging
from threading import Thread
from grid_strategy.APITest import DataAPI
from exchangeConnection.exx.exxService import getOrder, order, cancelOrder


class GridStrategy(Thread):
    def __init__(self, *args):
        super().__init__()
        self.starting_price = args[0]
        self.grid_counts = args[1]
        self.trade_amount = args[2]
        self.currency_type = args[3]
        self.order_type = args[4]
        self.id_list = list()

    def log_info(self, log_name):
        """
        日志文件
        :param log_name: 日志文件名
        :return:
        """
        logging.basicConfig(filename="../%s.log" % log_name,
                            filemode="w",
                            format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                            datefmt="%d-%M-%Y %H:%M:%S",
                            level=logging.DEBUG)

    def get_markets_data(self):
        """
        获取市场行情数据
        :return:
        """
        data_api = DataAPI()
        markets_data = data_api.markets_api()[self.currency_type]
        return markets_data

    def connect_db(self, sql):
        """
        数据库操作
        :param sql: 执行的SQL语句
        :return:
        """
        try:
            conn = pymysql.connect(host="192.168.4.201",
                                   user="root",
                                   passwd="password",
                                   db="exx_quantitativetrading",
                                   port=3306,
                                   charset="utf8")
            cur = conn.cursor()  # 获取一个游标对象
            cur.execute(sql)
            conn.commit()
            # data = cur.fetchall()  # 返回元组，元素也是元组，一个元组表示一个
            cur.close()
            conn.close()
        except Exception as e:
            conn.rollback()
            self.log_info("db")
            logging.exception("DB CONNECT ERROR...", e)
            print("数据库连接错误...", e)

    def place_order(self, item=None, order_type=None, flag=0):
        """
        下单，根据flag判断批量/单笔
        :param flag: 默认参数
        :return:
        """
        try:
            markets_data = self.get_markets_data()
        except Exception as e:
            self.log_info("api")
            logging.exception("GET MARKETS DATA FAILED...", e)
            print("获取市场信息失败...", e)
        else:
            a, b = self.starting_price
            for i in range(self.grid_counts):
                self.trade_amount = random.uniform(float(markets_data.get("minAmount")), 10)
                if self.order_type == "buy" and flag == 0:
                    a, b = a-0.2, a
                elif self.order_type == "sell" and flag == 0:
                    a, b = b, b+0.2
                price = random.uniform(a, b)
                price = round(price, markets_data.get("priceScale"))
                amount = round(self.trade_amount, markets_data.get("amountScale"))
                try:
                    if order_type is None:
                        res = order(str(amount), self.currency_type, str(price), self.order_type)  # 修改self.order_type
                        if res.get("id") is not None:
                            self.id_list.append({res.get("id"): {"price_range": (a, b), "order_type": self.order_type}})
                    else:
                        res = order(str(amount), self.currency_type, str(price), order_type)
                        if res.get("id") is not None:
                            if item is not None:
                                self.id_list.remove(item)
                            self.id_list.append({res.get("id"): {"price_range": (a, b), "order_type": order_type}})
                    sql = "insert into exx_order(price, amount, currency, ordertype, orderid)" \
                          " values({},'{}','{}','{}','{}')".format(price, str(amount), self.currency_type,
                                                                   self.order_type, res.get("id"))
                    self.connect_db(sql)

                except Exception as e:
                    self.log_info("api")
                    logging.exception("PLACE ORDER ERROR...", e)
                    print("下单失败", e)
                # time.sleep(0.1)

    def completed_order_info(self, price, item, order_info, order_type):
        """
        更新挂单信息
        :param price: 撤单后，再次挂单的价格
        :param item: 挂单id及价格区间
        :param order_info: 挂单信息
        :return:
        """
        try:
            b_id = list(item.keys())[0]
            ret = cancelOrder(self.currency_type, b_id)
            # print("-"*20, ret, type(ret["code"]))
            # 撤单成功后，下单并添加下单id及价格区间
            if ret.get("code") in [100, 211, 212]:
                res = order(str(order_info["trade_amount"]),
                            self.currency_type,
                            str(price),
                            order_type)  # 调用api
                if res.get("id") is not None:
                    self.id_list.remove(item)
                    self.id_list.append({res.get("id"): {"price_range": (price - 0.1, price + 0.1),
                                                         "order_type": order_type}})
            print("+"*20)
        except Exception as e:
            self.log_info("api")
            logging.exception("UPDATE ORDER FAILED...", e)
            print("更新挂单失败")

    def update_order_info(self):
        """
        获取挂单信息
        :return:
        """
        try:
            markets_data = self.get_markets_data()
        except Exception as e:
            self.log_info("api")
            logging.exception("GET_ORDER_INFO...", e)
            print("获取挂单信息失败...", e)
        else:
            self.grid_counts = 1
            num = 0
            while True:
                print("id列表", self.id_list, len(self.id_list))
                for item in self.id_list:
                    b_id = list(item.keys())[0]
                    limit = item[b_id]["price_range"]
                    order_type = item[b_id]["order_type"]
                    try:
                        order_info = getOrder(self.currency_type, b_id)  # 调用api
                        print(b_id, limit, order_info)

                        # 挂单交易完成，撤单并生成对应的buy/sell挂单
                        if order_info.get("status") in [2]:
                            if order_info.get("type") == "buy":
                                price = order_info.get("price")*(1+0.002)
                                price = round(price, markets_data.get("priceScale"))
                                t = Thread(target=self.completed_order_info, args=(price, item, order_info, "sell"))
                                t.start()
                            elif order_info.get("type") == "sell":
                                price = order_info.get("price")*(1-0.002)
                                price = round(price, markets_data.get("priceScale"))
                                t = Thread(target=self.completed_order_info, args=(price, item, order_info, "buy"))
                                t.start()

                        # 挂单在一段时间内未成交，撤单并重新下单
                        elif order_info.get("status") in [0, 1] and num == 2:
                            res = cancelOrder(self.currency_type, b_id)
                            print("*"*50, res.get("code"))
                            if res.get("code") in [100, 211, 212]:
                                # self.id_list.remove(item)
                                self.starting_price = limit
                                self.place_order(item, order_type, 1)
                                # t1 = Thread(target=self.place_order, args=(item, order_type, 1))
                                # t1.start()

                    except Exception as e:
                        self.log_info("api")
                        logging.exception("GET_ORDER_INFO...", e)
                        print("获取挂单状态失败...", e)
                num += 1
                if num == 3:
                    num = 0
                # time.sleep(1)

    def run(self):
        self.place_order()
        self.update_order_info()


if __name__ == "__main__":
    currency_type = "eth_usdt"
    thread1 = GridStrategy((101, 101), 50, 0, currency_type, "buy")
    thread2 = GridStrategy((98, 98), 50, 0, currency_type, "sell")
    thread1.start()
    thread2.start()




