

EXX_SERVICE = {
    # "SERVICE_API": "http://192.168.4.66:8804/api/",     # 测试环境接口
    "SERVICE_API": "http://172.31.103.236:8804/api/",   # 生产环境接口
}

# EXX_MARKET = {
#     "host_url": "http://192.168.4.171:9008",
#     "markets_url": "http://192.168.4.171:9008/data/v1/markets",  # Exx所有市场url
#     "tickers_url": "http://192.168.4.171:9008/data/v1/tickers",  # 所有行情url
#     "ticker_url": "http://192.168.4.171:9008/data/v1/ticker",    # 单一市场行情url
#     "depth_url": "http://192.168.4.171:9008/data/v1/depth",      # 市场深度
#     "trades_url": "http://192.168.4.171:9008/data/v1/trades",    # 历史记录
#     "klines_url": "http://192.168.4.171:9008/data/v1/klines",    # K线
# }

# 生产环境接口
EXX_MARKET = {
    "host_url": "http://172.31.103.223:8201",
    "markets_url": "http://172.31.103.223:8201/data/v1/markets",  # Exx所有市场url
    "tickers_url": "http://172.31.103.223:8201/data/v1/tickers",  # 所有行情url
    "ticker_url": "http://172.31.103.223:8201/data/v1/ticker",    # 单一市场行情url
    "depth_url": "http://172.31.103.223:8201/data/v1/depth",      # 市场深度
    "trades_url": "http://172.31.103.223:8201/data/v1/trades",    # 历史记录
    "klines_url": "http://172.31.103.223:8201/data/v1/klines",    # K线
}

# huobi config
HUOBI = {
    "CNY_1":
        {
            "SERVICE_API": "https://api.huobi.com/apiv3",
        },
    "USD_1":
        {
            "SERVICE_API": "https://api.huobi.com/apiv3",
        },
}

# bitvc config
BITVC = {
    "CNY_1":
        {
            "ACCESS_KEY": "",
            "SECRET_KEY": "",
            "SERVICE_API": "https://api.bitvc.com/api/",
            "FUTURE_SERVICE_API": "https://api.bitvc.com/futures/"
        }
}

# okcoin config
OKCOIN = {
    "CNY_1":
        {
            "ACCESS_KEY": "",
            "SECRET_KEY": "",
            "SERVICE_API": "https://www.okcoin.cn",  # okcoin国内站
        },

    "USD_1":
        {
            "ACCESS_KEY": "",
            "SECRET_KEY": "",
            "SERVICE_API": "https://www.okcoin.com",  # okcoin国际站
        },
}

