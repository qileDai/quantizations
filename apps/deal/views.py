import threading
import time
import math
import re
import json

from django.db.models import Q
from collections import OrderedDict
from .models import Account, Property, LastdayAssets, Robot, TradingPlatform, OrderInfo
from .forms import AccountModelForm
from apps.rbac.models import UserInfo
from django.core.paginator import Paginator
from apps.deal.asset.get_assets import GetAssets
from dealapi.exx.exxMarket import MarketCondition
from dealapi.exx.exxService import ExxService
from apps.deal.Strategy.Grid import GridStrategy
from django.contrib.sessions.models import Session

from django.core.exceptions import ValidationError
from rest_framework import serializers
from utils import restful
from utils.mixin import LoginRequireMixin
from rest_framework import generics
from apps.deal.serializers import AccountSerializer, RobotSerializer, OrderInfoSerializer, LastdayAssetsSerializer, PropertySerializer, PlatformSerializer
from apps.rbac.serializers import UserSerializer

# Create your views here.


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


class AccountList(LoginRequireMixin, generics.CreateAPIView):
    """
    显示用户所有账户信息
    """
    serializer_class = AccountSerializer

    def get(self, request):
        pageNum = request.GET.get('pageIndex', 1)
        pagesize = request.GET.get('pageSize')
        # 获取用户id
        try:
            sessionid = request.META.get("HTTP_SESSIONID")
            session_data = Session.objects.get(session_key=sessionid)
            user_id = session_data.get_decoded().get('user_id')
        except Exception as e:
            return restful.params_error(message="未获取到sessionid")
            print(e)
        # user_id = 1
        if not user_id:
            return restful.params_error(message='账户失效，请重新登陆！')
        # 获取账户信息
        accounts = Account.objects.filter(users__id=user_id)
        # 分页
        try:
            paginator = Paginator(Account.objects.filter(users__id=user_id), pagesize)
            page_obj = paginator.page(int(pageNum))
        except:
            return restful.params_error(message='页码错误')
        # 获取勾选币种
        currency_list = Property.objects.filter(currency_status='1').values("currency",).distinct()
        ret = list(currency_list)
        data = json.dumps(ret)
        # data = PropertySerializer(currency_list, fields=('currency',), many=True).data
        numPerPage = len(page_obj.object_list)
        totalCount = accounts.count()
        totalPageNum = paginator.num_pages

        context = {
            'numPerPage': numPerPage,
            'PageNum': int(pageNum),
            'result': AccountSerializer(page_obj.object_list, many=True).data,
            # 'result': AccountSerializer(page_obj.object_list, fields=('id', 'title'), many=True).data,
            'totalCount': totalCount,
            'totalPageNum': totalPageNum,
            'currency_list': data,
        }
        return restful.result(data=context)


class GetCurrencies(LoginRequireMixin, generics.CreateAPIView):
    """
    获取用户所有币种
    """
    def get(self, request):
        # 获取用户所有币种
        try:
            sessionid = request.META.get("HTTP_SESSIONID")
            session_data = Session.objects.get(session_key=sessionid)
            user_id = session_data.get_decoded().get('user_id')
        except Exception as e:
            return restful.params_error(message="未获取到sessionid")
            print(e)
        if user_id:
            currency_list = Property.objects.filter(account__users__id=user_id).values("currency",).distinct()
            ret = list(currency_list)
            # currency_list = serialize('json', currency_list)
            data = json.dumps(ret)
            return restful.result(data=data)
        else:
            return restful.params_error(message='未获取到账户登陆信息，请检查是否登陆')


