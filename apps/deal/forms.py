import re
from django import forms
from apps.deal.models import Account, TradingPlatform, Property,Robot
from django.forms import fields
from django.core.exceptions import ValidationError
from utils.forms import FormMixin


class AccountModelForm(forms.ModelForm,FormMixin):
    platform = forms.IntegerField()
    class Meta:
        model = Account
        fields = ['users', 'title', 'accesskey', 'secretkey']
        labels = {
            "title":"账户名称"
        }

    # 在类中定义 clean_字段名() 方法，就能够实现对特定字段进行校验。
    def clean_title(self):
        title = self.cleaned_data.get('title')
        user_obj = Account.objects.filter(title=title).first()
        if user_obj:
            raise ValidationError('该平台名已经存在,请重新输入!')  # 验证名字是否存在
        else:
            return title


class RobotFrom(forms.ModelForm):

    class Meta:
        model = Robot
        fields = '__all__'



