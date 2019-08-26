from django.shortcuts import render, redirect, reverse
from .models import UserInfo, Role, Permission, Menu
from .forms import UserInfoModelForm, UserInfoAddModelForm, RoleModelForm, PermissionModelForm, MenuModelForm
from django.conf import settings


# 用户登录装饰器
def is_login(func):
    def wrapper(request, *args, **kwargs):
        if 'ADMIN' in request.session:
            res = func(request, *args, **kwargs)
            return res
        else:
            return redirect(settings.LOGIN_URL)
    return wrapper


@is_login
def index(request):
    return render(request, 'rbac/index.html')


@is_login
def users(request):
    """查询所有用户信息"""
    user_list = UserInfo.objects.all()
    return render(request, 'rbac/users.html', {'user_list': user_list})


@is_login
def users_new(request):
    if request.method == "GET":
        # 传入ModelForm对象
        model_form = UserInfoAddModelForm()
        return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '新增用户'})
    else:
        model_form = UserInfoAddModelForm(request.POST)
        print('-------------', model_form)
        if model_form.is_valid():
            # users_obj = model_form.cleaned_data.pop("confirm_password")
            # new_user_obj = UserInfo.objects.create(**model_form.cleaned_data)
            # new_user_obj.authors.add(*users_obj)
            model_form.save()
            return redirect(reverse('rbac:users'))
        else:
            return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '新增用户'})


@is_login
def users_edit(request, id):
    user_obj = UserInfo.objects.filter(id=id).first()
    if request.method == 'GET':
        model_form = UserInfoModelForm(instance=user_obj)
        return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '编辑用户'})
    else:
        model_form = UserInfoModelForm(request.POST, instance=user_obj)
        if model_form.is_valid():
            model_form.save()
            return redirect(reverse('rbac:users'))
        else:
            return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '编辑用户'})


@is_login
def users_delete(request, id):
    user_obj = UserInfo.objects.filter(id=id).first()
    user_obj.delete()
    return redirect(reverse('rbac:users'))


@is_login
def roles(request):
    role_list = Role.objects.all()
    return render(request, 'rbac/roles.html', {'role_list': role_list})


@is_login
def roles_new(request):
    if request.method == "GET":
        # 传入ModelForm对象
        model_form = RoleModelForm()
        return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '新增角色'})
    else:
        model_form = RoleModelForm(request.POST)
        if model_form.is_valid():
            model_form.save()
            return redirect(reverse('rbac:role'))
        else:
            return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '新增角色'})


@is_login
def roles_edit(request, id):
    role_obj = Role.objects.filter(id=id).first()
    if request.method == 'GET':
        model_form = RoleModelForm(instance=role_obj)
        return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '编辑角色'})
    else:
        model_form = RoleModelForm(request.POST, instance=role_obj)
        if model_form.is_valid():
            model_form.save()
            return redirect(reverse('rbac:role'))
        else:
            return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '编辑角色'})


@is_login
def roles_delete(request, id):
    role_obj = Role.objects.filter(id=id).first()
    role_obj.delete()
    return redirect(reverse(roles))


@is_login
def permissions(request):
    permission_list = Permission.objects.all()
    return render(request, 'rbac/permissions.html', {'permission_list': permission_list})


@is_login
def permissions_new(request):
    if request.method == "GET":
        # 传入ModelForm对象
        model_form = PermissionModelForm()
        return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '新增权限'})
    else:
        model_form = PermissionModelForm(request.POST)
        if model_form.is_valid():
            model_form.save()
            return redirect(reverse(permissions))
        else:
            return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '新增权限'})


@is_login
def permissions_edit(request, id):
    permission_obj = Permission.objects.filter(id=id).first()
    if request.method == 'GET':
        model_form = PermissionModelForm(instance=permission_obj)
        return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '编辑权限'})
    else:
        model_form = PermissionModelForm(request.POST, instance=permission_obj)
        if model_form.is_valid():
            model_form.save()
            return redirect(reverse(permissions))
        else:
            return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '编辑权限'})


@is_login
def permissions_delete(request, id):
    permission_obj = Role.objects.filter(id=id).first()
    permission_obj.delete()
    return redirect(reverse(permissions))


@is_login
def menus(request):
    menu_list = Menu.objects.all()
    return render(request, 'rbac/menus.html', {'menu_list': menu_list})


@is_login
def menus_new(request):
    if request.method == "GET":
        # 传入ModelForm对象
        model_form = MenuModelForm()
        return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '新增菜单'})
    else:
        model_form = MenuModelForm(request.POST)
        if model_form.is_valid():
            model_form.save()
            return redirect(reverse(menus))
        else:
            return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '新增菜单'})


@is_login
def menus_edit(request, id):
    menu_obj = Menu.objects.filter(id=id).first()
    if request.method == 'GET':
        model_form = MenuModelForm(instance=menu_obj)
        return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '编辑菜单'})
    else:
        model_form = MenuModelForm(request.POST, instance=menu_obj)
        if model_form.is_valid():
            model_form.save()
            return redirect(reverse(menus))
        else:
            return render(request, 'rbac/common_edit.html', {'model_form': model_form, 'title': '编辑菜单'})


@is_login
def menus_delete(request, id):
    menu_obj = Role.objects.filter(id=id).first()
    menu_obj.delete()
    return redirect(reverse(menus))

