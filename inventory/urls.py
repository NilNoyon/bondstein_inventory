from django.conf.urls import url
from django.urls import path
from inventory import views


urlpatterns = [
    # supplier...
    path('client-list', views.clientList, name='client_list'),

    path('add-client', views.addClient, name='add_client'),
    path('get-client', views.getClient, name='get_client'),
    path('update-client', views.updateClient, name='update_client'),
    path('delete-client', views.deleteClient, name='delete_client'),

    # ajax method..

]
