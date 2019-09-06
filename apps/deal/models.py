from django.db import models
from apps.rbac.models import UserInfo

# Create your models here.


# class UserManager(models.Manager):
#     def get_user_info(self, user_id):
#         try:
#             user_info = UserInfo.objects.get(id=user_id)
#         except UserInfo.DoesNotExist:
#             user_info = None
#         return user_info


class TradingPlatform(models.Model):
    """
    平台信息
    """
    Platform_name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.Platform_name


class Account(models.Model):
    """
    账户信息
    """
    title = models.CharField(max_length=32, unique=True)
    accesskey = models.CharField(max_length=128, unique=True)
    secretkey = models.CharField(max_length=128, unique=True)
    createtime = models.DateTimeField(auto_now_add=True)
    users = models.ForeignKey(UserInfo, on_delete=models.CASCADE, null=True, blank=True)
    platform = models.ForeignKey("TradingPlatform", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class Property(models.Model):
    """
    资产信息
    """
    currency = models.CharField(max_length=32)
    original_assets = models.DecimalField(max_digits=10, decimal_places=2)
    charge_record = models.CharField(max_length=32, default='0')
    withdraw_record = models.CharField(max_length=32, default='0')
    lastday_assets = models.CharField(max_length=32)

    currency_status = models.CharField(max_length=10, default='0')
    # 账户与资产信息一对多关系
    account = models.ForeignKey("Account", on_delete=models.CASCADE, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True)


