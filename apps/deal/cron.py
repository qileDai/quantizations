import time
from dealapi.exx.exxService import ExxService
from dealapi.exx.exxMarket import MarketCondition
from utils import restful
from pymysql import *
from django.conf import settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exxTrading.settings")  # project_name 项目名称


def main(sql, params=None):
    try:
        # 创建Connection连接
        conn = connect(host=settings.DATABASES.get('default')['HOST'],
                       port=settings.DATABASES.get('default')['PORT'],
                       database=settings.DATABASES.get('default')['NAME'],
                       user=settings.DATABASES.get('default')['USER'],
                       password=settings.DATABASES.get('default')['PASSWORD'],
                       charset='utf8')
    except Exception as e:
        print('数据库连接错误', e)
        return restful.result(message='数据库连接错误')
    else:
        # 获取cursor ------执行sql语句的对象
        cur = conn.cursor()
        # 执行sql语句
        cur.execute(sql, params)
        # 提交
        conn.commit()
        # 关闭 游标对象 和 连接对象
        cur.close()
        conn.close()
        return cur.fetchall()


def exx_scheduled_job():
    print('启动定时任务', "当前时间:"+time.strftime("%H:%M:%S", time.localtime(time.time())))
    # 获取所有用户的EXX账户信息
    sql = "select acc.id,accesskey,secretkey from deal_account as acc INNER JOIN deal_tradingplatform as tr " \
          "on acc.platform_id = tr.id where Platform_name = 'EXX';"
    ret = main(sql)
    # 调用接口，获取所有行情信息
    market_api = MarketCondition()
    info = market_api.get_tickers()
    print(info)

    # 遍历账户信息
    for accountid, accesskey, secretkey in ret:
        try:
            # 调用接口，获取账户信息
            service_api = ExxService(secretkey, accesskey)
            data = service_api.get_balance()
            print(data)
        except:
            return restful.result(message='调用接口失败')
        # 更新24时资产信息
        sql = "select * from deal_lastdayassets where account_id=%s"
        params1 = (accountid,)
        res = main(sql, params1)
        for item in res:
            key = item[1]
            key_pair = key.lower() + '_usdt'
            try:
                sql = "update deal_lastdayassets set lastday_assets=%s,last=%s where currency=%s and account_id=%s"
                last = info.get(key_pair, None)
                if last:
                    params2 = (float(data['funds'][key]['total']), float(last.get('last')), key, accountid)
                    main(sql, params2)
                elif key.lower() == 'usdt':
                    params2 = (float(data['funds'][key]['total']), 1, key, accountid)
                    main(sql, params2)
                else:
                    params2 = (float(data['funds'][key]['total']), 0, key, accountid)
                    main(sql, params2)
            except Exception as e:
                print('该币种不存在，请添加', e)
                return restful.result(message='该币种不存在，请添加')


def huobi_scheduled_job():
    print('huobi-------------------------')


exx_scheduled_job()





