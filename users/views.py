from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from .models import *
from .forms import *
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from django.contrib import messages
from django.core import serializers
from django.db.models import Q
import json
from notifications.signals import notify

# Create your views here.


def index(request):
    if not request.user.is_active:
        return render(request, "login.html")
    else:
        return redirect('users:dashboard')
        # return JsonResponse({'foo':'bar'})

def dashboard(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            return render(request, "dashboard/admin_dashboard.html")
        else:
            return render(request, 'dashboard/user_dashboard.html')

#########################
## Login, Logout Error
#########################

def loginUser(request):
    if request.method == 'POST':
        if request.POST['username']:
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
        print(user)
        if user is None:
            message = 'User name / Password Mismatched!'
            messages.warning(request, message)
        else:
            login(request, user)
            message = 'Welcome to Bondstein Inventory Management System!'
            messages.success(request, message)
        return redirect('users:index')
    else:
        message = 'You are not allowed to login!'
        messages.warning(request, message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def logoutUser(request):
    logout(request)
    message = 'Successfully Logged Out!'
    messages.success(request, message)
    return redirect('users:index')

def error_404_view(request):
    return redirect('dashboard')

def handler500(request, *args, **argv):
    return redirect('dashboard')

def otherSettings(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            roles = Role.objects.all()
            warehouses = Warehouse.objects.all()
            status = Status.objects.all()
            users = User.objects.exclude(Q(is_superuser=True)).all()
            context = {'roles': roles, 'warehouses':warehouses, 'status': status}
            return render(request, "settings.html", context)
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#########################
## Users Roles
#########################
### users settings
def userSettings(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            roles = Role.objects.all()
            warehouses = Warehouse.objects.all()
            status = Status.objects.all()
            users = User.objects.exclude(Q(is_superuser=True)).all()
            context = {'roles': roles, 'warehouses':warehouses, 'status': status,'users':users}
            return render(request, "users/list.html", context)
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def addRole(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                form = Role.objects.get_or_create(name=request.POST.get('role_name'))
                message = 'User Role added successfully!'
                messages.success(request, message)
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('users:other_settings')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def deleteRole(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                role = Role.objects.get(id=request.POST.get('id'))
                role.delete()
                response_data = {}
                response_data['status'] = 'OK'

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def getRole(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                roles = Role.objects.get(id=request.POST.get('id'))
                response_data = {}
                response_data['name'] = roles.name

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def updateRole(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                roles = Role.objects.get(id=request.POST.get('id'))
                roles.role = request.POST.get('role_name')
                roles.save()
                message = 'User Role Updated successfully!'
                messages.success(request, message)
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('users:other_settings')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


#########################
## warehouse
def addWarehouse(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                request.POST = request.POST.copy()
                form = WarehouseForm(request.POST)
                if form.is_valid():
                    form.save()
                    message = 'Warehouse added successfully!'
                    messages.success(request, message)
                else:
                    for field in form:
                        for error in field.errors:
                            messages.warning(request, "%s : %s" % (field.name, error))
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('users:other_settings')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def deleteWarehouse(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                warehouse = Warehouse.objects.get(id=request.POST.get('id'))
                warehouse.delete()
                response_data = {}
                response_data['status'] = 'OK'

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def getWarehouse(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                warehouse = Warehouse.objects.get(id=request.POST.get('id'))
                response_data = {}
                response_data['name'] = warehouse.name
                response_data['address'] = warehouse.address
                response_data['contact'] = warehouse.contact

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def updateWarehouse(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                warehouse = Warehouse.objects.get(id=request.POST.get('id'))
                warehouse.name = request.POST.get('name')
                warehouse.address = request.POST.get('address')
                warehouse.contact = request.POST.get('contact')
                warehouse.save()
                message = 'Warehouse Updated successfully!'
                messages.success(request, message)
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('users:other_settings')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#########################
#########################
## users
#########################
def add(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                request.POST = request.POST.copy()
                request.POST['fullname'] = request.POST.get('fullname').title()
                request.POST['password'] = make_password('bond@stein', salt=None, hasher='default')
                form = UserAddForm(request.POST)
                # return HttpResponse(form)
                if form.is_valid():
                    user = form.save()
                    message = 'User added successfully!'
                    messages.success(request, message)
                else:
                    for field in form:
                        for error in field.errors:
                            messages.warning(request, "%s : %s" % (field.name, error))
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('users:users_settings')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@csrf_exempt
def delete(request):
    user = User.objects.get(id=request.POST.get('id', ''))
    message = user.name+' - user Have Been Deleted!'
    user.delete()
    messages.error(request, message)
    return redirect('users:type_and_users')


@csrf_exempt
def get(request):
    if not request.user.is_superuser:
        return redirect('users:dashboard')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                user = User.objects.get(id=request.POST.get('id'))
                response_data = {}
                response_data['username'] = user.username
                response_data['fullname'] = user.fullname
                response_data['role'] = user.role_id
                response_data['email'] = user.email
                response_data['warehouse'] = user.warehouse_id
                response_data['designation'] = user.designation
                response_data['is_active'] = user.is_active

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def update(request):
    if not request.user.is_superuser:
        return redirect('users:dashboard')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                request.POST = request.POST.copy()
                user = User.objects.get(id=request.POST.get('id', ''))
                form = UserUpdateForm(request.POST, instance=user)
                # return HttpResponse(form)
                if form.is_valid():
                    updatedUser = form.save()
                    message = 'User Updated successfully!'
                    messages.success(request, message)
                else:
                    for field in form:
                        for error in field.errors:
                            messages.warning(request, "%s : %s" % (field.name, error))
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('users:type_and_users')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def changePassword(request):
    if not request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            user = request.user
            if request.POST['con_pass'] == request.POST['new_pass']:
                user.password =  make_password(request.POST['con_pass'], salt=None, hasher='default')
                user.save()
                message = 'Password Changed Successfully!'
                messages.success(request, message)
            else:
                message = 'New and Confirm Password Did Not Matched!'
                messages.error(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@csrf_exempt
def resetPassword(request):
    user = User.objects.get(id=request.POST.get('id', ''))
    user.password =  make_password('bond@stein', salt=None, hasher='default')
    user.save()
    message = user.fullname+' - Pasword Have Been Reseted!'
    messages.error(request, message)
    return redirect('users:users_settings')

#########################
## Status
#########################

def addStatus(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                form = Status.objects.get_or_create(name=request.POST.get('status').title(),status_class=request.POST.get('status_class').lower())
                message = 'Status added successfully!'
                messages.success(request, message)
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('users:other_settings')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def deleteStatus(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                status = Status.objects.get(id=request.POST.get('id'))
                status.delete()
                response_data = {}
                response_data['status'] = 'OK'

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def getStatus(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                status = Status.objects.get(id=request.POST.get('id'))
                response_data = {}
                response_data['status'] = status.name

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def updateStatus(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                status = Status.objects.get(id=request.POST.get('id'))
                status.name = request.POST.get('status').title()
                status.status_class = request.POST.get('status_class').title()
                status.save()
                message = 'Status Updated successfully!'
                messages.success(request, message)
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('users:other_settings')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
