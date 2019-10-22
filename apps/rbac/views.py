from django.shortcuts import render, redirect, reverse, HttpResponse
from .models import UserInfo, Role, Menu, Permission
from django.views.generic import View
from utils import restful
from django.core.paginator import Paginator
from urllib import parse
from .forms import UserInfoModelForm, UserInfoAddModelForm, RoleModelForm, PermissionModelForm, MenuModelForm, \
EditUserForm
import hashlib
from django.middleware.csrf import get_token ,rotate_token
from django.conf import settings
from .service.init_permission import init_permission
from utils.mixin import LoginRequireMixin
from .models import NewMenu
from .serializers import PermissonSerializer, MenuSerializer, UserSerializer, RoleSerializer, NewmenuSerializer
from django.contrib.auth import login,logout,authenticate
from django.views.decorators.csrf import csrf_exempt
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

def get_csrf(request):
    csrf_token= get_token(request)
    print(csrf_token)
    context = {
        "csrf_token": csrf_token
    }
    return restful.result(data=context)

class Login(View):
    def get(self,request):
        csrf_token= get_token(request)
        print(csrf_token)
        context = {
            "csrf_token":csrf_token
        }
        return restful.result(data=context)
    def post(self,request):
        request.META["CSRF_COOKIE_USED"] = True
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        hl = hashlib.md5()
        hl.update(password.encode(encoding='utf-8'))
        password = hl.hexdigest()
        uers = UserInfo.objects.filter(username=username,password=password).first()
        if uers:
            print("sdfs")
            request.session.clear()
            request.session['is_login'] = True
            request.session['user_id'] = uers.id
            # request.session.set_expiry(600)
            # init_permission(request, uers)
            return restful.ok()
        else:
            return restful.result(message="用户名或密码错误！")


@csrf_exempt
def login(request):
    if request.method == "GET":
        print("带起了")
        csrf_token= get_token(request)
        context = {
            "csrf_token": csrf_token
        }
        return restful.result(data=context)
    else:
        request.META["CSRF_COOKIE_USED"] = True
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username,password)
        hl = hashlib.md5()
        hl.update(password.encode(encoding='utf-8'))
        password = hl.hexdigest()
        print(password)

        user_obj = UserInfo.objects.filter(username=username, password=password).first()
        print(user_obj)
        if not user_obj:
            return render(request, "cms/login.html", {'error': '用户名或密码错误！'})
        elif user_obj.status == 0:
            return render(request, "cms/login.html", {'error': '用户已被禁用，请联系管理员！'})
        else:  # 普通用户
            request.session.clear()
            request.session['is_login'] = True
            request.session['user_id'] = user_obj.id
            # request.session.set_expiry(600)
            # init_permission(request, user_obj)  # 调用权限初始化
            print("asdlfjafjladjfal")
            return redirect('/rbac/index/')


@is_login
def index(request):
    if 'is_login' in request.session:
        return render(request, 'cms/index.html')
    else:
        return redirect('settings.LOGIN_URL')


def logout(request):
    request.session.clear()
    # return restful.ok(message="成功")
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
        return restful.ok()
    else:
        return restful.params_error(message=form.get_errors())


@is_login
def add_users(request):
    form = UserInfoAddModelForm(request.POST)
    if form.is_valid():
        form.save()
        return restful.ok(message="成功")
    else:
        return restful.params_error(message=form.errors)


def add_menu(request):
    form = MenuModelForm(request.POST)
    if form.is_valid():
        form.save()
        return restful.ok()
    else:
        return restful.params_error(message=form.get_errors())


@is_login
def delete_users(request):
    pk = request.POST.get('user_id')
    # print(pk)
    try:
        UserInfo.objects.filter(pk=pk).delete()
        return restful.ok(message="成功")
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
    pk = request.POST.get('role_id')
    try:
        Role.objects.filter(pk=pk).delete()
        return restful.ok(message="成功")
    except:
        return restful.params_error(message='该角色不存在')


@is_login
def add_permission(request):
    form = PermissionModelForm(request.POST)
    print('*' * 20)
    if form.is_valid():
        title = form.cleaned_data.get('title')
        url = form.cleaned_data.get('url')
        menu_id = form.cleaned_data.get('menu')
        menu = Menu.objects.get(pk=menu_id)
        Permission.objects.create(title=title, url=url, menu=menu)
        return restful.ok()
    else:
        return restful.params_error(form.get_errors())


