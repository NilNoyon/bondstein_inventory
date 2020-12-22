from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate
from .models import User
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from django.contrib import messages
from django.core import serializers
from django.db.models import Q
import json


# Create your views here.


def index(request):
    if not request.user.is_authenticated:
        return render(request, "login.html")
    else:
        # return redirect('dashboard')
        return JsonResponse({'foo':'bar'})

def dashboard(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.user.is_superuser:
            return render(request, "dashboard/admin_dash.html")
        else:
            return render(request, 'dashboard/user_dashboard.html')

#########################
## Login, Logout Error
#########################

def loginUser(request):
    if request.method == 'POST':
        if '@' in request.POST['username']:
            try:
                user = User.objects.get(username=request.POST['username'])
                if user.is_active == False:
                    message = 'Inactive user! Sorry you don\'t have permission to access Smart Tracker'
                    messages.error(request, message)
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                username = user.username
            except User.DoesNotExist:
                message = 'User does not exist!'
                messages.error(request, message)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            username=request.POST['username']

        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is None:
            message = 'User name / Password Mismatched!'
            messages.warning(request, message)
        else:
            login(request, user)
            message = 'Welcome to Bondstein Inventory Management System!'
            messages.success(request, message)
        return redirect('dashboard')
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def logoutUser(request):
    logout(request)
    message = 'Successfully Logged Out!'
    messages.success(request, message)
    return redirect('index')

def error_404_view(request):
    return redirect('dashboard')

def handler500(request, *args, **argv):
    return redirect('dashboard')
