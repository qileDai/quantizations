from ..models import UserInfo, Menu


def init_permission(request, user_obj):
    """
    用户权限信息初始化，获取当前用户所有权限信息，并保存到Session中
    此处的request以及user_obj参数均为对象，user为登陆成功时在数据库中查询到的user对象
    :param request: 
    :param user_obj: 
    :return: 
    """
    # user_obj是UserInfo模型类对象，user_obj.roles关联Role模型类
    permission_item_list = user_obj.roles.values('permissions__url',
                                                 'permissions__title',
                                                 'permissions__menu_id').distinct()
    # print(permission_menu_list)
    permission_url_list = []  # 用户权限url列表，--> 用于中间件验证用户权限
    permission_menu_list = []  # 用户权限url所属菜单列表 [{"title":xxx, "url":xxx, "menu_id": xxx},{},]

    for item in permission_item_list:
        permission_url_list.append(item['permissions__url'])
        if item['permissions__menu_id']:
            temp = {"title": item['permissions__title'],
                    "url": item["permissions__url"],
                    "menu_id": item["permissions__menu_id"]}
            permission_menu_list.append(temp)

    menu_list = list(Menu.objects.values('id', 'title', 'parent_id'))
    # 注：session在存储时，会先对数据进行序列化，因此对于Queryset对象写入session， 加list()转为可序列化对象

    from django.conf import settings

    print('permission_url_list ------------------- ', permission_url_list)
    print('permission_menu_list ------------------- ', permission_menu_list)
    print('menu_list ------------------- ', menu_list)
    # 设置session保存用户权限url列表
    request.session[settings.SESSION_PERMISSION_URL_KEY] = permission_url_list

    # 设置session保存 权限菜单 和 所有菜单
    request.session[settings.SESSION_MENU_KEY] = {
        settings.ALL_MENU_KEY: menu_list,
        settings.PERMISSION_MENU_KEY: permission_menu_list,
    }

    request.session[settings.LOGIN] = True
    request.session['user_id'] = user_obj.id
    request.session.set_expiry(300)

    print('request.session[settings.SESSION_PERMISSION_URL_KEY] ------------------- ',
          request.session[settings.SESSION_PERMISSION_URL_KEY])
