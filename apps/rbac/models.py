from django.db import models

# Create your models here.

class Menu(models.Model):
    """菜单表"""
    caption = models.CharField(max_length=32)
    parent = models.ForeignKey('Menu',on_delete=models.CASCADE,null=True)
    # 定义菜单间的自引用关系
    # 权限url 在 菜单下；菜单可以有父级菜单；还要支持用户创建菜单，因此需要定义parent字段（parent_id）
    # blank=True 意味着在后台管理中填写可以为空，根菜单没有父级菜单
    def __str__(self):
        # 显示层级菜单
        caption_list = [self.caption]
        p = self.parent
        while p:
            caption_list.insert(0,p.caption)
            p = p.parent

        return "_".join(caption_list)

class Permission(models.Model):
    """权限表"""
    title = models.CharField(max_length=64)
    url = models.CharField(max_length=255)
    menu = models.ForeignKey('Menu',on_delete=models.CASCADE,null=True)

    # 显示带菜单前缀的权限
    def __str__(self):
        return '权限名称：%s ------权限所在菜单 %s' %(self.title,self.menu)

class Role(models.Model):
    """角色：绑定权限"""
    rolename = models.CharField(max_length=32)
    permission = models.ManyToManyField('Permission')


    def __str__(self):
        return '角色：%s -----权限 %s' %(self.rolename,self.permission)

class UserInfo(models.Model):
    """ 用户：划分角色"""
    # telephone = models.CharField(max_length=11,unique=True)

    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    email = models.EmailField()
    role = models.ManyToManyField('Role')
    # telephone = models.CharField(max_length=11,unique=True)
    # create_time = models.DateTimeField(auto_now_add=True)
    # status = models.IntegerField(default=1)

    # 定义用户和角色的多对多关系
    def __str__(self):
        return self.username
