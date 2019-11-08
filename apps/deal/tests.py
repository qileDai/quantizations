from django.test import TestCase

# Create your tests here.
import requests
import re,time

aa = -4866.74
print(str(aa) + '%')



def str_util( data):
    str_data = re.findall('\d+\.\d*', data)[0]
    new_str = round(float(str_data), 2)
    return new_str
sss = str_util("3423423.2usdt")
print(type(float(sss)),sss)



