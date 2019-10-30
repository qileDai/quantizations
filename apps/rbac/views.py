from django.shortcuts import render, redirect
from .models import UserInfo, Role, Permission
from django.views.generic import View
from utils import restful
from django.core.paginator import Paginator
from urllib import parse
from .forms import UserInfoModelForm, UserInfoAddModelForm, RoleModelForm, EditUserForm,LoginForm
from django.conf import settings
from utils.mixin import LoginRequireMixin
from django.contrib.sessions.models import Session
from .models import NewMenu, RoleMenu
from .serializers import  UserSerializer, RoleSerializer, NewmenuSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from .token_module import get_token, out_token
from django.contrib.auth import login,logout,authenticate
from django.db.models import Q
from rest_framework import generics
from utils.mixin import LoginRequireMixin
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.views import APIView
import json
import django


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



class Login(generics.CreateAPIView):
    def post(self, request):
        form = LoginForm(request.Post)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember = form.cleaned_data.get('remember')
            user = authenticate(request,username=username,password=password)
            pass




@csrf_exempt
def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if username == '':
        return restful.params_error(message="用户名不能为空")
    if password == '':
        return restful.params_error(message="密码不能为空")
    # hl = hashlib.md5()
    # hl.update(password.encode(encoding='utf-8'))
    # password = hl.hexdigest()
    # print(password)
    user_obj = UserInfo.objects.filter(username=username, password=password).first()
    print(user_obj)
    if not user_obj:
        return restful.params_error(message="用户名或密码错误,请重新登录")
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
        # token = Token.objects.create(user=user_id)
        # print(token)
        context = {
            'expire': 86400,
            'isCustomize': 0,
            'userId': user_id,
            'sessionid': session_id
        }
        request.session.set_expiry(600)
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


""""
添加角色
"""
@is_login
class AddRoles(generics.CreateAPIView):
    serializer_class = RoleSerializer

    def post(self, request):
        form = RoleModelForm(request.POST)
        if form.is_valid():
            rolename = form.cleaned_data.get("rolename")
            if not rolename:
                return restful.params_error(message="rolename is null")
            description = form.cleaned_data.get("description")
            Role.objects.create(rolename=rolename, description=description)
            return restful.ok()
        else:
            return restful.params_error(message=form.get_errors())



"""
添加角色
"""
@is_login
def add_roles(request):
    form = RoleModelForm(request.POST)
    if form.is_valid():
        rolename = form.cleaned_data.get("rolename")
        description = form.cleaned_data.get("description")
        Role.objects.create(rolename=rolename, description=description)
        return restful.ok(message="成功")
    else:
        return restful.params_error(message=form.get_errors())

"""
添加用户
"""
@is_login
def add_users(request):
    form = UserInfoAddModelForm(request.POST)
    if form.is_valid():
        form.save()
        return restful.ok(message="成功")
    else:
        return restful.params_error(message=form.get_errors())


"""
删除用户
"""
@is_login
def delete_users(request):
    pk = request.POST.get('user_id')
    print(pk)
    # print(pk)
    try:
        if pk:
            UserInfo.objects.filter(pk=pk).delete()
            return restful.ok(message="成功")
        else:
            return restful.params_error(message="user_id为空")
    except:
        return restful.params_error(message="该用户不存在")

"""
角色列表
@:Method Get 
@:param rolename
@:param  pageIndex
@:param pageSize 
"""
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

