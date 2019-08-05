# _*_ coding:utf-8 _*_
import requests
from signature.ExxSignature import sha512_signature
import time

"""
委托下单交易
"""
baseUrl = "http://192.168.4.66:8804/api/"
secretKey = b"c6b2ee35465dfddf535e8ddaeaaaf4ee8a90894e"
accesskey = "accesskey=3b56369d-8072-461e-91f6-243b6277af01"

"""
委托下单
:param: amount 交易数量
:param: currency:eth_usdt 交易的对
:param: price:1024 价格
:param: type:buy/sell 交易类型
:return: int 交易id
"""


def order(amount, currency, price, type):
    try:
      current_time = str(int(time.time() * 1000))
      params = "&amount=" + amount + "&currency=" + currency + "&price=" +price + "&type=" + type
      url = baseUrl + "order" + "?" + accesskey + params + \
            "&nonce=" + current_time + "&signature=" + sha512_signature(params)
      response = requests.get(url)
      result = response.json()
    except Exception as e:
      print("委托下单失败",e)
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
        params = "&id="+ id +"&currency="+currency
        url = baseUrl + "cancel" + "?" +accesskey + params +"&nonce=" +current_time + \
              "&signature="+ sha512_signature(params)
        response = requests.get(url)
        result = response.json()
        print(result)
    except Exception as e:
        print("取消委托失败",e)
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
        params = "&currency=" + currency +"&id=" + id
        url = baseUrl + "getOrder" + "?" + accesskey + params + "&nonce=" + current_time + \
              "&signature=" + sha512_signature(params)
        print(url)
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
        print("获取多个买单或卖单失败",e)
    return  result

"""
:param:null
:url: https://trade.exx.com/api/getBalance?accesskey=your_access_key&nonce=当前时间毫秒数&signature=请求加密签名串
:return
"""


def getBalance():
    params = ""
    current_time = str(int(time.time() * 1000))
    url = baseUrl + "getBalance" + "?" + accesskey + "&nonce=" + current_time +\
          "&signature=" + sha512_signature(params)
    response = requests.get(url)
    result = response.json()
    print(result)











