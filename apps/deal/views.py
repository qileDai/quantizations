from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import View
from .models import Account, Property, LastdayAssets, Market, Robot, TradingPlatform, OrderInfo
from apps.rbac.models import UserInfo
from django.core.paginator import Paginator
from urllib import parse
from apps.deal.asset.get_assets import GetAssets
from dealapi.exx.exxMarket import MarketCondition
from dealapi.exx.exxService import ExxService
from .forms import AccountModelForm, RobotFrom,EditAccountFrom
from django.db.models import Q
from utils.mixin import LoginRequireMixin
from utils import restful
from apps.deal.Strategy.Grid import GridStrategy
# Create your views here.r


class AccountList(LoginRequireMixin, View):
    """
    显示用户所有账户信息
    """

    def get(self, request):
        page = int(request.GET.get('p', 1))
        user_id = request.session.get("user_id")
        # 获取账户信息
        accounts = Account.objects.filter(users__id=user_id)
        # 获取用户所有币种
        currency_list = Property.objects.filter(account__users__id=user_id).distinct()
        print(accounts)
        # 分页
        paginator = Paginator(accounts, 10)
        page_obj = paginator.page(page)
        context_data = get_pagination_data(paginator, page_obj)
        context = {
            # 用户信息分页列表
            'accounts_list': page_obj.object_list,
            'accounts': accounts,
            'page_obj': page_obj,
            'paginator': paginator,
            'platfotms': TradingPlatform.objects.all(),
            # 用户所有账户币种信息
            'currency_list': currency_list,
            'properties': Property.objects.all(),
        }
        context.update(context_data)
        return render(request, 'management/tradingaccount.html', context=context)


class AddAccount(View):
    """
    添加账户
    """
    def post(self, request):
        model_form = AccountModelForm(request.POST)
        if model_form.is_valid():
            # save()返回一个还未保存至数据库的对象,用这个对象添加一些额外的数据，然后在用save()保存到数据库
            obj = model_form.save(commit=False)
            user_id = request.session.get("user_id")
            user_obj = UserInfo.objects.get(id=user_id)
            # 添加数据需为模型类对象
            obj.users = user_obj
            obj.save()
            return restful.ok()
        else:
            return restful.params_error(model_form.get_errors())

def accountinfo(request):
        accout_id = request.POST.get('pk')
        print("ss")
        print(accout_id)
        account = Account.objects.get(pk=accout_id)
        context = {
           'account': account,
        }
        print(account)
        return render(request,'management/tradingaccount.html',context=context)

