# encoding: utf-8
from rest_framework import serializers
from .models import Role, UserInfo, Menu, Permission,NewMenu


class RoleSerializer(serializers.ModelSerializer):
    permission = Permission.title
    class Meta:
        model = Role
        fields = ('id', 'rolename', 'permission')


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ('id','username','phone_number','nickname','email','status')
        # fields = '__all__'


class PermissonSerializer(serializers.ModelSerializer):
    menu = Menu.title

    class Meta:
        model = Permission
        fields = ('id', 'title', 'url', 'menu')

class NewmenuSerializer(serializers.ModelSerializer):

    class Meta:
        fields = "__all__"


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('id', 'title', 'url', 'parent')
