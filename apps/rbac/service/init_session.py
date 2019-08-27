# _*_coding:utf-8_*_
from django.conf import settings
from apps.rbac.models import Menu

def init_permission(request,user_obj):
    """
      初始化用户权限, 写入session
      :param request:
      :param user_obj:
      :return:
      """

    permission_list = user_obj.roles.values('permission__title',
                                           'permission__url',
                                           'permission__menu_id', ).distinct()
    permission_urllist = []
    # 用户权限url列表，--> 用于中间件验证用户权限
    permission_menulist = []
    # 用户权限url所属菜单列表 [{"title":xxx, "url":xxx, "menu_id": xxx},{},]

    for iteam in permission_list:
        permission_urllist.append(iteam['permission__url'])
        if iteam['permission__menu_id']:
            temp = {'title': iteam['permission__title'],
                    'url': iteam['permission__url'],
                    'menu_id': iteam['permission__menu_id']}
            permission_menulist.append(temp)
    menulist = list(Menu.objects.values('id', 'caption', 'parent_id'))
    # 注：session在存储时，会先对数据进行序列化，因此对于Queryset对象写入session，加list()转为可序列化对象
    # 保存用户权限url列表
    request.session[settings.SESSION_PERMISSION_URL_KEY] = permission_urllist

    # 保存 权限菜单 和所有 菜单；用户登录后作菜单展示用
    request.session[settings.SESSION_MENU_KEY] = {
        settings.ALL_MENU_KEY: menulist,
        settings.PERMISSION_MENU_KEY: permission_menulist,
    }
