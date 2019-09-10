from django.db import models
from apps.rbac.models import UserInfo


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
    # 账户名称
    title = models.CharField(max_length=32, unique=True)
    accesskey = models.CharField(max_length=128, unique=True)
    secretkey = models.CharField(max_length=128, unique=True)
    # 创建时间
    createtime = models.DateTimeField(auto_now_add=True)
    # 与用户表是多对一关系
    users = models.ForeignKey(UserInfo, on_delete=models.CASCADE, null=True, blank=True)
    # 与平台表是多对一关系
    platform = models.ForeignKey("TradingPlatform", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class Property(models.Model):
    """
    资产信息
    """
    # 币种
    currency = models.CharField(max_length=32)
    # 初始资产
    original_assets = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    # 增资记录
    charge_record = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    # 提币记录
    withdraw_record = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    # 币种显示状态
    currency_status = models.CharField(max_length=10, default='0')
    # 账户与资产信息一对多关系
    account = models.ForeignKey("Account", on_delete=models.CASCADE, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True)


class LastdayAssets(models.Model):
    """
    昨日24时账户资产信息
    """
    currency = models.CharField(max_length=32)
    # 昨日24时资产信息
    lastday_assets = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    # 与用户表时多对一关系
    account = models.ForeignKey("Account", on_delete=models.CASCADE, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True)


class Market(models.Model):
    name = models.CharField(max_length=32)   # 市场名称


class Robot(models.Model):
    Robot_Status = (
        ("运行中", 1),
        ("已停止", 0),
    )
    trading_account = models.ForeignKey('Account', on_delete=models.CASCADE)    # 交易账户外键account
    currency = models.CharField(max_length=32)                                  # 交易币种
    market = models.CharField(max_length=32)                                    # 交易市场
    trading_strategy = models.CharField(max_length=32)                          # 交易策略
    total_money = models.DecimalField(max_digits=19, decimal_places=2)          # 总投入
    float_profit = models.DecimalField(max_digits=19, decimal_places=2)         # 浮动盈亏
    realized_profit = models.DecimalField(max_digits=19, decimal_places=2)      # 实现利润
    total_profit = models.DecimalField(max_digits=19, decimal_places=2)         # 总利润
    annual_yield = models.DecimalField(max_digits=5, decimal_places=2)          # 年化收益率
    create_time = models.DateTimeField(auto_now_add=True)                       # 创建时间
    status = models.SmallIntegerField(choices=Robot_Status)                     # 状态
    current_price = models.DecimalField(max_digits=10,decimal_places=2)         #当前价
    orders_frequency = models.IntegerField()                                    #挂单频率
    resistance = models.DecimalField(max_digits=10,decimal_places=2)            #阻力位
    support_level = models.DecimalField(max_digits=10,decimal_places=2)         #支撑位
    girding_num = models.IntegerField()                                         #网格数量
    procudere_fee = models.CharField(max_length=10)                             #交易手续费
    min_num = models.IntegerField()                                             #最小网格数量
    max_num = models.IntegerField()                                             #最大的网格数量
    girding_profit = models.CharField(max_length=32)                            #网格利润
    stop_price = models.DecimalField(max_digits=19,decimal_places=2)            #止损价
    warning_price = models.DecimalField(max_digits=19,decimal_places=2)         #w预警价

    class Meta:
        ordering = ['-create_time']

