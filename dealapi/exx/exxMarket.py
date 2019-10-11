# _*_ coding:utf-8 _*_
import logging
import requests
from dealapi import accountConfig

"""
市场行情类
"""


class MarketCondition(object):

    def __init__(self, currency=None):
        self.currency = currency

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
            response = requests.get(accountConfig.EXX_MARKET['markets_url'])
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
            response = requests.get(accountConfig.EXX_MARKET['tickers_url'])
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
    def get_ticker(self):
        url = accountConfig.EXX_MARKET['ticker_url'] + "?" + "currency=" + self.currency
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
    def get_depth(self):
        url = accountConfig.EXX_MARKET['depth_url'] + "?" + "currency=" + self.currency
        try:
            response = requests.get(url)
            res = response.json()
        except requests.exceptions.RequestException as e:
            print("获取市场行情失败", e)
        return res

    """
     https://api.exx.com/data/v1/trades?currency=eth_hsr
    """
    def get_history(self):
        url = accountConfig.EXX_MARKET['trades_url'] + "?" + "currency=" + self.currency
        try:
            response = requests.get(url)
            res = response.json()
        except requests.exceptions.RequestException as e:
            print("获取历史成交失败", e)
        return res

    """
    获取K线
    """
    def get_klines(self, ktype, ksize):
        url = accountConfig.EXX_MARKET['klines_url'] + "?" + "market=" + self.currency + \
              "&type=" + ktype + "&size=" + ksize
        try:
            response = requests.get(url)
            res = response.json()
        except requests.exceptions.RequestException as e:
            print("获取K线失败", e)
        return res

    def get_ticker_buy1_price(self):
        res = MarketCondition.get_ticker(self.currency)
        # 处理买一价格
        buy1_price = res["buy"]
        return buy1_price

    def get_ticker_sell1_price(self):
        res = MarketCondition.get_ticker(self.currency)
        # 处理卖一价格
        sell1_price = res["buy"]
        return sell1_price


if __name__ == "__main__":
    market = MarketCondition('btc_usdt')
    result = market.get_ticker()
    print(result)



