from django.shortcuts import render, redirect
from .models import UserInfo, Role, Permission
from django.views.generic import View
from utils import restful
from django.core.paginator import Paginator
from urllib import parse
from .forms import UserInfoModelForm, UserInfoAddModelForm, RoleModelForm, EditUserForm,LoginForm
from django.conf import settings
from django.contrib.sessions.models import Session
from .models import NewMenu, RoleMenu
from .serializers import  UserSerializer, RoleSerializer, NewmenuSerializer
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from rest_framework import generics
from utils.mixin import LoginRequireMixin
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.views import APIView
import json,re
import traceback
from utils import RsaUtil
from django_redis import get_redis_connection


# Create your views here.

# 用户登录装饰器
def is_login(func):
    def wrapper(request, *args, **kwargs):
        try:
            sessionid = request.META.get("HTTP_SESSIONID")
            session_data = Session.objects.get(session_key=sessionid)
            is_login = session_data.get_decoded().get('is_login')
            if is_login is True:
                res = func(request, *args, **kwargs)
                return res
            else:
                return restful.server_error(message="session失效，请重新登录！")
        except:
            return restful.unauth(message="session失效，请重新登录！")
    return wrapper

"""
生成公钥返回给前端
"""
def setKey(request):
    RsaUtil.create_keys()
    conn = get_redis_connection()
    public_key = conn.get('pubkey').decode('utf-8')
    context = {
        'publicKey':public_key
    }
    return restful.result(data=context)


@csrf_exempt
def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if username is None:
        return restful.params_error(message="用户名不能为空")
    if password is None:
        return restful.params_error(message="密码不能为空")
    # hl = hashlib.md5()
    # hl.update(password.encode(encoding='utf-8'))
    # password = hl.hexdigest()
    # print(password)
    user_obj = UserInfo.objects.filter(username=username, password=password).first()

    if not user_obj:
        return restful.params_error(message="用户名或密码错误,请重新登录")
    elif user_obj.status == 0:
        return restful.params_error(message="用户已被禁用")
    # 确认用户是否又权限登录
    role = user_obj.roles.all()
    if role:
        request.session.clear()
        request.session['is_login'] = True
        request.session['user_id'] = user_obj.id
        user_id = request.session['user_id']
        request.session.set_expiry(600)
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
            'sessionid': session_id,

        }
        return restful.result(data=context)
    else:
        return restful.unauth(message="该用户没有权限！")



def logout(request):
    request.session.clear()
    return restful.ok(message="成功")
    # return redirect('../../login/')


""""
添加角色
"""

class AddRoles(LoginRequireMixin,generics.CreateAPIView):
    serializer_class = RoleSerializer

    def post(self, request):
        try:
            rolename = request.POST.get("rolename")
            role = Role.objects.filter(rolename=rolename)
            if role:
                return restful.params_error(message="角色已存在，请重新输入")
            description = request.POST.get("description")
            Role.objects.create(rolename=rolename, description=description)
            return restful.ok(message="成功")

        except Exception as e:
            traceback.print_exc()
            print(e)


