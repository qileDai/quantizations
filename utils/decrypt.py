from hashlib import md5
from string import ascii_letters,digits
from itertools import permutations
from time import time
import base64,json

data = base64.b64decode("YTg5NmJkYzg1NWJlNjY3OTllMzJmYjU3NDc5ODFlZGNjNTc4MmRlYjp7ImlzX2xvZ2luIjp0cnVlLCJ1c2VyX2lkIjoxNCwiX3Nlc3Npb25fZXhwaXJ5IjozMDB9").decode("utf-8")
# user_id = data['user_id']
# print(user_id)
print(data)