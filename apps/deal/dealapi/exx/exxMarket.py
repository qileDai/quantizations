# _*_ coding:utf-8 _*_
import logging
import requests
from requests import ReadTimeout,ConnectionError
"""
市场行情类
"""
host_url = "http://192.168.4.171:9008"
markets_url = host_url + "/data/v1/markets"  # Exx所有市场url
tickers_url = host_url + "/data/v1/tickers"  # 所有行情url
ticker_url = host_url + "/data/v1/ticker"    # 单一市场行情url
depth_url = host_url + "/data/v1/depth"       # 市场深度


class MarketCondition(object):

    def __init__(self):
        pass

    """
    获取所有市场
    :return: dict 
    minAmount     : 最小交易金额
    amountScale   : 买方币小数点
    priceScale    : 卖方币小数点
    maxLevels     : 最大杠杆倍数，0表示不开放杠杆
    isOpen        : 是否开盘
    """

    def get_markets(self):
        try:
            response = requests.get(markets_url)
            res = response.json()
        except requests.exceptions.RequestException as e:
            print("获取市场失败", e)
        return res
    """
    获取市场行情
    :return dict
    vol       : 成交量(最近的24小时)
    last          : 最新成交价
    sell          : 卖一价
    buy           : 买一价
    weekRiseRate  : 周涨跌幅
    riseRate      : 24小时涨跌幅
    high          : 最高价
    low           : 最低价
    monthRiseRate : 30日涨跌幅

    """
    def get_tickers(self):
        try:
            response = requests.get(tickers_url)
            res = response.json()
        except requests.exceptions.RequestException as e:
            print("获取市场行情失败", e)
        return res

    """
    获取单一交易对的市场行情
    :param 交易对
    :return dict
    vol       : 成交量(最近的24小时)
    last          : 最新成交价
    sell          : 卖一价
    buy           : 买一价
    weekRiseRate  : 周涨跌幅
    riseRate      : 24小时涨跌幅
    high          : 最高价
    low           : 最低价
    monthRiseRate : 30日涨跌幅
    """
    def get_ticker(self,currency):
        url = ticker_url + "?" + "currency=" + currency
        try:
            response = requests.get(url)
            res = response.json()
        except requests.exceptions.RequestException as e:
            print("获取市场行情失败", e)
        return res
    """
    获取市场深度
    :param 交易对
    :return dict
    asks : 卖方深度
    bids : 买方深度
    timestamp : 此次深度的产生时间戳

    """
    def get_depth(self, currency):
        url = depth_url + "?" + "currency=" + currency
        try:
            response = requests.get(url)
            res = response.json()
        except requests.exceptions.RequestException as e:
            print("获取市场行情失败", e)
        return res
    """
    
    """
    def get_ticker_buy1_price(self, currency):
        res = MarketCondition.get_ticker(currency)
        # 处理买一价格
        buy1_price = res["buy"]
        return buy1_price

    def get_ticker_sell1_price(self, currency):
        res = MarketCondition.get_ticker(currency)
        # 处理卖一价格
        sell1_price = res["buy"]
        return sell1_price


# if __name__ == "__main__":
#     market = MarketCondition()
#     result = market.get_markets()
#     print(result)



