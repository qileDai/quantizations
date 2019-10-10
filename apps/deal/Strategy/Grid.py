import random
from pymysql import *
import time
import datetime
import logging
from threading import Thread
from dealapi.exx.exxService import ExxService
from dealapi.exx.exxMarket import MarketCondition
from apps.deal.models import Account, Property, LastdayAssets
import traceback
import threading


class GridStrategy(Thread):

    def __init__(self, **kwargs):
        # kwargs = {'robot_obj': robot_obj, 'order_type': order_type}
        super().__init__()
        self.robot_obj = kwargs['robot_obj']                                          # 机器人对象
        self.currency_type = self.robot_obj.currency.lower() + '_' + self.robot_obj.market.lower()    # 交易对
        self.order_type = kwargs['order_type']                                        # 挂单类型
        self.id_dict = dict()                                                         # 挂单字典，保存挂单信息
        self.grid_range = float(self.robot_obj.resistance - self.robot_obj.support_level) / float(self.robot_obj.girding_num)
        self.Flag = True  # 停止标志位
        self.start_time = datetime.datetime.now()       # 启动时间
        self.lock = threading.Lock()

        # 初始化平台接口对象
        account_obj = Account.objects.get(id=self.robot_obj.trading_account_id)  # 获取账户信息
        platform = account_obj.platform                                          # 账户对应的平台
        if str(platform) == 'EXX':
            self.market_api = MarketCondition(self.currency_type)
            self.server_api = ExxService(account_obj.secretkey, account_obj.accesskey)
        elif str(platform) == 'HUOBI':
            pass
        elif str(platform) == 'BINANCE':
            pass

    def getParm(self):
        """
        外部获得内部信息函数
        :return:
        """
        return self.id_list

    def setFlag(self, parm):
        """
        停止线程的操作函数
        :param parm:
        :return:
        """
        self.Flag = parm  # boolean

    def log_info(self, log_name):
        """
        日志文件
        :param log_name: 日志文件名
        :return:
        """
        logging.basicConfig(
            filename="../%s.log" % log_name,
            filemode="w",
            format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
            datefmt="%d-%M-%Y %H:%M:%S",
            level=logging.DEBUG,
        )

    def connect_db(self, sql, params=None):
        """
        数据库操作
        :param sql: 执行的SQL语句
        :return:
        """
        try:
            # 创建Connection连接
            conn = connect(host='192.168.4.201',
                           port=3306,
                           database='exx_quantitative_admin',
                           user='root',
                           password='password',
                           charset='utf8')
        except Exception as e:
            print('数据库连接错误', e)
        else:
            # 获取cursor ------执行sql语句的对象
            cur = conn.cursor()
            # 执行sql语句
            cur.execute(sql, params)
            # 提交
            conn.commit()
            # 关闭 游标对象 和 连接对象
            cur.close()
            conn.close()
            return cur.fetchone()

    def place_one_order(self, item=None):
        """
        单笔下单
        :param item: "买n": {""id": res.get("id"),price_range": (a, b),"order_type": self.order_type,
                            "price": price,"amount": amount}
        :return:
        """
        try:
            # 获取下单数量
            sql = "select min_num,max_num from deal_robot where id = %s"
            ret = self.connect_db(sql, (self.robot_obj.id,))
            amount = round(random.uniform(ret[0], ret[1]), 3)
        except Exception as e:
            # self.log_info("api")
            # logging.exception("GET MARKETS DATA FAILED...", e)
            print("获取下单数量失败...", e)
        else:
            # 更新单笔挂单
            a, b = item[1]["price_range"]
            price = random.uniform(a, b)
            res = self.server_api.order(str(amount), self.currency_type, str(price), item[1]["order_type"])
            if res.get("id") is not None:
                # 下单成功
                self.lock.acquire()
                self.id_dict[res.get("id")] = {
                    "grade": item[1]["grade"],
                    "price_range": (a, b),
                    "order_type": self.order_type,
                    "price": price,
                    "amount": amount,
                    "trade_amount": 0,
                    "reverse": False,
                }
                del self.id_dict[item[0]]
                # print('删除--------------------------------------------------------------')
                self.lock.release()
            else:
                new_key = item[0] + "failed"
                self.lock.acquire()
                self.id_dict[new_key] = self.id_dict.pop(item[0])
                self.lock.release()

    def place_many_order(self):
        """
        批量下单
        :return:
        """
        try:
            # 调用实例方法,获取市场行情数据
            markets_data = self.market_api.get_markets()
        except Exception as e:
            # self.log_info("api")
            # logging.exception("GET MARKETS DATA FAILED...", e)
            print("获取市场信息失败...", e)
        else:
            # 计算买一价，卖一价
            min_buy1 = float(self.robot_obj.current_price)-self.grid_range*3/2
            max_buy1 = float(self.robot_obj.current_price)-self.grid_range
            min_sell1 = float(self.robot_obj.current_price)+self.grid_range
            max_sell1 = float(self.robot_obj.current_price)+self.grid_range*3/2
            # 获取挂单数量，实时查询数据库
            sql = "select min_num,max_num from deal_robot where id = %s"
            ret = self.connect_db(sql, (self.robot_obj.id,))
            amount = round(random.uniform(ret[0], ret[1]), 3)

            n = self.robot_obj.girding_num      # 批量挂原始单

            for i in range(n):
                # 批量更新
                grade = self.order_type + str(i+1)
                # 计算原始挂单价格区间
                if self.order_type == "buy":
                    a, b = min_buy1-self.grid_range*i, max_buy1-self.grid_range*i
                    # 获取挂卖单价的小数位
                    price = round(random.uniform(a, b), markets_data.get("priceScale", 2))
                elif self.order_type == "sell":
                    a, b = min_sell1+self.grid_range*i, max_sell1+self.grid_range*i
                    # 获取挂买单价的小数位
                    price = round(random.uniform(a, b), markets_data.get("amountScale", 2))

                try:
                    res = self.server_api.order(str(amount), self.currency_type, str(price), self.order_type)
                    # 下单成功，添加下单id
                    if res.get("id") is not None:
                        self.lock.acquire()
                        self.id_dict[res.get("id")] = {
                            "grade": grade,
                            "price_range": (a, b),
                            "order_type": self.order_type,
                            "price": price,
                            "amount": amount,
                            "trade_amount": 0,
                            "reverse": False,
                        }
                        self.lock.release()

                except Exception as e:
                    # self.log_info("api")
                    # logging.exception("PLACE ORDER ERROR...", e)
                    print('traceback.print_exc():', traceback.print_exc())
                    print("下单失败", e)
                time.sleep(0.1)
        print('-'*10, len(self.id_dict))

    def save_completedorder(self, order_info):
        """
        保存已完成订单信息
        :param order_info: 委托单信息
        :return:
        """
        print('*'*10, '保存已完成订单信息')
        closing_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(order_info.get("trade_date")/1000))

        sql_select = "select * from deal_orderinfo where order_id = %s"
        ret = self.connect_db(sql_select, (order_info.get("id"),))
        if ret:
            # ret不为空，更新部分成交挂单数据
            sql = "update deal_orderinfo set closing_price=%s,total_price=%s where order_id=%s"
            closing_price = float(ret[2])+float(order_info.get("price"))
            total_price = float(ret[3])+float(order_info.get("trade_amount"))*float(order_info.get("price"))
            self.connect_db(sql, (closing_price, total_price, order_info.get("id")))

        else:
            # ret为空，保存已完成挂单信息
            sql = "insert into deal_orderinfo(currency_pair, order_type, order_id, " \
                  "closing_price, total_price, closing_time, robot_id) " \
                  "values('{}','{}','{}','{}',{},'{}','{}')".format(
                    self.currency_type, order_info.get("type"),
                    order_info.get("id"), float(order_info.get("price")),
                    float(order_info.get("trade_amount"))*float(order_info.get("price")),
                    str(closing_time), self.robot_obj.id)
            self.connect_db(sql)

    def cancel_orders(self):
        """
        撤单
        :return:
        """
        for i in range(1, 10):
            # time.sleep(1)
            results = self.server_api.get_openorders(self.currency_type, i, self.order_type)
            try:
                if results:
                    for result in results:
                        if result:
                            id = result['id']
                            response = self.server_api.cancel_order(self.currency_type, id)
                            print(response)
            except Exception as e:
                print("%s单撤单完成:" % self.order_type, e)

    def completed_order_info(self, price, item, order_info, order_type):
        """
        已完成订单进行反向挂单
        :param price: 反向挂单的价格
        :param item: "id": {"grade": grade,price_range": (a, b),"order_type": self.order_type,
                            "price": price,"amount": amount,"trade_amount": None}
        :param order_info: 委托单信息
        :param order_type: 挂单类型
        :return:
        """
        try:
            if order_info.get("status") in [2]:
                print(order_info["trade_amount"], item[1]["trade_amount"])
                amount = float(order_info["trade_amount"])-float(item[1]["trade_amount"])

                # 反向挂单
                res = self.server_api.order(str(amount), self.currency_type, str(price), order_type)
                # 下单成功，添加反向挂单数据
                if item[1]["reverse"]:
                    mark = False
                else:
                    mark = True

                if res.get("id") is not None:
                    self.lock.acquire()
                    del self.id_dict[item[0]]
                    self.id_dict[res.get("id")] = {
                        "grade": item[1]["grade"],
                        "price_range": item[1]["price_range"],
                        "order_type": order_type,
                        "price": price,
                        "amount": amount,
                        "trade_amount": 0,
                        "reverse": mark
                    }
                    self.lock.release()
            elif order_info.get("status") in [3] and (item[1]["reverse"] is False):

                if item[1].get("trade_amount") == 0:
                    nums = order_info["trade_amount"]
                else:
                    nums = float(order_info["trade_amount"])-float(item[1]["trade_amount"])
                # 更新部分成交订单的数据
                self.lock.acquire()
                self.id_dict[item[0]]["trade_amount"] = order_info["trade_amount"]
                self.id_dict[item[0]]["amount"] = str(nums)
                self.lock.release()
                # 下单
                res = self.server_api.order(str(nums), self.currency_type, str(price), order_type)
                print('挂单数量', nums, type(nums), res)
                # 下单成功，添加部分成交订单中的已完成订单
                if res.get("id") is not None:
                    self.lock.acquire()
                    self.id_dict[res.get("id")] = {
                        "grade": item[1]["grade"],
                        "price_range": item[1]["price_range"],
                        "order_type": order_type,
                        "price": price,
                        "amount": str(nums),
                        # "trade_amount": order_info["trade_amount"],
                        "trade_amount": 0,
                        "reverse": True,
                    }
                    self.lock.release()
        except Exception as e:
            # self.log_info("api")
            # logging.exception("UPDATE ORDER FAILED...", e)
            print('traceback.print_exc():', traceback.print_exc())
            print("反向挂单失败", e)

    def reverse_order(self):
        """
        反向挂单
        :return:
        """
        try:
            markets_data = self.market_api.get_markets()
        except Exception as e:
            # self.log_info("api")
            # logging.exception("GET_ORDER_INFO...", e)
            print("获取挂单信息失败...", e)
        else:
            # 循环控制，读取数据库数据
            while True:
                if not self.Flag:
                    break
                else:
                    # 根据价格排序
                    if self.order_type == "sell":
                        self.lock.acquire()
                        id_dicts = sorted(self.id_dict.items(), key=lambda x: x[1]["price"])
                        self.lock.release()
                    elif self.order_type == "buy":
                        self.lock.acquire()
                        id_dicts = sorted(self.id_dict.items(), key=lambda x: x[1]["price"], reverse=True)
                        self.lock.release()
                    # 循环挂单信息
                    for item in list(id_dicts[0:5]):
                        # item格式[('123456',{"id": res.get("id"),price_range": (a, b),"order_type": self.order_type,
                        # "price": price,"amount": amount,"trade_amount": None}),...]
                        # 获取要更新挂单id
                        b_id = item[0]
                        try:
                            # 调用接口，获取委托单信息，如status,type,price等----------------------------API
                            order_info = self.server_api.get_order(self.currency_type, b_id)

                            # 已完成挂单交易，撤单并反向挂单
                            if order_info.get("status") in [2]:
                                print('已完成反向挂单', order_info.get("status"))
                                # 保存已完成的挂单信息
                                self.save_completedorder(order_info)
                                if order_info.get("type") == "buy":
                                    # 反向挂单价，不做更新
                                    price = order_info.get("price")+self.grid_range
                                    price = round(price, markets_data.get("priceScale"))
                                    # 启动反向挂单
                                    self.completed_order_info(price, item, order_info, "sell")

                                elif order_info.get("type") == "sell":
                                    price = order_info.get("price")-self.grid_range
                                    price = round(price, markets_data.get("amountScale"))
                                    self.completed_order_info(price, item, order_info, "buy")

                            # 部分成交挂单
                            elif order_info.get("status") == 3 and (item[1].get("trade_amount") != order_info.get("trade_amount")):
                                print('部分成交反向挂单', item[1].get("trade_amount"), order_info.get("trade_amount"))
                                # 保存已完成的挂单信息
                                self.save_completedorder(order_info)
                                if order_info.get("type") == "buy":
                                    # 反向挂单价，不做更新
                                    price = order_info.get("price")+self.grid_range
                                    price = round(price, markets_data.get("priceScale"))
                                    # 启动反向挂单
                                    self.completed_order_info(price, item, order_info, "sell")

                                elif order_info.get("type") == "sell":
                                    price = order_info.get("price")-self.grid_range
                                    price = round(price, markets_data.get("amountScale"))
                                    self.completed_order_info(price, item, order_info, "buy")

                        except Exception as e:
                            # self.log_info("api")
                            # logging.exception("GET_ORDER_INFO...", e)
                            print('traceback.print_exc():', traceback.print_exc())
                            print("获取委托单失败...", e)
                        time.sleep(0.1)

            if not self.Flag:
                for i in range(2):
                    self.cancel_orders()
                    # cancel_thread = Thread(target=self.cancel_orders)
                    # cancel_thread.start()

    def update_order_info(self):
        """
        更新一段时间内未交易的挂单
        :return:
        """
        # 挂单，检测卖一和买一update_order_info
        while True:
            if not self.Flag:
                break
            else:
                # 实时查询数据库中的刷单频率
                sql = "select orders_frequency from deal_robot where id = %s"
                orders_frequency = self.connect_db(sql, (self.robot_obj.id,))
                print('刷单频率', orders_frequency[0])
                # 未成功下单
                li_range = self.id_dict.items()
                for elem in list(li_range):
                    if 'failed' in elem[0]:
                        print("未成功下单", elem[0])
                        self.place_one_order(elem)

                self.lock.acquire()
                if len(self.id_dict) <= 10:
                    order_dicts = self.id_dict.items()
                else:
                    # 对价格进行排序
                    if self.order_type == "sell":
                        temp_dicts = sorted(self.id_dict.items(), key=lambda x: x[1]["price"])
                        order_dicts = random.sample(temp_dicts[0:10], 8)
                    elif self.order_type == "buy":
                        temp_dicts = sorted(self.id_dict.items(), key=lambda x: x[1]["price"], reverse=True)
                        order_dicts = random.sample(temp_dicts[0:10], 8)
                # print('*'*20, list(order_dicts))
                self.lock.release()
                # 循环挂单信息
                for item in list(order_dicts):
                    # 获取要更新挂单id
                    b_id = item[0]
                    try:
                        # 调用接口，获取委托单信息，如status,type,price等----------------------------API
                        order_info = self.server_api.get_order(self.currency_type, b_id)
                        # 挂单在一段时间内未成交，撤单并重新下单，不包括反向挂单
                        if (order_info.get("status") in [0, 1]) and (item[1]["reverse"] is False):
                            res = self.server_api.cancel_order(self.currency_type, b_id)
                            if res.get("code") in [100, 211, 212]:
                                # 撤单成功再下单
                                time.sleep(0.1)
                                self.place_one_order(item)

                    except Exception as e:
                        # self.log_info("api")
                        # logging.exception("GET_ORDER_INFO...", e)
                        print('traceback.print_exc():', traceback.print_exc())
                        print("获取委托单失败...", e)
            # 控制更新频率
                time.sleep(orders_frequency[0])

        if not self.Flag:
            for i in range(2):
                self.cancel_orders()
                # cancel_thread = Thread(target=self.cancel_orders)
                # cancel_thread.start()

    def run_thread(self):
        """
        运行更新挂单和反向挂单
        :return:
        """
        thread1 = Thread(target=self.reverse_order,)
        thread2 = Thread(target=self.update_order_info,)
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

    def run(self):
        self.place_many_order()
        self.run_thread()



