from django.db import models
from django.utils import timezone


class NewMenu(models.Model):
    menu_type = (
        (1, "目录"),
        (0, "菜单"),
        (2, "按钮"),
    )
    parentid = models.ForeignKey("NewMenu", on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=32, null=True)
    url = models.CharField(max_length=200, null=True)
    perms = models.CharField(max_length=500, null=True)
    type = models.IntegerField(choices=menu_type)
    orderNum = models.IntegerField()

    class Meta:
        ordering = ['orderNum']

        # 定义菜单间的自引用关系
        # 权限url 在 菜单下；菜单可以有父级菜单；还要支持用户创建菜单，因此需要定义parent字段（parent_id）
        # blank=True 意味着在后台管理中填写可以为空，根菜单没有父级菜单

    def __str__(self):
        # 显示层级菜单
        title_list = [self.name]
        p = self.parentid
        while p:
            title_list.insert(0, p.name)
            p = p.parentid
        return '-'.join(title_list)


class Menu(models.Model):
    """
    菜单
    """
    title = models.CharField(max_length=32, unique=True)
    url = models.CharField(max_length=32)
    parent = models.ForeignKey("Menu", on_delete=models.CASCADE, null=True, blank=True)

    # 定义菜单间的自引用关系
    # 权限url 在 菜单下；菜单可以有父级菜单；还要支持用户创建菜单，因此需要定义parent字段（parent_id）
    # blank=True 意味着在后台管理中填写可以为空，根菜单没有父级菜单

    def __str__(self):
        # 显示层级菜单
        title_list = [self.title]
        p = self.parent
        while p:
            title_list.insert(0, p.title)
            p = p.parent
        return '-'.join(title_list)


class Permission(models.Model):
    """
    权限
    """
    title = models.CharField(max_length=32, unique=True)
    url = models.CharField(max_length=128, unique=True)


class Role(models.Model):
    """
    角色：绑定权限
    """
    rolename = models.CharField(max_length=64, unique=True)
    # menus = models.ManyToManyField("NewMenu")
    description = models.CharField(max_length=1000,null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    # 定义角色和权限的多对多关系
    class Meta:
        ordering = ['-create_time']
    def __str__(self):
        return self.rolename


class RoleMenu(models.Model):
    role = models.ForeignKey("Role", on_delete=models.CASCADE, null=True, blank=True)
    menu = models.ForeignKey("NewMenu", on_delete=models.CASCADE, null=True, blank=True)



class UserInfo(models.Model):
    """
    用户：划分角色
    """
    User_Status = (
        (0, '禁用'),
        (1, '正常')
    )
    username = models.CharField(max_length=32)
    phone_number = models.CharField(max_length=32)
    password = models.CharField(max_length=128)
    nickname = models.CharField(max_length=32)
    email = models.EmailField()
    status = models.SmallIntegerField(choices=User_Status, default=1)
    create_time = models.DateTimeField(auto_now_add=True)
    roles = models.ManyToManyField("Role")

    # 定义用户和角色的多对多关系
    class Meta:
        ordering = ['-create_time']

    def __str__(self):
        return self.username