class AddAccount(LoginRequireMixin, generics.CreateAPIView):
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
        try:
            sessionid = request.META.get("HTTP_SESSIONID")
            session_data = Session.objects.get(session_key=sessionid)
            user_id = session_data.get_decoded().get('user_id')
            # user_id = 1
        except Exception as e:
            print(e)
            return restful.params_error(message='未获取到sessionid')
        if model_form.is_valid():
            # save()返回一个还未保存至数据库的对象,用这个对象添加一些额外的数据，然后在用save()保存到数据库
            obj = model_form.save(commit=False)
            user_obj = UserInfo.objects.get(id=user_id)
            # 添加数据需为模型类对象
            obj.users = user_obj
            obj.save()
            accounts = Account.objects.filter(Q(title=obj) & Q(platform=model_form.cleaned_data['platform']))
            currency = Property.objects.values("currency").distinct()
            select_currency = Property.objects.filter(currency_status='1').values("currency").distinct()

            print(accounts, currency, select_currency)
            # 给新账户添加币种/初始资产
            try:
                market_api = MarketCondition()
                info1 = market_api.get_tickers()
                for account in accounts:
                    for cur in currency:
                        print(cur['currency'])
                        try:
                            ser_obj = ExxService(model_form.cleaned_data['secretkey'], model_form.cleaned_data['accesskey'])
                            info = ser_obj.get_balance()
                            info = info['funds']
                            total = info[cur['currency']]['total']
                            transaction_pair = cur['currency'].lower() + '_usdt'
                            data = info1.get(transaction_pair, None)
                            if data:
                                last = data.get('last')
                            elif cur['currency'].lower() == 'usdt':
                                last = 1
                            else:
                                last = 0
                        except:
                            # total = 1
                            return restful.params_error(message='平台接口调用失败或者平台没有该币种')
                        if cur in select_currency:
                            # 勾选状态为1
                            LastdayAssets.objects.create(currency=cur['currency'], account=account,
                                                         lastday_assets=total, last=last, currency_status=1)
                            Property.objects.create(currency=cur['currency'], account=account,
                                                    currency_status=1, original_assets=total, last=last)
                        else:
                            LastdayAssets.objects.create(currency=cur['currency'], account=account,
                                                         lastday_assets=total, last=last, currency_status=0)
                            Property.objects.create(currency=cur['currency'], account=account,
                                                    currency_status=0, original_assets=total, last=last)
                return restful.ok()
            except:
                import traceback
                traceback.print_exc()
        else:
            return restful.params_error(model_form.get_errors())


def accountinfo(request):
    accout_id = request.POST.get('id')
    account = Account.objects.get(id=accout_id)
    serialize = AccountSerializer(account)
    print(serialize.data)
    return restful.result(data=serialize.data)


class EditAccount(LoginRequireMixin, generics.ListCreateAPIView):
    """
    get:
    获取要修改账户信息.
    post:
    提交修改信息.
    """
    serializer_class = AccountSerializer

    def get(self, request):
        # 接收json数据
        data = request.body.decode("utf-8")
        currency_data = json.loads(data)
        account_id = currency_data.get('account_id')
        if account_id:
            account = Account.objects.get(id=account_id)
            account = AccountSerializer(account)
            return restful.result(data=account.data)
        else:
            return restful.params_error(message='参数为空')

    def post(self, request):
        try:
            sessionid = request.META.get("HTTP_SESSIONID")
            session_data = Session.objects.get(session_key=sessionid)
            user_id = session_data.get_decoded().get('user_id')
        except Exception as e:
            print(e)
            return restful.params_error(message="未获取到sessionid")
        try:
            data = request.body.decode("utf-8")
            currency_data = json.loads(data)
            id = currency_data.get('id')
            title = currency_data.get('title')
            accesskey = currency_data.get('accesskey')
            secretkey = currency_data.get('secretkey')
            platform = currency_data.get('platform')
            print(title, accesskey, secretkey, platform, user_id)
            Account.objects.filter(id=id).update(title=title, accesskey=accesskey,
                                                 secretkey=secretkey, platform=platform)
            return restful.ok()
        except ExxService as e:
            print(e)
            return restful.result(message='参数错误')


class DeleteAccount(LoginRequireMixin, generics.CreateAPIView):
    """
    删除账户
    """
    serializer_class = AccountSerializer

    def post(self, request):
        try:
            pk = request.POST.get('id')
            Account.objects.filter(id=pk).delete()
            return restful.ok()
        except:
            return restful.params_error(message="参数错误或该账户不存在")


class ShowAssert(LoginRequireMixin, generics.CreateAPIView):
    """
    显示账户资产信息
    """
    serializer_class = AccountSerializer

    def post(self, request):
        try:
            id = request.POST.get('id')
        except Exception as e:
            print(e)
            return restful.params_error(message='参数错误')
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


