
from django.contrib import admin
from django.urls import path, re_path
from . import views

app_name = 'deal'
urlpatterns = [
    path('addaccount/', views.AddAccount.as_view(), name='addaccount'),
    path('accountlist/', views.AccountList.as_view(), name='accountlist'),
    path('editaccount/', views.EditAccount.as_view(), name='editaccount'),
    path('deleteaccount/', views.DeleteAccount.as_view(), name='deleteaccount'),
    path('showassert/', views.ShowAssert.as_view(), name='showassert'),
    path('chargeaccount/', views.ChargeAccount.as_view(), name='chargeaccount'),
    path('withdraw/', views.WithDraw.as_view(), name='withdraw'),
    path('configcurrency/', views.ConfigCurrency.as_view(), name='configcurrency'),

]
