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
import json,datetime
from datetime import date, datetime, timedelta
from notifications.signals import notify
from pre_order.models import *
from inventory.models import *

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
        total_pre_order = PreOrder.objects.all().count()
        total_item = ItemDetails.objects.all().count()
        total_warehouse = Warehouse.objects.all().count()
        total_salesorder = SalesOrder.objects.all().count()
        total_sto = STChallan.objects.all().count()
        stock_in = []
        stock_out = []
        damage = []
        # for stock in
        stocks_data = getProcessWiseTotalQuantity(request,1,'From Vendor')
        stock_out_data = getProcessWiseTotalQuantity(request,1,'To Client')
        damage_data = getProcessWiseTotalQuantity(request,1,'Damage')
        for i in stocks_data:
            details = {
                'slug':i['slug'],
                'quantity':i['data'],
            }
            stock_in.append(details)

        for i in stock_out_data:
            details = {
                'slug':i['slug'],
                'quantity':i['data'],
            }
            stock_out.append(details)

        for i in damage_data:
            details = {
                'slug':i['slug'],
                'quantity':i['data'],
            }
            damage.append(details)
         
        context = {
            'total_po':total_pre_order,
            'total_item':total_item,
            'total_warehouse':total_warehouse,
            'total_so':total_salesorder,
            'total_sto':total_sto,
            'stock_in':stock_in,
            'stock_out':stock_out,
            'damage':damage,
        }
        if request.user.is_superuser:
            return render(request, "dashboard/admin_dashboard.html", context)
        else:
            return render(request, 'dashboard/user_dashboard.html', context)

def getProcessWiseTotalQuantity(request,warehouse,process):
    today = datetime.today().date()
    last_day = datetime.today() - timedelta(days=1)
    this_week = datetime.today() - timedelta(days=6)
    last_day_of_this_week = datetime.today() - timedelta(days=7)
    last_week = (datetime.today() - timedelta(days=13))
    last_month = today.month - 1
    if last_month == 0:
        last_month = 12
        last_year = today.year - 1
    if today.month < 9:
        this_month_like = str(today.year)+'-0'+str(today.month)+'%'
    else:
        date_like = str(today.year)+'-'+str(today.month)+'%'
    if last_month < 9:
        last_month_like = str(today.year)+'-0'+str(last_month)+'%'
    else:
        last_month_like = str(last_year)+'-'+str(last_month)+'%'

    # text_format = ['Today','Last Day','This Week','Last Week','This Month','Last Month']
    text_format = ['Today','Last Day','This Week']
    result = []
    if process == 'From Vendor':
        result.append(ScannedBarcode.objects.filter(from_vendor=True,scanning_date__date=today).count())

        result.append(ScannedBarcode.objects.filter(from_vendor=True,scanning_date__date=last_day.date()).count())

        result.append(ScannedBarcode.objects.filter(from_vendor=True).count())
    elif process == 'To Client':
        result.append(ScannedBarcode.objects.filter(to_client=True,scanning_date__date=today).count())

        result.append(ScannedBarcode.objects.filter(to_client=True,scanning_date__date=last_day.date()).count())

        result.append(ScannedBarcode.objects.filter(to_client=True).count())
    elif process == 'Damage':
        result.append(ScannedBarcode.objects.filter(damage=True,scanning_date__date=today).count())

        result.append(ScannedBarcode.objects.filter(damage=True,scanning_date__date=last_day.date()).count())

        result.append(ScannedBarcode.objects.filter(damage=True).count())


    # result.append(ScannedBarcode.objects.filter(process=process,part=1,scanned_at__range=[last_week,last_day_of_this_week],bcb__bc__company=company).aggregate(data=Sum('accepted_qty')))
    
    # month_data = Production.objects.raw("select p.*, sum(p.accepted_qty) as data from production p, bundle_card_barcodes bcb, bundle_cards bc where p.bcb_id=bcb.id and bcb.bc_id=bc.id and p.scanned_at like %s and p.process_id=%s and p.part_id=1 and bc.company_id=%s;",[this_month_like,process,company.id])
    # for i in month_data:
    #     result.append({'data':i.data})
    
    # last_month_data = Production.objects.raw("select p.*, sum(p.accepted_qty) as data from production p, bundle_card_barcodes bcb, bundle_cards bc where p.bcb_id=bcb.id and bcb.bc_id=bc.id and p.scanned_at like %s and p.process_id=%s and p.part_id=1 and bc.company_id=%s;",[last_month_like,process,company.id])
    # for i in last_month_data:
    #     result.append({'data':i.data})
    data_result = []
    counter = 0
    for i in text_format:
        details = {
            'slug':i,
            'data':result[counter],
        }
        data_result.append(details)
        counter += 1
    return data_result

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
    return render(request, '404.html')

def handler500(request, *args, **argv):
    return redirect(request, '500.html')

def otherSettings(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        try:
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
        except:
            return redirect('users:error_404_view')

#########################
## Users Roles
#########################
### users settings
def userSettings(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        try:
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
        except:
            return redirect('users:error_404_view')

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
        try:
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
        except:
            return redirect('users:error_404_view')
@csrf_exempt
def getRole(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        try:
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
        except:
            return redirect('users:error_404_view')

@csrf_exempt
def updateRole(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        try:
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
        except:
            return redirect('users:error_404_view')


#########################
## warehouse
def addWarehouse(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        try:
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
        except:
            return redirect('users:error_404_view')

@csrf_exempt
def deleteWarehouse(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        try:
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
        except:
            return redirect('users:error_404_view')

@csrf_exempt
def getWarehouse(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        try:
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
        except:
            return redirect('users:error_404_view')

@csrf_exempt
def updateWarehouse(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        try:
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
        except:
            return redirect('users:error_404_view')

#########################
#########################
## users
#########################
def add(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        try:
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
        except:
            return redirect('users:error_404_view')


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
        try:
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
        except:
            return redirect('users:error_404_view')


@login_required
def update(request):
    if not request.user.is_superuser:
        return redirect('users:dashboard')
    else:
        try:
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
        except:
            return redirect('users:error_404_view')


@login_required
def changePassword(request):
    if not request.user.is_authenticated:
        return redirect('index')
    else:
        try:
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
        except:
            return redirect('users:error_404_view')


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
        try:
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
        except:
            return redirect('users:error_404_view')

@csrf_exempt
def deleteStatus(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        try:
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
        except:
            return redirect('users:error_404_view')

@csrf_exempt
def getStatus(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        try:
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
        except:
            return redirect('users:error_404_view')

@csrf_exempt
def updateStatus(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        try:
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
        except:
            return redirect('users:error_404_view')
