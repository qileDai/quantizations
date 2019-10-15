import redis

try:
    # host is the redis host,the redis server and client are required to open, and the redis default port is 6379
    pool = redis.ConnectionPool(host='192.168.4.179', password='sHZQ4zLB6LasF8ox', port=6379, db=0)
    print("connected success.")
except:
    print("could not connect to redis.")
r = redis.Redis(connection_pool=pool)























