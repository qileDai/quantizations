# _*_ codingLutf-8 _*_

import hashlib
import time
import hmac
import accountConfig

# 在此输入您的Key
ACCESS_KEY = accountConfig.EXX["ACCESS_KEY"]
SECRET_KEY = accountConfig.EXX["SECRET_KEY"]
SERVICE_API = accountConfig.EXX["SERVICE_API"]


"""
exx交易签名
:param: amount 交易数量
:param: currency:eth_usdt 交易的对
:param: price:1024 价格
:param: type:buy/sell 交易类型
:return: int 交易id
:return: bytes 加密签名 
"""
def sha512_signature(params):
    current_time = str(int(time.time() * 1000))
    # 拼接加密参数
    # param = "&amount" + amount + "&currency" + currency + "&price" + price + "&type" + type
    # 拼接assckey、时间、参数
    str_params = ACCESS_KEY + params + "&nonce=" + current_time
    list_parmas = str_params.split("&")
    sort_parmas = sorted(list_parmas)
    singature_parmas = "&".join(sort_parmas)
    singature_parmas = bytes(singature_parmas, encoding="utf-8")
    signature = hmac.new(bytes(SECRET_KEY,encoding="utf-8"), singature_parmas, hashlib.sha512).hexdigest()

    return signature