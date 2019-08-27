# _*_ coding:utf-8 _*_
from django import forms
from utils.forms import FormMixin
from .models import UserInfo,Menu,Permission,Role

class UserInfoModelForm(forms.ModelForm,FormMixin):
    # role = forms.IntegerField()
    class Meta:
        model = UserInfo
        fields = '__all__'
        # fields = ('username','password','email')
        labels = {
            'username': '用户名',
            'password': '密码',
            'email': '邮箱',
            'role': '角色',
        }




class RoleModelForm(forms.ModelForm,FormMixin):
    class Meta:
        model = Role
        fields = '__all__'
        # fields = ('username','password','email')
        labels = {
            'rolename': '角色',
            'permission': '权限',
        }


class PermissionModelForm(forms.ModelForm,FormMixin):
    menu = forms.IntegerField()
    class Meta:
        model = Permission
        fields = ('title','url')


class MenuModelForm(forms.ModelForm,FormMixin):
    menu = forms.CharField(max_length=32)
    class Meta:
        model = Menu
        fields = '__all__'
        labels = {
            'title': '菜单',
            'parent': '父级菜单',
        }


