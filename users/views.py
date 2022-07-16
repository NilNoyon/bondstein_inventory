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
from .decorators import permission
import pandas as pd

# Create your views here.s

def index(request):
    if not request.user.is_active:
        return render(request, "login.html")
    else:
        return redirect('users:dashboard')

def dashboard(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        total_pre_order = PreOrder.objects.all().count()
        total_item = ItemDetails.objects.all().count()
        total_warehouse = Warehouse.objects.exclude(name__icontains='float').count()
        total_salesorder = SalesOrder.objects.all().count()
        total_so_item = SODetails.objects.all().values('item_details').distinct().count()
        total_sto = STChallan.objects.all().count()
        total_sto_item = STCDetails.objects.all().values('item_details').distinct().count()
        total_fo = FloatingSalesDetails.objects.all().count()
        total_fo_item = FloatingSalesDetails.objects.all().values('item_details').distinct().count()
        stock_in = []
        stock_out = []
        damage = []
        warehouses = []
        # for stock in
        if request.user.is_superuser:
            warehouses = Warehouse.objects.exclude(name__icontains='float')
            stocks_data = getProcessWiseTotalQuantity(request,0,'From Vendor')
            stock_out_data = getProcessWiseTotalQuantity(request,0,'To Client')
            damage_data = getProcessWiseTotalQuantity(request,0,'Damage')
        else:
            warehouse = request.user.warehouse
            stocks_data = getProcessWiseTotalQuantity(request,warehouse,'From Vendor')
            stock_out_data = getProcessWiseTotalQuantity(request,warehouse,'To Client')
            damage_data = getProcessWiseTotalQuantity(request,warehouse,'Damage')
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
            'total_so_item':total_so_item,
            'total_sto':total_sto,
            'total_sto_item':total_sto_item,
            'total_fo':total_fo,
            'total_fo_item':total_fo_item,
            'stock_in':stock_in,
            'stock_out':stock_out,
            'damage':damage,
            'warehouses': warehouses,
        }
        if request.user.is_superuser:
            return render(request, "dashboard/admin_dashboard.html", context)
        else:
            return render(request, 'dashboard/user_dashboard.html', context)

def getProcessWiseTotalQuantity(request,warehouse,process):
    today = datetime.now()
    last_day = datetime.today() - timedelta(days=1)
    this_week = datetime.today() - timedelta(days=6)
    last_day_of_this_week = datetime.today() - timedelta(days=7)
    last_week = (datetime.today() - timedelta(days=13))
    last_month = today.month - 1
    if last_month == 0:
        last_month = 12
    last_year = today.year - 1
    if today.month <= 9:
        this_month_like = str(today.year)+'-0'+str(today.month)+'%'
    else:
        date_like = str(today.year)+'-'+str(today.month)+'%'
    if last_month <= 9:
        last_month_like = str(today.year)+'-0'+str(last_month)+'%'
    else:
        last_month_like = str(last_year)+'-'+str(last_month)+'%'

    # text_format = ['Today','Last Day','This Week','Last Week','This Month','Last Month']
    text_format = ['Today','Last Day','This Week']
    result = []
    if warehouse == 0:
        if process == 'From Vendor':
            result.append(ScannedBarcode.objects.filter(from_vendor=1,scanning_date=today.date(),).count())
            result.append(ScannedBarcode.objects.filter(from_vendor=1,scanning_date=last_day.date()).count())
            result.append(ScannedBarcode.objects.filter(from_vendor=1,scanning_date__gte=this_week.date()).count())
        elif process == 'To Client':
            result.append(ScannedBarcode.objects.filter(to_client=1,scanning_date=last_day.date()).count())
            result.append(ScannedBarcode.objects.filter(to_client=1,scanning_date=last_day.date()).count())
            result.append(ScannedBarcode.objects.filter(to_client=1,scanning_date__gte=this_week.date()).count())
        elif process == 'Damage':
            result.append(ScannedBarcode.objects.filter(damage=1,scanning_date=today.date()).count())
            result.append(ScannedBarcode.objects.filter(damage=1,scanning_date=last_day.date()).count())
            result.append(ScannedBarcode.objects.filter(damage=1,scanning_date__gte=this_week.date()).count())
    else:
        if process == 'From Vendor':
            result.append(ScannedBarcode.objects.filter(from_vendor=1,scanning_date=today.date(),barcode__warehouse=warehouse).count())
            result.append(ScannedBarcode.objects.filter(from_vendor=1,scanning_date=last_day.date(),barcode__warehouse=warehouse).count())
            result.append(ScannedBarcode.objects.filter(from_vendor=1,scanning_date__gte=this_week.date(),barcode__warehouse=warehouse).count())
        elif process == 'To Client':
            result.append(ScannedBarcode.objects.filter(to_client=1,scanning_date=today.date(),barcode__warehouse=warehouse).count())
            result.append(ScannedBarcode.objects.filter(to_client=1,scanning_date=last_day.date(),barcode__warehouse=warehouse).count())
            result.append(ScannedBarcode.objects.filter(to_client=1,scanning_date__gte=this_week.date(),barcode__warehouse=warehouse).count())
        elif process == 'Damage':
            result.append(ScannedBarcode.objects.filter(damage=1,scanning_date=today.date(),barcode__warehouse=warehouse).count())
            result.append(ScannedBarcode.objects.filter(damage=1,scanning_date=last_day.date(),barcode__warehouse=warehouse).count())
            result.append(ScannedBarcode.objects.filter(damage=1,scanning_date__gte=this_week.date(),barcode__warehouse=warehouse).count())


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

