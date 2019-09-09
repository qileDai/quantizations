from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import View
from .models import Account, Property
from django.core.paginator import Paginator
from dealapi.exx.exxService import ExxService
from dealapi.exx.exxMarket import MarketCondition
from .forms import AccountModelForm
from django.db.models import Q

# Create your views here.


class AccountList(View):
    def get(self, request):
        page = int(request.GET.get('p', 1))
        user_id = request.session.get("user_id")
        print("-"*20)
        print(user_id)
        # 获取账户信息
        accounts = Account.objects.filter(users__id=user_id)
        print(accounts)

        # 分页
        paginator = Paginator(accounts, 10)
        page_obj = paginator.page(page)
        context_data = get_pagination_data(paginator, page_obj)
        context = {
            'accounts_list': page_obj.object_list,
            'accounts': accounts,
            'page_obj': page_obj,
            'paginator': paginator,
        }
        context.update(context_data)
        return render(request, 'management/tradingaccount.html', context)


class AddAccount(View):
    def get(self, request):
        model_form = AccountModelForm()
        return render(request, 'management/tradingaccount.html', {'model_form': model_form, 'title': '新增账户'})

    def post(self, request):
        model_form = AccountModelForm(request.POST)
        print('-'*20, model_form)
        if model_form.is_valid():
            model_form.save()
            return redirect('../accountlist/')
        else:
            return render(request, 'management/tradingaccount.html', {'model_form': model_form, 'title': '新增用户'})


class EditAccount(View):
    def get(self, request, id):
        account_obj = Account.objects.filter(id=id).first()
        model_form = AccountModelForm(instance=account_obj)
        return render(request, 'management/tradingaccount.html', {'model_form': model_form, 'title': '编辑账户'})

    def post(self, request, id):
        account_obj = Account.objects.filter(id=id).first()
        model_form = AccountModelForm(request.POST, instance=account_obj)
        if model_form.is_valid():
            model_form.save()
            return redirect('../accountlist/')
        else:
            return render(request, 'management/tradingaccount.html', {'model_form': model_form, 'title': '编辑用户'})


class DeleteAccount(View):
    def get(self, id):
        account_obj = Account.objects.filter(id=id).first()
        account_obj.delete()
        return redirect('../accountlist/')


class ShowAssert(View):
    def get(self, request, id):
        account_obj = Account.objects.get(id=id)
        platform = account_obj.platform
        # TradingPlatform.objects.filter(Account__id=1)
        if platform.Platform_name == 'EXX':
            service_api = ExxService(platform.Platform_name, account_obj.secretkey, account_obj.accesskey)      # 创建接口对象
            res = service_api.get_balance()  # 获取用户的资产信息
            market_api = MarketCondition()
            res1 = market_api.get_tickers()   # 获取所有行情信息
        elif platform.Platform_name == 'HUOBI':
            pass

        show_currency = Property.objects.filter(Q(account_id=id) & Q(currency_status='1'))
        lastday_assets = 0
        current_assets = 0
        original_assets = 0
        withdraw_record = 0
        currency_list = list()
        transaction_pair = list()
        assets_dict = dict()
        profit_loss_dict = dict()

        for queryset in show_currency:
            lastday_assets += float(queryset.lastday_assets)
            original_assets += float(queryset.original_assets)
            withdraw_record += float(queryset.withdraw_record)
            currency_list.append(queryset.currency)
            transaction_pair.append(queryset.currency.lower() + '_usdt')  # 不同平台参考币种不一样，此处不能写死
            assets_dict[queryset.currency] = list()
            assets_dict[queryset.currency].append(str(queryset.original_assets))  # 初始资产
        print(transaction_pair)
        # 计算当前总资产
        for key, value in res['funds'].items():
            if key in currency_list:
                current_assets += float(value['total'])
                assets_dict[key].insert(0, str(float(value['balance']) + float(value['freeze'])))
                assets_dict[key].insert(0, value['freeze'])
                assets_dict[key].insert(0, value['balance'])

        # 获取当前参考价
        for key1, value1 in res1.items():
            if key1 in transaction_pair:
                key = key1.split('_')[0].upper()
                assets_dict[key].insert(0, value1.get('last', 0))

        asset_change = current_assets - lastday_assets
        print(lastday_assets, currency_list, current_assets)
        print(assets_dict)
        # asset_dict格式{'币种': [参考价，可用，冻结，当前总资产，初始资产]}
        # profit_loss_dict格式{}
        context = {
            'Platform_name': platform.Platform_name,
            'asset_change': asset_change,
            'original_assets': original_assets,
            'withdraw_record': withdraw_record,
            'assets_dict': assets_dict
        }
        return HttpResponse(res)


class ChargeAccount(View):
    def post(self, request, id):
        currency = request.POST.get('currency')
        num = request.POST.get('currency-number')
        if currency:
            pass


class WithDraw(View):
    pass


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
