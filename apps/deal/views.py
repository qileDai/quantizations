from django.shortcuts import render, redirect, reverse, HttpResponse
from django.views.generic import View
from .models import Account, TradingPlatform, Property
from django.core.paginator import Paginator

from .forms import AccountModelForm
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
        elif platform.Platform_name == 'HUOBI':
            pass

        print(res, '*'*20)
        # funds = res.get('funds')
        return HttpResponse(res)


class ChargeAccount(View):
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