"""
角色列表
@:Method Get 
@:param username
@:param status
@:param  pageIndex
@:param pageSize 
"""
class userListView(generics.ListCreateAPIView):
    def get(self, request):
        pageNum = request.GET.get('pageIndex', 1)
        pagesize = request.GET.get('pageSize')
        username = request.GET.get('username')
        status = request.GET.get('status')
        paginator = Paginator(UserInfo.objects.all(),20)
        print("ss",paginator)
        users = UserInfo.objects.all()
        print("aaa",users)
        if username:
            paginator = Paginator(UserInfo.objects.filter(username=username), 20)
            users = UserInfo.objects.filter(username=username)
        elif status:
            paginator = Paginator(UserInfo.objects.filter(status=status), 20)
            users = UserInfo.objects.filter(status=status)
        elif username & status:
            paginator = Paginator(UserInfo.objects.filter(Q(status=status) & Q(username=username)), 20)
            users = UserInfo.objects.filter(Q(status=status) & Q(username=username))
        page_obj = paginator.page(int(pageNum))
        numPerPage = len(page_obj.object_list),
        totalCount = users.count(),
        totalPageNum = paginator.num_pages
        # context_data = get_pagination_data(paginator, page_obj)
        context = {
            'numPerPage': numPerPage,
            'PageNum': int(pageNum),
            'result': UserSerializer(page_obj.object_list, many=True).data,
            'totalCount': totalCount,
            'totalPageNum': totalPageNum,
        }

        return restful.result(data=context)

"""
角色列表
@:Method Get 
@:param username
@:param status
@:param  pageIndex
@:param pageSize 
"""
class RoleList(View):
    def get(self, request):
        try:
            roleList = []
            pageIndex = request.GET.get('pageIndex', 1)
            # print(pageIndex)
            # pageSize = request.GET.get('pageSize',20)
            # print(pageSize)
            rolename = request.GET.get('rolename')
            if rolename:
                roles = Role.objects.filter(rolename__icontains=rolename)
            else:
                roles = Role.objects.all()
            m = 0
            for role in roles:
                role_data = RoleSerializer(role).data
                roleList.append(role_data)
                roleList[m]['menuIdList'] = list()
                menus = RoleMenu.objects.filter(role=role.id)
                n= 0
                for menu in menus:
                    roleList[m]['menuIdList'].append(menu.menu_id)
                    n += 1
                m += 1
            pg = PageNumberPagination()
            totalCount = roles.count()
            totalPageNum = int(totalCount) / int(pg.page_size)
            context = {
                'numPerPage': pageIndex,
                'PageNum': pg.page_size,
                'result': roleList,
                'totalCount': totalCount,
                'totalPageNum': ''

            }
        except Exception:
            return restful.params_error(message="获取角色列表失败")
        return restful.result(data=context)


"""
获取所有用户
"""


class getAllUsers(APIView):
    def get(self, request,*args,**kwargs):
        try:
            token = django.middleware.csrf.get_token(request)
            print(token)
            username = request.GET.get('username')
            status = request.GET.get('status')
            pageIndex = request.GET.get('pageIndex',1)
            # pageSize = request.GET.get("pageSize")
            # print(pageIndex,pageSize)
            if username:
                users_list = UserInfo.objects.filter(username__icontains=username)

            elif status:
                users_list = UserInfo.objects.filter(status=status)
            else:
                users_list = UserInfo.objects.all()
            # 根据url参数 获取分页数据
            # obj = StandardResultSetPagination()
            pg = PageNumberPagination()
            page_user_list = pg.paginate_queryset(queryset=users_list, request=request, view=self)
            print('page',page_user_list)

            # 对数据序列化 普通序列化 显示的只是数据
            ser = UserSerializer(instance=page_user_list, many=True)  # 多个many=True # instance：把对象序列化
            totalCount = users_list.count()
            totalPageNum = int(totalCount)/ int(pg.page_size)
            print(pg.page_size)
            print(totalPageNum)
            print(pg.page_size)
            context = {
                'numPerPage': pageIndex,
                'PageNum': pg.page_size,
                'result': ser.data,
                'totalCount': totalCount,
                'totalPageNum':'',
                'token':token
            }
        except Exception:
            return restful.params_error(message="获取用户列表信息错误")
        return restful.result(data=context)




"""
删除角色
"""
@is_login
def delete_roles(request):
    pk = request.POST.get('id')
    try:
        if pk:
            Role.objects.filter(pk=pk).delete()
            return restful.ok(message="成功")
        else:
            return restful.params_error(message="role_id is null")
    except:
        return restful.params_error(message='该角色不存在')



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

