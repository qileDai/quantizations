from rest_framework import serializers
from .forms import Account, TradingPlatform, Robot
from .models import OrderInfo


class PlatformSerializer(serializers.ModelSerializer):

    class Meta:
        model = TradingPlatform
        fields = ('id', 'Platform_name')


class AccountSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer()

    class Meta:
        model = Account
        fields = ('id', 'title', 'accesskey', 'secretkey', 'users_id', 'platform')
        extra_kwargs = {
            'title': {
                'required': True,
                'help_text': '账户名称'
            },
            'accesskey': {
                'required': True,
                'help_text': '平台对应的accesskey'
            },
            'secretkey': {
                'required': True,
                'help_text': '平台对应的secretkey'
            },
            'platform': {
                'required': True,
                'help_text': '选择的平台名称'
            },
        }


class RobotSerializer(serializers.ModelSerializer):
    trading_account = AccountSerializer()

    class Meta:
        model = Robot
        fields = '__all__'


class OrderInfoSerializer(serializers.ModelSerializer):
    robot = RobotSerializer()

    class Meta:
        model = OrderInfo
        fields = ('id', 'order_type', 'closing_price', 'total_price', 'closing_time', 'robot', 'currency_pair', 'order_id')





