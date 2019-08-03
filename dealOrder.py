# _*_ coding:utf-8 _*_
from order import order,getOrder,getOpenOrders,getBalance,cancelOrder
import random
import time

price = 1023
is_stop = True

def buy_order():
    while is_stop:
        num = random.uniform(2, 100)
        num = str(num)
        buy_price = price + 0.1
        buy_price = str(buy_price)
        time.sleep(0.2)
        result = order(num, "eth_usdt$@#@&&&", buy_price, "buy")
        print(result)
def sell_order():
    while is_stop:
        num = random.uniform(2, 100)
        num = str(num)
        sell_price = price - 0.1
        sell_price = str(sell_price)
        time.sleep(0.2)
        result = order(num, "eth_usdt", sell_price, "sell")
        print(result)


def getOrders(type):
    for i in range(1,8):
        results = getOpenOrders("eth_usdt",i,type)
        for result in results:
            if result == "":
                return
            id  = result['id']
            time.sleep(0.5)
            ss = cancelOrder("eth_usdt",id)
            print(ss)



if __name__ == "__main__":
    getOrders("buy")









