from django.shortcuts import render, redirect
from .models import UserInfo, Role, Menu, Permission
from django.views.generic import View
from utils import restful
from django.core.paginator import Paginator
from urllib import parse
from .forms import UserInfoModelForm, UserInfoAddModelForm, RoleModelForm, PermissionModelForm, MenuModelForm, \
    EditUserForm
import hashlib
from django.middleware.csrf import get_token, rotate_token
from django.conf import settings
from utils.mixin import LoginRequireMixin
from .models import NewMenu, RoleMenu
from .serializers import PermissonSerializer, MenuSerializer, UserSerializer, RoleSerializer, NewmenuSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework import permissions
from .token_module import get_token, out_token
from django.db.models import Q
from rest_framework import generics


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
    csrf_token = get_token(request)
    print(csrf_token)
    context = {
        "csrf_token": csrf_token
    }
    return restful.result(data=context)


class Login(View):
    def get(self, request):
        csrf_token = get_token(request)
        print(csrf_token)
        context = {
            "csrf_token": csrf_token
        }
        return restful.result(data=context)

    def post(self, request):
        request.META["CSRF_COOKIE_USED"] = True
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        hl = hashlib.md5()
        hl.update(password.encode(encoding='utf-8'))
        password = hl.hexdigest()
        uers = UserInfo.objects.filter(username=username, password=password).first()
        if uers:
            print("sdfs")
            request.session.clear()
            request.session['is_login'] = True
            request.session['user_id'] = uers.id
            request.session.clear_expired()
            request.session.set_expiry(10)
            # init_permission(request, uers)

            return restful.ok()
        else:
            return restful.result(message="用户名或密码错误！")


@csrf_exempt
def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if username == '':
        return restful.params_error(message="用户名不能为空")
    if password == '':
        return restful.params_error(message="密码不能为空")
    print(username, password)
    hl = hashlib.md5()
    hl.update(password.encode(encoding='utf-8'))
    password = hl.hexdigest()
    print(password)
    user_obj = UserInfo.objects.filter(username=username, password=password).first()
    print(user_obj)
    if not user_obj:
        return restful.params_error(message="用户名或密码错误")
    elif user_obj.status == 0:
        return restful.params_error(message="用户已被禁用")
    else:  # 普通用户
        request.session.clear()
        request.session['is_login'] = True
        request.session['user_id'] = user_obj.id
        user_id = request.session['user_id']
        if not request.session.session_key:
            request.session.create()
            session_id = request.session.session_key
        else:
            session_id = request.session.session_key
        print('----------', session_id)
        # token = Token.objects.create(user=user_id)
        # print(token)
        context = {
            'expire': 86400,
            'isCustomize': 0,
            'userId': user_id,
            'sessionid': session_id
        }
        request.session.set_expiry(300)

        # return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json,charset=utf-8")
        # return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json")
        # init_permission(request, user_obj)  # 调用权限初始化
        # return  HttpResponse(context, content_type="application/json;charset=utf-8")
        # json.dumps(result, ensure_ascii=False), content_type = "application/json,charset=utf-8"
        return restful.result(data=context)



def index(request):
    if 'is_login' in request.session:
        return render(request, 'cms/index.html')
    else:
        return redirect('settings.LOGIN_URL')


def logout(request):
    request.session.clear()
    return restful.ok(message="成功")
    # return redirect('../../login/')



def account(request):
    roles = Role.objects.all()
    users = UserInfo.objects.all()
    context = {
        'users': users,
        'roles': roles,
    }
    return render(request, 'cms/account.html', context=context)



def menu(request):
    menus = Menu.objects.all()
    context = {
        'menus': menus
    }
    return render(request, 'cms/menu.html', context=context)



def permission(request):
    menus = Menu.objects.all()
    permissions = Permission.objects.all()
    context = {
        'menus': menus,
        'permissions': permissions
    }
    return render(request, 'cms/permission.html', context=context)



def role(request):
    roles = Role.objects.all()
    permissions = Permission.objects.all()
    # print(permissions)
    context = {
        'roles': roles,
        'permissions': permissions
    }
    return render(request, 'cms/role.html', context=context)