class EditRole(LoginRequireMixin,View):
    def post(self, request):
        role_id = request.POST.get("id")
        role_name = request.POST.get("rolename")
        print(role_name)
        description = request.POST.get('description')
        if role_name == '':
            return restful.params_error(message="角色名称不能为空")
        elif role_id == '':
            return restful.params_error(message="角色id不能为空")
        # elif role_name:
        #     obj = Role.objects.get(pk=role_id)
        #     if obj.rolename == role_name:
        #         return restful.params_error(message="角色名不能跟原角色名一样")
        else:
            Role.objects.filter(pk=role_id).update(rolename=role_name, description=description)
        return restful.ok(message="角色修改成功")


@is_login
def edit_users(request):
    """
    编辑用户
    """
    try:
        username = request.POST.get("username")
        print(username)
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        status = request.POST.get("status")
        roles = request.POST.get("roles")
        pk = request.POST.get("user_id")
        print(phone_number)
        if pk:
            user = UserInfo.objects.filter(pk=pk)
            print(user)
            if user:
                if len(phone_number) != 11:
                    return restful.params_error(message="手机号长度不是11位，请重新输入")
                # elif email:
                #     pattern = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
                #     if re.search(pattern, email):
                #         print("sfasdf")
                #         return
                #     else:
                #         raise restful.params_error(message='邮箱格式错误!')  # 指定的邮箱格式                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           else:

                user_obj = UserInfo.objects.get(pk=pk)
                UserInfo.objects.filter(pk=pk).update(username=username, phone_number=phone_number
                                                      , email=email, status=status)
                # user_obj.roles.remove()
                user_obj.roles.set(roles)
            else:
                return restful.params_error(message="user_id is Invaid")
        else:
            return restful.params_error(message="user_id is null")
    except Exception as e:
        return restful.params_error(message=e)
    return restful.ok(message="成功")


"""
修改账户密码
"""
class UpdatePasssword(LoginRequireMixin,generics.CreateAPIView):
    serializer_class = UserSerializer
    def post(self, request, *args, **kwargs):
        try:
            user_id = request.POST.get("id")
            old_password = request.POST.get("old_password")
            if user_id:
                user = UserInfo.objects.filter(pk=user_id)
                if user:
                    if old_password:
                        user_obj = UserInfo.objects.get(pk=user_id)
                        password1 = user_obj.password
                        if password1 != old_password:
                            return restful.params_error(message="原始密码输入错误")
                    new_password = request.POST.get('password')
                    print(new_password)
                    if new_password:
                        UserInfo.objects.filter(pk=user_id).update(password=new_password)
                    elif new_password.isdecimal() or new_password.isalpha():
                        return restful.params_error(message='密码为数字加字母')
                    elif len(new_password) < 6:
                        return restful.params_error(message='密码长度需大于6位')
                    else:
                        return restful.params_error(message="新密吗不能为空")
                else:
                    return restful.params_error(message="user_id id Invaid")

            else:
                return restful.params_error(message="user_id is null")
        except Exception as e:
            return restful.params_error(message=e)
        return restful.ok(message="账户密码修改成功")


"""
分配权限
当角色没有权限点时添加权限
当角色有权限点时修改权限
"""
class AllotPermissson(LoginRequireMixin,View):
    def post(self, request):
        try:
            data = request.body.decode("utf-8")
            print(data)
            menu_data = json.loads(data)
            print(menu_data)
            role_id = menu_data.get("role_id")
            print(role_id)
            if role_id:
                menu_lsit = menu_data.get("menu_list")
                role_obj = RoleMenu.objects.filter(role_id=role_id)
                if role_obj:
                    old_menu = []
                    for obj in role_obj:
                        old_menu.append(obj.menu_id)
                    add_list = list(set(menu_lsit).difference(set(old_menu)))
                    dele_list = list(set(old_menu).difference(set(menu_lsit)))
                    for add_name in add_list:
                        RoleMenu.objects.create(role_id=role_id, menu_id=add_name)
                    for dele_name in dele_list:
                        RoleMenu.objects.filter(Q(role_id=role_id) & Q(menu_id=dele_name)).delete()
                else:
                    for menu in menu_lsit:
                        RoleMenu.objects.create(role_id=role_id, menu_id=menu)
            else:
                return restful.params_error(message="角色id不能为空")
        except Exception as e:
            return restful.params_error("分配权限失败", message=e)
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

