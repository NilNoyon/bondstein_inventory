from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'users';

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.loginUser, name='login'),
    path('logout', views.logoutUser, name='logout'),
    path('404', views.error_404_view, name='error_404_view'),
    path('500', views.handler500, name='handler500'),

    # dashboard
    path('dashboard', views.dashboard, name='dashboard'),
    path('ajax-get-dashboard', views.getDashboard, name='get_dashboard'),
    # users dashboard..
    path('users',views.userSettings, name='users_settings'),
    path('users-roles-warehouses-status',views.otherSettings, name='other_settings'),

    # status...
    path('add_status', views.addStatus, name='add_status'),
    path('get_status', views.getStatus, name='get_status'),
    path('update_status', views.updateStatus, name='update_status'),
    path('delete_status', views.deleteStatus, name='delete_status'),

    # roles...
	path('add_role', views.addRole, name='add_role'),
	path('get_role', views.getRole, name='get_role'),
	path('update_role', views.updateRole, name='update_role'),
	path('delete_role', views.deleteRole, name='delete_role'),

    # warehouses...
    path('add_warehouse', views.addWarehouse, name='add_warehouse'),
    path('get_warehouse', views.getWarehouse, name='get_warehouse'),
    path('update_warehouse', views.updateWarehouse, name='update_warehouse'),
    path('delete_warehouse', views.deleteWarehouse, name='delete_warehouse'),

	# users....
	path('add', views.add, name='add'),
    path('get', views.get, name='get'),
    path('update', views.update, name='update'),
    path('delete', views.delete, name='delete'),
    path('changed-password/', views.changePassword, name='change_password'),
    path('reset-password/', views.resetPassword, name='reset_password'),

    # for access control...
    path('user/access-control-setup/', views.user_access_control_setup, name='user_access_control_setup'),
    path('user/access-control-load/', views.load_user_access_list, name='load_user_access_list'),
    path('user/access-control-list/', views.user_access_control_list, name='user_access_control_list'),
    path('user/access-control/<int:id>/delete/', views.delete_user_access_control, name='delete_user_access_control'),
    path('access-denied', views.access_denied, name='access_denied'),
]