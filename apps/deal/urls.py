from django.contrib import admin
from django.urls import path
from . import views

app_name = 'deal'
urlpatterns = [
    path('addaccount/', views.AddAccount.as_view(), name='addaccount'),
    path('accountlist/', views.AccountList.as_view(), name='accountlist'),
    path('getcurrencies/', views.GetCurrencies.as_view(), name='getcurrencies'),
    path('editaccount/', views.EditAccount.as_view(), name='editaccount'),
    path('deleteaccount/', views.DeleteAccount.as_view(), name='deleteaccount'),
    path('showassert/', views.ShowAssert.as_view(), name='showassert'),
    path('chargeaccount/', views.ChargeAccount.as_view(), name='chargeaccount'),
    path('withdraw/', views.WithDraw.as_view(), name='withdraw'),
    path('configcurrency/', views.ConfigCurrency.as_view(), name='configcurrency'),
    path('showcollectasset/', views.ShowCollectAsset.as_view(), name='showcollectasset'),
    path('accountinfo/', views.accountinfo, name='accountinfo'),
    path('selectcurrency/', views.SelectCurrency.as_view(), name='selectcurrency'),

    path('robotList/', views.RobotList.as_view(), name='robotList'),
    path('startrobot/', views.StartRobot.as_view(), name='startrobot'),
    path('showtradedetail/', views.ShowTradeDetail.as_view(), name='showtradedetail'),
    path('getaccountinfo/', views.GetAccountInfo.as_view(), name='getaccountinfo'),
    path('createrobot/', views.CreateRobot.as_view(), name='createrobot'),
    path('robot_protection/', views.RobotProtection.as_view(), name='robot_protection'),
    path('showconfig/', views.ShowConfig.as_view(), name='showconfig'),
    path('showconfiginfo/', views.ShowConfigInfo.as_view(), name='showconfiginfo'),
    path('warning_users/', views.WarningUsers.as_view(), name='warning_users'),
    path('robot_yield/', views.RobotYield.as_view(), name='robot_yield'),


]
