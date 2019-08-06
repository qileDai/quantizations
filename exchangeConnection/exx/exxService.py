# _*_ coding:utf-8 _*_
import requests
from requests import ConnectionError,ReadTimeout
from exchangeConnection.exx.util import sha512_signature
import time

from utils import Logger
import accountConfig

log = Logger.MylogHandler("exxdeal")



"""
Exx交易平台交易类
"""
baseUrl = accountConfig.EXX["SERVICE_API"]
secretKey = accountConfig.EXX["SECRET_KEY"]
accesskey = accountConfig.EXX["ACCESS_KEY"]


"""
委托下单
:param: amount 交易数量
:param: currency:eth_usdt 交易的对
:param: price:1024 价格
:param: type:buy/sell 交易类型
:return: int 交易id
"""
def order(amount, currency, price, type):
    result = {}
    current_time = str(int(time.time() * 1000))
    if isinstance(amount,int):
        amount = str(amount)
    # print(current_time)
    try:
        params = "&amount=" + amount + "&currency=" + currency + "&price=" + price + "&type=" + type
        url = baseUrl + "order" + "?" + accesskey + params + \
              "&nonce=" + current_time + "&signature=" + sha512_signature(params)
        try:
            response = requests.get(url,timeout=5)
            result = response.json()
        except(ConnectionError, ReadTimeout) as e:
            log.error("请求下单链接失败",e)
        # 签名验证不通过，开始重新3次连接，3次连接不成功退出连接
        if result['code'] == 103:
            for i in range(1, 4):
                response = requests.get(url)
                result = response.json()
                log.info("请求第%s次" %str(i))
                # if result['code'] != 100:
                #     return result.update({"code":400,"message":"请求失败"})
    except Exception as e:
        log.error("委托下单失败",e)
    return result


"""
取消委托
:param: currency：eth_btc 交易对
:param: id：123456789  交易id
:return: json 对象
"""

def cancelOrder(currency, id):

    try:
        current_time = str(int(time.time() * 1000))
        params = "&id=" + id + "&currency=" + currency
        url = baseUrl + "cancel" + "?" + accesskey + params + "&nonce=" + current_time + \
              "&signature=" + sha512_signature(params)
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

def getOrder(currency, id):
    result = {}
    try:
        current_time = str(int(time.time() * 1000))
        params = "&currency=" + currency + "&id=" + id
        url = baseUrl + "getOrder" + "?" + accesskey + params + "&nonce=" + current_time + \
              "&signature=" + sha512_signature(params)
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

def getOpenOrders(currency, pageIndex, type):
    if isinstance(pageIndex,int):
        pageIndex = str(pageIndex)
    try:
        current_time = str(int(time.time() * 1000))
        params = "&pageIndex=" + pageIndex + "&currency=" + currency + "&type=" + type
        url = baseUrl + "getOpenOrders" + "?" + accesskey + params + "&nonce=" + current_time + \
              "&signature=" + sha512_signature(params)
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

def getBalance():
    params = ""
    current_time = str(int(time.time() * 1000))
    url = baseUrl + "getBalance" + "?" + accesskey + "&nonce=" + current_time + \
          "&signature=" + sha512_signature(params)
    response = requests.get(url)
    result = response.json()
    print(result)













