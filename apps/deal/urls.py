
from django.contrib import admin
from django.urls import path, re_path
from . import views

app_name = 'deal'
urlpatterns = [
    path('addaccount/', views.AddAccount.as_view(), name='addaccount'),
    path('accountlist/', views.AccountList.as_view(), name='accountlist'),
    re_path(r'editaccount/(\d*)/*$', views.EditAccount.as_view(), name='editaccount'),
    path('deleteaccount/<int:id>/', views.DeleteAccount.as_view(), name='deleteaccount'),
    path('showassert/', views.ShowAssert.as_view(), name='showassert'),
    path('chargeaccount/<int:id>', views.ChargeAccount.as_view(), name='chargeaccount'),
    path('withdraw/<int:id>', views.WithDraw.as_view(), name='withdraw'),
    path('configcurrency/', views.ConfigCurrency.as_view(), name='configcurrency'),

]
