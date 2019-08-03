import pymysql
import random
import time
import logging
from threading import Thread
from APITest import DataAPI
from order import getOrder, order, cancelOrder, getOpenOrders


class GridStrategy(Thread):
    def __init__(self, *args):
        super().__init__()
        self.starting_price = args[0]
        self.grid_counts = args[1]
        self.trade_amount = args[2]
        self.change_by_day = args[3]
        self.currency_type = args[4]
        self.order_type = args[5]
        self.id_list = list()

    def log_info(self, log_name):
        logging.basicConfig(filename="../%s.log" % log_name,
                            filemode="w",
                            format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                            datefmt="%d-%M-%Y %H:%M:%S",
                            level=logging.DEBUG)

    def get_markets_data(self):
        data_api = DataAPI()
        markets_data = data_api.markets_api()[self.currency_type]
        return markets_data

    def connect_db(self, sql):
        try:
            conn = pymysql.connect(host="192.168.4.201",
                                   user="root",
                                   passwd="password",
                                   db="exx_quantitativetrading",
                                   port=3306,
                                   charset="utf8")
        except Exception as e:
            conn.rollback()
            self.log_info("db")
            logging.exception("数据库连接错误...", e)
            print("数据库连接错误...", e)
        else:
            cur = conn.cursor()  # 获取一个游标
            cur.execute(sql)
            conn.commit()
            data = cur.fetchall()  # 返回元组，元素也是元组，一个元组表示一个
            cur.close()
            conn.close()

    def place_order(self, flag=0):
        # 下单，根据flag判断批量/单笔
        try:
            markets_data = self.get_markets_data()
        except Exception as e:
            self.log_info("db")
            logging.exception("获取市场信息失败...", e)
            print("获取市场信息失败...", e)
        else:
            a, b = self.starting_price
            for item in range(self.grid_counts):
                self.trade_amount = random.uniform(float(markets_data["minAmount"]), 10)
                if self.order_type == "buy" and flag == 0:
                    a, b = a-0.5, a
                elif self.order_type == "sell" and flag == 0:
                    a, b = b, b+0.5
                price = random.uniform(a, b)
                price = round(price, markets_data["priceScale"])
                amount = round(self.trade_amount, markets_data["amountScale"])
                try:
                    res = order(str(amount), self.currency_type, str(price), self.order_type)
                    sql = "insert into exx_order(price, amount, currency, ordertype, orderid)" \
                          " values({},'{}','{}','{}','{}')".format(price, str(amount), self.currency_type, self.order_type, res["id"])
                    self.connect_db(sql)
                    # 字典存放下单id,key为buy/sell，value为id列表
                    self.id_list.append({res["id"]: (a, b)})
                except Exception as e:
                    self.log_info("api")
                    logging.exception("下单失败...", e)
                    print("下单失败")
                time.sleep(0.5)

        print(self.id_list)

    def get_order_info(self):
        # 获取订单信息
        try:
            markets_data = self.get_markets_data()
        except Exception as e:
            self.log_info("db")
            logging.exception("获取市场信息失败...", e)
            print("数据库连接错误...", e)
        else:
            self.grid_counts = 1
            while True:
                for item in self.id_list:
                    b_id = list(item.keys())[0]
                    limit = item[b_id]
                    try:
                        order_info = getOrder(self.currency_type, b_id)  # 调用api
                        print(b_id, limit, order_info)
                        # 挂单交易完成，生成对应的buy/sell挂单
                        if order_info["status"] in [2, 3]:
                            if order_info["type"] == "buy":
                                price = order_info["price"]*(1+0.005)
                                price = round(price, markets_data["priceScale"])
                                self.id_list.remove(item)
                                order(str(order_info["trade_amount"]),
                                      self.currency_type,
                                      str(price),
                                      "sell")  # 调用api
                            elif order_info["type"] == "sell":
                                price = order_info["price"]*(1-0.005)
                                price = round(price, markets_data["priceScale"])
                                self.id_list.remove(item)
                                order(str(order_info["trade_amount"]),
                                      self.currency_type,
                                      str(price),
                                      "buy")  # 调用api

                        # 挂单在一段时间内未成交，撤单并重新下单
                        # elif order_info["status"] == 0:
                        #     res = cancelOrder(self.currency_type, b_id)
                        #     self.id_list.remove(item)
                        #     self.starting_price = limit
                        #     if res["code"] in ["100", "211", "212"]:
                        #         self.place_order(1)
                    except Exception as e:
                        print(e)
                    time.sleep(1)
                time.sleep(10)

    def run(self):
        self.place_order()
        self.get_order_info()


if __name__ == "__main__":
    currency_type = "eth_usdt"
    change = round(random.uniform(0.004, 0.005), 3)
    # b_order = GridStrategy((99, 100), 10, 0, change, currency_type, "buy")
    # s_order = GridStrategy((101, 102), 10, 0, change, currency_type, "sell")
    thread1 = GridStrategy((99, 100), 10, 0, change, currency_type, "buy")
    thread2 = GridStrategy((98, 99), 10, 0, change, currency_type, "sell")
    thread1.start()
    thread2.start()




