import pymysql
import random
import time
from threading import Thread
from exx_deal.APITest import DataAPI
from exx_deal.order import getOrder, order, cancelOrder, getOpenOrders


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

    def connect_db(self, sql):
        try:
            conn = pymysql.connect(host="192.168.4.201", user="root", passwd="password",
                                   db="exx_quantitativetrading", port=3306, charset="utf8")
        except Exception as e:
            print("数据库连接错误...", e)
        else:
            cur = conn.cursor()  # 获取一个游标对象
            cur.execute(sql)
            data = cur.fetchall()  # 返回元组，元素也是元组，一个元组表示一个
            cur.close()
            conn.close()

    def place_order(self, flag=0):
        # 下单，根据flag判断批量/单笔
        try:
            data_api = DataAPI()
            markets_data = data_api.markets_api()[self.currency_type]
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
                # sql = "insert into ..."
                res = order(str(amount), self.currency_type, str(price), self.order_type)
                print(res)
                # 字典存放下单id,key为buy/sell，value为id列表
                self.id_list.append({res["id"]: (a, b)})
                time.sleep(0.5)
            print(self.id_list)
        except Exception as e:
            print("下单失败...", e)

    def get_order_info(self):
        # 获取订单信息
        self.grid_counts = 1
        data_api = DataAPI()
        markets_data = data_api.markets_api()[self.currency_type]
        while True:
            for item in self.id_list:
                b_id = list(item.keys())[0]
                limit = item[b_id]
                try:
                    order_info = getOrder(self.currency_type, b_id)
                    print(b_id, limit, order_info)
                    # 挂单交易完成，生成对应的buy/sell挂单
                    if order_info["status"] in [2, 3]:
                        if order_info["type"] == "buy":
                            price = order_info["price"]*(1+0.005)
                            price = round(price, markets_data["priceScale"])
                            # sql = "select * from ..."
                            # res = self.connect_db(sql)
                            self.id_list.remove(item)
                            order(str(order_info["trade_amount"]), self.currency_type, str(price), "sell")
                        elif order_info["type"] == "sell":
                            price = order_info["price"]*(1-0.005)
                            price = round(price, markets_data["priceScale"])
                            # sql = "select * from ..."
                            # res = self.connect_db(sql)
                            self.id_list.remove(item)
                            order(str(order_info["trade_amount"]), self.currency_type, str(price), "buy")

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
