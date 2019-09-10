from apps.deal.models import Account, Property, LastdayAssets, Market, Robot
from django.db.models import Q
from dealapi.exx.exxService import ExxService
from dealapi.exx.exxMarket import MarketCondition


class GetAssets(object):
    def __init__(self, account_obj, platform):
        self.account_obj = account_obj
        self.platform = platform

    def showassets(self):
        if self.platform.Platform_name == 'EXX':
            service_api = ExxService(self.platform.Platform_name,
                                     self.account_obj.secretkey,
                                     self.account_obj.accesskey)  # 创建接口对象
            res = service_api.get_balance()  # 获取用户的资产信息
            market_api = MarketCondition()
            res1 = market_api.get_tickers()  # 获取所有行情信息
        elif self.platform.Platform_name == 'HUOBI':
            pass

        show_currency = Property.objects.filter(Q(account_id=id) & Q(currency_status='1'))
        lastday_obj = LastdayAssets.objects.filter(account_id=id)
        lastday_assets = 0  # 昨日24时资产
        current_total = 0  # 当前资产
        original_total = 0  # 初始资产
        withdraw_record = 0  # 提币
        currency_list = list()  # 币种列表
        transaction_pair = list()  # 交易对
        assets_dict = dict()
        profit_loss_dict = dict()
        # 计算账户所有币种的昨日24时总资产
        for lastday_asset in lastday_obj:
            lastday_assets += float(lastday_asset.lastday_assets)

        # 计算账户总初始资产/总提币，获取币种初始资产
        for queryset in show_currency:
            original_total += float(queryset.original_assets)
            withdraw_record += float(queryset.withdraw_record)
            currency_list.append(queryset.currency)
            # 参考币种
            transaction_pair.append(queryset.currency.lower() + '_usdt')
            assets_dict[queryset.currency] = dict()
            # 初始资产
            assets_dict[queryset.currency]['original_assets'] = str(queryset.original_assets)
            profit_loss_dict[queryset.currency] = dict()
            # 历史盈亏
            profit_loss_dict[queryset.currency]['original_assets'] = str(queryset.original_assets)

        print(transaction_pair)
        # 计算当前总资产
        for key, value in res['funds'].items():
            if key in currency_list:
                current_total += float(value['total'])
                assets_dict[key]['current_assets'] = value['total']
                assets_dict[key]['freeze'] = value['freeze']
                assets_dict[key]['balance'] = value['balance']
                profit_loss_dict[key]['current_assets'] = value['total']
                profit_loss_dict[key]['gap'] = str(float(profit_loss_dict[key]['current_assets']) -
                                                   float(profit_loss_dict[key]['original_assets']))

        # 获取当前参考价
        for key1, value1 in res1.items():
            if key1 in transaction_pair:
                key = key1.split('_')[0].upper()
                assets_dict[key]['last'] = value1['last']
                profit_loss_dict[key]['last'] = value1['last']
                profit_loss_dict[key]['convert'] = str(
                    float(profit_loss_dict[key]['gap']) * float(profit_loss_dict[key]['last']))
                transaction_pair.remove(key1)

        for item in transaction_pair:
            key = item.split('_')[0].upper()
            assets_dict[key]['last'] = '0'
            profit_loss_dict[key]['convert'] = '0'

        # 资产变化
        asset_change = dict()
        asset_change['number'] = current_total - lastday_assets
        asset_change['percent'] = (current_total - lastday_assets) / lastday_assets
        # 历史盈亏
        history_profit = dict()
        history_profit['number'] = current_total + withdraw_record - original_total
        history_profit['percent'] = (current_total + withdraw_record - original_total) / original_total
        print(lastday_assets, currency_list, current_total)
        print(assets_dict)
        print(profit_loss_dict)

        context = {
            # 平台名称
            'Platform_name': self.platform.Platform_name,
            # 今日资产变化
            'asset_change': asset_change,
            # 初始总资产
            'original_assets': original_total,
            # 历史盈亏
            'history_profit': history_profit,
            # 总提币
            'withdraw_record': withdraw_record,
            # 资产表
            'assets_dict': assets_dict,
            # 损益表
            'profit_loss_dict': profit_loss_dict,
        }

        return context




