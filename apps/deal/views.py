from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import View
from .models import Account, Property, LastdayAssets, Market, Robot,TradingPlatform
from apps.rbac.models import UserInfo
from django.core.paginator import Paginator
from urllib import parse
from apps.deal.asset.get_assets import GetAssets
from dealapi.exx.exxMarket import MarketCondition
from .forms import AccountModelForm
from django.db.models import Q
from utils.mixin import LoginRequireMixin
from utils import restful

# Create your views here.


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
        }
        context.update(context_data)
        return render(request, 'management/tradingaccount.html', context)


class AddAccount(View):
    """
    添加账户
    """
    def post(self, request):
        model_form = AccountModelForm(request.POST)
        if model_form.is_valid():
            user_id = request.session.get("user_id")
            title = model_form.cleaned_data.get("title")
            accesskey = model_form.cleaned_data.get("accesskey")
            secretkey = model_form.cleaned_data.get("secretkey")
            platform_id = request.POST.get("platform")
            Account.objects.create(title=title,accesskey=accesskey,secretkey=secretkey
                                   ,platform_id=platform_id,users_id=user_id)
            return restful.ok()
        else:
            return restful.params_error(model_form.get_errors())


class EditAccount(View):
    """
    编辑账户
    """

    def post(self, request):
        id = request.POST.get('pk')
        account_obj = Account.objects.filter(id=id).first()
        model_form = AccountModelForm(request.POST, instance=account_obj)
        if model_form.is_valid():
            model_form.save()
            return redirect('../accountlist/')
        else:
            return render(request, 'management/tradingaccount.html', {'model_form': model_form, 'title': '编辑用户'})


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
        context = con.showassets()

        print(context)
        return render(request, 'management/tradingaccount.html', context)


class ShowCollectAsset(View):
    """
    汇总资产信息
    """
    def get(self, request):
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
                print(key)
                for key1, value1 in elem['assets_dict'][key].items():
                    if key1 in context_list[0]['assets_dict'][key]:
                        context_list[0]['assets_dict'][key][key1] = float(context_list[0]['assets_dict'][key][key1]) \
                                                                    + float(value1)
                    else:
                        context_list[0]['assets_dict'][key][key1] = value1
        # return render(request, 'management/tradingaccount.html', context_list[0])
        print(context_list[0])
        return HttpResponse('ok')


class ChargeAccount(View):
    """
    增资
    """

    def post(self, request):
        id = request.POST.get('pk')
        account_obj = Account.objects.get(id=id)  # 获取账户信息
        platform = account_obj.platform  # 账户对应的平台
        currency = request.POST.get('currency')
        num = request.POST.get('currency-number')
        # 根据平台调用对应接口
        try:
            if platform == 'EXX':
                currency = currency.lower() + '_usdt'
                market_api = MarketCondition(currency)
                info = market_api.get_ticker()  # 获取EXX单个交易对行情信息
            elif platform == 'HUOBI':
                pass
        except:
            info = 0
        if currency:
            property_obj = Property.objects.filter(Q(account_id=id) & Q(currency=currency))
            original_assets = property_obj.original_assets + float(num)*info['ticker']['last']
            Property.objects.filter(Q(account_id=id) & Q(currency=currency)).update(original_assets=original_assets)


class WithDraw(View):
    """
    提币
    """

    def post(self, request):
        id = request.POST.get('pk')
        account_obj = Account.objects.get(id=id)  # 获取账户信息
        platform = account_obj.platform  # 账户对应的平台
        currency = request.POST.get('currency')
        num = request.POST.get('currency-number')
        # 根据平台调用对应接口
        try:
            if platform == 'EXX':
                currency = currency.lower() + '_usdt'
                market_api = MarketCondition(currency)
                info = market_api.get_ticker()  # 获取EXX单个交易对行情信息
            elif platform == 'HUOBI':
                pass
        except:
            info = 0
        if currency:
            property_obj = Property.objects.filter(Q(account_id=id) & Q(currency=currency))
            # 提币折合成usdt
            original_assets = property_obj.original_assets + float(num)*info['ticker']['last']
            Property.objects.filter(Q(account_id=id) & Q(currency=currency)).update(original_assets=original_assets)


class ConfigCurrency(View):
    """
    币种新增/配置
    """

    def post(self, request):
        currency = request.POST.get('currency')
        if currency:
            user_id = request.session.get("user_id")
            # 获取账户信息
            accounts = Account.objects.filter(users__id=user_id)
            # 保存币种信息
            for obj in accounts:
                # 账户存在此币种则不添加
                property_obj = Property.objects.filter(Q(account_id=obj.id) & Q(currency=currency))
                if property_obj:
                    continue
                LastdayAssets.objects.create(currency='currency', account_id=obj.id)
                Property.objects.create(currency='currency', account_id=obj.id)
        currency_info = LastdayAssets.objects.all()
        context = {
            # 币种信息
            'currency_info': currency_info,
        }
        return render(request, 'management/tradingaccount.html', context)


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
