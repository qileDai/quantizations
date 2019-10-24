import threading
import time
import math
import re
import json

from urllib import parse
from django.db.models import Q
from django.shortcuts import render, redirect, HttpResponse
from .models import Account, Property, LastdayAssets, Market, Robot, TradingPlatform, OrderInfo
from .forms import AccountModelForm, RobotFrom, EditAccountFrom
from apps.rbac.models import UserInfo
from django.core.paginator import Paginator
from apps.deal.asset.get_assets import GetAssets
from dealapi.exx.exxMarket import MarketCondition
from dealapi.exx.exxService import ExxService
from apps.deal.Strategy.Grid import GridStrategy

from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import serializers
from utils import restful
from utils.mixin import LoginRequireMixin
from rest_framework import generics
from django.core.serializers import serialize
from apps.deal.serializers import AccountSerializer, RobotSerializer, OrderInfoSerializer, LastdayAssetsSerializer, PropertySerializer, PlatformSerializer
from apps.rbac.serializers import UserSerializer

# Create your views here.


# class AccountList(LoginRequireMixin, generics.CreateAPIView):
class AccountList(generics.CreateAPIView):
    """
    显示用户所有账户信息
    """
    serializer_class = AccountSerializer

    def get(self, request):
        pageNum = request.GET.get('pageIndex', 1)
        pagesize = request.GET.get('pageSize')
        # user_id = request.session.get("user_id")
        user_id = 1
        if not user_id:
            return restful.params_error(message='账户失效，请重新登陆！')
        # 获取账户信息
        accounts = Account.objects.filter(users__id=user_id)
        # 分页
        paginator = Paginator(Account.objects.filter(users__id=user_id), 2)
        page_obj = paginator.page(int(pageNum))
        # print(paginator.num_pages)
        numPerPage = len(page_obj.object_list),
        totalCount = accounts.count(),
        totalPageNum = paginator.num_pages
        context = {
            'numPerPage': numPerPage,
            'PageNum': int(pageNum),
            'result': AccountSerializer(page_obj.object_list, many=True).data,
            'totalCount': totalCount,
            'totalPageNum': totalPageNum,
        }
        # print(context)
        return restful.result(data=context)


class GetCurrencies(generics.CreateAPIView):
    """
    获取用户所有币种
    """
    def get(self, request):
        # 获取用户所有币种
        # user_id = request.session.get("user_id")
        user_id = 1
        if user_id:
            currency_list = Property.objects.filter(account__users__id=user_id).values("currency",).distinct()
            ret = list(currency_list)
            # currency_list = serialize('json', currency_list)
            data = json.dumps(ret)
            return restful.result(data=data)
        else:
            return restful.params_error(message='为获取到账户登陆信息，请检查是否登陆')


class AddAccount(generics.CreateAPIView):
    """
    添加账户
    """
    # queryset = Account.objects.get_queryset().order_by('id')
    serializer_class = AccountSerializer

    def get(self, request):
        platform = TradingPlatform.objects.all()
        data = PlatformSerializer(platform, many=True).data
        return restful.result(message=data)

    def post(self, request):
        model_form = AccountModelForm(request.POST)
        if model_form.is_valid():
            # save()返回一个还未保存至数据库的对象,用这个对象添加一些额外的数据，然后在用save()保存到数据库
            obj = model_form.save(commit=False)
            # user_id = request.session.get("user_id")
            user_id = 1
            user_obj = UserInfo.objects.get(id=user_id)
            # 添加数据需为模型类对象
            obj.users = user_obj
            obj.save()
            accounts = Account.objects.filter(Q(title=obj) & Q(platform=model_form.cleaned_data['platform']))
            currency = Property.objects.values("currency").distinct()

            print(accounts, currency)
            # 给新账户添加币种
            for account in accounts:
                for cur in currency:
                    LastdayAssets.objects.create(currency=cur['currency'], account=account)
                    Property.objects.create(currency=cur['currency'], account=account, currency_status=0)
            return restful.ok()
        else:
            return restful.params_error(model_form.get_errors())


def accountinfo(request):
    accout_id = request.POST.get('id')
    account = Account.objects.get(id=accout_id)
    serialize = AccountSerializer(account)
    print(serialize.data)
    return restful.result(data=serialize.data)


