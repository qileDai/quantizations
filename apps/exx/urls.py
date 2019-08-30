from django.urls import path
from . import views
app_name = 'exx'
urlpatterns = [
    path('trading_account/',views.trading_account,name='trading_account'),
    path('girding/',views.girding,name='girding'),
    path('index/',views.index,name='index'),


]