from django.urls import path
from . import views
app_name = 'exx'
urlpatterns = [
    path('trading_account/',views.trading_account,name='trading_account'),


]