# _*_ coding:utf-8 _*_
from grid_strategy.order import getOpenOrders, cancelOrder
import time

price = 1023
is_stop = True


def cancel_orders(type):
    print("开始执行%s单撤单" %type)
    print("*****" * 2)
    for i in range(1, 20):
        results = getOpenOrders("eth_usdt", i, type)
        try:
            if results:
                for result in results:
                    if result:
                        id = result['id']
                        time.sleep(0.5)
                        response = cancelOrder("eth_usdt", id)
                        print(response)
        except Exception as e:
            print("%s单撤单完成:" %type, e)


if __name__ == "__main__":
    cancel_orders("buy")
    cancel_orders("sell")









