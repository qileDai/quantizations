import pymysql
import random
import time
from exx_deal.APITest import DataAPI
from exx_deal.order import getOrder, order, cancelOrder, getOpenOrders


class GridStrategy(object):
    def __init__(self, *args):
        self.starting_price = args[0]
        self.grid_counts = args[1]
        self.trade_amount = args[2]
        self.change_by_day = args[3]
        self.currency_type = args[4]

    def connect_db(self, sql):
        conn = pymysql.connect(host="192.168.4.201", user="root", passwd="password",
                               db="exx_quantitativetrading", port=3306, charset="utf8")
        cur = conn.cursor()  # 获取一个游标
        cur.execute("sql")
        data = cur.fetchall()
        cur.close()
        conn.close()

    def buy_order(self):
        data_api = DataAPI()
        order_type = "buy"
        markets_data = data_api.markets_api()[self.currency_type]
        for item in range(self.grid_counts):
            self.trade_amount = random.uniform(float(markets_data["minAmount"]), 100)
            if self.trade_amount >= float(markets_data["minAmount"]) :
                price = self.starting_price*(1-self.change_by_day)**item
                price = round(price, markets_data["priceScale"])
                amount = round(self.trade_amount, markets_data["amountScale"])
                # sql = "insert into ..."
                result = order(str(amount), self.currency_type, str(price), order_type)
                time.sleep(1)
            else:
                print("msg:低于最小买入量，最小买入量为：%f" % float(markets_data["minAmount"]))

    def sell_order(self):
        data_api = DataAPI()
        # ticker_data = data_api.ticker_api(self.currency_type)
        # grid_price = self.starting_price
        markets_data = data_api.markets_api()[self.currency_type]
        order_type = "sell"
        for item in range(self.grid_counts):
            self.trade_amount = random.uniform(float(markets_data["minAmount"]), 100)
            if self.trade_amount >= float(markets_data["minAmount"]):
                price = self.starting_price*(1+self.change_by_day)**item
                price = round(price, markets_data["priceScale"])
                amount = round(self.trade_amount, markets_data["amountScale"])
                # sql = "insert into ..."
                result = order(str(amount), self.currency_type, str(price), order_type)
                time.sleep(1)
            else:
                print("msg:低于最小卖出量，最小卖出量为：%f" % float(markets_data["minAmount"]))

    def get_order_info(self):
        # 获取订单信息
        order_info = getOrder()
        print(order_info)
        if order_info["status"] == 2:
            if order_info["type"] == "buy":
                price = order_info["price"]*(1+0.005)
                # sql = "select * from ..."
                # res = self.connect_db(sql)
                order(str(price), str(order_info["trade_amount"]), self.currency_type, "sell")
            else:
                price = order_info["price"]*(1-0.005)
                # sql = "select * from ..."
                # res = self.connect_db(sql)
                order(str(price), str(order_info["trade_amount"]), self.currency_type, "buy")
        return None


if __name__ == "__main__":
    # currency_type = "eth_usdt"
    # change = round(random.uniform(0.004, 0.005), 3)
    # b_order = GridStrategy((100, 101), 10, 0, change, currency_type)
    # s_order = GridStrategy((100, 101), 10, 0, change, currency_type)
    # b_order.buy_order()
    # s_order.sell_order()
    get_order = getOpenOrders("eth_usdt", "10", "sell")
    print(get_order)
    for item in get_order:
        id = str(item['id'])
        print(id)
        cancelOrder("eth_usdt", id)
