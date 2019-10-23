import random
import traceback
import threading
from pymysql import *
import time
import logging
from threading import Thread
from dealapi.exx.exxService import ExxService
from dealapi.exx.exxMarket import MarketCondition
from apps.deal.models import Account, Property, LastdayAssets, Robot
from .WarningAccount import WarningAccount


class GridStrategy(Thread):

    def __init__(self, **kwargs):
        # kwargs = {'robot_obj': robot_obj, 'order_type': order_type}
        super().__init__()
        self.robot_obj = kwargs['robot_obj']        # 机器人对象
        self.currency_type = self.robot_obj.currency.lower() + '_' + self.robot_obj.market.lower()    # 交易对
        self.order_type = kwargs['order_type']      # 挂单类型
        self.grid_range = float(self.robot_obj.resistance - self.robot_obj.support_level) / float(self.robot_obj.girding_num)
        self.Flag = True                            # 停止标志位
        self.start_time = time.time()               # 启动时间
        self.lock = threading.Lock()                # 锁对象
        self.id_dict = dict()                       # 挂单字典，保存挂单信息

        # 初始化平台接口对象
        account_obj = Account.objects.get(id=self.robot_obj.trading_account_id)  # 获取账户信息
        platform = account_obj.platform             # 账户对应的平台
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
            # 限制价格
            price = random.uniform(a, b)
            if price <= self.robot_obj.support_level:
                price = self.robot_obj.support_level
            elif price >= self.robot_obj.resistance:
                price = self.robot_obj.resistance

            res = self.server_api.order(str(amount), self.currency_type, str(price), item[1]["order_type"])
            if res.get("id") is not None:
                # 下单成功
                self.lock.acquire()
                self.id_dict[res.get("id")] = {
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
            n = self.robot_obj.girding_num      # 批量挂原始单

            for i in range(n):
                # 计算原始挂单价格区间
                amount = round(random.uniform(ret[0], ret[1]), 3)
                if self.order_type == "buy":
                    a, b = min_buy1-self.grid_range*i, max_buy1-self.grid_range*i
                    # 获取挂卖单价的小数位
                    price = round(random.uniform(a, b), markets_data.get("priceScale", 2))
                    if a <= self.robot_obj.support_level:
                        price = self.robot_obj.support_level
                elif self.order_type == "sell":
                    a, b = min_sell1+self.grid_range*i, max_sell1+self.grid_range*i
                    # 获取挂买单价的小数位
                    price = round(random.uniform(a, b), markets_data.get("amountScale", 2))
                    if b >= self.robot_obj.resistance:
                        price = self.robot_obj.resistance
                try:
                    res = self.server_api.order(str(amount), self.currency_type, str(price), self.order_type)
                    # 下单成功，添加下单id
                    if res.get("id") is not None:
                        self.lock.acquire()
                        self.id_dict[res.get("id")] = {
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

                if (price == self.robot_obj.support_level) or (price == self.robot_obj.resistance):
                    break
                time.sleep(0.1)

        print('-'*10, self.id_dict)

    def save_completedorder(self, item, order_info):
        """
        保存已完成订单信息
        :param order_info: 委托单信息
        :param item:
        :return:
        """
        print('*'*10, '保存已完成订单信息')
        closing_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(order_info.get("trade_date")/1000))

        sql_select = "select * from deal_orderinfo where order_id = %s"
        ret = self.connect_db(sql_select, (order_info.get("id"),))
        if ret:
            # ret不为空，更新部分成交挂单数据
            sql = "update deal_orderinfo set closing_price=%s,total_price=%s where order_id=%s"
            closing_price = float(ret[2])
            num = float(order_info["trade_amount"])-float(item[1]["trade_amount"])
            total_price = float(ret[3]) + num * float(order_info.get("price"))
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
            results = self.server_api.get_openorders(self.currency_type, i, self.order_type)
            try:
                if results:
                    for result in results:
                        if result:
                            id = result['id']
                            response = self.server_api.cancel_order(self.currency_type, id)
                            # print(response)
            except Exception as e:
                print("%s单撤单完成:" % self.order_type)

    def completed_order_info(self, price, item, order_info, order_type, numb=None):
        """
        已完成订单进行反向挂单
        :param price: 反向挂单的价格
        :param numb: 反向挂单的数量
        :param item: "id": {"grade": grade,price_range": (a, b),"order_type": self.order_type,
                            "price": price,"amount": amount,"trade_amount": None}
        :param order_info: 委托单信息
        :param order_type: 挂单类型
        :return:
        """
        try:
            if order_info.get("status") in [2]:
                print(order_info["trade_amount"], item[1]["trade_amount"])
                if numb:
                    amount = numb
                else:
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
                        "price_range": item[1]["price_range"],
                        "order_type": order_type,
                        "price": price,
                        "amount": amount,
                        "trade_amount": 0,
                        "reverse": mark,
                        "id": item[0],
                    }
                    self.lock.release()

            elif order_info.get("status") in [3] and (item[1]["reverse"] is False):
                # 计算部分成交订单中下单数量
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
                        "price_range": item[1]["price_range"],
                        "order_type": order_type,
                        "price": price,
                        "amount": str(nums),
                        "trade_amount": 0,
                        "reverse": True,
                        "id": item[0],
                    }
                    self.lock.release()
            print(self.id_dict)
        except Exception as e:
            # self.log_info("api")
            # logging.exception("UPDATE ORDER FAILED...", e)
            print('traceback.print_exc():', traceback.print_exc())
            print("反向挂单失败", e)

    def merge_reverse_order(self, item):
        """
        同笔挂单反向多笔订单,再次反向挂单需合并
        :param item:
        :return:
        """
        iD = item[1].get("id")
        status_list = list()        # 同笔挂单反向多笔订单，将状态码放入同一列表中，判断是否需要再次反向挂单
        trade_amount = 0
        id_list = list()
        temp_dict = self.id_dict.items()
        for k, v in temp_dict:
            if v.get("id") == iD:
                try:
                    order_info = self.server_api.get_order(self.currency_type, k)
                    status_list.append(order_info.get("status"))
                    id_list.append(k)
                    trade_amount += order_info.get("trade_amount")
                except Exception as e:
                    print("获取委托单失败...", e)
        print('/-'*30, status_list, id_list)
        if len(set(status_list)) == 1:
            for elem in id_list[1:]:
                self.lock.acquire()
                # 删除id相同的挂单
                del self.id_dict[elem]
                self.lock.release()
            return True, trade_amount
        else:
            return False, None

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

            while True:
                if not self.Flag:
                    break
                else:
                    self.lock.acquire()
                    id_dicts = sorted(self.id_dict.items(), key=lambda x: x[1]["price"])
                    self.lock.release()
                    # 循环挂单信息
                    for item in id_dicts:
                        # 获取要更新挂单id
                        b_id = item[0]
                        trade_amount = None
                        try:
                            # 调用接口，获取委托单信息，如status,type,price等----------------------------API
                            order_info = self.server_api.get_order(self.currency_type, b_id)

                            # 已完成挂单交易，撤单并反向挂单
                            if order_info.get("status") in [2]:
                                print('已完成反向挂单', order_info.get("status"))

                                # 保存已完成的挂单信息
                                self.save_completedorder(item, order_info)
                                # 对已完成的反向挂单进行判断，若多笔id相同需要合并成一笔下单
                                if item[1].get("id"):
                                    ret, trade_amount = self.merge_reverse_order(item)
                                    if not ret:
                                        continue

                                if order_info.get("type") == "buy":
                                    # 反向挂单价，不做更新
                                    price = order_info.get("price")+self.grid_range
                                    # price = round(price, markets_data.get("priceScale"))
                                    # 启动反向挂单
                                    self.completed_order_info(price, item, order_info, "sell", trade_amount)

                                elif order_info.get("type") == "sell":
                                    price = order_info.get("price")-self.grid_range
                                    self.completed_order_info(price, item, order_info, "buy", trade_amount)

                            # 部分成交挂单
                            elif order_info.get("status") == 3 and \
                                    (item[1].get("trade_amount") != order_info.get("trade_amount")) and \
                                    (item[1].get("id") is None):
                                print('部分成交反向挂单', item[1].get("trade_amount"), order_info.get("trade_amount"))
                                # 保存已完成的挂单信息
                                self.save_completedorder(item, order_info)
                                if order_info.get("type") == "buy":
                                    # 反向挂单价，不做更新
                                    price = order_info.get("price")+self.grid_range
                                    # 启动反向挂单
                                    self.completed_order_info(price, item, order_info, "sell")

                                elif order_info.get("type") == "sell":
                                    price = order_info.get("price")-self.grid_range
                                    # price = round(price, markets_data.get("amountScale"))
                                    self.completed_order_info(price, item, order_info, "buy")
                        except Exception as e:
                            # self.log_info("api")
                            # logging.exception("GET_ORDER_INFO...", e)
                            print('traceback.print_exc():', traceback.print_exc())
                            print("获取委托单失败...", e)
                        time.sleep(0.2)
            if not self.Flag:
                for i in range(3):
                    self.cancel_orders()

    def update_order_info(self):
        """
        更新一段时间内未交易的挂单
        :return:
        """
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
                    if self.order_type == "sell":
                        # 针对sell类型的挂单进行排序
                        # temp_dicts = sorted(self.id_dict.items(), key=lambda x: (x[1]["order_type"], x[1]["price"]))
                        temp_dicts = dict()
                        for k, v in self.id_dict.items():
                            if v["order_type"] == "sell":
                                temp_dicts[k] = v
                        temp_dicts = sorted(temp_dicts.items(), key=lambda x: x[1]["price"])
                        if len(temp_dicts) > 8:
                            order_dicts = random.sample(temp_dicts[0:10], random.randint(1, 6))
                        else:
                            order_dicts = random.sample(temp_dicts, len(temp_dicts))

                    elif self.order_type == "buy":
                        # temp_dicts = sorted(self.id_dict.items(), key=lambda x: (x[1]["order_type"], x[1]["price"]))
                        temp_dicts = dict()
                        for k, v in self.id_dict.items():
                            if v["order_type"] == "buy":
                                temp_dicts[k] = v
                        temp_dicts = sorted(temp_dicts.items(), key=lambda x: x[1]["price"], reverse=True)
                        if len(temp_dicts) > 8:
                            order_dicts = random.sample(temp_dicts[0:10], random.randint(1, 6))
                        else:
                            order_dicts = random.sample(temp_dicts, len(temp_dicts))

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
                time.sleep(orders_frequency[0]/1000)

