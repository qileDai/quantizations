import re
from django import forms
from apps.deal.models import Account, TradingPlatform, Property,Robot
from django.forms import fields
from django.core.exceptions import ValidationError
from utils.forms import FormMixin


class AccountModelForm(forms.ModelForm, FormMixin):

    class Meta:
        model = Account
        fields = ['users', 'platform', 'title', 'accesskey', 'secretkey']
        labels = {
            "title": "账户名称",
        }

    # 在类中定义 clean_字段名() 方法，就能够实现对特定字段进行校验。
    def clean_title(self):
        title = self.cleaned_data.get('title')
        user_obj = Account.objects.filter(title=title).first()
        if user_obj:
            raise ValidationError('该平台名已经存在,请重新输入!')  # 验证名字是否存在
        else:
            return title


class EditAccountFrom(forms.ModelForm,FormMixin):
    pk = forms.IntegerField()
    platform = forms.IntegerField()

    class Meta:
        model = Account
        fields = ('users', 'title', 'accesskey', 'secretkey')


class RobotFrom(forms.ModelForm,FormMixin):

    class Meta:
        model = Robot
        fields = ['trading_account','currency','market','trading_strategy','total_money','float_profit','realized_profit','total_profit',
                  'annual_yield','protection','status','current_price','orders_frequency','resistance','support_level',
                  'girding_num','procudere_fee','min_num','max_num','girding_profit','stop_price','warning_price','warning_account','run_status']

    # def clean_resistance(self):
    #     resistance = self.cleaned_data.get('resistance')
    #     print(resistance)
    #     last = self.cleaned_data.get('current_price')
    #     if float(resistance) < float(last):
    #         raise ValidationError('阻力位不能低于当前价,请重新输入!')
    #     else:
    #         return resistance
    #     stop_price = self.cleaned_data.get('stop_price')
    #     if stop_price == '':
    #         raise ValidationError('止损价不能为空!')
    #     warning_price = self.cleaned_data.get('warning_price')
    #     if warning_price == '':
    #         raise ValidationError('预警价不能为空!')
    #
    # def clean_support_level(self):
    #     support_level = self.cleaned_data.get('support_level')
    #     last = self.cleaned_data.get('current_price')
    #     if float(support_level) > float(last):
    #         raise ValidationError('支撑位不能高于当前价,请重新输入!')
    #     else:
    #         return support_level

