from apps.deal.models import Account, Property, LastdayAssets
from django.db.models import Q
from dealapi.exx.exxService import ExxService
from dealapi.exx.exxMarket import MarketCondition


class GetAssets(object):
    """
    计算资产表和损益表各类数据
    """
    def __init__(self, id, account_obj, platform, flag=None):
        self.id = id
        self.account_obj = account_obj
        self.platform = platform
        self.flag = flag

    def showassets(self):
        # 调用对应平台API
        if self.platform.Platform_name == 'EXX':
            # 创建接口对象
            service_api = ExxService(self.account_obj.secretkey,    # key解码
                                     self.account_obj.accesskey)
            # 获取用户的资产信息
            balance_info = service_api.get_balance()
            balance_info = balance_info['funds']
            # 获取所有行情信息
            market_api = MarketCondition()
            market_info = market_api.get_tickers()
        elif self.platform.Platform_name == 'HUOBI':
            # 返回数据格式需要统一, 待完成-----------------------------------------------
            pass
        elif self.platform.Platform_name == 'BINANCE':
            pass

        if self.flag:
            # self.flag为True，表示账户数据汇总，不同平台需获取EXX参考价进行折算
            exx_market_api = MarketCondition()
            exx_market_info = exx_market_api.get_tickers()

        show_currency = Property.objects.filter(Q(account_id=self.id) & Q(currency_status='1'))
        lastday_obj = LastdayAssets.objects.filter(account_id=self.id)
        lastday_assets = 0  # 昨日24时资产
        current_total = 0  # 当前资产
        original_total = 0  # 初始资产
        withdraw_record = 0  # 提币
        assets_dict = dict()    # 资产字典
        profit_loss_dict = dict()   # 损益字典

        # 计算账户所有币种的昨日24时总资产
        for lastday_asset in lastday_obj:
            print(lastday_asset.lastday_assets)
            lastday_assets += float(lastday_asset.lastday_assets)*float(lastday_asset.last)

        # 计算账户总初始资产/总提币，获取币种初始资产
        for queryset in show_currency:
            # 账户总初始资产
            original_total += float(queryset.original_assets)
            # 提币总额
            withdraw_record += float(queryset.withdraw_record)
            # 损益表字典
            profit_loss_dict[queryset.currency] = dict()
            # 交易市场
            transaction_pair = queryset.currency.lower() + '_usdt'
            # 资产表-初始资产
            assets_dict[queryset.currency] = dict()
            assets_dict[queryset.currency]['original_assets'] = str(queryset.original_assets)
            # 当前参考价
            if self.flag:
                # 资产汇总，所有平台参考价以EXX为准
                last = exx_market_info.get(transaction_pair, None)
            else:
                last = market_info.get(transaction_pair, None)
            if last:
                # 资产表-参考价
                assets_dict[queryset.currency]['last'] = last.get('last')
                # 损益表-参考价
                profit_loss_dict[queryset.currency]['last'] = last.get('last')
            else:
                assets_dict[queryset.currency]['last'] = 0
                profit_loss_dict[queryset.currency]['last'] = 0
            # 资产表-交易币种总资产
            assets_dict[queryset.currency]['current_assets'] = balance_info[queryset.currency]['total']
            # 资产表-交易币种冻结
            assets_dict[queryset.currency]['freeze'] = balance_info[queryset.currency]['freeze']
            # 资产表-交易币种可用
            assets_dict[queryset.currency]['balance'] = balance_info[queryset.currency]['balance']
            # 多币种总资产
            current_total += float(balance_info[queryset.currency]['total']) * \
                             float(assets_dict[queryset.currency]['last'])
            # 损益表-当前总资产
            profit_loss_dict[queryset.currency]['current_assets'] = balance_info[queryset.currency]['total']
            # 损益表-初始资产
            profit_loss_dict[queryset.currency]['original_assets'] = str(queryset.original_assets)
            # 损益表-差额
            profit_loss_dict[queryset.currency]['gap'] = str(float(profit_loss_dict[queryset.currency]['current_assets']) -
                                                             float(profit_loss_dict[queryset.currency]['original_assets']))
            # 损益表-折合差额
            profit_loss_dict[queryset.currency]['convert'] = str(float(profit_loss_dict[queryset.currency]['gap']) *
                                                                 float(profit_loss_dict[queryset.currency]['last']))

        # 资产变化
        asset_change = dict()
        asset_change['number'] = current_total - lastday_assets
        if self.flag:
            asset_change['lastday_assets'] = lastday_assets
        else:
            if lastday_assets != 0:
                asset_change['percent'] = (current_total - lastday_assets) / lastday_assets
            else:
                asset_change['percent'] = 0
        # 历史盈亏
        history_profit = dict()
        history_profit['number'] = current_total + withdraw_record - original_total
        if self.flag:
            history_profit['original_total'] = original_total
        else:
            if original_total != 0:
                history_profit['percent'] = (current_total + withdraw_record - original_total) / original_total
            else:
                history_profit['percent'] = 0
        print(lastday_assets, current_total)
        # print(assets_dict)
        # print(profit_loss_dict)

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
        print(context)
        return context




