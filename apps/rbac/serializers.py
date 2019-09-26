#encoding: utf-8
from rest_framework import serializers
from .models import Role,UserInfo,Menu,Permission

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id','Rolenmae','permission')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ('id','title','accesskey','secretkey','users_id','platform')

class PermissonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id')



