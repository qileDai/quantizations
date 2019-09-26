from django.shortcuts import render, redirect, reverse, HttpResponse
from .models import UserInfo, Role, Menu, Permission
from django.views.generic import View
from utils import restful
from django.core.paginator import Paginator
from urllib import parse
from .forms import UserInfoModelForm, UserInfoAddModelForm, RoleModelForm, PermissionModelForm, MenuModelForm
import hashlib
from django.conf import settings
from .service.init_permission import init_permission
from utils.mixin import LoginRequireMixin
# Create your views here.


# 用户登录装饰器
def is_login(func):
    def wrapper(request, *args, **kwargs):
        if 'is_login' in request.session:
            res = func(request, *args, **kwargs)
            return res
        else:
            return redirect(settings.LOGIN_URL)
    return wrapper


def login(request):
    if request.method == "GET":
        return render(request, "cms/login.html")
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        hl = hashlib.md5()
        hl.update(password.encode(encoding='utf-8'))
        password = hl.hexdigest()
        user_obj = UserInfo.objects.filter(username=username, password=password).first()
        if not user_obj:
            return render(request, "cms/login.html", {'error': '用户名或密码错误！'})
        elif user_obj.status == 0:
            return render(request, "cms/login.html", {'error': '用户已被禁用，请联系管理员！'})
        elif user_obj.type == 1:               # 管理员
            request.session.clear()
            request.session['is_login'] = True
            request.session['user_id'] = user_obj.id
            request.session.set_expiry(600)
            return render(request, 'cms/index.html')
        else:                                   # 普通用户
            init_permission(request, user_obj)  # 调用权限初始化
            return redirect('/rbac/index/')


@is_login
def index(request):
    if 'is_login' in request.session:
        return render(request, 'cms/index.html')
    else:
        return redirect('settings.LOGIN_URL')


def logout(request):
    request.session.clear()
    return redirect('../../login/')


@is_login
def account(request):
    roles = Role.objects.all()
    users = UserInfo.objects.all()
    context = {
        'users': users,
        'roles': roles,
    }
    return render(request, 'cms/account.html', context=context)


@is_login
def menu(request):
    menus = Menu.objects.all()
    context = {
        'menus': menus
    }
    return render(request, 'cms/menu.html', context=context)


@is_login
def permission(request):
    menus = Menu.objects.all()
    permissions = Permission.objects.all()
    context = {
        'menus': menus,
        'permissions': permissions
    }
    return render(request, 'cms/permission.html', context=context)


@is_login
def role(request):
    roles = Role.objects.all()
    permissions = Permission.objects.all()
    # print(permissions)
    context = {
        'roles': roles,
        'permissions': permissions
    }
    return render(request, 'cms/role.html', context=context)


@is_login
def users_list(request):
    users = UserInfo.objects.all()
    context = {
      'users': users
    }
    return render(request, 'cms/account.html', context=context)


@is_login
def add_roles(request):
    form = RoleModelForm(request.POST)
    if form.is_valid():
        form.save()
        print("dfsd")
        return restful.ok()
    else:
        return restful.params_error(message=form.get_errors())


@is_login
def add_users(request):
    form = UserInfoModelForm(request.POST)
    print("afadf")
    if form.is_valid():
        print("sdaf")
        form.save()
        return restful.ok()
    else:
        return restful.params_error(message=form.get_errors())


@is_login
def delete_users(request):
    pk = request.POST.get('pk')
    # print(pk)
    try:
        UserInfo.objects.filter(pk=pk).delete()
        return restful.ok()
    except:
        return restful.params_error(message="该用户不存在")


class RolesListView(LoginRequireMixin, View):
    def get(self, request):
        # request.GET：获取出来的所有数据，都是字符串类型
        page = int(request.GET.get('p', 1))
        rolename = request.GET.get('rolename-seach')
        print(rolename)
        roles = Role.objects.all()
        # request.GET.get(参数,默认值)
        # 这个默认值是只有这个参数没有传递的时候才会使用
        # 如果传递了，但是是一个空的字
        # 符串，那么也不会使用默认值
        if rolename:
            roles = Role.objects.filter(rolename__icontains=rolename)
            print(roles)
        paginator = Paginator(roles, 10)
        print(paginator)
        page_obj = paginator.page(page)
        context_data = get_pagination_data(paginator, page_obj)
        context = {
            'roles': page_obj.object_list,
            'page_obj': page_obj,
            'paginator': paginator,
            'rolename': rolename,
            'permissions': Permission.objects.all(),
            'url_query': '&' + parse.urlencode({
                'rolename': rolename or '',
            })
        }
        context.update(context_data)

        return render(request, 'cms/role.html', context=context)