"""
添加用户
"""
class AddUsers(LoginRequireMixin,generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        try:
            username = request.POST.get("username")
            email = request.POST.get("email")
            phone_number = request.POST.get("phone_number")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            status = request.POST.get("status")
            roles = request.POST.get("roles")

            # 验证数据库中用户是否存在
            user_info = UserInfo.objects.filter(username=username)
            if user_info:
                return restful.params_error(message="该用户名已经存在,请换个名字!")
            # 验证数据库是否存在phone
            user_phone = UserInfo.objects.filter(phone_number=phone_number)
            if user_phone:
                return restful.params_error(message="该手机号已被注册")
            elif len(phone_number) != 11:
                return restful.params_error(message="手机号长度不是11位，请重新输入！")

            pattern = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
            if re.search(pattern, email) is None:
                return restful.params_error(message='邮箱格式错误!')
            # 密码验证
            if password.isdecimal() or password.isalpha():
                return restful.params_error('密码为数字加字母')
            elif len(password) < 6:
                return restful.params_error(message="密码长度需大于6位")

            # 密码跟确认密码验证
            if password != confirm_password:
                return restful.params_error(message="两次密码输入不一致!")

            # 保存用户信息到userinfo表中
            UserInfo.objects.create(username=username,password=password,email=email,
                                    phone_number=phone_number,status=status)
            # 查询数据库userinfo信息
            user = UserInfo.objects.get(Q(username=username) & Q(phone_number=phone_number))
            user.roles.add(roles)
            return restful.ok(message="成功")
        except Exception as e:
            traceback.print_exc()
            print(e)


"""
删除用户
"""
@is_login
def delete_users(request):
    pk = request.POST.get('user_id')
    try:
        if pk:
            UserInfo.objects.filter(pk=pk).delete()
            return restful.ok(message="成功")
        else:
            return restful.params_error(message="user_id为空")
    except Exception as e:
        return restful.params_error(message=e)


"""
角色列表
@:Method Get 
@:param username
@:param status
@:param  pageIndex
@:param pageSize 
"""
class RoleList(LoginRequireMixin,View):
    def get(self, request):
        try:
            roleList = []
            pageIndex = request.GET.get('pegeIndex', 1)
            pageSize = request.GET.get("pageSize", 20)
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
            paginator = Paginator(roleList,pageSize)
            page_obj = paginator.page(int(pageIndex))
            print(page_obj)
            totalCount = roles.count()
            numPerPage = len(page_obj.object_list)
            totalPageNum = paginator.num_pages
            context = {
                'numPerPage': numPerPage,
                'PageNum': int(pageSize),
                'result': page_obj.object_list,
                'totalCount': totalCount,
                'totalPageNum': totalPageNum,

            }
        except Exception:
            return restful.params_error(message="获取角色列表失败")
        return restful.result(data=context)


"""
获取所有用户
"""

class getAllUsers(LoginRequireMixin,APIView):
    def get(self, request,*args,**kwargs):
        try:
            username = request.GET.get('username')
            status = request.GET.get('status')
            pageIndex = request.GET.get('pegeIndex',1)
            pageSize = request.GET.get("pageSize",20)
            if username:
                users_list = UserInfo.objects.filter(username__icontains=username)
            elif status:
                users_list = UserInfo.objects.filter(status=status)
            else:
                users_list = UserInfo.objects.all()
            # 根据url参数 获取分页数据
            pg = StandardResultSetPagination()
            paginator = Paginator(users_list, pageSize)
            page_obj = paginator.page(int(pageIndex))
            numPerPage = len(page_obj.object_list)
            totalCount = users_list.count()
            totalPageNum = paginator.num_pages
            context = {
                'numPerPage': numPerPage,
                'PageNum': pageSize,
                'result': UserSerializer(page_obj.object_list,many=True).data ,
                'totalCount': totalCount,
                'totalPageNum': totalPageNum,
                # 'token':token
            }
        except Exception:
            return restful.params_error(message="获取用户列表信息错误")
        # return restful.result(data=context)
        return restful.result(data=context)




""" 
删除角色
"""
@is_login
def delete_roles(request):
    pk = request.POST.get('id')
    try:
        if pk:
            users = UserInfo.objects.all()
            for user in users:
                user_roles = user.roles.all()
                for usr_role in user_roles:
                    if int(pk) == usr_role.id:
                        return restful.params_error(message="该角色已被用户关联，不能删除！")
                    # else:
            Role.objects.filter(pk=pk).delete()
            return restful.ok(message="成功")
        else:
            return restful.params_error(message="role_id is null")
    except Exception as e:
        print(e)
        return restful.params_error(message='该角色不存在')



"""
角色修改
"""

class EditRole(LoginRequireMixin,View):
    def post(self, request):
        role_id = request.POST.get("id")
        role_name = request.POST.get("rolename")
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



def edit_users(request):
    """
    编辑用户
    """
    try:
        username = request.POST.get("username")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        status = request.POST.get("status")
        roles = request.POST.get("roles")
        pk = request.POST.get("user_id")
        if pk:
            user = UserInfo.objects.filter(pk=pk)
            if user:
                if len(phone_number) != 11:
                    return restful.params_error(message="手机号长度不是11位，请重新输入")
                pattern = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
                if re.search(pattern, email) is None:
                    return restful.params_error(message='邮箱格式错误!')
                user_obj = UserInfo.objects.get(pk=pk)
                UserInfo.objects.filter(pk=pk).update(username=username, phone_number=phone_number
                                                      , email=email, status=status)
                user_obj.roles.clear()
                try:
                    user_obj.roles.add(roles)
                except Exception as e:
                    print(e)
            else:
                return restful.params_error(message="user_id is invalid")
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
            print(user_id)
            old_password = request.POST.get("old_password")
            new_password = request.POST.get('password')
            if user_id:
                user = UserInfo.objects.filter(pk=user_id)
                if user:
                    if old_password:
                        user_obj = UserInfo.objects.get(pk=user_id)
                        password1 = user_obj.password
                        if password1 != old_password:
                            return restful.params_error(message="原始密码输入错误")
                    if new_password:
                        if new_password.isdecimal() or new_password.isalpha():
                            return restful.params_error(message='密码为数字加字母')
                        elif len(new_password) < 6:
                            return restful.params_error(message='密码长度需大于6位')
                        else:
                            UserInfo.objects.filter(pk=user_id).update(password=new_password)
                else:
                    return restful.params_error(message="user_id id invalid")
            else:
                return restful.params_error(message="user_id is null")
        except Exception as e:
            print(e)
            return restful.params_error(message="密码修改失败")
        return restful.ok(message="账户密码修改成功")



class AllotPermissson(LoginRequireMixin,View):
    """
    分配权限
    当角色没有权限点时添加权限
    当角色有权限点时修改权限
    """
    def post(self, request):
        try:
            data = request.body.decode("utf-8")
            menu_data = json.loads(data)
            role_id = menu_data.get("role_id")
            if role_id:
                menu_list = menu_data.get("menu_list")
                role_obj = RoleMenu.objects.filter(role_id=role_id)
                if role_obj:
                    old_menu = []
                    for obj in role_obj:
                        old_menu.append(obj.menu_id)
                    add_list = list(set(menu_list).difference(set(old_menu)))
                    dele_list = list(set(old_menu).difference(set(menu_list)))
                    for add_name in add_list:
                        RoleMenu.objects.create(role_id=role_id, menu_id=add_name)
                    for dele_name in dele_list:
                        RoleMenu.objects.filter(Q(role_id=role_id) & Q(menu_id=dele_name)).delete()
                else:
                    for menu in menu_list:
                        RoleMenu.objects.create(role_id=role_id, menu_id=menu)
            else:
                return restful.params_error(message="角色id不能为空")
        except Exception as e:
            return restful.params_error("分配权限失败")
        return restful.ok(message="成功")





"""
根据用户角色获取
"""

class getAllMenus(LoginRequireMixin,generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        try:
            sessionid = request.META.get("HTTP_SESSIONID")
            session_data = Session.objects.get(session_key = sessionid)
            user_id = session_data.get_decoded().get('user_id')
            datas_list = []           # 菜单详情关系 list
            menu_list = []            # 菜单id list
            permission_list = []      # 权限码list
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
                                    m += 1
                            n += 1
                    context = {
                        'menuList': datas_list,
                        'mnues': menu_list,
                        'permissions': permission_list,

                    }
                else:
                    return restful.params_error(message="权限为空")
            else:
                return restful.params_error(message="user_id is null")
        except Exception as e:
            return restful.params_error(message="获取权限菜单失败")
        return restful.result(data=context)


class SelectMenu(LoginRequireMixin,View):
    """
    获取所有的菜单信息
    """
    def get(self, request):
        try:
            menu_list = NewMenu.objects.all()
            serialize = NewmenuSerializer(menu_list, many=True)
            return restful.result(data=serialize.data)
        except:
            return restful.params_error(message="获取菜单详情失败")



def get_pagination_data(paginator, page_obj, around_count=2):
    """
    分页函数
    """
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
    default_limit = 20
    #url 中传入的显示数据条数的参数
    limit_query_param = 'pageSize'
    #url中传入的数据位置的参数
    offset_query_param = 'pegeIndex'
    #最大每页显示条数
    max_limit = None