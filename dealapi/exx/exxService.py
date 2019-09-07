# _*_ coding:utf-8 _*_
import requests
import time
import hmac
import hashlib
from requests import ConnectionError, ReadTimeout
from utils import Logger


baseurl = {"SERVICE_API": "http://192.168.4.66:8804/api/",
       }


class ExxService(object):
    log = Logger.MylogHandler("exxdeal")

    def __init__(self, platform, secretkey, accesskey):
        self.platform = platform
        self.baseUrl = baseurl["SERVICE_API"]
        self.secretkey = secretkey
        self.accesskey = "accesskey=" + accesskey

    def sha512_signature(self, params):
        current_time = str(int(time.time() * 1000))
        # 拼接加密参数assckey、时间、参数
        # param = "&amount" + amount + "&currency" + currency + "&price" + price + "&type" + type
        str_params = self.accesskey + params + "&nonce=" + current_time
        list_parmas = str_params.split("&")
        sort_parmas = sorted(list_parmas)
        singature_parmas = "&".join(sort_parmas)
        singature_parmas = bytes(singature_parmas, encoding="utf-8")
        signature = hmac.new(bytes(self.secretkey, encoding="utf-8"), singature_parmas, hashlib.sha512).hexdigest()

        return signature

    """
    委托下单
    :param: amount 交易数量
    :param: currency:eth_usdt 交易的对
    :param: price:1024 价格
    :param: type:buy/sell 交易类型
    :return: int 交易id
    """
    def order(self, amount, currency, price, type):
        result = {}
        current_time = str(int(time.time() * 1000))
        if isinstance(amount,int):
            amount = str(amount)
        # print(current_time)
        try:
            params = "&amount=" + amount + "&currency=" + currency + "&price=" + price + "&type=" + type
            url = self.baseUrl + "order" + "?" + self.accesskey + params + \
                  "&nonce=" + current_time + "&signature=" + self.sha512_signature(params)
            try:
                response = requests.get(url, timeout=5)
                result = response.json()
            except(ConnectionError, ReadTimeout) as e:
                self.log.error("请求下单链接失败", e)
            # 签名验证不通过，开始重新3次连接，3次连接不成功退出连接
            if result['code'] == 103:
                for i in range(1, 4):
                    response = requests.get(url)
                    result = response.json()
                    self.log.info("请求第%s次" % str(i))
                    # if result['code'] != 100:
                    #     return result.update({"code":400,"message":"请求失败"})
        except Exception as e:
            self.log.error("委托下单失败", e)
        return result


    """
    取消委托
    :param: currency：eth_btc 交易对
    :param: id：123456789  交易id
    :return: json 对象
    """

    def cancel_order(self, currency, id):
        try:
            current_time = str(int(time.time() * 1000))
            params = "&id=" + id + "&currency=" + currency
            url = self.baseUrl + "cancel" + "?" + self.accesskey + params + "&nonce=" + current_time + \
                  "&signature=" + self.sha512_signature(params)
            response = requests.get(url)
            result = response.json()
            # print(result)
        except Exception as e:
            print("取消委托失败", e)
        return result

    """
    获取委托买单或卖单
    :param: id : 123456789 交易id
    :param: currency :eth_btc  交易对 
    :return: json 对象
    """

    def get_order(self, currency, id):
        result = {}
        try:
            current_time = str(int(time.time() * 1000))
            params = "&currency=" + currency + "&id=" + id
            url = self.baseUrl + "getOrder" + "?" + self.accesskey + params + "&nonce=" + current_time + \
                  "&signature=" + self.sha512_signature(params)
            # print(url)
            response = requests.get(url)
            result = response.json()

        except Exception as e:
            print("获取委托买单或买单失败", e)
        return result

    """
     获取多个委托买单或卖单，每次请求返回10条记录
    :param:  pageIndex : 获取页数 
    :param: currency :eth_btc  交易对 
    :param:  type : buy/sell 交易类型
    :return: josn对象
    """

    def get_openorders(self, currency, pageindex, type):
        if isinstance(pageindex, int):
            pageindex = str(pageindex)
        try:
            current_time = str(int(time.time() * 1000))
            params = "&pageIndex=" + pageindex + "&currency=" + currency + "&type=" + type
            url = self.baseUrl + "getOpenOrders" + "?" + self.accesskey + params + "&nonce=" + current_time + \
                  "&signature=" + self.sha512_signature(params)
            print(url)
            response = requests.get(url)
            result = response.json()
        except Exception as e:
            print("获取多个买单或卖单失败", e)
        return result

    """
    :param:null
    :url: https://trade.exx.com/api/getBalance?accesskey=your_access_key&nonce=当前时间毫秒数&signature=请求加密签名串
    :return
    """

    def get_balance(self):
        params = ""
        current_time = str(int(time.time() * 1000))
        url = self.baseUrl + "getBalance" + "?" + self.accesskey + "&nonce=" + current_time + \
              "&signature=" + self.sha512_signature(params)
        response = requests.get(url)
        result = response.json()
        # print('+'*20, result)
        return result


# service_api = ExxService('EXX', 'c6b2ee35465dfddf535e8ddaeaaaf4ee8a90894e', '3b56369d-8072-461e-91f6-243b6277af01')
# data = service_api.get_balance()
# print(data)







