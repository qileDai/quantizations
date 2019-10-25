import hashlib
import re
from django.forms import ModelForm
from .models import UserInfo, Role, Permission, Menu
from django.forms import fields
from django.core.exceptions import ValidationError
from utils.forms import FormMixin
from django import forms


class UserInfoModelForm(forms.ModelForm, FormMixin):
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


class UserInfoAddModelForm(ModelForm):

    confirm_password = fields.CharField(label="确认密码", max_length=64)

    class Meta:
        model = UserInfo  # 对应模型类
        fields = ['username', 'password', 'confirm_password', 'phone_number', 'email', 'roles', 'status']  # 所有字段
        labels = {
            'username': '用户名',
            'password': '密码',
            'confirm_password': '确认密码',
            'phone_number': '手机号',
            # 'nickname': '昵称',
            'email': '邮箱',
            'roles': '角色',
        }

    # 在类中定义 clean_字段名() 方法，就能够实现对特定字段进行校验。
    def clean_username(self):
        username = self.cleaned_data.get('username')
        user_obj = UserInfo.objects.filter(username=username).first()
        if user_obj:
            raise ValidationError('该用户名已经存在,请换个名字!')  # 验证名字是否存在
        else:
            return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        user_obj = UserInfo.objects.filter(phone_number=phone_number).first()
        if phone_number is None:
            raise ValidationError('手机号不能为空')
        elif user_obj:
            raise ValidationError('该手机号已被注册')
        elif len(phone_number) != 11:
            raise ValidationError('手机号长度不是11位，请重新输入')
        else:
            return phone_number

    def clean_password(self):
        password = self.cleaned_data.get('password')  # 验证密码合法性
        # 这里用isdecimal，建议别用isdigit，不准确
        if password.isdecimal() or password.isalpha():
            raise ValidationError('密码为数字加字母')
        elif len(password) < 6:
            print(password)
            raise ValidationError('密码长度需大于6位')
        else:
            hl = hashlib.md5()
            hl.update(password.encode(encoding='utf-8'))
            self.cleaned_data["password"] = hl.hexdigest()
            return password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        pattern = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
        if re.search(pattern, email):
            return email
        else:
            raise ValidationError('邮箱格式错误!')  # 指定的邮箱格式

    # 在类中定义 clean_字段名() 方法，就能够实现对特定字段进行校验。
    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data["confirm_password"]
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError("两次密码输入不一致")
            return confirm_password  # 验证完成一定要返回，才能添加到 cleaned_data 字典中. 其他地方才能通过cleaned_data获取到

    # 在类中定义 clean() 方法，就能够实现对字段进行全局校验，字段全部验证完，局部钩子也全部执行完之后，执行这个全局钩子校验。
    # def clean(self):
    #     """密码加密"""
    #     password = self.cleaned_data.get("password")
    #     hl = hashlib.md5()
    #     hl.update(password.encode(encoding='utf-8'))
    #     self.cleaned_data["password"] = hl.hexdigest()
    #     print(self.cleaned_data, self.cleaned_data["password"])
    #     return self.cleaned_data    # 全局钩子要返回所有的数据


class RoleModelForm(forms.ModelForm, FormMixin):
    # 设置非必填字段
    # permissions = forms.CharField(required=False)

    class Meta:
        model = Role
        fields = ('rolename','description')



class PermissionModelForm(forms.ModelForm, FormMixin):
    menu = forms.IntegerField()

    class Meta:
        model = Permission
        fields = ('title', 'url')


class MenuModelForm(ModelForm, FormMixin):
    class Meta:
        model = Menu
        fields = '__all__'
        labels = {
            'title': '菜单',
            'parent': '父级菜单',
        }

class EditUserForm(forms.ModelForm,FormMixin):
    pk = forms.IntegerField()
    class Meta:
        model = UserInfo
        fields = ('username', 'phone_number', 'email', 'roles', 'status')

# class EditRoleForm(forms)
