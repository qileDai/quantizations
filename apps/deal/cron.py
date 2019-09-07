import time
from dealapi.exx.exxService import ExxService
from dealapi.exx.exxMarket import MarketCondition
from pymysql import *


def main(sql, params=None):
    # 创建Connection连接
    conn = connect(host='192.168.4.201',
                   port=3306,
                   database='exx_quantitative_admin',
                   user='root',
                   password='password',
                   charset='utf8')
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
    print('启动定时任务', "当前时间::"+time.strftime("%H:%M:%S", time.localtime(time.time())))
    # 获取用户所有的EXX账户信息
    sql = "select acc.id,accesskey,secretkey from deal_account as acc INNER JOIN deal_tradingplatform as tr " \
          "on acc.platform_id = tr.id where Platform_name = 'EXX';"
    ret = main(sql)
    # 遍历账户信息
    for accountid,accesskey,secretkey in ret:
        try:
            service_api = ExxService('EXX', secretkey, accesskey)
            data = service_api.get_balance()
            print(data)
        except:
            return '调用接口失败'
        # 循环用户信息接口币种数据，并在数据库中更新资产信息
        for key, value in data['funds'].items():
            lastday_assets = value['total']
            try:
                sql = "select id from deal_lastdayassets where currency=%s and account_id=%s"
                params1 = (key, accountid)
                res = main(sql, params1)
                if res:
                    print(key)
                    sql = "update deal_lastdayassets set lastday_assets=%s where currency=%s and account_id=%s"
                    params2 = (float(lastday_assets), key, accountid)
                    main(sql, params2)
            except:
                print('该币种不存在，请添加')


def huobi_scheduled_job():
    print('huobi-------------------------')

exx_scheduled_job()