def edit_permission(request):
    permission_id = request.POST.get('permission_id')
    permissionss = Permission.objects.get(pk=permission_id)
    serialize = PermissonSerializer(permissionss)
    return restful.result(data=serialize.data)

"""
返回用户信息
"""
class UserInfos(View):
    def post(self, request):
        user_id = request.POST.get("user_id")
        user = UserInfo.objects.get(pk=user_id)
        serialize = UserSerializer(user)
        return restful.result(data=serialize.data)

"""
返回角色信息
"""
def role_info(request):
    role_id = request.POST.get('role_id')
    role = Role.objects.get(pk=role_id)
    serialize = RoleSerializer(role)
    return restful.result(data=serialize.data)


"""
角色修改
"""
class EditRole(View):
    def post(self,request):
        role_id = request.POST.get("role_id")
        role_name = request.POST.get("role_name")
        if role_name:
            Role.objects.filter(pk=role_id).update(rolename=role_name)
        else:
            return restful.params_error(message="角色名称不能为空")
        return restful.ok(message="角色修改成功")




def edit_Menu(request):
    menu_id = request.POST.get(2)
    menu = Menu.objects.get(pk=menu_id)
    serialize = MenuSerializer(menu)
    return restful.result(serialize.data)

class EditUsers(View):
    def post(self,request):
        form = EditUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            phone_number = form.cleaned_data.get("phone_number")
            password = form.cleaned_data.get("password")
            email = form.cleaned_data.get("email")
            status = form.cleaned_data.get("status")
            roles = form.cleaned_data.get("status")
            pk = form.cleaned_data.get("id")
            UserInfo.objects.filter(pk=pk).update(username=username,phone_number=phone_number,password=password
                                                  ,email=email,status=status,roles=roles)
            return restful.ok(message="成功")
        else:
            return restful.params_error(form.get_errors())



def delete_permission(request):
    pk = request.POST.get('pk')
    try:
        Permission.objects.filter(pk=pk).delete()
        return restful.ok()
    except:
        return restful.params_error(message="该权限不存在")

"""
修改账户密码
"""
class UpdatePassword(View):
    def post(self, request):
        try:
            user_id = request.POST.get("user_id")
            old_password = request.POST.get("old_password")
            if old_password:
                user_obj = UserInfo.objects.get(pk = user_id)
                password1 = user_obj.password
                if password1 != old_password:
                    return restful.params_error(message="原始密码输入错误")
            new_password = request.POST.get('password')
            # password2 = request.POST.get("")
            UserInfo.objects.filter(pk=user_id).update(password=new_password)
        except Exception as e:
            print(e)
        return restful.ok(message="账户密码修改成功")

"""
获取用户权限点跟一级菜单目录
"""
class UserMenuPermission(View):
    def get(self, request):
        user_id = request.session.get("user_id")  # 获取用户id
        user = UserInfo.objects.get(pk=user_id)
        menu_obj = NewMenu.objects.filter(parentid=0)
        serialize = NewmenuSerializer(menu_obj)
        roleids = user.roles
        permission_list = []
        for role_id in roleids:
            role = Role.objects.get(pk=1)
            for menu in role.menus:
                menu_obj = NewMenu.objects.get(pk=menu)
                # serialize = NewmenuSerializer(menu_obj)
                permission = menu_obj.perms
                permission_list.append(permission)

        context = {
            'menu_list': serialize.data,
            'permissions': permission_list
        }
        print(context)
        return restful.result(data=context)

class GetUserPermisssion(View):
    def get(self, request):
        user_id = request.session.get("user_id")  # 获取用户id
        user = UserInfo.objects.get(pk=user_id)

"""
分配权限
当角色没有权限点时添加权限
当角色有权限点时修改权限
"""
class AllotPermissson(View):
    def post(self,request):
        try:
            menu_list = request.POST.get("menu_list")  #获取菜单id list
            role_id = request.POST.get("role_id")     #获取角色id
            role = Role.objects.get(pk=role_id)
            obj = role.menus.all()
            if obj:
                role.menus.set(menu_list)
            else:
                for menus in menu_list:
                    role.menus.add(menus)
        except Exception as e:
            return restful.params_error("分配权限失败",data=e)

        return restful.ok(message="成功")



def menu_permission(request):
    menus = NewMenu.objects.exclude(parentid=0).order_by("orderNum")
    print(menus)
    serializer = NewmenuSerializer(menus, many=True)
    print(serializer.data)
    return restful.result(data=serializer.data)


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


