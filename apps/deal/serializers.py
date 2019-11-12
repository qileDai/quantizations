from rest_framework import serializers
from .forms import Account, TradingPlatform, Robot
from .models import OrderInfo, Property, LastdayAssets, Currency


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        """
        在super执行之前将传递的'fields'中的字段从kwargs取出并剔除，避免其传递给基类ModelSerializer
        注意此处'fields'中在默认'self.fields'属性中不存在的字段将无法被序列化,
        也就是'fields'中的字段应该是'self.fields'的子集
        :param args:
        :param kwargs:
        """
        fields = kwargs.pop('fields', None)
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            # 从默认'self.fields'属性中剔除非'fields'中指定的字段
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class PlatformSerializer(serializers.ModelSerializer):

    class Meta:
        model = TradingPlatform
        fields = ('id', 'Platform_name')


# class AccountSerializer(serializers.ModelSerializer):
#     platform = PlatformSerializer()
#     createtime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
#
#     class Meta:
#         model = Account
#         fields = ('id', 'title', 'accesskey', 'secretkey', 'users_id', 'createtime', 'platform')
#         extra_kwargs = {
#             'id': {
#                 'required': True,
#                 'help_text': 'ID'
#             },
#             'title': {
#                 'required': True,
#                 'help_text': '账户名称'
#             },
#             'accesskey': {
#                 'required': True,
#                 'help_text': '平台对应的accesskey'
#             },
#             'secretkey': {
#                 'required': True,
#                 'help_text': '平台对应的secretkey'
#             },
#             'platform': {
#                 'required': True,
#                 'help_text': '选择的平台名称'
#             },
#         }
class AccountSerializer(DynamicFieldsModelSerializer):
    """
     此处的'fields'字段是用来替换上面Serializer内部Meta类中指定的`'fields'属性值
    """
    # 序列化外键
    platform_name = serializers.CharField(source='platform.Platform_name')
    platform_id = serializers.IntegerField()
    createtime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Account
        fields = ('id', 'title', 'accesskey', 'secretkey', 'users_id', 'createtime', 'platform_name', 'platform_id')


class RobotSerializer(DynamicFieldsModelSerializer):
    # 序列化外键
    # account = AccountSerializer()
    account_title = serializers.CharField(source='trading_account.title')
    account_id = serializers.IntegerField(source='trading_account.id')
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Robot
        fields = '__all__'


class OrderInfoSerializer(serializers.ModelSerializer):
    # robot_id = serializers.IntegerField(source='robot.id')
    closing_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = OrderInfo
        # fields = ('id', 'order_type', 'closing_price', 'total_price', 'closing_time', 'robot', 'currency_pair',)
        fields = '__all__'


class PropertySerializer(DynamicFieldsModelSerializer):
    # 序列化外键
    account_name = serializers.CharField(source='account.title')
    account_id = serializers.IntegerField()
    updatetime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Property
        fields = '__all__'


class LastdayAssetsSerializer(serializers.ModelSerializer):
    account = AccountSerializer()

    class Meta:
        model = LastdayAssets
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Currency
        fields = '__all__'











