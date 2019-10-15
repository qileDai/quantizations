#encoding: utf-8
from rest_framework import serializers
from .forms import Account,TradingPlatform,Robot

class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradingPlatform
        fields = ('id','Platform_name')

class AccountSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer()
    class Meta:
        model = Account
        fields = ('id','title','accesskey','secretkey','users_id','platform')

class RobotSerializer(serializers.ModelSerializer):
    trading_account = AccountSerializer()
    class Meta:
        model = Robot
        fields = ('id','trading_account','currency','market','trading_strategy','total_money','float_profit'
                  ,'realized_profit','total_profit','annual_yield','create_time','status','protection',
                 'current_price','orders_frequency','resistance','support_level', 'girding_num','procudere_fee'
                  ,'min_num','max_num','girding_profit','stop_price','warning_price','warning_account','run_status')






