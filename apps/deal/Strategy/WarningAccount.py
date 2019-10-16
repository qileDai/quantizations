import redis


class WarningAccount(object):

    def __init__(self):

        try:
            # 连接redis
            pool = redis.ConnectionPool(host='192.168.4.179', password='sHZQ4zLB6LasF8ox', port=6379, db=0)
            print("connected success.")
        except:
            print("could not connect to redis.")
        r = redis.Redis(connection_pool=pool)