# ----------------------------------------------------------------------------------------------------------------------

    def set_risk_strategy(self):
        """
        设置风险策略
        :return:
        """
        # 实时获取交易对当前价
        while True:
            markets_data = self.market_api.get_ticker()
            current_price = markets_data.get("ticker")["last"]
            # 当前价低于止损价
            if float(current_price) <= float(self.robot_obj.stop_price):
                self.Flag = False
                time.sleep(3)
                # 停止策略之后更改状态
                Robot.objects.filter(id=self.robot_obj.id).update(run_status=1, status=0)
                # 获取卖单信息
                getopen_data = self.server_api.get_openorders(self.currency_type, '1', 'sell')
                if isinstance(getopen_data, dict):
                    # 获取卖一价
                    try:
                        depth_data = self.market_api.get_depth()
                        print('+'*30, depth_data)
                        sell_1_price, sell_1_amount = depth_data.get("bids")[0]
                        self.server_api.order(sell_1_amount, self.currency_type, sell_1_price, "sell")
                    except:
                        print("未获取到买一价")
                        break
                else:
                    # 一段时间内未成交，撤单
                    self.cancel_orders()

            # 当前价低于预警价
            elif float(current_price) <= float(self.robot_obj.warning_price):
                # 实时查询数据库中的warning_time
                sql = "select warning_time from deal_robot where id = %s"
                warning_time = self.connect_db(sql, (self.robot_obj.id,))
                # 获取机器人的预警账户
                warning_account = self.robot_obj.warning_account
                acc_list = list()
                acc_list.append(warning_account)
                warn = WarningAccount(acc_list, '网格', self.currency_type)
                warn.send_msg()
                print('---------预警', warning_time)
                time.sleep(float(warning_time[0])*60)
            else:
                break

    def run_thread(self):
        """
        运行更新挂单和反向挂单
        :return:
        """
        thread1 = Thread(target=self.reverse_order,)
        thread2 = Thread(target=self.update_order_info,)
        thread3 = Thread(target=self.set_risk_strategy,)
        thread1.start()
        thread2.start()
        time.sleep(10)
        thread3.start()
        thread1.join()
        thread2.join()
        thread3.join()

    def run(self):
        self.place_many_order()
        self.run_thread()