def users_list(request):
    users = UserInfo.objects.all()
    context = {
        'users': users
    }
    return render(request, 'cms/account.html', context=context)



class AddRoles(generics.CreateAPIView):
    serializer_class = RoleSerializer
    def post(self,request):
        form = RoleModelForm(request.POST)
        if form.is_valid():
            rolename = form.cleaned_data.get("rolename")
            description = form.cleaned_data.get("description")
            Role.objects.create(rolename=rolename, description=description)
            return restful.ok()
        else:
            return restful.params_error(message=form.get_errors())

# class AddRole(View):
#     serializer_class = UserSerializer


def add_roles(request):
    form = RoleModelForm(request.POST)
    if form.is_valid():
        rolename = form.cleaned_data.get("rolename")
        description = form.cleaned_data.get("description")
        Role.objects.create(rolename=rolename, description=description)
        return restful.ok()
    else:
        return restful.params_error(message=form.get_errors())



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


class RoleList(View):
    def get(self, request):
        roles = Role.objects.all()
        # pageNum = request.GET.get('pageIndex', 1)
        # pagesize = request.GET.get('pageSize')
        # rolename = request.GET.get('rolename')
        roles = Role.objects.all()
        if roles:
            serialize = RoleSerializer(roles, many=True)
            roles_data = serialize.data
        # else:
        #     return restful.params_error(message="no roles data")
        # if rolename:
        #     roles = Role.objects.filter(rolename__icontains=rolename)
        #     serialize = RoleSerializer(roles, many=True)
        #     roles_data = serialize.data

        return restful.result(data=roles_data)


"""
获取所有用户
"""


class getAllUsers(View):
    def get(self, request):
        userList = []
        users = UserInfo.objects.all()
        # for user in users:
        #     user_data = UserSerializer(user, many=True).data
        #     userList.append(user_data)
        #     print(userList)

        serialize = UserSerializer(users, many=True)
        print(serialize.data)
        datas = serialize.data
        # for  user_data in datas:
        #     user = UserInfo.objects.get(pk=user_data['id'])
        #     print(type(user_data))
        #     print(user)
        #     roles = user.roles.all()
        #     for role in roles:
        #         print(role.rolename)
        #         user_data['role'] = role.rolename
        #         userList.append(user_data)

        return restful.result(data=datas)


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
        return restful.ok(message="成功")
    except:
        return restful.params_error(message="该目录不存在")



def delete_roles(request):
    pk = request.POST.get('role_id')
    try:
        Role.objects.filter(pk=pk).delete()
        return restful.ok(message="成功")
    except:
        return restful.params_error(message='该角色不存在')



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


class UserList(View):
    def post(self, request):
        pageNum = request.GET.get('pageIndex', 1)
        pagesize = request.GET.get('pageSize')
        user_id = request.POST.get("user_id")
        user = UserInfo.objects.get(pk=user_id)
        serialize = UserSerializer(user)
        return restful.result(data=serialize.data)


"""
返回角色信息
"""


def role_info(request):
    role_id = request.POST.get('role_id')
    if role_id:
        role = Role.objects.get(pk=role_id)
        serialize = RoleSerializer(role)
        return restful.result(data=serialize.data)
    else:
        return restful.params_error(message="角色id不存在")


"""
角色修改
"""


class EditRole(View):
    def post(self, request):
        role_id = request.POST.get("role_id")
        role_name = request.POST.get("role_name")
        description = request.POST.get('description')
        print(role_id,role_name,description)
        if role_name:
            Role.objects.filter(pk=role_id).update(rolename=role_name,description=description)
        else:
            return restful.params_error(message="角色名称不能为空")
        return restful.ok(message="角色修改成功")


class EditUsers(View):
    def post(self, request):
        form = EditUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            phone_number = form.cleaned_data.get("phone_number")
            password = form.cleaned_data.get("password")
            email = form.cleaned_data.get("email")
            status = form.cleaned_data.get("status")
            roles = form.cleaned_data.get("roles")
            pk = form.cleaned_data.get("id")
            UserInfo.objects.filter(pk=pk).update(username=username, phone_number=phone_number, password=password
                                                  , email=email, status=status, roles=roles)
            return restful.ok(message="成功")
        else:
            return restful.params_error(form.get_errors())


