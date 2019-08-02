# _*_ conding:utf-8 _*_
import time
import hashlib
import hmac

accesskey = "accesskey=3b56369d-8072-461e-91f6-243b6277af01"
secretKey = b"c6b2ee35465dfddf535e8ddaeaaaf4ee8a90894e"



"""
委托下单签名
:param: amount 交易数量
:param: currency:eth_usdt 交易的对
:param: price:1024 价格
:param: type:buy/sell 交易类型
:return: int 交易id
":return: bytes 加密签名 
"""
def sha512_signature(params):
    current_time = str(int(time.time() * 1000))
    # 拼接加密参数
    # param = "&amount" + amount + "&currency" + currency + "&price" + price + "&type" + type
    # 拼接assckey、时间、参数
    str_params = accesskey + params + "&nonce=" + current_time
    list_parmas = str_params.split("&")
    sort_parmas = sorted(list_parmas)
    singature_parmas = "&".join(sort_parmas)
    singature_parmas = bytes(singature_parmas, encoding="utf-8")
    signature = hmac.new(secretKey, singature_parmas, hashlib.sha512).hexdigest()

    return signature






