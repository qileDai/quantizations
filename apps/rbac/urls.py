from django.urls import path
from . import views

app_name = 'rbac'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('edit_users/', views.edit_users, name='edit_users'),
    path('add_users/', views.AddUsers.as_view(), name='add_users'),
    path('delete_users/', views.delete_users, name='delete_users'),
    path('updatepw/', views.UpdatePasssword.as_view(), name='updatepw'),
    path('add_roles/', views.AddRoles.as_view(), name='add_roles'),
    path('delete_roles/', views.delete_roles, name='delete_roles'),
    path('edit_role/', views.EditRole.as_view(), name='edit_role'),

    path('allot_permission/', views.AllotPermissson.as_view(), name='allot_permission'),
    path('all_users/', views.getAllUsers.as_view(), name='all_users'),
    path('all_roles/', views.RoleList.as_view(), name='all_roles'),
    path('all_menus/', views.getAllMenus.as_view(), name='all_menus'),
    path('selectmenu/', views.SelectMenu.as_view(), name='selectmenu'),
    path('setkey/', views.setKey, name='setkey'),




]
