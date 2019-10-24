# encoding: utf-8
from rest_framework import serializers
from .models import Role, UserInfo, Menu, Permission,NewMenu


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields ="__all__"


class UserSerializer(serializers.ModelSerializer):
    # roles = RoleSerializer()
    class Meta:
        model = UserInfo
        fields = ('id','username','phone_number','nickname','email','status','create_time')
        # fields = '__all__'


class PermissonSerializer(serializers.ModelSerializer):
    menu = Menu.title

    class Meta:
        model = Permission
        fields = ('id', 'title', 'url', 'menu')

class NewmenuSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewMenu
        fields = ('id','name','url','perms','type','orderNum','parentid')

    def get_menus(self,obj):
        title_list = [self.name]
        p = self.parentid
        while p:
            title_list.insert(0, p.name)
            p = p.parentid
            title_list.append(p)
        return title_list




class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('id', 'title', 'url', 'parent')
