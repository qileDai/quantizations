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
    title = models.CharField(max_length=32, verbose_name="账户名称", unique=True)
    accesskey = models.CharField(max_length=128)
    secretkey = models.CharField(max_length=128)
    # 创建时间
    createtime = models.DateTimeField(auto_now_add=True)
    # 与用户表是多对一关系
    users = models.ForeignKey(UserInfo, on_delete=models.CASCADE, blank=True)
    # 与平台表是多对一关系
    platform = models.ForeignKey("TradingPlatform", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-createtime']

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
    # 创建时当前价
    last = models.DecimalField(max_digits=18, decimal_places=8, default=0)
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
    # 昨日24时参考价
    last = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    # 币种显示状态
    currency_status = models.CharField(max_length=10, default='0')
    # 与用户表时多对一关系
    account = models.ForeignKey("Account", on_delete=models.CASCADE, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True)


class Market(models.Model):
    name = models.CharField(max_length=32)   # 市场名称


class Robot(models.Model):
    Robot_Status = (
        (1, "运行中"),
        (0, "已停止"),
        (2, "运行中(保护)"),
        (3, "停止中(保护)"),
    )
    Robot_Protect = (
        (1, "保护"),
        (0, "解除"),
    )
    Run_Status = (
        (0, '停止'),
        (1, '运行')
    )
    trading_account = models.ForeignKey('Account', on_delete=models.CASCADE)                # 交易账户外键account
    currency = models.CharField(max_length=32)                                              # 交易币种
    market = models.CharField(max_length=32)                                                # 交易市场
    trading_strategy = models.CharField(max_length=32)                                      # 交易策略
    total_money = models.CharField(max_length=64,null=True)                                 # 总投入
    float_profit = models.CharField(max_length=64,null=True)                                # 浮动盈亏
    realized_profit = models.CharField(max_length=64,null=True)                              # 实现利润
    total_profit = models.CharField(max_length=64,null=True)                                # 总利润
    annual_yield = models.CharField(max_length=64,null=True)                                # 年化收益率
    create_time = models.DateTimeField(auto_now_add=True)                                   # 创建时间
    status = models.SmallIntegerField(choices=Robot_Status, default=0)                      # 状态
    protection = models.SmallIntegerField(choices=Robot_Protect, default=0)                 # 机器人保护状态

    current_price = models.CharField(max_length=32,null=True)                      # 当前价
    currency_num = models.CharField(max_length=32,null=True)                     #交易币种数量
    market_num = models.CharField(max_length=32,null=True)                      #交易市场币种数量
    orders_frequency = models.IntegerField()                                    # 挂单频率
    resistance = models.DecimalField(max_digits=10, decimal_places=2)           # 阻力位
    support_level = models.DecimalField(max_digits=10, decimal_places=2)        # 支撑位
    girding_num = models.IntegerField()                                         # 网格数量
    procudere_fee = models.CharField(max_length=10)                             # 交易手续费
    min_num = models.IntegerField()                                             # 最小网格数量
    max_num = models.IntegerField()                                             # 最大的网格数量
    girding_profit = models.CharField(max_length=32)                            # 网格利润
    stop_price = models.DecimalField(max_digits=19, decimal_places=2)           # 止损价
    warning_price = models.DecimalField(max_digits=19, decimal_places=2)        # 预警价
    warning_account = models.CharField(max_length=1024, null=True)              # 预警账户
    run_status = models.SmallIntegerField(choices=Run_Status, default=1)        # 运行状态
    running_time = models.CharField(max_length=128)                             # 运行时间
    end_time = models.CharField(max_length=128,default=0)                                 #结束时间
    total_time = models.CharField(max_length=128,default=0)                               #总运行时间
    warning_time = models.CharField(max_length=32)                              # 运行时间

    class Meta:
        ordering = ['-create_time']


class OrderInfo(models.Model):
    """
    已完成挂单信息
    """
    order_type = models.CharField(max_length=10)                            # 订单类型
    closing_price = models.DecimalField(max_digits=18, decimal_places=8)    # 成交价
    total_price = models.DecimalField(max_digits=18, decimal_places=8)      # 成交总价
    closing_time = models.DateTimeField()                                   # 订单完成时间
    robot = models.ForeignKey("Robot", on_delete=models.CASCADE, null=True, blank=True)
    currency_pair = models.CharField(max_length=32)
    mark = models.IntegerField()
    order_id = models.IntegerField()

