from django.db import models

# Create your models here.

class Account(models.Model):
    account_name = models.CharField(max_length=32)
    platform = models.CharField(max_length=32)
    pub_time = models.DateTimeField(auto_now_add=True)

class RobotManagement(models.Model):
    Girdding_Status = (
        ("运行中", 1),
        ("已停止", 0),
    )
    trading_account = models.ForeignKey('Account',on_delete=models.CASCADE)
    curry = models.CharField(max_length=32)
    market = models.CharField(max_length=32)
    total_money = models.DecimalField(max_digits=19,decimal_places=2)
    realized_profit = models.DecimalField(max_digits=19,decimal_places=2)
    total_profit = models.DecimalField(max_digits=19,decimal_places=2)
    pub_time = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(choices=Girdding_Status)

