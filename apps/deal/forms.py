import re
from django.forms import ModelForm
from apps.deal.models import Account, TradingPlatform, Property
from django.forms import fields
from django.core.exceptions import ValidationError


class AccountModelForm(ModelForm):

    class Meta:
        model = Account
        fields = ['users', 'platform', 'title', 'accesskey', 'secretkey']
        labels = {
            'users': '用户',
            'platform': '平台',
            'title': '账户名',
            'accesskey': 'Access Key',
            'secretkey': 'Secret Key'
        }

    # 在类中定义 clean_字段名() 方法，就能够实现对特定字段进行校验。
    def clean_title(self):
        title = self.cleaned_data.get('title')
        user_obj = Account.objects.filter(title=title).first()
        if user_obj:
            raise ValidationError('该平台名已经存在,请重新输入!')  # 验证名字是否存在
        else:
            return title