class EditAccount(generics.ListCreateAPIView):
    """
    get:
    获取要修改账户信息.
    post:
    提交修改信息.
    """
    serializer_class = AccountSerializer

    def get(self, request):
        account_id = request.GET.get('account_id')
        if account_id:
            account = Account.objects.get(id=account_id)
            account = AccountSerializer(account)
            return restful.result(data=account.data)
        else:
            return restful.params_error(message='参数为空')

    def post(self, request):
        form = EditAccountFrom(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            accesskey = form.cleaned_data.get('accesskey')
            secretkey = form.cleaned_data.get('secretkey')
            platform = form.cleaned_data.get('platform')
            pk = form.cleaned_data.get('id')
            # user_id = request.session.get("user_id")
            user_id = 1
            print(title, accesskey, secretkey, platform, pk, user_id)
            Account.objects.filter(pk=pk).update(title=title, accesskey=accesskey, secretkey=secretkey,
                                                 platform=platform, users=user_id)
            return restful.ok()
        else:
            return restful.params_error(form.get_errors())


class DeleteAccount(generics.CreateAPIView):
    """
    删除账户
    """
    serializer_class = AccountSerializer

    def post(self, request):
        pk = request.POST.get('id')
        try:
            Account.objects.filter(id=pk).delete()
            return restful.ok()
        except:
            return restful.params_error(message="该账户不存在")


class ShowAssert(generics.CreateAPIView):
    """
    显示账户资产信息
    """
    serializer_class = AccountSerializer

    def post(self, request):
        id = request.POST.get('id')
        print('+-'*10, id)
        if id:
            # 获取账户信息
            account_obj = Account.objects.get(id=id)
            # 账户对应的平台
            platform = account_obj.platform
            # 创建对象
            con = GetAssets(id, account_obj, platform)
            data = con.showassets()
            return restful.result(data=data)
        else:
            return restful.params_error(message='参数为空')


class ShowCollectAsset(generics.CreateAPIView):
    """
    汇总资产信息
    """
    serializer_class = AccountSerializer

    def post(self, request):

        account_list = request.POST.getlist('id')
        print(account_list)
        if account_list:
            accounts = account_list
        else:
            # user_id = request.session.get("user_id")
            user_id = 1
            account_lists = Account.objects.filter(users=user_id)
            for account in account_lists:
                accounts = list()
                accounts.append(account.id)

        flag = True
        context_list = list()
        for id in accounts:
            print("*" * 20, id)
            # 获取账户信息
            account_obj = Account.objects.get(id=id)
            # 账户对应的平台
            platform = account_obj.platform
            # 创建对象
            con = GetAssets(id, account_obj, platform, flag)
            context = con.showassets()
            context_list.append(context)
        # 汇总资产表数据
        for key in context_list[0]['assets_dict']:
            for elem in context_list[1:]:
                for key1, value1 in elem['assets_dict'][key].items():
                    if key1 in context_list[0]['assets_dict'][key]:
                        context_list[0]['assets_dict'][key][key1] = float(context_list[0]['assets_dict'][key][key1]) \
                                                                    + float(value1)
                    else:
                        context_list[0]['assets_dict'][key][key1] = value1
        # 汇总资产变化/初始总资产/历史盈亏/
        print('资产汇总', '-' * 20)
        print(context_list[0])
        return restful.result(data=context_list[0])


class ChargeAccount(generics.CreateAPIView):
    """
    增资
    """
    serializer_class = AccountSerializer

    def post(self, request):
        id = request.POST.get('id')
        currency = request.POST.get('currency')
        num = request.POST.get('num')
        print(id, currency, num)
        if id and currency and num:
            account_obj = Account.objects.get(id=id)  # 获取账户信息
            platform = account_obj.platform  # 账户对应的平台
            # 根据平台调用对应接口
            try:
                if str(platform) == 'EXX':
                    currency_pair = currency.lower() + '_usdt'
                    market_api = MarketCondition(currency_pair)
                    info = market_api.get_ticker()  # 获取EXX单个交易对行情信息
                    info = info['ticker']['last']
                elif str(platform) == 'HUOBI':
                    pass
            except:
                info = 0
            try:
                property_obj = Property.objects.get(Q(account_id=id) & Q(currency=currency))
                original_assets = float(property_obj.original_assets) + float(num) * float(info)
                print('/-'*10, original_assets)
                Property.objects.filter(Q(account_id=id) & Q(currency=currency)).update(original_assets=original_assets)
                return restful.ok()
            except:
                return restful.params_error(message='账户没有此币种')
        else:
            return restful.params_error(message='参数为空')


class WithDraw(generics.CreateAPIView):
    """
    提币
    """
    serializer_class = AccountSerializer

    def post(self, request):
        id = request.POST.get('id')
        currency = request.POST.get('currency')
        num = request.POST.get('num')
        if id and currency and num:
            account_obj = Account.objects.get(id=id)  # 获取账户信息
            platform = account_obj.platform  # 账户对应的平台
            # 根据平台调用对应接口
            try:
                if str(platform) == 'EXX':
                    currency_pair = currency.lower() + '_usdt'
                    market_api = MarketCondition(currency_pair)
                    info = market_api.get_ticker()  # 获取EXX单个交易对行情信息
                    last = info['ticker']['last']
                elif str(platform) == 'HUOBI':
                    pass
            except:
                print('未获取到当前价')
                last = 0
            if currency:
                # 提币折合成usdt
                property_obj = Property.objects.get(Q(account_id=id) & Q(currency=currency))
                withdraw_record = float(property_obj.withdraw_record) + float(num) * float(last)
                Property.objects.filter(Q(account_id=id) & Q(currency=currency)).update(withdraw_record=withdraw_record)
                return restful.ok()
        else:
            return restful.params_error(message='参数为空')


class ConfigCurrency(generics.CreateAPIView):
    """
    币种新增/配置
    """
    serializer_class = AccountSerializer

    def post(self, request):
        currency = request.POST.get('currency')
        currency_list = list()
        currency_list.append(currency)
        if currency_list:
            # user_id = request.session.get("user_id")
            user_id = 1
            accounts = Account.objects.filter(users=user_id)
            for account in accounts:
                print(account.id, '-' * 30)
                for currency in currency_list:
                    if currency:
                        # 账户存在此币种则不添加
                        property_obj = Property.objects.filter(Q(account=account.id) & Q(currency=currency))
                        print('+' * 30, list(property_obj))
                        if not list(property_obj):
                            # 保存币种信息
                            LastdayAssets.objects.create(currency=currency, account=account)
                            Property.objects.create(currency=currency, account=account, currency_status=0)
                    else:
                        return restful.params_error(message='请选择账户币种')
            # 返回数据为json格式
            data = Property.objects.values("currency").distinct()
            return restful.result(data=list(data))
        else:
            return restful.params_error(message='请选择账户币种')


class SelectCurrency(generics.CreateAPIView):
    """
    勾选的币种
    """
    serializer_class = AccountSerializer

    def post(self, request):
        currency_list = request.POST.getlist('currency')
        if currency_list:
            Property.objects.values("currency").update(currency_status='0')
            LastdayAssets.objects.values("currency").update(currency_status='0')
            for cur in currency_list:
                Property.objects.filter(currency=cur).update(currency_status='1')
                LastdayAssets.objects.filter(currency=cur).update(currency_status='1')
            return restful.ok()
        else:
            return restful.params_error(message='参数为空')


# ----------------------------------------------------------------------------------------------------------------------
# 创建机器人
class CreateRobot(generics.CreateAPIView):
    """
    获取配置策略的参数
    """
    serializer_class = AccountSerializer

    def post(self, request):
        form = RobotFrom(request.POST)
        # is_valid()方法会根据model字段的类型以及自定义方法来验证提交的数据
        if form.is_valid():
            form.save()
            return restful.ok()
        else:
            return restful.params_error(message=form.get_errors())


def get_account_info(currency, market, id):
    """
    获取用户信息
    :param currency: 交易币种
    :param market: 交易市场
    :param id: 机器人id
    :return:
    """
    # 获取账户所属的用户信息
    account_obj = Account.objects.get(id=id)
    # 账户对应的平台
    platform = account_obj.platform
    # 获取用户信息
    user_obj = UserInfo.objects.all()
    if str(platform) == 'EXX':
        # 创建交易接口对象---------------------------------------------------------------------API
        service_obj = ExxService(account_obj.secretkey, account_obj.accesskey)
        # 创建行情接口对象
        currency_pair = currency.lower() + '_' + market.lower()
        market_obj = MarketCondition(currency_pair)

    elif str(platform) == 'HUOBI':
        pass

    return user_obj, service_obj, market_obj


class GetAccountInfo(generics.CreateAPIView):
    """
    展示交易对可用额度/当前价,计算默认值
    """
    serializer_class = AccountSerializer

    def data_format(self, data):
        data = str(round(float(data), 2))
        return data

    def post(self, request):
        currency = request.POST.get('curry-title')
        market = request.POST.get('market-title')
        # 获取账户id
        id = request.POST.get('account_id')
        if currency and market and id:
            # 调用get_account_info函数
            user_obj, service_obj, market_obj = get_account_info(currency, market, id)
            try:
                info = service_obj.get_balance()
                info = info.get('funds')
                info1 = market_obj.get_ticker()
                info1 = info1['ticker']
                info2 = market_obj.get_klines('1day', '30')
                info2 = info2.get('datas')
            except:
                return restful.params_error(message='币种错误，请核对！')

            # 计算阻力位/支撑位的默认值
            if int(info2.get('limit', 0)) <= 30:
                max = 0
                min = 0
                for i in info2['data']:
                    max += float(i[2])
                    min += float(i[3])
            context = {
                # 账户起始交易币种总资产
                'total_currency': self.data_format(info[currency.upper()].get('total')) + ' ' + currency,
                # 账户起始交易市场币种总资产
                'total_market': self.data_format(info[market.upper()].get('total')) + ' ' + market,
                # 交易币种可用
                'currency': self.data_format(info[currency.upper()].get('balance')) + ' ' + currency,
                # 交易市场可用
                'market': self.data_format(info[market.upper()].get('balance')) + ' ' + market,
                # 当前价
                'last': self.data_format(info1.get('last')) + '' + market,
                # 阻力位
                'resistance': round(float(max / int(info2['limit'])), 2),
                # 支撑位
                'support_level': round(float(min / int(info2['limit'])), 2),

            }
            print(context)
            return restful.result(data=context)
        else:
            return restful.params_error(message='参数为空')


class RobotProtection(generics.CreateAPIView):
    """
    机器人保护
    """
    serializer_class = AccountSerializer

    def post(self, request):
        id = request.POST.get('robot_id')
        flag = request.POST.get('flag')
        protect = request.POST.get('protect')
        if id and flag and protect:
            Robot.objects.filter(id=id).update(status=flag)
            Robot.objects.filter(id=id).update(protection=protect)

            return restful.ok()
        else:
            return restful.params_error(message='参数为空')


class StartRobot(generics.CreateAPIView):
    """
    管理机器人
    """
    serializer_class = AccountSerializer
    order_list = ""

    def post(self, request):
        # 多个和一个
        ids = request.POST.get('robot_id')
        # Flag为1启动，为0停止
        Flag = request.POST.get('flag')
        if Flag is None:
            return restful.params_error(message='参数为空')
        if ids:
            robots = Robot.objects.filter(id=ids)
        elif Flag == 1:
            robots = Robot.objects.filter(Q(status=0) & Q(protection=1))
        elif Flag == 0:
            robots = Robot.objects.filter(Q(status=1) & Q(protection=1))

        Flag = int(Flag)
        # 调用对应策略
        for robot_obj in robots:
            if robot_obj.trading_strategy == '网格交易V1.0' and Flag == 1:
                Robot.objects.filter(id=robot_obj.id).update(run_status=0, status=Flag)
                # Robot.objects.filter(id=robot_obj.id).update(status=Flag)
                # 启动线程
                thread1 = GridStrategy(robot_obj=robot_obj, order_type="buy")
                thread2 = GridStrategy(robot_obj=robot_obj, order_type="sell")
                thread1.start()
                thread2.start()
                print('-' * 30, '启动线程')
            elif robot_obj.trading_strategy == '网格交易V1.0' and Flag == 0:
                Robot.objects.filter(id=robot_obj.id).update(run_status=1, status=Flag)
                # Robot.objects.filter(id=robot_obj.id).update(run_status=1)
                # 停止线程
                for item in threading.enumerate():
                    try:
                        # 获取线程对应的机器人
                        robot = item.robot_obj
                        if robot_obj.id == robot.id:
                            item.setFlag(False)
                            rtime = time.time() - item.start_time
                            Robot.objects.filter(id=robot_obj.id).update(running_time=rtime)
                    except:
                        print('对象没有属性robot_obj')
                        continue

            elif robot_obj.trading_strategy == '三角套利V1.0':
                pass
            elif robot_obj.trading_strategy == '搬砖套利V1.0':
                pass

        StartRobot.order_list = threading.enumerate()
        return restful.ok()


class ShowTradeDetail(generics.CreateAPIView):
    """
    展示机器人交易详情
    """
    serializer_class = AccountSerializer

    def data_format(self, data):
        data = str(round(float(data), 2))
        return data

    def changeTime(self, allTime):
        day = 24 * 60 * 60
        hour = 60 * 60
        min = 60
        if allTime < 60:
            return "%d 秒" % math.ceil(allTime)
        elif allTime > day:
            days = divmod(allTime, day)
            return "%d 天, %s" % (int(days[0]), self.changeTime(days[1]))
        elif allTime > hour:
            hours = divmod(allTime, hour)
            return '%d 时, %s' % (int(hours[0]), self.changeTime(hours[1]))
        else:
            mins = divmod(allTime, min)
            return "%d 分, %d 秒" % (int(mins[0]), math.ceil(mins[1]))

    def sort_data(self, order_info):
        sells = dict()
        buys = dict()
        for k, v in order_info.items():
            if v["order_type"] is "sell":
                sells[k] = v
            elif v["order_type"] is "buy":
                buys[k] = v
        buys = sorted(buys.items(), key=lambda x: x[1]["price"], reverse=True)
        sells = sorted(sells.items(), key=lambda x: x[1]["price"])
        return dict(sells), dict(buys)

    def post(self, request):
        # 获取机器人id
        id = request.POST.get('robot_id')
        if id:
            robot_obj = Robot.objects.get(id=id)
            currency = robot_obj.currency
            market = robot_obj.market
            # 调用函数
            try:
                user_obj, service_obj, market_obj = get_account_info(currency, market, robot_obj.trading_account_id)
                info = service_obj.get_balance()
                # print("交易详情"+info)
                info = info.get('funds')
                info1 = market_obj.get_ticker()
                info1 = info1.get('ticker')
            except Exception as e:
                return restful.params_error(message='币种错误，请核对！')
            property_obj = Property.objects.get(Q(account_id=robot_obj.trading_account) & Q(currency=currency))
            closed_order = OrderInfo.objects.filter(robot=id).order_by("-id")
            serialize = OrderInfoSerializer(closed_order, many=True)

            # 获取挂单信息
            order_info = dict()
            running_time = 0
            for item in StartRobot.order_list:
                try:
                    # 获取机器人对应的线程对象
                    robot = item.robot_obj
                    if id == str(robot.id):
                        # 向字典中添加数据
                        order_info = {**order_info, **item.id_dict}
                    running_time = time.time() - item.start_time
                except:
                    print('对象没有属性robot_obj')
                    continue
            sell, buy = self.sort_data(order_info)

            context = {
                # 交易币种和交易市场
                'currency_market': {"currency": currency, "market": market},
                # 已完成笔数
                'closed_num': len(closed_order),
                # 已完成挂单信息
                'closed_info': serialize.data,
                # 未完成笔数
                'open_num': len(order_info),
                # 未完成卖单信息
                'SELL': sell,
                # 未完成买单信息
                'BUY': buy,
                # 总投入
                'total_input': self.data_format(property_obj.original_assets),
                # 运行时间
                'running_time': self.changeTime(running_time),
                # 交易币种可用
                'currency_balance': self.data_format(info[currency.upper()].get('balance')) + ' ' + currency,
                # 交易市场可用
                'market_balance': self.data_format(info[market.upper()].get('balance')) + ' ' + market,
                # 交易币种冻结
                'currency_freeze': self.data_format(info[currency.upper()].get('freeze')) + ' ' + currency,
                # 交易市场冻结
                'market_freeze': self.data_format(info[market.upper()].get('freeze')) + ' ' + market,
                # 当前价
                'last': self.data_format(info1.get('last')) + ' ' + market,
                # 总收益
                'profit': self.data_format(
                    (float(info[currency.upper()].get('total')) - float(property_obj.original_assets))
                    * float(info1.get('last'))) + ' ' + market,
            }

            # print(context)
            # print('/-' * 30, len(sell), len(buy))
            return restful.result(data=context)
        else:
            return restful.params_error(message='参数为空')


class ShowConfigInfo(generics.CreateAPIView):
    """
    展示机器人配置信息
    """
    serializer_class = AccountSerializer

    def data_format(self, data):
        data = str(round(float(data), 2))
        return data

    def post(self, request):
        id = request.POST.get('robot_id')
        if id:
            robot_obj = Robot.objects.get(id=id)
            account_obj = Account.objects.filter(id=robot_obj.trading_account.id).first()
            # data = serialize("json", Robot.objects.filter(id=id))
            account = Robot.objects.get(id=id)
            serialize = RobotSerializer(account)
            user_obj, service_obj, market_obj = get_account_info(robot_obj.currency, robot_obj.market,
                                                                 robot_obj.trading_account.id)
            try:
                info = service_obj.get_balance()
                info = info.get('funds')
            except:
                return restful.params_error(message='币种错误，请核对！')
            # print(json.loads(data)['pk'], type(json.loads(data)))
            context = {
                # 交易币种可用
                'currency': self.data_format(info[robot_obj.currency.upper()].get('balance')) + ' ' + robot_obj.currency,
                # 交易市场可用
                'market': self.data_format(info[robot_obj.market.upper()].get('balance')) + ' ' + robot_obj.market,
                # 账户信息
                'account_name': str(account_obj.title),
                # 机器人信息
                'robot': serialize.data,
            }
            print(context)
            return restful.result(data=context)
        else:
            return restful.params_error(message='参数为空')


class ShowConfig(generics.CreateAPIView):
    """
    修改机器人配置信息
    """
    serializer_class = AccountSerializer

    def post(self, request):
        # 获取机器人id
        id = request.POST.get('robot_id')
        # 获取挂单频率
        orders_frequency = request.POST.get('orders_frequency')
        # 获取挂单最小数量
        min_num = request.POST.get('min_num')
        # 获取挂单最大数量
        max_num = request.POST.get('max_num')
        # 获取止损价
        stop_price = request.POST.get('stop_price')
        # 获取预警价
        warning_price = request.POST.get('warning_price')

        Robot.objects.filter(id=id).update(
            orders_frequency=orders_frequency,
            min_num=min_num,
            max_num=max_num,
            stop_price=stop_price,
            warning_price=warning_price,
        )
        return restful.ok()


class WarningUsers(generics.CreateAPIView):
    """
    序列化预警账户
    """
    serializer_class = AccountSerializer

    def get(self, request):
        users = UserInfo.objects.filter(status=1)
        print(users)
        # data = serialize('json', users)
        serialize = UserSerializer(users, many=True)

        return restful.result(data=serialize.data)


# ----------------------------------------------------------------------------------------------------------------------

class RobotList(generics.CreateAPIView):
    """
    机器人管理列表页面
    """
    serializer_class = AccountSerializer

    def get(self, request):
        pageNum = int(request.GET.get('pageIndex', 1))
        if pageNum is None:
            return restful.params_error(message='参数为空')
        pagesize = request.GET.get('pageSize')
        # 拿到下拉框交易币种值
        curry = request.GET.get('deal-curry')
        # 拿到下拉框交易市场值
        marke_id = request.GET.get('deal_market')
        # 拿到交易状态
        status = request.GET.get('deal_status')

        robots = Robot.objects.all()
        if curry:
            robots = Robot.objects.filter(currency__icontains=curry)
        if marke_id:
            robots = Robot.objects.filter(market=marke_id)
        if status:
            robots = Robot.objects.filter(status=status)

        paginator = Paginator(robots, 10)
        page_obj = paginator.page(pageNum)
        numPerPage = len(page_obj.object_list),
        totalCount = robots.count(),
        totalPageNum = paginator.num_pages

        context = {
            'numPerPage': numPerPage,
            'PageNum': pageNum,
            'result': RobotSerializer(page_obj.object_list, many=True).data,
            'totalCount': totalCount,
            'totalPageNum': totalPageNum,
        }

        return restful.result(data=context)


class RobotYield(generics.CreateAPIView):
    """
    机器人收益计算更新到数据库
    """
    serializer_class = AccountSerializer
    robot_yield = {}

    # 用作对数据做精度处理
    def data_format(self, data):
        data = str(round(float(data), 2))
        return data

    def post(self, request):
        # 获取用户id
        # user_id = request.session.get("user_id")
        user_id = 1
        accounts = Account.objects.filter(users=user_id)
        print(accounts)
        for account in accounts:
            exx_service = ExxService(account.secretkey, account.accesskey)
            robots = Robot.objects.filter(trading_account_id=account.id)
            for robot in robots:
                robot_id = robot.id  # 机器人id
                print("机器人id:"+str(robot_id))
                currency = robot.currency  # 交易币种
                market = robot.market  # 市场币种
                total_money = re.findall('\d+\.\d\d',robot.total_money)[0]  # 总投入
                print("总投入", total_money)
                last_price = robot.current_price  # 当时价格
                start_time = float(robot.running_time)    # 创建时间
                try:
                    print("交易币种："+currency,"市场币种:"+market,"账户id:"+ str(account.id))
                    user_obj, service_obj, market_obj = get_account_info(currency, market, account.id)
                    info = exx_service.get_balance()
                    info = info.get('funds')
                    info1 = market_obj.get_ticker()
                    info1 = info1.get('ticker')
                    current_price = info1.get('last')  # 最新价格
                    balance_currency = self.data_format(info[currency.upper()].get('total'))                            #可用的交易币种数量
                    balance_market = self.data_format(info[market.upper()].get('total'))                                #冻结的市场币种
                    current_time = time.time()         #获取最新的时间

                    run_time = (int(current_time) - int(start_time))/1000*60  #运行多少分钟
                    print(balance_market,balance_currency)
                    residue_num = ((float(balance_currency) ) / float(last_price) ) + (float(balance_market) )
                    float_profit = residue_num * float(current_price) - float(total_money) * float(last_price)           #浮动盈亏（折算为交易市场币种）：当前剩余币种数量*当前价格-总投入数量*当时价格
                    realized_profit = residue_num - float(total_money)                                                   #实现利润（折算为交易市场币种）：当前剩余币种数量-总投入数量
                    total_profit = float_profit + realized_profit                                                         #总利润（折算为交易市场币种）：浮动盈亏+实现利润
                    annual_yield = realized_profit / float(total_money) / (run_time * 525600 * 1 )                        #年化收益率：实现利润/总投入/运行分钟数*525,600*100%
                    Robot.objects.filter(id=robot_id).update(float_profit=self.data_format(float_profit),
                                                             realized_profit=self.data_format(realized_profit),
                                                             total_profit=self.data_format(total_profit),
                                                             annual_yield=self.data_format(annual_yield))
                    robot_obj = Robot.objects.get(id=robot_id)
                    serialize = RobotSerializer(robot_obj)   #序列化机器人数据返回客户端
                    print(serialize.data)
                    context = {
                        'id': robot_id,
                        'float_profit': self.data_format(float_profit) + market,
                        'realized_profit': self.data_format(realized_profit) + market,
                        'total_profit': self.data_format(total_profit) + market,
                        'annual_yield': self.data_format(annual_yield) + '%'
                    }
                    self.robot_yield.update(context)
                except robot.DoesNotExist:
                    robot_obj = None
        return restful.result(data=serialize.data)


# # 分页
# def get_pagination_data(paginator, page_obj, around_count=2):
#     current_page = page_obj.number
#     num_pages = paginator.num_pages
#
#     left_has_more = False
#     right_has_more = False
#
#     if current_page <= around_count + 2:
#         left_pages = range(1, current_page)
#     else:
#         left_has_more = True
#         left_pages = range(current_page - around_count, current_page)
#
#     if current_page >= num_pages - around_count - 1:
#         right_pages = range(current_page + 1, num_pages + 1)
#     else:
#         right_has_more = True
#         right_pages = range(current_page + 1, current_page + around_count + 1)
#
#
#
#     return {
#         # left_pages：代表的是当前这页的左边的页的页码
#         'left_pages': left_pages,
#         # right_pages：代表的是当前这页的右边的页的页码
#         'right_pages': right_pages,
#         'current_page': current_page,
#         'left_has_more': left_has_more,
#         'right_has_more': right_has_more,
#         'num_pages': num_pages
#     }
