import random
from pymysql import *
import time
import logging
from threading import Thread
from dealapi.exx.exxService import ExxService
from dealapi.exx.exxMarket import MarketCondition
from apps.deal.models import Account, Property, LastdayAssets


class GridStrategy(Thread):

    def __init__(self, **kwargs):
        # kwargs = {'robot_obj': robot_obj, 'order_type': order_type}
        super().__init__()
        self.robot_obj = kwargs['robot_obj']                                          # 机器人对象
        self.currency_type = self.robot_obj.currency + '_' + self.robot_obj.market    # 交易对
        self.order_type = kwargs['order_type']                                        # 挂单类型
        self.id_list = list()                                                         # 挂单id列表
        self.grid_range = (self.robot_obj.resistance - self.robot_obj.support_level) / self.robot_obj.girding_num
        self.Flag = True  # 停止标志位

        # 初始化平台接口对象
        account_obj = Account.objects.get(id=self.robot_obj.trading_account_id)  # 获取账户信息
        platform = account_obj.platform                                          # 账户对应的平台
        if str(platform) == 'EXX':
            self.market_api = MarketCondition(self.currency_type)
            self.server_api = ExxService(account_obj.accesskey, account_obj.secretkey)
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

    def get_markets_data(self):
        """
        获取市场行情数据
        :return:
        """
        markets_data = self.market_api.get_markets()    # --------------------------------API
        return markets_data.get(self.currency_type)

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

    def place_order(self, item=None, order_type=None, flag=0):
        """
        下单，根据flag判断批量or单笔
        :param flag: 默认参数
        :param item: {res.get("id"): {"price_range": (a, b), "order_type": self.order_type, "price": price,
                    "amount": amount}}
        :param order_type: 下单类型
        :return:
        """
        try:
            # 调用实例方法,获取市场行情数据
            markets_data = self.get_markets_data()
        except Exception as e:
            self.log_info("api")
            logging.exception("GET MARKETS DATA FAILED...", e)
            print("获取市场信息失败...", e)
        else:
            # 计算买一价，卖一价
            min_buy1 = self.robot_obj.current_price-self.grid_range*3/2
            max_buy1 = self.robot_obj.current_price-self.grid_range
            min_sell1 = self.robot_obj.current_price+self.grid_range
            max_sell1 = self.robot_obj.current_price+self.grid_range*3/2

            for i in range(self.robot_obj.girding_num):
                # 根据挂单类型计算挂单价格区间
                if self.order_type == "buy" and flag == 0:
                    a, b = min_buy1-self.grid_range*i, max_buy1-self.grid_range*i
                    # 获取挂卖单价的小数位
                    price = round(random.uniform(a, b), markets_data.get("priceScale"))
                elif self.order_type == "sell" and flag == 0:
                    a, b = min_sell1+self.grid_range*i, max_sell1+self.grid_range*i
                    # 获取挂买单价的小数位
                    price = round(random.uniform(a, b), markets_data.get("amountScale"))

                # 获取挂单数量
                amount = random.uniform(self.robot_obj.min_num, self.robot_obj.min_num)
                try:
                    if order_type is None:
                        # 如果order_type为空，挂原始单
                        res = self.server_api.order(str(amount), self.currency_type, str(price), self.order_type)
                        # 下单成功，添加下单id
                        if res.get("id") is not None:
                            self.id_list.append(
                                {res.get("id"): {"price_range": (a, b),
                                                 "order_type": self.order_type,
                                                 "price": price,
                                                 "amount": amount}}
                            )
                    else:
                        # 如果order_type不为空，更新挂单
                        b_id = list(item.keys())[0]
                        a, b = item[b_id]["price_range"]
                        price = random.uniform(a, b)
                        res = self.server_api.order(str(amount), self.currency_type, str(price), order_type)
                        if res.get("id") is not None:
                            if item is not None:
                                # item不为空，移除需要撤单的数据
                                self.id_list.remove(item)
                            self.id_list.append(
                                {res.get("id"): {"price_range": (a, b),
                                                 "order_type": order_type,
                                                 "price": price,
                                                 "amount": amount}}
                            )

                except Exception as e:
                    self.log_info("api")
                    logging.exception("PLACE ORDER ERROR...", e)
                    print("下单失败", e)
                # time.sleep(0.1)

    def completed_order_info(self, b_id, price, item, order_info, order_type):
        """
        已完成订单进行反向挂单
        :param price: 反向挂单的价格
        :param b_id: 挂单id
        :param item: {res.get("id"): {"price_range": (a, b),"order_type": self.order_type,"price": price,
                    "amount": amount}}
        :param order_info: 委托单信息
        :param order_type: 挂单类型
        :return:
        """
        try:
            # 调用撤单接口
            ret = self.server_api.cancel_order(self.currency_type, b_id)
            # print("-"*20, ret, type(ret["code"]))

            # 撤单成功后，下单并添加下单id及价格区间
            if ret.get("code") in [100, 211, 212]:
                # 调用下单接口
                res = self.server_api.order(
                    str(order_info["trade_amount"]),    # 已完成的委托单信息，获取成交的数量
                    self.currency_type,                 # 交易对
                    str(price),
                    order_type
                )
                if res.get("id") is not None:
                    self.id_list.remove(item)
                    self.id_list.append(
                        {res.get("id"): {"price_range": None,
                                         "order_type": self.order_type,
                                         "price": price,
                                         "amount": order_info["trade_amount"]}}
                    )

        except Exception as e:
            self.log_info("api")
            logging.exception("UPDATE ORDER FAILED...", e)
            print("更新挂单失败")

    def save_completedorder(self, item, order_info):
        """
        保存已完成订单信息
        :param item: {res.get("id"): {"price_range": (a, b),"order_type": self.order_type,"price": price,
                    "amount": amount}}
        :param order_info: 委托单信息
        :return:
        """
        closing_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(order_info.get("trade_date")/1000))

        sql_select = "select * from deal_orderinfo where order_id = %s"
        ret = self.connect_db(sql_select, (order_info.get("id"),))
        if ret:
            # ret不为空，更新部分成交挂单数据
            sql = "update deal_orderinfo set closing_price=%s,total_price=%s where order_id=%s"
            closing_price = float(ret[3])+float(order_info.get("price"))
            total_price = float(order_info.get("trade_amount")) * float(order_info.get("price"))
            self.connect_db(sql, (closing_price, total_price, order_info.get("id")))

        else:
            # ret为空，保存已完成挂单信息
            sql = "insert into deal_orderinfo(currency_pair, order_type, order_id, " \
                  "closing_price, total_price, closing_time, account_id) " \
                  "values('{}','{}','{}','{}',{},'{}','{}')".format(
                    self.currency_type, order_info.get("type"),
                    order_info.get("id"), float(order_info.get("price")),
                    float(order_info.get("trade_amount")) * float(order_info.get("price")),
                    closing_time, self.robot_obj.id)
            self.connect_db(sql)

    def update_order_info(self):
        """
        更新挂单信息
        :return:
        """
        try:
            markets_data = self.get_markets_data()
        except Exception as e:
            self.log_info("api")
            logging.exception("GET_ORDER_INFO...", e)
            print("获取挂单信息失败...", e)
        else:
            # 循环控制，读取数据库数据
            # num = self.robot_obj.orders_frequency
            num = 0
            # 单笔下单
            self.robot_obj.girding_num = 1
            while True:
                if not self.Flag:
                    break
                else:
                    print("id列表", self.id_list, len(self.id_list))
                    for item in self.id_list:
                        # 获取要更新挂单id
                        b_id = list(item.keys())[0]
                        # 挂单价格区间
                        limit = item[b_id]["price_range"]
                        # 挂单类型
                        order_type = item[b_id]["order_type"]
                        try:
                            # 调用接口，获取委托单信息，如status,type,price等----------------------------API
                            order_info = self.server_api.get_order(self.currency_type, b_id)

                            # 已完成挂单交易，撤单并反向挂单
                            if order_info.get("status") in [2, 3]:
                                # 保存已完成的挂单信息
                                self.save_completedorder(item, order_info)
                                if order_info.get("type") == "buy":
                                    # 反向挂单价，不做更新
                                    price = order_info.get("price")+self.grid_range
                                    price = round(price, markets_data.get("priceScale"))
                                    t = Thread(target=self.completed_order_info,
                                               args=(b_id, price, item, order_info, "sell"))
                                    t.start()
                                elif order_info.get("type") == "sell":
                                    price = order_info.get("price")-self.grid_range
                                    price = round(price, markets_data.get("amountScale"))
                                    t = Thread(target=self.completed_order_info,
                                               args=(b_id, price, item, order_info, "buy"))
                                    t.start()

                            # 挂单在一段时间内未成交，撤单并重新下单，不包括反向挂单
                            elif (order_info.get("status") in [0, 1]) and (limit is not None) and num == 2:
                                res = self.server_api.cancel_order(self.currency_type, b_id)
                                print("*"*50, res.get("code"))
                                if res.get("code") in [100, 211, 212]:
                                    # 撤单成功再下单
                                    self.place_order(item, order_type, 1)
                                    # t1 = Thread(target=self.place_order, args=(item, order_type, 1))
                                    # t1.start()

                            # elif order_info.get("status") in [3]:
                            #     # 保存部分成交的挂单信息
                            #     self.save_completedorder(item, order_info)

                        except Exception as e:
                            self.log_info("api")
                            logging.exception("GET_ORDER_INFO...", e)
                            print("获取挂单状态失败...", e)
                    # 控制已完成和未完成挂单的更新频率
                    num += 1
                    if num == 3:
                        num = 0
                    # time.sleep(1)

    def run(self):
        self.place_order()
        self.update_order_info()