@csrf_exempt
def getDashboard(request):
    warehouse = request.POST.get('warehouse')
    if warehouse == 0:
        total_pre_order = PreOrder.objects.all().count()
        total_item = ItemDetails.objects.all().count()
        total_warehouse = Warehouse.objects.exclude(name__icontains='float').count()
        total_salesorder = SalesOrder.objects.all().count()
        total_so_item = SODetails.objects.all().values('item_details').distinct().count()
        total_sto = STChallan.objects.all().count()
        total_sto_item = STCDetails.objects.all().values('item_details').distinct().count()
        total_fo = FloatingSalesDetails.objects.all().count()
        total_fo_item = FloatingSalesDetails.objects.all().values('item_details').distinct().count()
        stock_in = []
        stock_out = []
        damage = []
        warehouses = []
        # for stock in
        stocks_data = getProcessWiseTotalQuantity(request,0,'From Vendor')
        stock_out_data = getProcessWiseTotalQuantity(request,0,'To Client')
        damage_data = getProcessWiseTotalQuantity(request,0,'Damage')

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
            'total_so_item':total_so_item,
            'total_sto':total_sto,
            'total_sto_item':total_sto_item,
            'total_fo':total_fo,
            'total_fo_item':total_fo_item,
            'stock_in':stock_in,
            'stock_out':stock_out,
            'damage':damage,
        }
        return render(request, "dashboard/dashboard.html", context)
    else:
        total_pre_order = PreOrder.objects.filter(created_by__warehouse=warehouse).count()
        total_item = ItemDetails.objects.filter(warehouse=warehouse).exclude(name__icontains='float').count()
        total_warehouse = Warehouse.objects.exclude(name__icontains='float').count()
        total_salesorder = SalesOrder.objects.filter(warehouse=warehouse).count()
        total_so_item = SODetails.objects.filter(so__warehouse=warehouse).values('item_details').distinct().count()
        total_sto = STChallan.objects.filter(from_warehouse=warehouse).count()
        total_sto_item = STCDetails.objects.filter(stc__from_warehouse=warehouse).values('item_details').distinct().count()
        total_fo = FloatingSalesDetails.objects.filter(floating_order__warehouse=warehouse).count()
        total_fo_item = FloatingSalesDetails.objects.filter(floating_order__warehouse=warehouse).values('item_details').distinct().count()
        stock_in = []
        stock_out = []
        damage = []
        warehouses = []
        # for stock in
        stocks_data = getProcessWiseTotalQuantity(request,warehouse,'From Vendor')
        stock_out_data = getProcessWiseTotalQuantity(request,warehouse,'To Client')
        damage_data = getProcessWiseTotalQuantity(request,warehouse,'Damage')

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
            'total_so_item':total_so_item,
            'total_sto':total_sto,
            'total_sto_item':total_sto_item,
            'total_fo':total_fo,
            'total_fo_item':total_fo_item,
            'stock_in':stock_in,
            'stock_out':stock_out,
            'damage':damage,
        }
        return render(request, "dashboard/dashboard.html", context)


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
                warehouses = Warehouse.objects.exclude(name__icontains='float')
                status = Status.objects.all()
                users = User.objects.exclude(Q(is_superuser=True)).all().order_by('-id')
                context = {'roles': roles, 'warehouses':warehouses, 'status': status}
                return render(request, "settings.html", context)
            else:
                message = 'You are not authorised!'
                messages.warning(request, message)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
                warehouses = Warehouse.objects.exclude(name__icontains='float')
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
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
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
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@csrf_exempt
def delete(request):
    try:
        user = User.objects.get(id=request.POST.get('id', ''))
        message = user.fullname+' - user Have Been Deleted!'
        user.delete()
        messages.error(request, message)
        return redirect('users:users_settingss')
    except Exception as e:
        return redirect('users:users_settingss')


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
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def update(request):
    if not request.user.is_superuser:
        return redirect('users:dashboard')
    else:
        try:
            if request.user.is_superuser:
                if request.method == 'POST':
                    request.POST = request.POST.copy()
                    user = User.objects.get(id=request.POST.get('id'))
                    form = UserUpdateForm(request.POST, instance=user)
                    if form.is_valid():
                        updatedUser = form.save()
                        message = 'User Updated successfully!'
                        messages.success(request, message)
                    else:
                        for field in form:
                            for error in field.errors:
                                messages.warning(request, "%s : %s" % (field.name, error))
                                print(error)
                else:
                    message = 'Method is not allowed!'
                    messages.warning(request, message)
                return redirect('users:users_settings')
            else:
                message = 'You are not authorised!'
                messages.warning(request, message)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@csrf_exempt
