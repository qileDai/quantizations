# _*_ coding:utf-8 _*_
from strategy.ExxMarket import MarketCondition
"""
三角套利
"""

ltc_btc_sell1_price = MarketCondition.get_ticker_sell1_price("ltc_btc")
ltc_btc_slippage = ""
btc_cny_sell1_price = MarketCondition.get_ticker_sell1_price("btc_cny")
btc_cny_slippage = ""
ltc_cny_buy1_price = MarketCondition.get_ticker_buy1_price("ltc_cny")
ltc_cny_slippage = ""
ltc_btc_fee = "" #ltc_btc费率
btc_cny_fee = "" # btc_cny费率
ltc_cny_fee = "" #ltc_cny 费率

P1 = btc_cny_sell1_price * (1 + btc_cny_slippage)
P2 = ltc_cny_buy1_price * (1 - ltc_cny_slippage)
P3 = ltc_btc_sell1_price *(1 + ltc_btc_slippage)



class ExxArbitrage(object):

    def __init__(self):
        pass






