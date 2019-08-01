# _*_ conding:utf-8 _*_
import time
import hashlib
import hmac

accesskey = "accesskey=3b56369d-8072-461e-91f6-243b6277af01"
secretKey = b"c6b2ee35465dfddf535e8ddaeaaaf4ee8a90894e"


"""
签名处理
:param：str_params 签名参数
:return: signature bytes
"""
def sha512_signature(str_params):
    list_parmas = str_params.split("&")
    sort_parmas = sorted(list_parmas)
    singature_parmas = "&".join(sort_parmas)
    singature_parmas = bytes(singature_parmas, encoding="utf-8")
    signature = hmac.new(secretKey, singature_parmas, hashlib.sha512).hexdigest()
    return signature
"""
委托下单签名
:param: amount 交易数量
:param: currency:eth_usdt 交易的对
:param: price:1024 价格
:param: type:buy/sell 交易类型
:return: int 交易id
":return: bytes 加密签名 
"""
def sha512_order_signature(params):
    current_time = str(int(time.time() * 1000))
    #拼接加密参数
    # param = "&amount" + amount + "&currency" + currency + "&price" + price + "&type" + type
    #拼接assckey、时间、参数
    str_params = accesskey + params +"&nonce=" +current_time
    list_parmas = str_params.split("&")
    sort_parmas = sorted(list_parmas)
    singature_parmas = "&".join(sort_parmas)
    singature_parmas = bytes(singature_parmas, encoding="utf-8")
    signature = hmac.new(secretKey, singature_parmas, hashlib.sha512).hexdigest()
    # signature = sha512_signature(str_params)
    # print(signature)
    return signature

"""
取消委托签名
:param: currency:eth_usdt 交易对
:param: id 交易单id
:return: bytes 加密签名 
"""
def sha512_cancel_signature(currency,id):
    # 拼接加密参数
    param = "&currency" + currency + "&id" + id
    # 拼接assckey、时间、参数
    str_params = accesskey + param + "&nonce=" +current_time
    signature = sha512_signature(str_params)
    return signature
"""
获取委托买单或卖单加密
:param: currency:th_usdt 交易对
:paran: id 交易单id
:return: bytes 加密签名 
"""
def sha512_getorder_signature(currency,id):
    # 拼接加密参数
    param = "&currency" + currency + "&id" + id
    # 拼接assckey、时间、参数
    str_params = accesskey + param + "&nonce=" + current_time
    signature = sha512_signature(str_params)
    return signature

"""
获取多个委托单加密签名
:param: currency:eth_usdt 交易对
:param: pageIndex 1
:param: bytes :buy/sell
"""


def sha512_getOpenOrders_siganture(currency,pageIndex,type):
    # 拼接加密参数
    param = "&currency" + currency + "&type" + type + "pageIndex" + pageIndex
    str_params = accesskey + param + "&nonce=" + current_time
    signature = sha512_signature(str_params)
    return signature

"""
获取用户信息签名
:return: bytes 加密签名 
"""

def sha512_getBlance_siganture():
    str_params = accesskey  + "&nonce=" + current_time
    signature = sha512_signature(str_params)
    return signature