"""
修改账户密码
"""


class UpdatePassword(View):
    def post(self, request):
        try:
            user_id = request.POST.get("user_id")
            old_password = request.POST.get("old_password")
            if old_password:
                user_obj = UserInfo.objects.get(pk=user_id)
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
        roleids = user.roles
        permission_list = []
        for role in roleids:
            role_obj = RoleMenu.objects.filter(role=role.id)
            for menu in role_obj:
                new_menu = NewMenu.objects.filter(pk=menu.menu)

        return restful.result(data="")


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
    def post(self, request):
        try:
            print("sdf")
            # new_menu = []
            # menu_list =list(request.POST.getlist("menu_list"))   # 获取菜单id list
            # print(menu_list)
            # print(type(menu_list))
            # for menu in menu_list:
            #     print(type(list(menu)))
            #     for m in menu:
            #         print(m)
            # print(type(menu_list),menu_list)
            menu_list = [2, 4]

            # for i in menu_list:
            #     print(i)
            #     if i =='':
            #        print("sdfasdf")
            #        menu_list.remove(' ')
            #
            #     # new_menu.append(i)
            # print(menu_list)

            role_id = request.POST.get("role_id")  # 获取角色id
            # role = Role.objects.get(pk=role_id)
            # print("")
            role_obj = RoleMenu.objects.filter(role_id=role_id)

            if role_obj:
                old_menu = []
                for obj in role_obj:
                    old_menu.append(obj.menu_id)
                adds = list(set(menu_list).difference(set(old_menu)))
                dele_list = list(set(old_menu).difference(set(menu_list)))
                for i in adds:
                    RoleMenu.objects.create(role_id=role_id, menu_id=i)
                for j in dele_list:
                    RoleMenu.objects.filter(Q(role_id=role_id) & Q(menu_id=j)).delete()
            else:
                for menu in menu_list:
                    RoleMenu.objects.create(role_id=role_id, menu_id=menu)
        except Exception as e:
            return restful.params_error("分配权限失败", data=e)

        return restful.ok(message="成功")


def menu_permission(request):
    menus = {}
    try:
        menu_data = NewMenu.objects.filter(parentid__isnull=True)
        for obj in menu_data:
            mu_data = NewMenu.objects.filter(parentid=obj.id).order_by('orderNum')
            menus[obj.name] = NewmenuSerializer(mu_data, many=True).data
            for objs in mu_data:
                try:
                    m_data = NewMenu.objects.filter(parentid=objs.id).order_by('orderNum')
                    menus[obj.name][objs.name] = NewmenuSerializer(m_data, many=True).data
                except:
                    continue

        return restful.result(data=menus)

    except Exception as e:
        return restful.params_error(message=u"获取菜单失败")


def get_all_menus(request):
    menu_list = []
    permission_list = []
    try:
        menu_data = NewMenu.objects.filter(parentid__isnull=True)
        permissions = NewMenu.objects.all().values().order_by('orderNum')
        for permission in permissions:
            permission_list.append(permission['perms'])
        n = 0
        for i in menu_data:
            data1 = NewmenuSerializer(i).data
            menu_list.append(data1)
            menu_list[n]['list'] = list()
            i_data = NewMenu.objects.filter(parentid=i.id)
            m = 0
            for j in i_data:
                data2 = NewmenuSerializer(j).data
                menu_list[n]['list'].append(data2)
                menu_list[n]['list'][m]['list'] = list()
                j_data = NewMenu.objects.filter(parentid=j.id)
                r = 0
                for k in j_data:
                    data3 = NewmenuSerializer(k).data
                    menu_list[n]['list'][m]['list'].append(data3)
                    menu_list[n]['list'][m]['list'][r]['list'] = list()
                    # menu_list[n]['list'][m]['list'] = list()
                    r += 1
                m += 1
            n = n + 1
        print(menu_list)
        context = {
            "menuList": menu_list,
            'permission': permission_list
        }

        return restful.result(data=context)
    except:
        return restful.params_error(message=u"获取菜单失败")


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