def resetPassword(request):
    try:
        user = User.objects.get(id=request.POST.get('id', ''))
        user.password =  make_password('bond@stein', salt=None, hasher='default')
        user.save()
        message = user.fullname+' - Pasword Have Been Reseted!'
        messages.error(request, message)
        return redirect('users:users_settings')
    except Exception as e:
        messages.warning(request, e)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
        except Exception as e:
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

### access control list...
@login_required
def user_access_control_setup(request):
    # chk_permission   = permission(request, reverse("user_access_control_setup"))
    # if chk_permission and chk_permission.view_action:
        # this is use for sync menulist from excel file
        #To read multiple sheet at once just follow this link, code needs to be change
        #https://pythoninoffice.com/read-multiple-excel-sheets-with-python-pandas/
        # xl = pd.read_excel("https://ebs.esquire.com.bd/assets/MenuList.xls", "Sheet1") \
        # Local sync menulist from excel file
        # xl = pd.read_excel("assets/MenuList.xls", "Sheet1") 
        # for i in range(0,len(xl)):
        #     chk_menu = MenuList.objects.filter(menu_url = xl['URL'][i])
        #     if not chk_menu:
        #         sub_menu_name, menu_icon = "", ""
        #         is_sub_menu = True if str(xl["Is Sub Menu"][i]).lower() == 'yes' else False
        #         if str(xl["Icon"][i]) != 'nan': menu_icon = str(xl["Icon"][i])
        #         if str(xl["Sub Menu Name"][i]) != 'nan': sub_menu_name = str(xl["Sub Menu Name"][i]).title()
        #         MenuList.objects.create(
        #             module_name = xl["Module"][i], menu_name =  xl["Menu Name"][i], menu_url = xl["URL"][i], menu_order = xl["Ordering"][i],
        #             menu_icon = menu_icon, sub_menu_name = sub_menu_name, is_sub_menu = is_sub_menu
        #         )

        if request.is_ajax():
            user_prev_list = json.loads(request.POST.get('user_prev_list'))
            user_id        = request.POST.get('user_id')
            # user_role      = request.POST.get('user_role')
            # designation    = request.POST.get('designation')
            # department    = request.POST.get('department')
            for data in user_prev_list:                    
                menu_id        = data['menu_id']
                view_action    = data['view_action']
                insert_action  = data['insert_action']
                update_action  = data['update_action']
                delete_action  = data['delete_action']
                
                if user_id:
                    chk_exist = UserPermission.objects.filter(user_id = user_id, menu_id = menu_id)
                    if chk_exist:
                        chk_exist.update(view_action = view_action, insert_action = insert_action, update_action = update_action, delete_action = delete_action)
                    else:
                        UserPermission.objects.create(user_id = user_id, menu_id = menu_id, view_action = view_action, insert_action = insert_action, update_action = update_action, delete_action = delete_action)
                else:
                    return JsonResponse("Something went wrong!",safe=False,content_type='application/json; charset=utf8')
            
            return JsonResponse("User access control setup successful",safe=False,content_type='application/json; charset=utf8')
        else:        
            context = {
                'menu_list': MenuList.objects.filter(status = True).order_by('module_name','menu_order'),
                'user_list': User.objects.filter(is_active = True).exclude(is_superuser=True)
            }
            return render(request, 'users/user_access_control_setup.html',context)
    # else:
    #     return redirect('/access-denied')

