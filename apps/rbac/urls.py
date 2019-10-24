
from django.urls import path
from . import views

app_name = 'rbac'
urlpatterns = [
    # path('login/', views.login, name='login'),
    path('index/', views.index, name='index'),
    path('logout/', views.logout, name='logout'),
    path('account_list/', views.userListView.as_view(), name='account_list'),
    path('role/', views.role, name='role'),
    path('add_roles/', views.add_roles, name='add_roles'),
    path('add_users/', views.add_users, name='add_users'),
    path('delete_users/', views.delete_users, name='delete_users'),
    path('delete_roles/', views.delete_roles, name='delete_roles'),
    path('permission_list/', views.PermissionListView.as_view(), name='permission_list'),
    path('add_permission/', views.add_permission, name='add_permission'),
    path('user_list/', views.userListView.as_view(), name='user_list'),
    path('rolesList/', views.RolesListView.as_view(), name='rolesList'),
    path('edit_permission/', views.edit_permission, name='edit_permission'),
    path('edit_role/', views.EditRole.as_view, name='edit_role'),
    path('user_info/', views.UserList.as_view(), name='user_info'),
    path('role_info/', views.role_info, name='role_info'),
    path('update_password/', views.UpdatePassword, name='update_password'),
    path('menu_permission/', views.menu_permission, name='menu_permission'),
    path('allot_permission/', views.AllotPermissson.as_view(), name='allot_permission'),
    path('user_permission/', views.UserMenuPermission.as_view(), name='user_permission'),
    path('get_csrf/', views.get_csrf, name='get_csrf'),
    path('all_users/', views.getAllUsers.as_view(), name='all_users'),
    path('all_roles/', views.getAllRoles.as_view(), name='all_roles'),
    path('all_menus/', views.get_all_menus, name='all_menus'),



]
