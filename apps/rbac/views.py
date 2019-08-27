from django.shortcuts import render,redirect,reverse,HttpResponse
from .models import UserInfo,Role,Menu,Permission
from apps.rbac.service.init_session import init_permission
from django.views.generic import View
from utils import restful
from django.core.paginator import Paginator
from urllib import parse
from django.db import connection
from .forms import UserInfoModelForm, RoleModelForm, PermissionModelForm

# Create your views here.

def login(request):
    if request.method == "GET":
        return render(request,"login.html")
    else:
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_obj = UserInfo.objects.filter(username=username,password=password).first()
        if not user_obj:
            return render(request,"cms/login.html",{"error","用户名或密码错误！"})
        else:
            init_permission(request,user_obj)
            return redirect('/index')

def logout(request):
    return render(request,'cms/login.html')

def index(request):
    return render(request,'cms/index.html')



def account(request):
    roles = Role.objects.all()
    users = UserInfo.objects.all()
    context = {
        'users': users,
        'roles':roles
    }
    return render(request,'cms/account.html',context=context)

def menu(request):
    menus = Menu.objects.all()
    context = {
        'menus':menus
    }
    return render(request,'cms/menu.html',context=context)

def permission(request):
    menus = Menu.objects.all()
    permissions = Permission.objects.all()
    context = {
        'menus':menus,
        'permissions':permissions
    }
    return render(request,'cms/permission.html',context=context)

def role(request):
    roles = Role.objects.all()
    permissions = Permission.objects.all()
    # print(permissions)
    context = {
        'roles':roles,
        'permissions':permissions
    }
    return render(request,'cms/role.html',context=context)


def users_list(request):
   users =UserInfo.objects.all()
   context = {
      'users':users
   }
   return render(request,'cms/account.html',context=context)

def roles(request):
    roles = Role.objects.all()
    permissions = Permission.objects.all()
    context = {
        'roles':roles,
        'permissions': permissions
    }
    return render(request,'cms/role.html',context=context)


def add_roles(request):
    form = RoleModelForm(request.POST)
    print('daiqile')
    if form.is_valid():
        form.save()
        # rolename = form.cleaned_data.get('rolename')
        # permission_id = form.cleaned_data.get('permission')
        # print(rolename,permission_id)
        # permission = Permission.objects.get(pk=permission_id)
        # # print(permission)
        # Role.objects.create(rolename=rolename, permission=permission)
        return restful.ok()
    else:
        return restful.params_error(message=form.get_errors())

def add_users(request):
    form = UserInfoModelForm(request.POST)
    print("afadf")
    if form.is_valid():
        print("sdaf")
        form.save()
        # username = form.cleaned_data.get('username')
        # password = form.cleaned_data.get('password')
        # email = form.cleaned_data.get('email')
        # role_id = form.cleaned_data.get('role')
        # role = Role.objects.get(pk=role_id)
        # UserInfo.objects.create(username=username,password=password,email=email)
        # user_id = UserInfo.objects.get()
        # cursor = connection.cursor()
        # cursor.execute('insert userinfo_role values(' + role + ')')
        return restful.ok()
    else:
        return restful.params_error(message=form.get_errors())

def delete_users(request):
    pk = request.POST.get('pk')
    print(pk)
    try:
        UserInfo.objects.filter(pk=pk).delete()
        return restful.ok()
    except:
        return restful.params_error(message="该用户不存在")

class RolesListView(View):
    def get(self, request):
        # request.GET：获取出来的所有数据，都是字符串类型
        page = int(request.GET.get('p', 1))
        rolename = request.GET.get('rolename-seach')
        roles = Role.objects.all()
        print(rolename)
        # request.GET.get(参数,默认值)
        # 这个默认值是只有这个参数没有传递的时候才会使用
        # 如果传递了，但是是一个空的字符串，那么也不会使用默认值
        if rolename:
            roles = Role.filter(rolename__icontains=rolename)
        paginator = Paginator(roles, 10)
        page_obj = paginator.page(page)

        context_data = self.get_pagination_data(paginator, page_obj)
        context = {
            'roles': page_obj.object_list,
            'page_obj': page_obj,
            'paginator': paginator,
            'url_query': '&' + parse.urlencode({
                'rolename': rolename or '',
            })
        }
        context.update(context_data)

        return render(request, 'cms/role.html', context=context)

    def get_pagination_data(self, paginator, page_obj, around_count=2):
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

def delete_roles(request):
    pk = request.POST.get('pk')
    try:
        Role.objects.filter(pk=pk).delete()
        return restful.ok()
    except:
        return restful.params_error(message='该角色不存在')

def add_permission(request):
    form = PermissionModelForm(request.POST)
    print('daiqoe')
    if form.is_valid():
        title = form.cleaned_data.get('title')
        url = form.cleaned_data.get('url')
        menu_id = form.cleaned_data.get('menu')
        menu = Menu.objects.get(pk=menu_id)
        Permission.objects.create(title=title,url=url,menu=menu)
        return restful.ok()
    else:
        return restful.params_error(form.get_errors())






















