import requests
import global_settings
import json


class DataAPI(object):
    """
    行情接口
    """
    def __init__(self):
        self.base_url = global_settings.DATA_BASE_URL

    def markets_api(self):
        url = self.base_url + global_settings.URL[0]
        response = requests.get(url)
        # print(response.json())
        return json.loads(response.text)

    def tickers_api(self):
        url = self.base_url + global_settings.URL[1]
        response = requests.get(url)
        return json.loads(response.text)

    def ticker_api(self, currency_type):
        url = self.base_url + global_settings.URL[2] + currency_type
        response = requests.get(url)
        return json.loads(response.text)

    def depth_api(self, currency_type):
        url = self.base_url + global_settings.URL[3] + currency_type
        response = requests.get(url)
        return json.loads(response.text)

    def trades_api(self, currency_type):
        url = self.base_url + global_settings.URL[4] + currency_type
        response = requests.get(url)
        return json.loads(response.text)

    # https://api.exx.com/data/v1/klines?market=eth_btc&type=1min&size=1&assist=cny
    def kline_api(self, currency_type, period_type, size, assist):
        url = self.base_url + global_settings.KLINE_TYPES % (currency_type, period_type, size, assist)
        response = requests.get(url)
        return json.loads(response.text)

#
# if __name__ == "__main__":
#     tt = DataAPI()
#     res = tt.markets_api()
#     # res = tt.depth_api("eth_btc")
#     print(res["eth_usdt"]["priceScale"])
