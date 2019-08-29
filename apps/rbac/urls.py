
from django.urls import path
from . import views
app_name = 'rbac'
urlpatterns = [
    # path('login/', views.login, name='login'),
    path('index/', views.index, name='index'),
    path('logout/', views.logout, name='logout'),
    path('account/', views.account, name='account'),
    path('role/', views.role, name='role'),
    path('menu/', views.menu, name='menu'),
    path('roles/', views.roles, name='roles'),
    path('add_roles/', views.add_roles, name='add_roles'),
    path('add_users/', views.add_users, name='add_users'),
    path('delete_users/', views.delete_users, name='delete_users'),
    path('delete_roles/', views.delete_roles, name='delete_roles'),
    path('permission/', views.permission, name='permission'),
    path('add_permission/', views.add_permission, name='add_permission'),
    path('user_list/', views.userListView.as_view(), name='user_list'),
    path('delete_menu/', views.delete_menu, name='delete_menu'),
    # path('RolesListView/',views.RolesListView.as_view(),name='RolesListView'),

]