class userListView(LoginRequireMixin, View):
    def get(self, request):
        page = int(request.GET.get('p', 1))
        print(page)
        username = request.GET.get('username')
        status = request.GET.get('status')
        users = UserInfo.objects.all()

        if username:
            users = UserInfo.objects.filter(username__icontains=username)
        if status:
            users = UserInfo.objects.filter(status__icontains=status)

        paginator = Paginator(users, 10)
        page_obj = paginator.page(page)
        context_data = get_pagination_data(paginator, page_obj)
        context = {
            'users': page_obj.object_list,
            'username': username,
            'status': status,
            'page_obj': page_obj,
            'paginator': paginator,
            'roles': Role.objects.all(),
            'url_query': '&' + parse.urlencode({
                'username': username or '',
                'status': status or '',
            })
        }
        # 更新context数据
        context.update(context_data)

        return render(request, 'cms/account.html', context=context)


class PermissionListView(LoginRequireMixin, View):
    def get(self, request):
        page = int(request.GET.get('p', 1))
        permission = request.GET.get('permission-seach')
        permissions = Permission.objects.all()
        if permission:
            permissions = Permission.objects.filter(title__icontains=permission)
        paginator = Paginator(permissions, 2)
        page_obj = paginator.page(page)
        context_data = get_pagination_data(paginator, page_obj)
        context = {
            'permissions': page_obj.object_list,
            'page_obj': page_obj,
            'paginator': paginator,
            'permission': permission,
            'menus': Menu.objects.all(),
            'url_query': '&' + parse.urlencode({
                'permission': permission or '',
            })
        }
        context.update(context_data)
        return render(request, 'cms/permission.html', context=context)


class MenuListView(LoginRequireMixin, View):
    def get(self, request):
        page = int(request.GET.get('p', 1))
        menu = request.GET.get('munu')
        menus = Menu.objects.all()
        if menu:
            menus = Menu.objects.filter(title__icontains=menu)
        paginator = Paginator(menus, 10)
        page_obj = paginator.page(page)
        context_data = get_pagination_data(paginator, page_obj)
        context = {
            'menus': page_obj.object_list,
            'page_obj': page_obj,
            'paginator': paginator,
            'menu': menu,
            'url_query': '&' + parse.urlencode({
                'menu': menu or '',
            })
        }
        context.update(context_data)
        return render(request, 'cms/menu.html', context=context)


def delete_menu(request):
    pk = request.POST.get('pk')
    print(pk)
    try:
        Menu.objects.filter(pk=pk).delete()
        return restful.ok()
    except:
        return restful.params_error(message="该目录不存在")


@is_login
def delete_roles(request):
    pk = request.POST.get('pk')
    try:
        Role.objects.filter(pk=pk).delete()
        return restful.ok()
    except:
        return restful.params_error(message='该角色不存在')


@is_login
def add_permission(request):
    form = PermissionModelForm(request.POST)
    print('*'*20)
    if form.is_valid():
        title = form.cleaned_data.get('title')
        url = form.cleaned_data.get('url')
        menu_id = form.cleaned_data.get('menu')
        menu = Menu.objects.get(pk=menu_id)
        Permission.objects.create(title=title, url=url, menu=menu)
        return restful.ok()
    else:
        return restful.params_error(form.get_errors())


class edit_permission(View):
    def get(self, request):
        permission_id = request.POST.get('permission_id')
        permissionss = Permission.objects.get(pk=permission_id)
        context = {
            'menus': Menu.objects.all(),
            'permissionss': permissionss
        }
        return render(request,'cms/permission.html',context=context)

    def post(self, request):
        pass


def delete_permission(request):
    pk = request.POST.get('pk')
    try:
        Permission.objects.filter(pk=pk).delete()
        return restful.ok()
    except:
        return restful.params_error(message="该权限不存在")


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