class ShowCollectAsset(LoginRequireMixin, generics.CreateAPIView):
    """
    汇总资产信息
    """
    serializer_class = AccountSerializer

    def post(self, request):
        try:
            data = request.body.decode("utf-8")
            currency_data = json.loads(data)    # 反序列化
            account_list = currency_data.get('id')
        except Exception as e:
            print(e)
            return restful.params_error(message='参数错误')
        if account_list:
            accounts = account_list
        else:
            return restful.result(data='')

        flag = True
        context_list = list()
        for id in accounts:
            # 获取账户信息
            account_obj = Account.objects.get(id=id)
            # 账户对应的平台
            platform = account_obj.platform
            # 创建对象
            con = GetAssets(id, account_obj, platform, flag)
            context = con.showassets()
            context_list.append(context)
        # print('******', context_list)
        # 汇总资产表数据
        for key in context_list[0]['assets_dict']:
            for elem in context_list[1:]:
                for key1, value1 in elem['assets_dict'][key].items():
                    if key1 is 'last':
                        continue
                    elif key1 in context_list[0]['assets_dict'][key]:
                        context_list[0]['assets_dict'][key][key1] = \
                            float(context_list[0]['assets_dict'][key][key1]) + float(value1)
                    else:
                        context_list[0]['assets_dict'][key][key1] = value1
        # 损益表汇总数据
        for key in context_list[0]['profit_loss_dict']:
            for elem in context_list[1:]:
                for key1, value1 in elem['profit_loss_dict'][key].items():
                    if key1 is 'last':
                        continue
                    elif key1 in context_list[0]['profit_loss_dict'][key]:
                        context_list[0]['profit_loss_dict'][key][key1] = \
                            float(context_list[0]['profit_loss_dict'][key][key1]) + float(value1)
                    else:
                        context_list[0]['profit_loss_dict'][key][key1] = value1
        # 汇总资产变化/初始总资产/历史盈亏/
        print('资产汇总', '-' * 20)
        # print(context_list[0])
        return restful.result(data=context_list[0])


