import time
from apps.deal.API.exx.exxService import ExxService
from apps.deal.API.exx.exxMarket import MarketCondition
from pymysql import *


def main(sql, params=None):
    # 创建Connection连接
    conn = connect(host='192.168.4.201',
                   port=3306,
                   database='exx_quantitative_trading',
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
    # 获取用户所有的账户信息
    sql = "select acc.id,accesskey,secretkey from deal_account as acc INNER JOIN app02_tradingplatform as tr " \
          "on acc.platform_id = tr.id where Platform_name = 'EXX';"
    ret = main(sql)
    # 遍历账户信息
    for accountid,accesskey,secretkey in ret:
        try:
            service_api = ExxService('EXX', secretkey, accesskey)
            data = service_api.get_balance()
        except:
            return '调用接口失败'

        for key, value in data['funds'].items():
            # if key == 'QC':
            #     value['total'] = '666'
            lastday_assets = value['total']
            try:
                sql = "select id from deal_property where currency=%s and accountid_id=%s"
                params1 = (key, accountid)
                res = main(sql, params1)
                sql = "insert into deal_property(id, currency, lastday_assets, accountid_id)" \
                      "value(%s, %s, '0', %s) on duplicate key update lastday_assets=%s"
                params2 = (res, key, accountid, lastday_assets)
                main(sql, params2)
            except:
                sql = "insert into deal_property(currency, lastday_assets, accountid_id)" \
                      "value(%s, '0', %s) on duplicate key update lastday_assets=%s"
                params = (key, accountid, lastday_assets)
                main(sql, params)


def huobi_scheduled_job():
    print('huobi-------------------------')

# exx_scheduled_job()





