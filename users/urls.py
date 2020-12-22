from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'users';

urlpatterns = [
    path('', views.index, name='index'),

    # dashboard
    path('dashboard', views.dashboard, name='dashboard'),
]