"""
获取所有的菜单级联关系

"""
def get_all_menus11(request):

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
                    # menu_list[n]['list'][m]['list'][r]['list'] = list()
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


"""
根据用户角色获取
"""

class getAllMenus(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        try:
            sessionid = request.META.get("HTTP_SESSIONID")
            session_data = Session.objects.get(session_key = sessionid)
            user_id = session_data.get_decoded().get('user_id')
            datas_list = []
            menu_list = []
            permission_list = []
            # user_id = request.session.get('user_id')
            if user_id:
                user = UserInfo.objects.get(id=user_id)
                roles = user.roles.all()
                for role in roles:
                    role_id = role.id
                menus = RoleMenu.objects.filter(role_id=role_id)
                length = len(menus)
                if length > 0:
                    for menu in menus:
                        menu_list.append(menu.menu_id)
                        perm = NewMenu.objects.get(pk=menu.menu_id)
                        permission_list.append(perm.perms)
                    menu_data = NewMenu.objects.filter(parentid__isnull=True)
                    n = 0
                    for i in menu_data:
                        if i.id in menu_list:
                            data1 = NewmenuSerializer(i).data
                            datas_list.append(data1)
                            datas_list[n]['list'] = list()
                            i_data = NewMenu.objects.filter(parentid=i.id)
                            m= 0
                            for j in i_data:
                                if j.id in menu_list:
                                    data2 = NewmenuSerializer(j).data
                                    datas_list[n]['list'].append(data2)
                                    try:
                                        datas_list[n]['list'][m]['list'] = list()
                                    except Exception as e:
                                        print(e)
                                    j_data = NewMenu.objects.filter(parentid=j.id)
                                    r = 0
                                    for k in j_data:
                                        if k.id in menu_list:
                                            data3 = NewmenuSerializer(k).data
                                            datas_list[n]['list'][m]['list'].append(data3)
                                            r += 1
                                    m +=1
                            n += 1
                    context = {
                        'menuList':datas_list,
                        'mnues':menu_list,
                        'permissions':permission_list
                    }
                else:
                    return restful.params_error(message="权限为空")
            else:
                return restful.params_error(message="user_id is null")
        except Exception as e:
            return restful.params_error(message=e)
        return restful.result(data=context)
"""
获取所有的菜单信息
"""
class SelectMenu(LoginRequireMixin,View):
    def get(self, request):
        try:
            allmenu_list = NewMenu.objects.all()
            serialize = NewmenuSerializer(allmenu_list, many=True)
            return restful.result(data=serialize.data)
        except:
            return restful.params_error(message="获取菜单详情失败")

"""
分页函数
"""
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


class ArticlePagination(PageNumberPagination):
    page_size = 20  # 表示每页的默认显示数量
    page_size_query_param = 'page_size'  # 表示url中每页数量参数
    page_query_param = 'p'  # 表示url中的页码参数
    max_page_size = 100  # 表示每页最大显示数量，做限制使用，避免突然大量的查询数据，数据库崩溃

"""
分页配置
"""
class StandardResultSetPagination(LimitOffsetPagination):
    #默认每页显示的条数
    default_limit = 10
    #url 中传入的显示数据条数的参数
    limit_query_param = 'pageSize'
    #url中传入的数据位置的参数
    offset_query_param = 'pageIndex'
    #最大每页显示条数
    max_limit = None