@csrf_exempt
@login_required
def load_user_access_list(request):
    chk_permission   = permission(request, reverse("user_access_control_setup"))
    if chk_permission and chk_permission.view_action:
        if request.is_ajax():
            access_list = list(UserPermission.objects.values().filter(user_id = int(request.POST.get('user'))))
            data = {
                "access_list":access_list,
            }
        return JsonResponse(data,safe=False,content_type='application/json; charset=utf8')
    else:
        return JsonResponse("You have no access on this action!",safe=False,content_type='application/json; charset=utf8')
                
@login_required
def user_access_control_list(request):
    chk_permission   = permission(request, reverse("user_access_control_list"))
    if chk_permission and chk_permission.view_action:
        user_list  = Users.objects.filter(status = True).exclude(is_superuser=1)

        if request.method == 'POST':
            user_id   = request.POST.get('user')
            access_list = []
            if user_id:
                access_list = UserPermission.objects.filter(user_id = int(user_id)).order_by("menu__module_name")

            context = {
                'access_list': access_list,
                'user_list': user_list,
                'user_id': int(user_id) if user_id else None,
            }
            return render(request, 'users/user_access_control_list.html', context)    
        else:        
            access_list = UserPermission.objects.filter(user_id = request.session.get('id')).order_by("menu__module_name")

            context = {
                    'access_list': access_list,
                    'user_list': user_list
                }
            return render(request, 'users/user_access_control_list.html', context)
    else:
        return redirect('/access-denied')
                
@csrf_exempt
@login_required
def delete_user_access_control(request, id):
    chk_permission   = permission(request, reverse("user_access_control_list"))
    if chk_permission and chk_permission.view_action and chk_permission.delete_action:
        UserPermission.objects.filter(id=id).delete()
        return JsonResponse("success",safe=False,content_type='application/json; charset=utf8')
    else:
        return JsonResponse("You have no access on this action!",safe=False,content_type='application/json; charset=utf8')
    
@login_required
def access_denied(request):
    return render(request, '404.html')