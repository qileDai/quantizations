from django.urls import path
from . import views

app_name = 'rbac'
urlpatterns = [
    path('users/', views.users, name='users'),
    path('users/new/', views.users_new, name='users_new'),
    path('users/edit/<int:id>/', views.users_edit, name='users_edit'),
    path('users/delete/<int:id>/', views.users_delete, name='users_delete'),

    path('roles/', views.roles, name='role'),
    path('roles/new/', views.roles_new, name='roles_new'),
    path('roles/edit/<int:id>/', views.roles_edit, name='roles_edit'),
    path('roles/delete/<int:id>/', views.roles_delete, name='roles_delete'),

    path('permissions/', views.permissions, name='permissions'),
    path('permissions/new/', views.permissions_new, name='permissions_new'),
    path('permissions/edit/<int:id>/', views.permissions_edit, name='permissions_edit'),
    path('permissions/delete/<int:id>/', views.permissions_delete, name='permissions_delete'),

    path('menus/', views.menus, name='menus'),
    path('menus/new/', views.menus_new, name='menus_new'),
    path('menus/edit/<int:id>/', views.menus_edit, name='menus_edit'),
    path('menus/delete/<int:id>/', views.menus_delete, name='menus_delete'),

    path('', views.index, name='index')
]