class EditAccount(View):
    """
    编辑账户
    """
    def get(self,request):
        accout_id = request.GET.get('account_id')
        print(accout_id)
        account = Account.objects.get(pk=accout_id)
        # context = {

        #    'account': account,
        # }
        # print(account)
        return render(request,'management/tradingaccount.html')

    def post(self, request):
        form = EditAccountFrom(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            accesskey = form.cleaned_data.get('accesskey')
            secretkey = form.cleaned_data.get('secretkey')
            platform = form.cleaned_data.get('platform')
            pk = form.cleaned_data.get('pk')
            user_id = request.session.get("user_id")
            Account.objects.filter(pk=pk).update(title=title,accesskey=accesskey,secretkey=secretkey,platform=platform,user_id=user_id)
            return restful.ok()
        else:
            return restful.params_error(form.get_errors())


class DeleteAccount(View):
    """
    删除账户
    """

    def post(self, request):
        pk = request.POST.get('pk')
        try:
            Account.objects.filter(pk=pk).delete()
            return restful.ok()
        except:
            return restful.params_error(message="该账户不存在")


class ShowAssert(View):
    """
    显示账户资产信息
    """
    def post(self, request):
        id = request.POST.get('pk')
        account_obj = Account.objects.get(id=id)  # 获取账户信息
        platform = account_obj.platform  # 账户对应的平台
        # 创建对象
        con = GetAssets(id, account_obj, platform)
        data = con.showassets()
        print(type(data))
        return render(request, 'management/tradingaccount.html')
        # return restful.result(data=data)


class ShowCollectAsset(View):
    """
    汇总资产信息
    """
    def post(self, request):
        # 多个账户
        # ids = request.POST.get("pk")
        ids = [1, 2]
        flag = True
        context_list = list()
        for id in ids:
            account_obj = Account.objects.get(id=id)  # 获取账户信息
            platform = account_obj.platform  # 账户对应的平台
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
        print('资产汇总', '-'*20)
        print(context_list[0])
        return restful.result(data=context_list[0])


class ChargeAccount(View):
    """
    增资
    """

    def post(self, request):
        id = request.POST.get('pk')
        account_obj = Account.objects.get(id=id)  # 获取账户信息
        platform = account_obj.platform  # 账户对应的平台
        print(str(platform))
        currency = request.POST.get('currency')
        num = request.POST.get('num')
        # 根据平台调用对应接口
        try:
            if str(platform) == 'EXX':
                currency_pair = currency.lower() + '_usdt'
                market_api = MarketCondition(currency_pair)
                info = market_api.get_ticker()  # 获取EXX单个交易对行情信息
            elif str(platform) == 'HUOBI':
                pass
        except:
            info = dict()
            info['ticker'] = {}
            info['last'] = 0
        if currency:
            property_obj = Property.objects.filter(Q(account_id=id) & Q(currency=currency))
            for obj in property_obj:
                original_assets = float(obj.original_assets) + float(num)*float(info['ticker']['last'])
                Property.objects.filter(Q(account_id=id) & Q(currency=currency)).update(original_assets=original_assets)
            return restful.ok()


class WithDraw(View):
    """
    提币
    """

    def post(self, request):
        id = request.POST.get('pk')
        account_obj = Account.objects.get(id=id)  # 获取账户信息
        platform = account_obj.platform  # 账户对应的平台
        currency = request.POST.get('currency')
        num = request.POST.get('num')
        # 根据平台调用对应接口
        try:
            if str(platform) == 'EXX':
                currency_pair = currency.lower() + '_usdt'
                market_api = MarketCondition(currency_pair)
                info = market_api.get_ticker()  # 获取EXX单个交易对行情信息
                # 调用提币接口
                withdraw_info = ExxService.xx()
            elif str(platform) == 'HUOBI':
                pass
        except:
            info = dict()
            info['ticker'] = {}
            info['last'] = 0
        if currency:
            property_obj = Property.objects.filter(Q(account_id=id) & Q(currency=currency))
            # 提币折合成usdt
            for obj in property_obj:
                original_assets = float(obj.original_assets) + float(num)*float(info['ticker']['last'])
                Property.objects.filter(Q(account_id=id) & Q(currency=currency)).update(original_assets=original_assets)
            return restful.ok()


class ConfigCurrency(View):
    """
    币种新增/配置
    """

    def post(self, request):
        currency = request.POST.get('currency')
        if currency:
            # 获取账户信息
            user_id = request.session.get("user_id")
            accounts = Account.objects.filter(id=user_id)

            for obj in accounts:
                # 账户存在此币种则不添加
                property_obj = Property.objects.filter(Q(account_id=obj.id) & Q(currency=currency))
                if property_obj:
                    continue
                # 保存币种信息
                LastdayAssets.objects.create(currency=currency, account_id=obj.id)
                Property.objects.create(currency=currency, account_id=obj.id)
        currency_info = LastdayAssets.objects.all()
        context = {
            # 币种信息
            'currency_info': currency_info,
        }
        return render(request, 'management/tradingaccount.html', context)


# ----------------------------------------------------------------------------------------------------------------------
# 创建机器人
class GetParams(View):
    """
    获取配置策略的参数
    """
    def post(self, request):
        model_form = RobotFrom(request.POST)
        print('-' * 30, model_form)
        # is_valid()方法会根据model字段的类型以及自定义方法来验证提交的数据
        if model_form.is_valid():
            model_form.save()
            return restful.ok()
        else:
            return restful.params_error(message="创建机器人失败")


def get_account_info(currency, market, id):
    robot_obj = Robot.objects.filter(id=id)
    # 获取账户所属的用户信息
    account_obj = robot_obj.trading_account_id
    # account_obj = Account.objects.filter(id=robot_obj.trading_account_id)
    # 账户对应的平台
    platform = account_obj.platform
    # 获取用户信息
    user_obj = UserInfo.objects.all()
    if platform == 'EXX':
        # 创建交易接口对象---------------------------------------------------------------------API
        con = ExxService(account_obj.accesskey, account_obj.secretkey)
        info = con.get_balance()
        info = info['funds']
        # 创建行情接口对象
        currency_pair = currency.lower() + '_' + market.lower()
        con1 = MarketCondition(currency_pair)
        info1 = con1.get_ticker()
        info2 = con1.get_klines('1day', '30')
    elif platform == 'HUOBI':
        pass

    return user_obj, info, info1, info2


class GetAccountInfo(View):
    """
    获取交易对可用额度/当前价,计算默认值
    """
    def post(self, request):
        currency = request.POST.get('curry-title')
        market = request.POST.get('market-title')
        # 获取机器人id
        id = request.POST.get('pk')
        # 调用函数
        user_obj, info, info1, info2 = get_account_info(currency, market, id)
        # 计算阻力位/支撑位的默认值
        if int(info2['limit']) <= 30:
            max = 0
            min = 0
            for i in info2['datas']['data']:
                max += float(i[2])
                min += float(i[3])

        context = {
            'currency': info[currency.upper()].get('balance'),
            'market': info[market.upper()].get('balance'),
            'last': info1['ticker'].get('last'),
            'resistance': float(max/int(info2['limit'])),
            'support_level': float(min/int(info2['limit'])),
            'users': user_obj,
        }
        print(info, info1, info2)
        print(context)
        return render(request, 'management/gridding.html', context)


class ShowTradeDetail(View):
    """
    展示机器人交易详情
    """
    def post(self, request):
        currency = request.POST.get('curry-title')
        market = request.POST.get('market-title')
        id = request.POST.get('pk')
        # 调用函数
        user_obj, info, info1, info2 = get_account_info(currency, market, id)
        finish_num = OrderInfo.objects.filter(robot=id)
        total_input = ""
        running_time = ""

        context = {
            'currency_balance': info[currency.upper()].get('balance'),
            'market_balance': info[market.upper()].get('balance'),
            'currency_freeze': info[currency.upper()].get('freeze'),
            'market_freeze': info[market.upper()].get('freeze'),
            'last': info1['ticker'].get('last'),
        }


class StartRobot(View):
    """
    运行机器人
    """
    def post(self, request):
        ids = request.POST.get('robot_id')
        # 调用对应策略
        for id in ids:
            robot_obj = Robot.objects.get(id=id)
            if robot_obj.trading_strategy == '网格策略V1.0':
                thread1 = GridStrategy(
                    robot_obj=robot_obj,
                    order_type="buy",
                )
                thread2 = GridStrategy(
                    account_id=robot_obj.trading_account_id,
                    current_price=robot_obj.current_price,
                    grid_num=robot_obj.girding_num,
                    trade_amount=(robot_obj.min_num, robot_obj.max_num),
                    currency_type=robot_obj.currency + '_' + robot_obj.market,

                    order_type="buy"
                )
                thread1.start()
                thread2.start()
            elif robot_obj.trading_strategy == '三角套利V1.0':
                pass
            elif robot_obj.trading_strategy == '搬砖套利V1.0':
                pass

# ----------------------------------------------------------------------------------------------------------------------
# 机器人管理
class RobotList(View):
    """
    机器人管理列表页面
    """
    def get(self, request):
        page = int(request.GET.get('p', 1))
        curry = request.GET.get('deal-curry')  # 拿到下拉框交易币种值
        market = request.GET.get('deal_market')  # 拿到下拉框交易市场值
        status = request.GET.get('deal_status')  # 拿到交易状态
        robots = Robot.objects.all()
        if curry:
            robots = Robot.objects.filter(currency__icontains=curry)
        if market:
            robots = Robot.objects.filter(market__icontains=market)
        if status:
            robots = Robot.objects.filter(status=status)

        paginator = Paginator(robots, 10)
        page_obj = paginator.page(page)
        context_data = get_pagination_data(paginator, page_obj)

        context = {
            'robots': page_obj.object_list,
            'page_obj': page_obj,
            'paginator': paginator,
            'properties': Property.objects.all(),
            'markets': Market.objects.all(),
            'accounts': Account.objects.all(),
            'url_query': '&' + parse.urlencode({
                'curry': curry or '',
                'market': market or '',
                'status': status or ''
            })
        }
        context.update(context_data)

        return render(request, 'management/gridding.html', context=context)


# 分页
def get_pagination_data(paginator, page_obj, around_count=2):
    current_page = page_obj.number
    num_pages = paginator.num_pages

    left_has_more = False
    right_has_more = False

    if current_page <= around_count + 2:
        left_pages = range(1, current_page)
    else:
        left_has_more = True
        left_pages = range(current_page - around_count, current_page)

    if current_page >= num_pages - around_count - 1:
        right_pages = range(current_page + 1, num_pages + 1)
    else:
        right_has_more = True
        right_pages = range(current_page + 1, current_page + around_count + 1)

    return {
        # left_pages：代表的是当前这页的左边的页的页码
        'left_pages': left_pages,
        # right_pages：代表的是当前这页的右边的页的页码
        'right_pages': right_pages,
        'current_page': current_page,
        'left_has_more': left_has_more,
        'right_has_more': right_has_more,
        'num_pages': num_pages
    }
