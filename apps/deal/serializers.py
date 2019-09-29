#encoding: utf-8
from rest_framework import serializers
from .forms import Account,TradingPlatform

class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradingPlatform
        fields = ('id','Platform_name')

class AccountSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer()
    class Meta:
        model = Account
        fields = ('id','title','accesskey','secretkey','users_id','platform')






