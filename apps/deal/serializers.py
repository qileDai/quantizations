#encoding: utf-8
from rest_framework import serializers



class UserSerializer(serializers.Serializer):
    platform = serializers.CharField(max_length=32)
    asset_change = serializers.CharField(max_length=32)
    original_total = serializers.DecimalField(max_digits=19,decimal_places=2)
    history_profit = serializers.DecimalField(max_digits=19,decimal_places=2)
    withdraw_record = serializers.DecimalField(max_digits=19,decimal_places=2)