class ChargeAccount(LoginRequireMixin, generics.CreateAPIView):
    """
    增资
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
                    info = info['ticker']['last']
                elif str(platform) == 'HUOBI':
                    pass
            except:
                print('未获取到该币种当前价')
                info = 1
            try:
                property_obj = Property.objects.get(Q(account_id=id) & Q(currency=currency))
                original_assets = float(property_obj.original_assets) + float(num)
                Property.objects.filter(Q(account_id=id) & Q(currency=currency)).update(original_assets=original_assets)
                return restful.ok()
            except:
                return restful.params_error(message='账户没有此币种')
        else:
            return restful.params_error(message='参数为空')


class WithDraw(LoginRequireMixin, generics.CreateAPIView):
    """
    提币
    """
    serializer_class = AccountSerializer

    def post(self, request):
        try:
            id = request.POST.get('id')
            currency = request.POST.get('currency')
            num = request.POST.get('num')
        except:
            return restful.result(message='参数错误')
        if id and currency and num:
            account_obj = Account.objects.get(id=id)  # 获取账户信息
            platform = account_obj.platform  # 账户对应的平台
            if currency:
                property_obj = Property.objects.get(Q(account_id=id) & Q(currency=currency))
                original_assets = float(property_obj.original_assets) - float(num)
                Property.objects.filter(Q(account_id=id) & Q(currency=currency)).update(original_assets=original_assets,
                                                                                        withdraw_record=num)
                return restful.ok()
        else:
            return restful.params_error(message='参数为空')


class ConfigCurrency(LoginRequireMixin, generics.CreateAPIView):
    """
    币种新增/配置
    """
    serializer_class = AccountSerializer

    def post(self, request):
        try:
            sessionid = request.META.get("HTTP_SESSIONID")
            session_data = Session.objects.get(session_key=sessionid)
            user_id = session_data.get_decoded().get('user_id')
            currency = request.POST.get('currency')
            # 根据平台判断币种
            marketinfo = MarketCondition()
            market_obj = marketinfo.get_markets()
            keys = [x[0] for x in market_obj.items() if currency.lower() in x[0].split('_')]
            if not keys:
                return restful.params_error(message='平台不存在该币种，请重新输入')
            currency_list = list()
            currency_list.append(currency)
        except:
            return restful.params_error(message='未获取到sessionid或参数错误')
        if currency_list:
            accounts = Account.objects.filter(users=user_id)
            for account in accounts:
                for currency in currency_list:
                    # 账户存在此币种则不添加
                    property_obj = Property.objects.filter(Q(account=account.id) & Q(currency=currency))
                    print('+' * 30, list(property_obj))
                    if not list(property_obj):
                        # 不存在则保存币种信息
                        try:
                            ser_obj = ExxService(account.secretkey, account.accesskey)
                            info = ser_obj.get_balance()
                            info = info['funds']
                            total = info[currency]['total']
                        except ExxService as e:
                            print(e)
                            return restful.params_error(message='调用接口失败')
                        # account必须为模型类对象
                        LastdayAssets.objects.create(currency=currency, account=account)
                        Property.objects.create(currency=currency, account=account, original_assets=total, currency_status=0)
            # 返回数据为json格式
            data = Property.objects.values("currency").distinct()
            return restful.result(data=list(data))
        else:
            return restful.params_error(message='请选择账户币种')


class SelectCurrency(LoginRequireMixin, generics.CreateAPIView):
    """
    勾选的币种
    """
    serializer_class = AccountSerializer

    def post(self, request):
        data = request.body.decode("utf-8")
        currency_data = json.loads(data)
        currency_list = currency_data.get('currency')
        if currency_list:
            Property.objects.values("currency").update(currency_status='0')
            LastdayAssets.objects.values("currency").update(currency_status='0')
            for cur in list(currency_list):
                Property.objects.filter(currency=cur).update(currency_status='1')
                LastdayAssets.objects.filter(currency=cur).update(currency_status='1')
            return restful.ok()
        else:
            return restful.params_error(message='参数为空')


# ----------------------------------------------------------------------------------------------------------------------
# 创建机器人
class CreateRobot(LoginRequireMixin, generics.CreateAPIView):
    """
    获取配置策略的参数
    """
    serializer_class = AccountSerializer

    def post(self, request):
        try:
            robot_data = request.body.decode("utf-8")
            currency_data = json.loads(robot_data)
            id = currency_data.get('trading_account')
            account_obj = Account.objects.get(id=id)
            del currency_data['trading_account']
            # 必须为模型类对象
            Robot.objects.create(**currency_data, trading_account=account_obj)
            return restful.ok()
        except Exception as e:
            print(e)
            return restful.result(message='参数错误')


class GetAccountInfo(LoginRequireMixin, generics.CreateAPIView):
    """
    展示交易对可用额度/当前价,计算默认值
    """
    serializer_class = AccountSerializer

    def data_format(self, data):
        data = str(round(float(data), 2))
        return data

    def post(self, request):
        try:
            data = request.body.decode('utf-8')
            tdata = json.loads(data)
            currency = tdata.get('curry_title')
            market = tdata.get('market_title')
            # 获取账户id
            id = tdata.get('account_id')
        except:
            return restful.params_error(message='参数错误')
        if currency and market and id:
            # 调用get_account_info函数
            user_obj, service_obj, market_obj = get_account_info(currency, market, id)
            try:
                info = service_obj.get_balance()
                info = info['funds']
                info1 = market_obj.get_ticker()
                info1 = info1['ticker']
                info2 = market_obj.get_klines('1day', '30')
                info2 = info2.get('datas')
            except:
                print(info)
                return restful.params_error(message='币种错误或者调用接口失败，请核对！')
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
            return restful.result(data=context)
        else:
            return restful.params_error(message='参数为空')


class SelectAccount(LoginRequireMixin, generics.CreateAPIView):
    """
    创建机器人选择账户
    """
    def get(self, request):
        accounts = Account.objects.all()
        accounts = AccountSerializer(accounts, many=True).data
        return restful.result(data=accounts)


class RobotProtection(LoginRequireMixin, generics.CreateAPIView):
    """
    机器人保护
    """
    serializer_class = AccountSerializer

    def post(self, request):
        try:
            data = request.body.decode('utf-8')
            data_dict = json.loads(data)
            id = data_dict.get('robot_id')
            flag = data_dict.get('flag')
            protect = data_dict.get('protect')
        except ExxService as e:
            print(e)
            return restful.result(message='参数错误')

        if id:
            if protect == 1:
                if flag == 0:
                    Robot.objects.filter(id=id).update(status=3, protection=0)
                elif flag == 1:
                    Robot.objects.filter(id=id).update(status=2, protection=0)
            elif protect == 0:
                if flag == 0 or flag == 3:
                    Robot.objects.filter(id=id).update(status=0, protection=1)
                elif flag == 1 or flag == 2:
                    Robot.objects.filter(id=id).update(status=1, protection=1)
            return restful.ok()
        else:
            return restful.params_error(message='参数为空')


class StartRobot(LoginRequireMixin, generics.CreateAPIView):
    """
    管理机器人
    """
    serializer_class = AccountSerializer
    order_list = ""

    def post(self, request):
        try:
            data = request.body.decode("utf-8")
            data_dict = json.loads(data)
            # 多个和一个
            ids = data_dict.get('robot_id')
            # Flag为1启动，为0停止
            Flag = data_dict.get('flag')
        except ExxService as e:
            print(e)
            return restful.result(message='参数错误')

        if Flag is None:
            return restful.params_error(message='参数flag为空')
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
                #获取机器人启动运行时间戳updta到数据库
                for item in threading.enumerate():
                    try:
                        # 获取线程对应的机器人
                        robot = item.robot_obj
                        if robot_obj.id == robot.id:
                            # item.setFlag(False)
                            rtime = item.start_time
                            Robot.objects.filter(id=robot_obj.id).update(running_time=rtime)

                    except:
                        print('对象没有属性robot_obj')
                        continue

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
                            end_time = time.time()
                            Robot.objects.filter(id=robot_obj.id).update(end_time=end_time)
                            run_time = time.time() - item.start_time
                            total_time = float(run_time) + float(robot.total_time)
                            Robot.objects.filter(id=robot_obj.id).update(total_time=total_time)
                    except:
                        print('对象没有属性robot_obj')
                        continue

            elif robot_obj.trading_strategy == '三角套利V1.0':
                pass
            elif robot_obj.trading_strategy == '搬砖套利V1.0':
                pass

        StartRobot.order_list = threading.enumerate()
        return restful.ok()


class ShowTradeDetail(LoginRequireMixin, generics.CreateAPIView):
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
        m = 0
        for k, v in order_info.items():
            if v["order_type"] is "sell":
                sells[m] = v
                m += 1
        n = 0
        for k, v in order_info.items():
            if v["order_type"] is "buy":
                buys[n] = v
                n += 1
        buys = sorted(buys.items(), key=lambda x: x[1]["price"], reverse=True)
        sells = sorted(sells.items(), key=lambda x: x[1]["price"])
        return dict(sells), dict(buys)

    def match_buy_sell(self, close_buy, close_sell, fee):
        try:
            closed_info = list()
            close_sell = list(close_sell)
            total_profit = 0
            for buy in close_buy:
                for sell in close_sell:
                    if buy['mark'] == sell['mark']:
                        buy['profit'] = float(sell['total_price'])*(1-float(fee))-float(buy['total_price'])*(1-float(fee))
                        total_profit += buy['profit']
                        close_sell.remove(sell)
                        for k, v in sell.items():
                            k1 = k + '1'
                            buy[k1] = v
                        closed_info.append(buy)
                        break
                else:
                    closed_info.append(buy)

            closed_info = closed_info + close_sell

            return closed_info, total_profit
        except:
            import traceback
            traceback.print_exc()

    def post(self, request):
        try:
            data = request.body.decode("utf-8")
            data_dict = json.loads(data)
            # 获取机器人id
            id = data_dict.get('robot_id')
            pageNum = int(data_dict.get('pageIndex', 1))
            pagesize = data_dict.get('pageSize')
        except ExxService as e:
            print(e)
            return restful.result(message='参数错误')
            # import traceback
            # traceback.print_exc()
        else:
            if id and pageNum:
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
                    print(e)
                    return restful.params_error(message='币种或交易对错误，请核对！')
                # 查询已完成订单
                property_obj = Property.objects.get(Q(account_id=robot_obj.trading_account) & Q(currency=currency))
                closed_order_buy = OrderInfo.objects.filter(Q(robot=id) & Q(order_type='buy')).order_by("-id")
                closed_order_sell = OrderInfo.objects.filter(Q(robot=id) & Q(order_type='sell')).order_by("-id")
                closed_buy = OrderInfoSerializer(closed_order_buy, many=True).data
                closed_sell = OrderInfoSerializer(closed_order_sell, many=True).data
                closed_info, total_profit = self.match_buy_sell(closed_buy, closed_sell, robot_obj.procudere_fee)
                # print('-='*20)
                # print(type(closed_sell))
                # 已完成订单分页
                try:
                    paginator = Paginator(closed_info, pagesize)
                    page_obj = paginator.page(pageNum)
                except:
                    import traceback
                    traceback.print_exc()
                    return restful.params_error(message='页码错误')
                numPerPage = len(page_obj.object_list)
                totalCount = len(closed_info)
                totalPageNum = paginator.num_pages

                # 获取挂单信息
                order_info = dict()
                running_time = 0
                for item in StartRobot.order_list:
                    try:
                        # 获取机器人对应的线程对象
                        robot = item.robot_obj
                        if id == robot.id:
                            # 向字典中添加数据
                            order_info = {**order_info, **item.id_dict}
                            if item.Flag:
                                running_time = time.time() - item.start_time
                            else:
                                running_time = 0
                    except:
                        print('对象没有属性robot_obj')
                        continue
                sell, buy = self.sort_data(order_info)
                print('----------------------------------', order_info)
                context = {
                    # 交易币种和交易市场
                    'currency_market': {"currency": currency, "market": market},
                    # 已完成笔数
                    'closed_num': len(closed_buy)+len(closed_sell),
                    # 已完成挂单信息
                    'closed_order': page_obj.object_list,
                    # 未完成笔数
                    'open_num': len(order_info),
                    # 未完成卖单信息
                    'open_sell': sell,
                    # 未完成买单信息
                    'open_buy': buy,
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
                    # 单笔收益
                    'profit': self.data_format(
                        (float(info[currency.upper()].get('total')) - float(property_obj.original_assets))
                        * float(info1.get('last'))) + ' ' + market,
                    # 总收益
                    'total_profit': total_profit,
                    'numPerPage': numPerPage,
                    'PageNum': pageNum,
                    'totalCount': totalCount,
                    'totalPageNum': totalPageNum,
                }

                # print(context)
                return restful.result(data=context)
            else:
                return restful.params_error(message='参数为空')


class ShowConfigInfo(LoginRequireMixin, generics.CreateAPIView):
    """
    展示机器人配置信息
    """
    # serializer_class = AccountSerializer

    def data_format(self, data):
        data = str(round(float(data), 2))
        return data

    def post(self, request):
        try:
            data = request.body.decode("utf-8")
            data_dict = json.loads(data)
            id = data_dict.get('robot_id')
            robot_obj = Robot.objects.get(id=id)
            account_id = robot_obj.trading_account.id
            account_obj = Account.objects.filter(id=account_id).first()
            serialize = RobotSerializer(robot_obj)
            user_obj, service_obj, market_obj = get_account_info(robot_obj.currency, robot_obj.market,
                                                                 robot_obj.trading_account.id)
            accounts = robot_obj.warning_account
            try:
                info = service_obj.get_balance()
                info = info.get('funds')
            except:
                return restful.params_error(message='币种错误，请核对！')

            context = {
                # 交易币种可用
                'currency': self.data_format(info[robot_obj.currency.upper()].get('balance')) + ' ' + robot_obj.currency,
                # 交易市场可用
                'market': self.data_format(info[robot_obj.market.upper()].get('balance')) + ' ' + robot_obj.market,
                # 账户信息
                'account_name': str(account_obj.title),
                # 机器人信息
                'robot': serialize.data,
                # 已勾选的预警用户
                'warning_account': accounts
            }
            return restful.result(data=context)
        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()
            return restful.result(message='参数错误')


class ShowConfig(LoginRequireMixin, generics.CreateAPIView):
    """
    修改机器人配置信息
    """
    serializer_class = AccountSerializer

    def post(self, request):
        try:
            data = request.body.decode("utf-8")
            data_dict = json.loads(data)
            # 获取机器人id
            id = data_dict.get('robot_id')

            del data_dict['robot_id']
            Robot.objects.filter(id=id).update(**data_dict)
            return restful.ok()
        except:
            import traceback
            traceback.print_exc()
            return restful.params_error(message='参数错误')


class WarningUsers(LoginRequireMixin, generics.CreateAPIView):
    """
    序列化预警账户
    """
    serializer_class = AccountSerializer

    def get(self, request):
        try:
            users = UserInfo.objects.filter(status=1)
            usr = UserSerializer(users, many=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(e)
        return restful.result(data=usr.data)


class RobotList(LoginRequireMixin, generics.CreateAPIView):
    """
    机器人管理列表页面
    """
    serializer_class = AccountSerializer

    def post(self, request):
        data = request.body.decode("utf-8")
        data_dict = json.loads(data)
        pageNum = int(data_dict.get('pageIndex', 1))
        pagesize = data_dict.get('pageSize')
        if pageNum is None:
            return restful.params_error(message='参数为空')

        robots = Robot.objects.all()
        try:
            paginator = Paginator(robots, pagesize)
            page_obj = paginator.page(pageNum)
        except:
            return restful.params_error(message='页码错误')
        numPerPage = len(page_obj.object_list)
        totalCount = robots.count()
        totalPageNum = paginator.num_pages

        context = {
            'numPerPage': numPerPage,
            'PageNum': pageNum,
            'result': RobotSerializer(page_obj.object_list, many=True).data,
            'totalCount': totalCount,
            'totalPageNum': totalPageNum,
            'account': RobotSerializer(robots, fields=('account_id', 'account_title'), many=True).data
        }

        return restful.result(data=context)


class SearchRobot(generics.CreateAPIView):
    """
    机器人搜索
    """
    def post(self, request):
        search = request.body.decode("utf-8")
        data_dict = json.loads(search)
        t_currency = data_dict.get('t_currency')
        t_market = data_dict.get('t_market')
        t_status = data_dict.get('t_status')
        search_dict = dict()
        if t_currency:
            search_dict['currency'] = t_currency
        if t_market:
            search_dict['market'] = t_market
        if t_status or t_status == 0:
            search_dict['status'] = t_status

        pageNum = int(data_dict.get('pageIndex', 1))
        pagesize = data_dict.get('pageSize')
        if pageNum is None:
            return restful.params_error(message='页码为空')

        robots = Robot.objects.all()
        try:
            paginator = Paginator(robots, pagesize)
            page_obj = paginator.page(pageNum)
        except:
            return restful.params_error(message='页码错误')
        numPerPage = len(page_obj.object_list)
        totalCount = robots.count()
        totalPageNum = paginator.num_pages
        t_data = Robot.objects.filter(**search_dict)
        # t_data = Robot.objects.filter(status='0')
        # 序列化
        context = {
            'numPerPage': numPerPage,
            'PageNum': pageNum,
            'result': RobotSerializer(t_data, many=True).data,
            'totalCount': totalCount,
            'totalPageNum': totalPageNum,
            'account': RobotSerializer(robots, fields=('account_id', 'account_title'), many=True).data
        }
        return restful.result(data=context)

# ----------------------------------------------------------------------------------------------------------------------


class RobotYield(generics.CreateAPIView):
    """
    机器人收益计算更新到数据库
    """
    serializer_class = AccountSerializer


    # 用作对数据做精度处理
    def data_format(self, data):
        data = str(round(float(data), 2))
        return data

    #对数据库中的数据四舍五入取2位小数点，并去掉单位
    def str_util(self,data):
        if data:
            str_data = re.findall('\d+\.\d*', data)[0]
            new_str = round(float(str_data), 2)
            return new_str
        else:
            return restful.params_error(message="机器人参数位空")

    def post(self, request):
        try:
            # 获取用户id
            robot_yield = []
            sessionid = request.META.get("HTTP_SESSIONID")
            session_data = Session.objects.get(session_key=sessionid)
            user_id = session_data.get_decoded().get('user_id')
            # 根据登录用户id拿到交易账户
            accounts = Account.objects.filter(users=user_id)
            for account in accounts:
                exx_service = ExxService(account.secretkey, account.accesskey)
                #根据交易账户id获取账户下所有的机器人
                robots = Robot.objects.filter((Q(trading_account_id=account.id) & Q(status=1)) | (Q(trading_account_id=account.id) & Q(status=2)))
                for robot in robots:
                    robot_id = robot.id  # 机器人id
                    print('id**********',robot_id)
                    currency = robot.currency  # 交易币种
                    market = robot.market  # 市场币种
                    # total_money = re.findall('\d+\.\d\d', robot.total_money)[0]  # 总投入
                    total_money = self.str_util(robot.total_money)  # 总投入
                    init_currency = self.str_util(robot.currency_num)  # 初始交易币种数量
                    init_market = self.str_util(robot.market_num)  # 初始市场币种数量
                    last_price = robot.current_price  # 当时价格
                    start_time = robot.running_time    # 创建时间
                    total_time = robot.total_time    #运行总时间秒
                    print(total_time)
                    try:
                        user_obj, service_obj, market_obj = get_account_info(currency, market, account.id)
                        info = exx_service.get_balance()
                        info = info.get('funds')
                        info1 = market_obj.get_ticker()
                        info1 = info1.get('ticker')
                        current_price = info1.get('last')  # 最新价格
                        balance_currency = self.data_format(info[currency.upper()].get('total'))                  #当前可用的交易币种数量包括冻结
                        balance_market = self.data_format(info[market.upper()].get('total'))                      #当前可用的市场币种数量
                        current_time = time.time()         #获取最新的时间
                        print(current_time,"current_time")
                        run_time = self.data_format((float(current_time) - float(start_time))/60)  #档次机器人运行多少分钟
                        before_time = self.data_format(float(total_time) /60)                      #以前机器人总共运行多少分钟
                        run_totalTime = float(before_time) + float(run_time)                         #运行总时间分钟

                        #------------------------------计算当次机器人启动运行产生的收益率-------------------------------------
                        # residue_num = ((float(balance_currency) ) / float(last_price) ) + (float(balance_market) )
                        float_profit = float(balance_currency) * float(current_price) - float(init_currency) * float(last_price)      #浮动盈亏（折算为交易市场币种）：当前剩余币种数量*当前价格-总投入数量*当时价格
                        realized_profit = float(balance_market) - float(init_market)                                                  #实现利润（折算为交易市场币种）：当前剩余币种数量-总投入数量
                        total_profit = float_profit + realized_profit                                                                 #总利润（折算为交易市场币种）：浮动盈亏+实现利润

                        annual_yield = (float(realized_profit) / float(total_money)) / float(run_totalTime) * 525600 * 1                   #年化收益率：实现利润/总投入/运行分钟数*525,600*100%

                        new_annual_yield = self.data_format(annual_yield)

                        yield_data= str(new_annual_yield) + '%'
                        print(yield_data)

                        #------------------------跟新收益率到数据库表中------------------------------------------------------
                        Robot.objects.filter(id=robot_id).update(float_profit=self.data_format(float_profit) + ' ' +market,
                                                                 realized_profit=self.data_format(realized_profit) + ' '+ market,
                                                                 total_profit=self.data_format(total_profit) + ' ' +  market ,
                                                                 annual_yield= yield_data)

                        # serialize = RobotSerializer(robot_obj)   #序列化机器人数据返回客户端
                        #                         # print(serialize.data)
                        robot_obj = Robot.objects.get(id=robot_id)
                        context = {
                            'id': robot_id,
                            'float_profit': self.data_format(float_profit) + market,
                            'realized_profit': self.data_format(realized_profit) + market,
                            'total_profit': self.data_format(total_profit) + market,
                            'annual_yield': self.data_format(annual_yield) + '%',
                            'srart_time':robot_obj.running_time,
                            'end_time': robot_obj.end_time,
                            'total_time': run_totalTime,
                            'run_time':run_time

                        }
                        robot_yield.append(context)
                    except robot.DoesNotExist:
                        return restful.params_error(message="机器人没有运行")
        except Exception as e:
            print(e)
        return restful.result(data=robot_yield)








