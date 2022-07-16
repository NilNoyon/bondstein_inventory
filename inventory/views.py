from .models import *
from pre_order.models import *
from .forms import *
from pre_order.forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from users.models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pprint
import xlwt
import json
import datetime
from notifications.signals import notify


# Create your views here.

#########################
## Clients
#########################
@login_required
def clientList(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        clients = Client.objects.all().order_by('-created_at').select_related()
        context = {'clients': clients}
        return render(request, "clients/list.html", context)

@login_required
def addClient(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                request.POST = request.POST.copy()

                form = ClientForm(request.POST)
                if form.is_valid():
                    client = form.save()

                    name = request.POST.getlist('person_name')
                    contact = request.POST.getlist('person_contact')
                    email = request.POST.getlist('person_email')
                    zipped = zip(name, contact, email)
                    for name, contact, email in zipped:
                    	data = {
                    		'name':name,
                    		'contact':contact,
                    		'email':email,
                    		'client':client.id,
                    	}
                    	rpform = ResponsiblePersonForm(data)
                    	if rpform.is_valid():
                    		rpform.save()
                    message = 'Clients added successfully!'
                    messages.success(request, message)
                else:
                    for field in form:
                        for error in field.errors:
                            messages.warning(request, "%s : %s" % (field.name, error))
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('client_list')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def deleteClient(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                supplier = Supplier.objects.get(id=request.POST.get('id'))
                supplier.delete()
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
def getClient(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                supplier = Supplier.objects.get(id=request.POST.get('id'))
                response_data = {}
                response_data['name'] = supplier.name
                response_data['contact'] = supplier.contact
                response_data['address'] = supplier.address

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def updateClient(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                supplier = Supplier.objects.get(id=request.POST.get('id'))
                supplier.name = request.POST.get('name')
                supplier.contact = request.POST.get('contact')
                supplier.address = request.POST.get('address')
                supplier.save()
                message = 'Supplier Updated successfully!'
                messages.success(request, message)
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('supplier_list')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#########################
## Sales Orders
#########################
@login_required
def SOList(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        sales_orders = SalesOrder.objects.all().order_by('-created_at')
        context = {
        	'sales_orders': sales_orders,
        }
        return render(request, "sales_orders/list.html", context)
@login_required
def addSO(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
    	if request.method == 'POST':
            request.POST = request.POST.copy()
            if request.user.is_superuser:
                request.POST['warehouse'] = 0
            else:
                request.POST['warehouse'] = request.user.warehouse.id
            request.POST['created_by'] = request.user.id
            form = SalesOrderForm(request.POST)
            if form.is_valid():
                so = form.save()

                item = request.POST.getlist('item_details')
                quantity = request.POST.getlist('quantity')
                # price = request.POST.getlist('price')
                zipped = zip(item, quantity)
                for item, quantity in zipped:
                	data = {
                		'item_details':item,
                		'quantity':quantity,
                		# 'price':price,
                		'so':so.id,
                	}
                	sodform = SODetailsForm(data)
                	if sodform.is_valid():
                		sodform.save()
                notify.send(request.user, recipient=User.objects.filter(is_superuser=True).first(),verb="has added a new sales orders {0}".format(str(so.so_no)))
                message = 'Sales Order added successfully!'
                messages.success(request, message)
            else:
                for field in form:
                    for error in field.errors:
                        messages.warning(request, "%s : %s" % (field.name, error))
            return redirect('so_details',so.id)
    	else:
            item_details = ItemDetails.objects.all()
            clients = Client.objects.all()
            sales_orders = SalesOrder.objects.all().count()
            so_date = datetime.datetime.now().date()
            
            context = {
                'item_details':item_details,
                'clients':clients,
                'so_date':so_date,
            }
            return render(request,'sales_orders/form.html',context)

@csrf_exempt
def deleteSO(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                so = SalesOrder.objects.get(id=request.POST.get('id'))
                so.delete()
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
def getSO(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                so = SalesOrder.objects.get(id=request.POST.get('id'))
                response_data = {}
                response_data['name'] = so.name
                response_data['contact'] = so.contact
                response_data['address'] = so.address

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def updateSO(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                supplier = Supplier.objects.get(id=request.POST.get('id'))
                supplier.name = request.POST.get('name')
                supplier.contact = request.POST.get('contact')
                supplier.address = request.POST.get('address')
                supplier.save()
                message = 'Supplier Updated successfully!'
                messages.success(request, message)
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('supplier_list')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def getResponsiblePerson(request):
	if request.POST.get('client'):
		persons = ResponsiblePerson.objects.filter(client = request.POST.get('client'))
		
		response_data = []
		for i in persons:
			data = {
			'id':i.id,
			'name':i.name,
			}
			response_data.append(data)
		return HttpResponse(
			json.dumps(response_data),
			content_type="application/json"
		)

def SODetail(request, id):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        so = SalesOrder.objects.get(id=id)
        so_details = SODetails.objects.filter(so=id)
        context = {'so': so,'so_details':so_details}
        return render(request, "sales_orders/details.html", context)

@login_required
def SODetailsList(request,id):
	if not request.user.is_active:
		return redirect('users:index')
	else:
		so_detail_list = SODetails.objects.filter(so=id)
		return render(request, 'sales_orders/detail_list.html',{'details':so_detail_list})

### Stock Out portion..
@login_required
def stockOut(request, id):
	if not request.user.is_active:
		return redirect('users:index')
	else:
		so_details = SODetails.objects.get(id=id)
		context = {
			'so_details':so_details,
			'action':'stock out',
			'from_vendor':False,
			'to_client':True,
			'to_technician':False,
			'damage':False,
		}
		return render(request,'stock/scan.html',context)

@csrf_exempt
def scanBarcode(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            so_details = request.POST.get('so_details')
            
            order_details = SODetails.objects.get(id=so_details)
            code = request.POST.get('barcode')

            data = scanTask(code,order_details)
            return HttpResponse(
                json.dumps(data),
                content_type="application/json"
            )
        else:
            message = 'Method is not allowed!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def scanTask(barcode, prod_details):
	try:
		barcode = ScannedBarcode.objects.get(barcode__barcode=barcode,from_vendor=True)
		if ScannedBarcode.objects.filter(barcode=barcode.barcode.id,to_client=True).exists():
			status = 'Failure'
			bc_data = {}
		elif barcode.barcode.po_details.item_details.id != prod_details.item_details.id:
			status = 'Not Matched'
			bc_data = {}
		else:
			try:
				status = 'Success'
				current_date = datetime.datetime.today()
				bc_data = {
					'bid': barcode.barcode.id,
	                'barcode': barcode.barcode.barcode,
	                'item_name': prod_details.item_details.name, 
	                'client': prod_details.so.client,
	                'warehouse': prod_details.so.warehouse.name,
	                'stock_out_date': current_date.strftime("%Y-%m-%d"),
                    'so_detials_qty': prod_details.quantity,
				}
			except ScannedBarcode.DoesNotExist:
				status = 'Not Found'
				bc_data = {}
	except ScannedBarcode.DoesNotExist:
		status = 'Not Exists'
		bc_data = {}

	response_data = {'status':status, 'bc_data': bc_data}
	return response_data

@login_required
def storeStockOut(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            storeScan(request)
            return redirect('so_list')
        else:
            message = 'Method is not allowed!'
            messages.warning(request, message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def storeScan(request):
    request.POST = request.POST.copy()
    scan_user = request.user.id
    barcode = request.POST.getlist('barcode')
    scanning_date = request.POST.getlist('stock_out_date')
    so_details = request.POST.get('so_details')
    from_vendor = request.POST.get('from_vendor')
    to_client = request.POST.get('to_client')
    to_technician = request.POST.get('to_technician')
    damage = request.POST.get('damage')
    try:
        obj = SODetails.objects.get(id=so_details)
        total_scanned_qty = len(barcode)
        if Stock.objects.filter(item=obj.item_details.item.id,warehouse=request.user.warehouse).last().quantity < int(total_scanned_qty):
        	message = 'Out of Stock'
        	messages.warning(request, message)
        	return True
        zipped = zip(barcode, scanning_date)
        for barcode, scanning_date in zipped:
            data = {
                'barcode':barcode,
                'scanning_date':datetime.datetime.strptime(scanning_date, '%Y-%m-%d'),
                'from_vendor':from_vendor,
                'to_client':to_client,
                'to_technician':to_technician,
                'damage':damage,
            }
            spForm = ScannedBarcodeForm(data)
            if spForm.is_valid():
                spForm.save()
                # pass
            else:
                for field in spForm:
                    for error in field.errors:
                        messages.warning(request, "%s : %s" % (field.name, error))

        last_stock_qty = Stock.objects.filter(item=obj.item_details.item.id,warehouse=request.user.warehouse).last().quantity
        
        if last_stock_qty > 0:
            Stock.objects.filter(item=obj.item_details.item.id,warehouse=request.user.warehouse).update(quantity=last_stock_qty - int(total_scanned_qty),updated_at=datetime.datetime.now())
        else:
            messages.warning(request, "Out of stock product scanned")
        data = {
            'item': obj.item_details.item.id,
            'quantity': int(total_scanned_qty),
            'activity': request.POST.get('action'),
            'warehouse': request.user.warehouse,
            'created_by': request.user.id,
        }
        stform = StockLogForm(data)
        stform.save()
        success = 1
    except Exception as e:
    	print(e)
    	message = 'Due to error data not saved!'
    	messages.warning(request,message)
    	success = 0
    if success == 1:
    	message = 'Successfully added!'
    	messages.success(request, message)

#########################
## Stock Item Transfer
#########################
@login_required
def STOList(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        st_challans = STChallan.objects.all().order_by('-created_at')
        context = {
            'st_challans': st_challans,
        }
        return render(request, "transfered/list.html", context)

@login_required
def addSTO(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            request.POST = request.POST.copy()
            request.POST['created_by'] = request.user.id
            form = STChallanForm(request.POST)
            if form.is_valid():
                stc = form.save()

                item = request.POST.getlist('item_details')
                quantity = request.POST.getlist('quantity')
                
                zipped = zip(item, quantity)
                for item, quantity in zipped:
                    data = {
                        'item_details':item,
                        'quantity':quantity,
                        'stc':stc.id,
                    }
                    stcdform = STCDetailsForm(data)
                    if stcdform.is_valid():
                        stcdform.save()
                notify.send(request.user, recipient=User.objects.filter(is_superuser=True).first(),verb="has added a new stock transfer orders {0}".format(str(stc.challan_no)))
                message = 'Stock Transfer Order added successfully!'
                messages.success(request, message)
            else:
                for field in form:
                    for error in field.errors:
                        messages.warning(request, "%s : %s" % (field.name, error))
            return redirect('sto_list')
        else:
            item_details = ItemDetails.objects.all()
            if request.user.is_superuser:
                warehouses = Warehouse.objects.all()
            else:
                warehouses = Warehouse.objects.exclude(id=request.user.warehouse.id).exclude(name__icontains='float').all()
            challans = STChallan.objects.all().count()
            date = datetime.datetime.now().date()
            
            context = {
                'item_details':item_details,
                'warehouses':warehouses,
                'date':date,
            }
            return render(request,'transfered/form.html',context)

@login_required
def scanForOut(request,id):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        stc = STCDetails.objects.get(id=id)
        context = {
            'stc':stc,
            'action':'stock transfer',
        }
        return render(request, "stock/scan_for_out.html", context)

@csrf_exempt
def deleteSTO(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                so = STChallan.objects.get(id=request.POST.get('id'))
                so.delete()
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

def STODetail(request, id):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        stc = STChallan.objects.get(id=id)
        sto_details = STCDetails.objects.filter(stc=id)
        context = {'stc': stc,'sto_details':sto_details}
        return render(request, "transfered/details.html", context)

@login_required
def STODetailsList(request,id):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        so_detail_list = STCDetails.objects.filter(stc=id)
        return render(request, 'transfered/detail_list.html',{'details':so_detail_list})

# stock transfer scanning portion
@csrf_exempt
def scanBarcodeForSTO(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            stc = request.POST.get('challan_details')
            order_details = STCDetails.objects.get(id=stc)

            code = request.POST.get('barcode')

            data = scanTaskForSTO(code,order_details)
            return HttpResponse(
                json.dumps(data),
                content_type="application/json"
            )
        else:
            message = 'Method is not allowed!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def scanTaskForSTO(barcode, prod_details):
    try:
        barcode = ScannedBarcode.objects.get(barcode__barcode=barcode,from_vendor=True)
        if ScannedBarcode.objects.filter(barcode=barcode.barcode.id,to_client=True).exists():
            status = 'Failure'
            bc_data = {}
        elif barcode.barcode.po_details.item_details.id != prod_details.item_details.id:
            status = 'Not Matched'
            bc_data = {}
        else:
            try:
                status = 'Success'
                current_date = datetime.datetime.today()
                bc_data = {
                    'bid': barcode.barcode.id,
                    'barcode': barcode.barcode.barcode,
                    'item_name': prod_details.item_details.name, 
                    'from_warehouse': prod_details.stc.from_warehouse.name,
                    'to_warehouse': prod_details.stc.to_warehouse.name,
                    'stock_out_date': current_date.strftime("%Y-%m-%d"),
                }
            except ScannedBarcode.DoesNotExist:
                status = 'Not Found'
                bc_data = {}
    except ScannedBarcode.DoesNotExist:
        status = 'Not Exists'
        bc_data = {}

    response_data = {'status':status, 'bc_data': bc_data}
    return response_data

@login_required
def storeSTO(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            request.POST = request.POST.copy()
            scan_user = request.user.id
            barcode = request.POST.getlist('barcode')
            scanning_date = request.POST.getlist('stock_out_date')
            stc = request.POST.get('stc')
            try:
                obj = STCDetails.objects.get(id=stc)
                total_scanned_qty = len(barcode)
                last_stock_qty = Stock.objects.filter(item=obj.item_details.item.id,warehouse=request.user.warehouse).last().quantity
                if last_stock_qty < int(total_scanned_qty):
                    message = 'Out of Stock'
                    messages.warning(request, message)
                    return True
                zipped = zip(barcode, scanning_date)
                for barcode, scanning_date in zipped:
                    data = {
                        'stcd': stc,
                        'barcode':barcode,
                        'scanning_date':datetime.datetime.strptime(scanning_date, '%Y-%m-%d'),
                    }
                    spForm = STCBarcodeForm(data)
                    if spForm.is_valid():
                        spForm.save()
                        bc = Barcode.objects.get(id=barcode)
                        bc.warehouse = Warehouse.objects.get(name='Floating Warehouse')
                        bc.save()
                    else:
                        for field in spForm:
                            for error in field.errors:
                                messages.warning(request, "%s : %s" % (field.name, error))


                if last_stock_qty > 0:
                    Stock.objects.filter(item=obj.item_details.item.id,warehouse=request.user.warehouse).update(quantity=last_stock_qty - int(total_scanned_qty),updated_at=datetime.datetime.now())

                data = {
                    'item': obj.item_details.item.id,
                    'quantity': int(total_scanned_qty),
                    'activity': request.POST.get('action'),
                    'warehouse': request.user.warehouse,
                    'created_by': request.user.id,
                }
                stform = StockLogForm(data)
                stform.save()
                success = 1
            except Exception as e:
                print(e)
                message = 'Due to error data not saved!'
                messages.warning(request,message)
                success = 0
            if success == 1:
                message = 'Successfully added!'
                messages.success(request, message)
            return redirect('sto_list')
        else:
            message = 'Method is not allowed!'
            messages.warning(request, message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def receiveSTChallan(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            challan_no = request.POST.get('stc')
            order_details = STChallan.objects.get(id=challan_no)
            order_details.is_received = True
            order_details.save()

            code = request.POST.getlist('barcode')

            for i in code:
                barcode = Barcode.objects.get(id=i)
                barcode.warehouse = order_details.to_warehouse
                barcode.save()
                try:
                    last_stock_qty = Stock.objects.filter(item=barcode.po_details.item_details.item.id,warehouse=request.user.warehouse).last().quantity
                except Exception as e:
                    last_stock_qty = 0
                if last_stock_qty > 0:
                    Stock.objects.filter(item=barcode.po_details.item_details.item.id,warehouse=request.user.warehouse).update(quantity=last_stock_qty + int(1))
                else:
                    data = {
                        'item': barcode.po_details.item_details.item.id,
                        'quantity': last_stock_qty + int(1),
                        'updated_by': request.user.id,
                        'warehouse': request.user.warehouse,
                    }
                    sform = StockForm(data)
                    if sform.is_valid():
                        ms = sform.save()
                    data = {
                        'item': barcode.po_details.item_details.item.id,
                        'quantity': last_stock_qty + int(1),
                        'activity': request.POST.get('action'),
                        'created_by': request.user.id,
                        'warehouse': request.user.warehouse,
                    }
                    stform = StockLogForm(data)
                    if stform.is_valid():
                        stform.save()    

            notify.send(request.user, recipient=User.objects.filter(is_superuser=True).first(),verb="Transfered order {0} received in {1}".format(str(order_details.challan_no),str(order_details.to_warehouse.name)))
            message = 'Stock Transfer Order received successfully!'
            messages.success(request, message)
            return redirect('receive_sto')
        else:
            context = {
                'action':'stock transfer receive',
            }
            return render(request, "stock/stock_receive.html", context)

@csrf_exempt
def getSTOInfo(request):
    challan_no = request.POST.get('barcode')
    if challan_no:
        try:
            challandata = []
            stc = STChallan.objects.get(challan_no=challan_no)
            if stc.is_received == False:
                for i in stc.stcdetails_set.all():
                    barcode = STCBarcode.objects.filter(stcd=i.id)
                    for j in barcode:
                        data = {
                            'bid': j.barcode_id,
                            'barcode': j.barcode.barcode,
                            'item_name': i.item_details.name, 
                            'from_warehouse': i.stc.from_warehouse.name,
                            'to_warehouse': i.stc.to_warehouse.name,
                            'stock_out_date': str(j.created_at),
                        }
                        challandata.append(data)
                challan_data = {'status': 'Success', 'challan_datas': challandata,'stc':stc.id}
            else:
                challan_data = {'status': 'Received'}
        except:
            challan_data = {'status': 'Not Found'}

        return HttpResponse(
            json.dumps(challan_data),
            content_type="application/json"
        )
    else:
        data = {'status': 'Not Exists'}
        return HttpResponse(
            json.dumps(data),
            content_type="application/json"
        )

#### Stock Transfer end #######

#########################
## Floating Sales
#########################
@login_required
def FIList(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        floating_orders = FloatingSalesOrder.objects.all().order_by('-created_at')
        context = {
            'floating_orders': floating_orders,
        }
        return render(request, "floating/list.html", context)

@login_required
def addFO(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            request.POST = request.POST.copy()
            request.POST['created_by'] = request.user.id
            request.POST['warehouse'] = request.user.warehouse
            form = FOForm(request.POST)
            if form.is_valid():
                fo = form.save()

                item = request.POST.getlist('item_details')
                barcode = request.POST.getlist('barcode')
                
                zipped = zip(item, barcode)
                for item, barcode in zipped:
                    data = {
                        'item_details':item,
                        'barcode':barcode,
                        'floating_order':fo.id,
                    }
                    fodform = FODetailsForm(data)
                    if fodform.is_valid():
                        fodform.save()
                    scan = {
                        'barcode':barcode,
                        'scanning_date':datetime.datetime.now(),
                        'from_vendor':False,
                        'to_client':False,
                        'to_technician':True,
                        'damage':False,
                    }
                    spForm = ScannedBarcodeForm(scan)
                    if spForm.is_valid():
                        spForm.save()
                    else:
                        for field in spForm:
                            for error in field.errors:
                                print(error)
                    items = ItemDetails.objects.get(id=item)
                    try:
                        last_stock_qty = Stock.objects.filter(item=items.item_id,warehouse=request.user.warehouse).last().quantity
                    except Exception as e:
                        print(e)
                        last_stock_qty = 0
                    if last_stock_qty > 0:
                        Stock.objects.filter(item=items.item_id,warehouse=request.user.warehouse).update(quantity=last_stock_qty - 1)

                    data = {
                        'item': items.id,
                        'quantity': 1,
                        'activity': "Floating order generated ",
                        'created_by': request.user.id,
                        'warehouse': request.user.warehouse,
                    }
                    stform = StockLogForm(data)
                    if stform.is_valid():
                        stform.save()
                notify.send(request.user, recipient=User.objects.filter(is_superuser=True).first(),verb="has added a new floating orders {0}".format(str(fo.order_no)))
                message = 'Floating Order added successfully!'
                messages.success(request, message)
            else:
                for field in form:
                    for error in field.errors:
                        messages.warning(request, "%s : %s" % (field.name, error))
            return redirect('fi_list')
        else:
            date = datetime.datetime.now().date()
            context = {
                'date':date,
            }
            return render(request,'floating/form.html',context)

@csrf_exempt
def scanBarcodeForFO(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            code = request.POST.get('barcode')

            data = scanTaskForFO(code)
            return HttpResponse(
                json.dumps(data),
                content_type="application/json"
            )
        else:
            message = 'Method is not allowed!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def scanTaskForFO(barcode):
    try:
        barcode = ScannedBarcode.objects.get(barcode__barcode=barcode,from_vendor=True)
        if ScannedBarcode.objects.filter(barcode=barcode.barcode.id,to_client=True).exists():
            status = 'Client'
            bc_data = {}
        elif ScannedBarcode.objects.filter(barcode=barcode.barcode.id,damage=True).exists():
            status = 'Damage'
            bc_data = {}
        elif ScannedBarcode.objects.filter(barcode=barcode.barcode.id,to_technician=True).exists():
            status = 'Technician'
            bc_data = {}
        else:
            try:
                status = 'Success'
                current_date = datetime.datetime.today()
                bc_data = {
                    'bid': barcode.barcode.id,
                    'barcode': barcode.barcode.barcode,
                    'item_name': barcode.barcode.po_details.item_details.name,
                    'item_details': barcode.barcode.po_details.item_details_id,
                }
            except ScannedBarcode.DoesNotExist:
                status = 'Not Found'
                bc_data = {}
    except ScannedBarcode.DoesNotExist:
        status = 'Not Exists'
        bc_data = {}

    response_data = {'status':status, 'bc_data': bc_data}
    return response_data
## Floating items details
@login_required
def FODetail(request, id):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        fs = FloatingSalesOrder.objects.get(id=id)
        fo_details = FloatingSalesDetails.objects.filter(floating_order=id).values_list('item_details').distinct()
        fs_details = []
        total_qty = 0
        for i in fo_details:
            try:
                fod = FloatingSalesDetails.objects.filter(floating_order=id,item_details=i[0])
                total_qty += fod.count()
                data = {
                    'item_name': fod.first().item_details.name,
                    'quantity': fod.count(),
                }
                fs_details.append(data)
            except Exception as e:
                print(e)
        context = {'fs': fs,'fs_details':fs_details}
        return render(request, "floating/details.html", context)

@login_required
def generateSO(request, id):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            request.POST = request.POST.copy()
            if request.user.is_superuser:
                request.POST['warehouse'] = ''
            else:
                request.POST['warehouse'] = request.user.warehouse.id
            request.POST['created_by'] = request.user.id
            fid = request.POST.get('fid')
            form = SalesOrderForm(request.POST)
            if form.is_valid():
                so = form.save()
                so.status = Status.objects.get(name='Complete')
                so.save()
                items = request.POST.getlist('item_details')
                item_set = set(items) # for unique item...
                for item in item_set:
                    data = {
                        'item_details':item,
                        'quantity':items.count(item),
                        'so':so.id,
                    }
                    sodform = SODetailsForm(data)
                    if sodform.is_valid():
                        so_details = sodform.save()
                        barcodes = request.POST.getlist('barcode')
                        to_client = True
                        try:
                            for barcode in barcodes:
                                obj = Barcode.objects.get(id=barcode)
                                data = {
                                    'barcode':barcode,
                                    'scanning_date':datetime.datetime.now(),
                                    'to_client':to_client,
                                }
                                spForm = ScannedBarcodeForm(data)
                                if spForm.is_valid():
                                    spForm.save()
                                    FloatingSalesDetails.objects.filter(floating_order=fid,barcode=barcode).update(is_sold=True)
                                else:
                                    for field in spForm:
                                        for error in field.errors:
                                            messages.warning(request, "%s : %s" % (field.name, error))
                                # last_stock_qty = Stock.objects.filter(item=obj.po_details.item_details.item.id)
                                # if last_stock_qty:
                                #     Stock.objects.filter(item=obj.po_details.item_details.item.id).update(quantity=int(last_stock_qty.quantity) - 1,updated_at=datetime.datetime.now())

                                data = {
                                    'item': obj.po_details.item_details.item.id,
                                    'quantity': 1,
                                    'activity': 'so generated from floating devices',
                                    'created_by': request.user.id,
                                    'warehouse': request.user.warehouse,
                                }
                                stform = StockLogForm(data)
                                stform.save()
                        except Exception as e:
                            print(e)

                notify.send(request.user, recipient=User.objects.filter(is_superuser=True).first(),verb="has added a new sales orders {0}".format(str(so.so_no)))
                message = 'Sales Order added successfully!'
                messages.success(request, message)
            return redirect('fi_list')
        else:
            date = datetime.datetime.now().date()
            fo_details = FloatingSalesDetails.objects.filter(floating_order=id,is_sold=False)
            floating_order = FloatingSalesOrder.objects.get(id=id)
            context = {
                'date':date,
                'fo_details': fo_details,
                'floating_order': floating_order,
            }
            return render(request,'floating/generate_so.html',context)

@csrf_exempt
def deleteFO(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                so = STChallan.objects.get(id=request.POST.get('id'))
                # so.delete()
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

@login_required
def reStock(request, id):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            barcodes = request.POST.getlist('barcode')
            fid = request.POST.get('fid')
            floating_order = FloatingSalesOrder.objects.get(id=fid)

            try:
                floating_order.total_return = len(barcodes)
                floating_order.save()

                for barcode in barcodes:
                    obj = Barcode.objects.get(id=barcode)

                    last_stock_qty = Stock.objects.filter(item=obj.po_details.item_details.item.id,warehouse=request.user.warehouse)
                    if last_stock_qty:
                        last_stock_qty.update(quantity=int(last_stock_qty.last().quantity) + 1,updated_at=datetime.datetime.now())

                    data = {
                        'item': obj.po_details.item_details.item.id,
                        'quantity': 1,
                        'activity': 're stock from floating devices',
                        'created_by': request.user.id,
                        'warehouse': request.user.warehouse,
                    }
                    stform = StockLogForm(data)
                    if stform.is_valid():
                        stform.save()
            except Exception as e:
                print(e)

            notify.send(request.user, recipient=User.objects.filter(is_superuser=True).first(),verb="has added a new sales orders {0}".format(str(floating_order.order_no)))
            message = 'Sales Order added successfully!'
            messages.success(request, message)
            return redirect('fi_list')
        else:
            date = datetime.datetime.now().date()
            fo_details = FloatingSalesDetails.objects.filter(floating_order=id,is_sold=False)
            floating_order = FloatingSalesOrder.objects.get(id=id)
            context = {
                'date':date,
                'fo_details': fo_details,
                'floating_order': floating_order,
                'action': 're stock',
            }
            return render(request,'stock/re_stock.html',context)

#### Report section ###
### Daily Report ###
@login_required
def dailyInventoryReport(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        warehouses = []
        if request.user.is_superuser:
            warehouses = Warehouse.objects.exclude(name__icontains='float')

        context = {
            'warehouses':warehouses,
        }
        return render(request,'reports/daily_report.html',context)
## get date wise inventory report ##
@csrf_exempt
def getDailyInventoryReport(request):
    from_date = request.POST.get('date')
    to_date = request.POST.get('to_date')
    warehouse = request.POST.get('warehouse')
    result = []
    try:
        stock_in_data = ScannedBarcode.objects.filter(from_vendor=1,scanning_date__range=[from_date,to_date])
        stock_out_data = ScannedBarcode.objects.filter(to_client=1,scanning_date__range=[from_date,to_date])
        float_data = ScannedBarcode.objects.filter(to_technician=1,scanning_date__range=[from_date,to_date])
        damage_data = ScannedBarcode.objects.filter(damage=1,scanning_date__range=[from_date,to_date])
        if int(warehouse) == 0:
            total_stock_in = stock_in_data.count()
            total_stock_out = stock_out_data.count()
            total_float = float_data.count()
            total_damage = damage_data.count()

            stock_in = stock_in_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            stock_out = stock_out_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            floats = float_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            damage = damage_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
        else:
            total_stock_in = stock_in_data.filter(barcode__warehouse=warehouse).count()
            total_stock_out = stock_out_data.filter(barcode__warehouse=warehouse).count()
            total_float = float_data.filter(barcode__warehouse=warehouse).count()
            total_damage = damage_data.filter(barcode__warehouse=warehouse).count()

            stock_in = stock_in_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            stock_out = stock_out_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            floats = float_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            damage = damage_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
        stockin_data = []
        stockout_data = []
        damage_data = []
        float_data = []
        for i in stock_in:
            if request.user.is_superuser:
                barcodes = stock_in_data.filter(barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            else:
                barcodes = stock_in_data.filter(barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            result = {
                'item_name':i[0],
                'item':i[1],
                'total_scanned':total_scanned,
                'barcodes': barcodes,
            }
            stockin_data.append(result)
        for i in stock_out:
            if request.user.is_superuser:
                barcodes = stock_out_data.filter(barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            else:
                barcodes = stock_out_data.filter(barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            result = {
                'item_name':i[0],
                'item':i[1],
                'total_scanned':total_scanned,
                'barcodes': barcodes,
            }
            stockout_data.append(result)
        for i in floats:
            if request.user.is_superuser:
                barcodes = float_data.filter(barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            else:
                barcodes = float_data.filter(barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            result = {
                'item_name':i[0],
                'item':i[1],
                'total_scanned':total_scanned,
                'barcodes': barcodes,
            }
            damage_data.append(result)
        for i in damage:
            if request.user.is_superuser:
                barcodes = damage_data.objects.filter(damage=1,barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            else:
                barcodes = damage_data.objects.filter(damage=1,barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            result = {
                'item_name':i[0],
                'item':i[1],
                'total_scanned':total_scanned,
                'barcodes': barcodes,
            }
            damage_data.append(result)
        data = {
            'total_stock_in':total_stock_in,
            'total_stock_out':total_stock_out,
            'total_float':total_float,
            'total_damage':total_damage,
            'stock_in':stockin_data,
            'stock_out':stockout_data,
            'floats':float_data,
            'damage':damage_data,
        }
        return render(request, 'reports/daily_report_info.html',{'result':data})
    except Exception as e:
        print(e)
        return render(request,'reports/daily_report_info.html',{'result':result})

## export date wise inventory report ##
@csrf_exempt
def exportDailyInventoryReport(request,from_date, to_date, warehouse):
    result = []
    try:
        stock_in_data = ScannedBarcode.objects.filter(from_vendor=1,scanning_date__range=[from_date,to_date])
        stock_out_data = ScannedBarcode.objects.filter(to_client=1,scanning_date__range=[from_date,to_date])
        float_data = ScannedBarcode.objects.filter(to_technician=1,scanning_date__range=[from_date,to_date])
        damage_data = ScannedBarcode.objects.filter(damage=1,scanning_date__range=[from_date,to_date])
        if int(warehouse) == 0:
            total_stock_in = stock_in_data.count()
            total_stock_out = stock_out_data.count()
            total_float = float_data.count()
            total_damage = damage_data.count()

            stock_in = stock_in_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            stock_out = stock_out_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            floats = float_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            damage = damage_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
        else:
            total_stock_in = stock_in_data.filter(barcode__warehouse=warehouse).count()
            total_stock_out = stock_out_data.filter(barcode__warehouse=warehouse).count()
            total_float = float_data.filter(barcode__warehouse=warehouse).count()
            total_damage = damage_data.filter(barcode__warehouse=warehouse).count()

            stock_in = stock_in_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            stock_out = stock_out_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            floats = float_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            damage = damage_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
        stockin_data = []
        stockout_data = []
        damage_data = []
        float_data = []
        for i in stock_in:
            if request.user.is_superuser:
                barcodes = stock_in_data.filter(barcode__po_details__item_details=i[1])
            else:
                barcodes = stock_in_data.filter(barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
            result = {
                'item_name':i[0],
                'barcodes': barcodes,
            }
            stockin_data.append(result)
        for i in stock_out:
            if request.user.is_superuser:
                barcodes = stock_out_data.filter(barcode__po_details__item_details=i[1])
            else:
                barcodes = stock_out_data.filter(barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
            result = {
                'item_name':i[0],
                'barcodes': barcodes,
            }
            stockout_data.append(result)
        for i in floats:
            if request.user.is_superuser:
                barcodes = float_data.filter(barcode__po_details__item_details=i[1])
            else:
                barcodes = float_data.filter(barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
            result = {
                'item_name':i[0],
                'barcodes': barcodes,
            }
            damage_data.append(result)
        for i in damage:
            if request.user.is_superuser:
                barcodes = damage_data.objects.filter(damage=1,barcode__po_details__item_details=i[1])
            else:
                barcodes = damage_data.objects.filter(damage=1,barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
            result = {
                'item_name':i[0],
                'barcodes': barcodes,
            }
            damage_data.append(result)
        first_sheet = [total_stock_in, total_stock_out, total_float, total_damage]
        response = HttpResponse(content_type='application/ms-excel')
        file_name = 'Daily_Report_'+ str(datetime.datetime.now().date())
        response['Content-Disposition'] = 'attachment; filename="{}.xls"'.format(file_name)

        wb = xlwt.Workbook(encoding='utf-8')
        bold_font_style = xlwt.XFStyle()
        bold_font_style.font.bold = True
        font_style = xlwt.XFStyle()
        # Frist Sheet for summary of stock in,stock out
        ws = wb.add_sheet('Daily Report')
        # Sheet header, first row
        row_num = 1
        columns = ['Total Stock In', 'Total Stock Out', 'Total Float', 'Total Damage',]
        # print(len(columns))
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], bold_font_style)
        # Sheet body, remaining rows
        row_num += 1
        for col_num in range(len(first_sheet)):
            ws.write(row_num, col_num, first_sheet[col_num], font_style)
        # wb.save(response)
        # end of summary
        # stock in sheet..
        ws = wb.add_sheet('Stock In')
        columns = ['#SI', 'Item Name', 'Barcode',]
        row_num = 1
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], bold_font_style)
        for row in stockin_data:
            for info in row['barcodes']:
                row_num += 1
                ws.write(row_num, 0, row_num-1, font_style)
                ws.write(row_num, 1, row['item_name'], font_style)
                ws.write(row_num, 2, info.barcode.barcode, font_style)
        # wb.save(response)
        #end of stock in
        #stock out sheet..
        ws = wb.add_sheet('Stock Out')
        columns = ['#SI', 'Item Name', 'Barcode',]
        row_num = 1
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], bold_font_style)
        for row in stockout_data:
            for info in row['barcodes']:
                row_num += 1
                ws.write(row_num, 0, row_num-1, font_style)
                ws.write(row_num, 1, row['item_name'], font_style)
                ws.write(row_num, 2, info.barcode.barcode, font_style)
        # wb.save(response)
        # end of stock out
        # Float sheet..
        ws = wb.add_sheet('Floating')
        columns = ['#SI', 'Item Name', 'Barcode',]
        row_num = 1
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], bold_font_style)
        for row in float_data:
            for info in row['barcodes']:
                row_num += 1
                ws.write(row_num, 0, row_num-1, font_style)
                ws.write(row_num, 1, row['item_name'], font_style)
                ws.write(row_num, 2, info.barcode.barcode, font_style)
        # wb.save(response)
        # end of float
        # damage sheet..
        ws = wb.add_sheet('Damage')
        columns = ['#SI', 'Item Name', 'Barcode',]
        row_num = 1
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], bold_font_style)
        for row in damage_data:
            for info in row['barcodes']:
                row_num += 1
                ws.write(row_num, 0, row_num-1, font_style)
                ws.write(row_num, 1, row['item_name'], font_style)
                ws.write(row_num, 2, info.barcode.barcode, font_style)
        wb.save(response)
        # end of damage
        return response
    except Exception as e:
        messages.warning(request, e)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

### Daily Report ###
@login_required
def monthlyInventoryReport(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        warehouses = []
        now = datetime.datetime.now()
        if request.user.is_superuser:
            warehouses = Warehouse.objects.exclude(name__icontains='float')
        year = []
        for i in range(int(now.year),int(2000), -1):
            year.append(i)
        context = {
            'warehouses':warehouses,
            'year': year,
            'current_month': now.month,
            'current_year': now.year,
        }
        return render(request,'reports/monthly_report.html',context)
## get date wise inventory report ##
@csrf_exempt
def getMonthlyInventoryReport(request):
    month = request.POST.get('month')
    year = request.POST.get('year')
    warehouse = request.POST.get('warehouse')
    result = []
    try:
        stock_in_data = ScannedBarcode.objects.filter(from_vendor=1,scanning_date__year=year,scanning_date__month=month)
        stock_out_data = ScannedBarcode.objects.filter(to_client=1,scanning_date__year=year,scanning_date__month=month)
        float_data = ScannedBarcode.objects.filter(to_technician=1,scanning_date__year=year,scanning_date__month=month)
        damage_data = ScannedBarcode.objects.filter(damage=1,scanning_date__year=year,scanning_date__month=month)
        if int(warehouse) == 0:
            total_stock_in = stock_in_data.count()
            total_stock_out = stock_out_data.count()
            total_float = float_data.count()
            total_damage = damage_data.count()

            stock_in = stock_in_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            stock_out = stock_out_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            floats = float_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            damage = damage_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
        else:
            total_stock_in = stock_in_data.filter(barcode__warehouse=warehouse).count()
            total_stock_out = stock_out_data.filter(barcode__warehouse=warehouse).count()
            total_float = float_data.filter(barcode__warehouse=warehouse).count()
            total_damage = damage_data.filter(barcode__warehouse=warehouse).count()
            
            stock_in = stock_in_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            stock_out = stock_out_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            floats = float_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            damage = damage_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
        stockin_data = []
        stockout_data = []
        damage_data = []
        float_data = []
        for i in stock_in:
            if request.user.is_superuser:
                barcodes = stock_in_data.filter(barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            else:
                barcodes = stock_in_data.filter(barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            result = {
                'item_name':i[0],
                'item':i[1],
                'total_scanned':total_scanned,
                'barcodes':barcodes,
            }
            stockin_data.append(result)
        for i in stock_out:
            if request.user.is_superuser:
                barcodes = stock_out_data.filter(barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            else:
                barcodes = stock_out_data.filter(barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            result = {
                'item_name':i[0],
                'item':i[1],
                'total_scanned':total_scanned,
                'barcodes': barcodes,
            }
            stockout_data.append(result)
        for i in floats:
            if request.user.is_superuser:
                barcodes = float_data.filter(barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            else:
                barcodes = float_data.filter(barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            result = {
                'item_name':i[0],
                'item':i[1],
                'total_scanned':total_scanned,
                'barcodes':barcodes,
            }
            damage_data.append(result)
        for i in damage:
            if request.user.is_superuser:
                barcodes = damage_data.filter(damage=1,barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            else:
                barcodes = damage_data.filter(damage=1,barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
                total_scanned = barcodes.count()
            result = {
                'item_name':i[0],
                'item':i[1],
                'total_scanned':total_scanned,
                'barcodes':barcodes,
            }
            damage_data.append(result)
        data = {
            'total_stock_in':total_stock_in,
            'total_stock_out':total_stock_out,
            'total_float':total_float,
            'total_damage':total_damage,
            'stock_in':stockin_data,
            'stock_out':stockout_data,
            'floats':float_data,
            'damage':damage_data,
        }
        return render(request, 'reports/monthly_report_info.html',{'result':data})
    except Exception as e:
        print(e)
        return render(request,'reports/monthly_report_info.html',{'result':result})

## export month wise inventory report ##
def month_name(number):
    months = ["Unknown","January","Febuary","March","April","May","June","July","August","September","October","November","December"]
    return months[int(number)]

@csrf_exempt
def exportMonthlyInventoryReport(request, month, year, warehouse):
    try:
        stock_in_data = ScannedBarcode.objects.filter(from_vendor=1,scanning_date__year=year,scanning_date__month=month)
        stock_out_data = ScannedBarcode.objects.filter(to_client=1,scanning_date__year=year,scanning_date__month=month)
        float_data = ScannedBarcode.objects.filter(to_technician=1,scanning_date__year=year,scanning_date__month=month)
        damage_data = ScannedBarcode.objects.filter(damage=1,scanning_date__year=year,scanning_date__month=month)
        if int(warehouse) == 0:
            total_stock_in = stock_in_data.count()
            total_stock_out = stock_out_data.count()
            total_float = float_data.count()
            total_damage = damage_data.count()

            stock_in = stock_in_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            stock_out = stock_out_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            floats = float_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            damage = damage_data.values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
        else:
            total_stock_in = stock_in_data.filter(barcode__warehouse=warehouse).count()
            total_stock_out = stock_out_data.filter(barcode__warehouse=warehouse).count()
            total_float = float_data.filter(barcode__warehouse=warehouse).count()
            total_damage = damage_data.filter(barcode__warehouse=warehouse).count()
            stock_in = stock_in_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            stock_out = stock_out_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            floats = float_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
            damage = damage_data.filter(barcode__warehouse=warehouse).values_list('barcode__po_details__item_details__name','barcode__po_details__item_details').distinct()
        stockin_data = []
        stockout_data = []
        damage_data = []
        float_data = []
        for i in stock_in:
            if request.user.is_superuser:
                barcodes = stock_in_data.filter(barcode__po_details__item_details=i[1])
            else:
                barcodes = stock_in_data.filter(barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
            result = {
                'item_name':i[0],
                'barcodes':barcodes,
            }
            stockin_data.append(result)
        for i in stock_out:
            if request.user.is_superuser:
                barcodes = stock_out_data.filter(barcode__po_details__item_details=i[1])
            else:
                barcodes = stock_out_data.filter(barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
            result = {
                'item_name':i[0],
                'barcodes': barcodes,
            }
            stockout_data.append(result)
        for i in floats:
            if request.user.is_superuser:
                barcodes = float_data.filter(barcode__po_details__item_details=i[1])
            else:
                barcodes = float_data.filter(barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
            result = {
                'item_name':i[0],
                'barcodes':barcodes,
            }
            damage_data.append(result)
        for i in damage:
            if request.user.is_superuser:
                barcodes = damage_data.filter(damage=1,barcode__po_details__item_details=i[1])
            else:
                barcodes = damage_data.filter(damage=1,barcode__warehouse=request.user.warehouse,barcode__po_details__item_details=i[1])
            result = {
                'item_name':i[0],
                'barcodes':barcodes,
            }
            damage_data.append(result)
        first_sheet = [total_stock_in, total_stock_out, total_float, total_damage]
        response = HttpResponse(content_type='application/ms-excel')
        file_name = 'Monthly_Report_'+ month_name(month)
        response['Content-Disposition'] = 'attachment; filename="{}.xls"'.format(file_name)

        wb = xlwt.Workbook(encoding='utf-8')
        bold_font_style = xlwt.XFStyle()
        bold_font_style.font.bold = True
        font_style = xlwt.XFStyle()
        # Frist Sheet for summary of stock in,stock out
        ws = wb.add_sheet('Monthly Report')
        # Sheet header, first row
        row_num = 1
        columns = ['Total Stock In', 'Total Stock Out', 'Total Float', 'Total Damage',]
        # print(len(columns))
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], bold_font_style)
        # Sheet body, remaining rows
        row_num += 1
        for col_num in range(len(first_sheet)):
            ws.write(row_num, col_num, first_sheet[col_num], font_style)
        # wb.save(response)
        # end of summary
        # stock in sheet..
        ws = wb.add_sheet('Stock In')
        columns = ['#SI', 'Item Name', 'Barcode',]
        row_num = 1
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], bold_font_style)
        for row in stockin_data:
            for info in row['barcodes']:
                row_num += 1
                ws.write(row_num, 0, row_num-1, font_style)
                ws.write(row_num, 1, row['item_name'], font_style)
                ws.write(row_num, 2, info.barcode.barcode, font_style)
        # wb.save(response)
        #end of stock in
        #stock out sheet..
        ws = wb.add_sheet('Stock Out')
        columns = ['#SI', 'Item Name', 'Barcode',]
        row_num = 1
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], bold_font_style)
        for row in stockout_data:
            for info in row['barcodes']:
                row_num += 1
                ws.write(row_num, 0, row_num-1, font_style)
                ws.write(row_num, 1, row['item_name'], font_style)
                ws.write(row_num, 2, info.barcode.barcode, font_style)
        # wb.save(response)
        # end of stock out
        # Float sheet..
        ws = wb.add_sheet('Floating')
        columns = ['#SI', 'Item Name', 'Barcode',]
        row_num = 1
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], bold_font_style)
        for row in float_data:
            for info in row['barcodes']:
                row_num += 1
                ws.write(row_num, 0, row_num-1, font_style)
                ws.write(row_num, 1, row['item_name'], font_style)
                ws.write(row_num, 2, info.barcode.barcode, font_style)
        # wb.save(response)
        # end of float
        # damage sheet..
        ws = wb.add_sheet('Damage')
        columns = ['#SI', 'Item Name', 'Barcode',]
        row_num = 1
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], bold_font_style)
        for row in damage_data:
            for info in row['barcodes']:
                row_num += 1
                ws.write(row_num, 0, row_num-1, font_style)
                ws.write(row_num, 1, row['item_name'], font_style)
                ws.write(row_num, 2, info.barcode.barcode, font_style)
        wb.save(response)
        # end of damage
        return response
    except Exception as e:
        messages.warning(request, e)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

### channel demand ###
def channelDemandAdd(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        warehouses = []
        stocks = []
        if request.user.is_superuser:
            warehouses = Warehouse.objects.exclude(name__icontains='float')
            stocks = Stock.objects.all().values_list('item','item__name').distinct()
            item_details = ItemDetails.objects.all()
        else:
            stocks = Stock.objects.filter(warehouse=request.user.warehouse).values_list('item','item__name')
            item_details = ItemDetails.objects.all()

        context = {
            'warehouses':warehouses,
            'stocks': stocks,
            'item_details': item_details,
        }
        return render(request,'channel_demand/add.html',context)

def save_channel_demand(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            name = request.POST.get('name')
            client_name = request.POST.get('client_name')
            month = request.POST.get('month')
            year = request.POST.get('year')
            created_by = request.user.id
            warehouse = request.POST.get('warehouse')
            devices = request.POST.getlist('device_type')
            quantity = request.POST.getlist('quantity')
            order_probability = request.POST.getlist('order_probability')
            weight = request.POST.getlist('weight')
            final_demand = request.POST.getlist('final_demand')

            data = {
                'name': name,
                'client_name': client_name,
                'month': month,
                'year': year,
                'created_by': created_by,
                'warehouse': warehouse,
            }
            cd_form = CDForm(data)
            if cd_form.is_valid():
                cdform = cd_form.save()
                zipped = zip(devices,quantity,order_probability,weight,final_demand)
                for devices,quantity,order_probability,weight,final_demand in zipped:
                    details = {
                        'channel': cdform.id,
                        'device_type': devices,
                        'quantity': quantity,
                        'final_demand': final_demand,
                        'order_probability': order_probability,
                        'weight': weight,
                    }
                    cddform = CDDetailsForm(details)
                    if cddform.is_valid():
                        cddform.save()
                    else:
                        for field in cddform:
                            for error in field.errors:
                                messages.warning(request, error)
                messages.success(request,'Saved Successfully!!')
                return redirect('add_channel_demand')
            else:
                for field in cd_form:
                    for error in field.errors:
                        messages.warning(request, error)
        messages.warning(request,'Wrong Method')
        return redirect('add_channel_demand')

  
### Forecast Report ###
@login_required
def forecastReport(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        warehouses = []
        stocks = []
        if request.user.is_superuser:
            warehouses = Warehouse.objects.exclude(name__icontains='float')
            stocks = Stock.objects.all().values_list('item','item__name').distinct()
        else:
            stocks = Stock.objects.filter(warehouse=request.user.warehouse).values_list('item','item__name')

        context = {
            'warehouses':warehouses,
            'stocks': stocks,
        }
        return render(request,'reports/forecast.html',context)

from statsmodels.tsa.ar_model import AutoReg
from collections import defaultdict

def forecast_value(data_list):
    # contrived dataset
    data = data_list
    # fit model
    model = AutoReg(data, lags=1)
    model_fit = model.fit()
    # make prediction
    yhat = model_fit.predict(len(data), len(data))
    return round(yhat[0],2)

MONTHS = ["None","January","Febuary","March","April","May","June","July","August","September","October","November","December"]
@csrf_exempt
def forecastReportInfo(request):
    items = request.POST.getlist('items[]')
    warehouse = request.POST.get('warehouse')
    result = []
    item_name = []
    item_price_and_qty = []
    total = []
    total_data = []
    unit_price = []
    quantity, in_transit_qty = [],[]
    total_item_list = []
    month_wise_item_qty = defaultdict(list)
    forecast = defaultdict()
    final_demand = defaultdict()
    additional_demand = defaultdict()
    buffer_ = defaultdict()
    total_demand = defaultdict()
    required_qty = []
    try:
        now = datetime.datetime.now()
        current_month = now.month
        current_year = now.year
        for i in items:
            item_name.append(Item.objects.filter(id=i).first().name)
            unit_price.append(ItemDetails.objects.filter(item_id=i,warehouse=warehouse).last().unit_price)
            quantity.append(Stock.objects.filter(item_id=i,warehouse=warehouse).last().quantity)
            stocked_qty = Barcode.objects.filter(po_details__item_details__item_id=i,warehouse=warehouse).count()
            intransit_qty = sum([p.quantity for p in PreOrderDetails.objects.filter(item_details__item_id=i,item_details__warehouse=warehouse)])
            in_transit_qty.append(intransit_qty-stocked_qty)

        total_asset, intransit_asset = [], []
        zipped = zip(unit_price,quantity)
        intransit_zipped = zip(unit_price,in_transit_qty)
        for u, q in zipped:
            total_asset.append(round(u*q))
        for iu,iq in intransit_zipped:
            intransit_asset.append(round(iu*iq))
        for i in range(1,current_month+1):
            qty = {}
            for j in items:
                qty[j] = ScannedBarcode.objects.filter(from_vendor=1,scanning_date__year=current_year,scanning_date__month=i,barcode__po_details__item_details__item=j,barcode__warehouse=warehouse).count()
            total_item_list.append(qty)
            data = {
                'month': MONTHS[i],
                'year': current_year,
                'datas': qty.values(),
                'total': sum([i for i in qty.values()]),
            }
            result.append(data)
        if(current_month < 12):
            previous_month = current_month - 12
            previous_year = current_year - 1
            for i in range(-1, previous_month-1, -1):
                index = MONTHS.index(MONTHS[i])
                qty = {}
                for j in items:
                    qty[j] = ScannedBarcode.objects.filter(from_vendor=1,scanning_date__year=previous_year,scanning_date__month=index,barcode__po_details__item_details__item=j,barcode__warehouse=warehouse).count()
                total_item_list.append(qty)
                data = {
                    'month': MONTHS[i],
                    'year': previous_year,
                    'datas': qty.values(),
                    'total': sum([j for j in qty.values()]),
                }
                result.insert(0, data)

        item_wise_total = {}
        item_wise_max = {}
        item_wise_min = {}
        item_wise_avg = {}

        for i in total_item_list:
            for key, val in i.items():
                item_wise_total[key] = item_wise_total.get(key,0) + val
                month_wise_item_qty[key].append(val)
        for i in items:
            item_wise_min[i] = min(d[i] for d in total_item_list)
            item_wise_max[i] = max(d[i] for d in total_item_list)
            item_wise_avg[i] = round(sum([d[i] for d in total_item_list]) / len(total_item_list))
        current_month = current_month+1 if current_month < 12 else 12
        for k, v in month_wise_item_qty.items():
            fv = forecast_value(v)
            forecast[k] = fv
            fd = sum([c.final_demand for c in ChannelDemandDetails.objects.filter(channel__month=current_month,channel__year=current_year,device_type__item_id=k)])
            final_demand[k] = fd
            ad = fv - fd if fv > fd else fd - fv
            additional_demand[k] = ad
            bf = round((ad+fv)*0.02 ,2)
            buffer_[k] = bf
            total_demand[k] = round(fv+ad+bf, 2)
        total_data.append({'month':'Total','data':item_wise_total.values(),'total':sum([j for j in item_wise_total.values()])})
        total_data.append({'month':'Avg','data':item_wise_avg.values(),'total':sum([j for j in item_wise_avg.values()])})
        total_data.append({'month':'Max','data':item_wise_max.values(),'total':sum([j for j in item_wise_max.values()])})
        total_data.append({'month':'Min','data':item_wise_min.values(),'total':sum([j for j in item_wise_min.values()])})
        zipped = zip(quantity,total_demand.values())
        for k, v in zipped:
            required_qty.append(round(v-k,2))
    except Exception as e:
        messages.warning(request, e)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    context = {
        'result': result,
        'item_name': item_name,
        'total_data': total_data,
        'unit_price': unit_price,
        'quantity': quantity,
        'total_asset': total_asset,
        'price': sum([q for q in total_asset]),
        'in_transit_qty':in_transit_qty,
        'intransit_asset':intransit_asset,
        'intransit_price':sum([q for q in intransit_asset]),
        'forecast_value':forecast.values(),
        'additional_demand': additional_demand.values(),
        'buffer': buffer_.values(),
        'total_demand': total_demand.values(),
        'required_qty': required_qty,
    }
    return render(request, 'reports/forecast_info.html',context)

@csrf_exempt
def forecastReportGraphInfo(request):
    items = request.POST.getlist('items[]')
    warehouse = request.POST.get('warehouse')
    result = []
    item_name = []
    item_price_and_qty = []
    total = []
    try:
        now = datetime.datetime.now()
        current_month = now.month
        current_year = now.year
        total_item_list = []
        for i in items:
            item_name.append(Item.objects.filter(id=i).first().name)
        total_price = []
        for i in range(1,current_month+1):
            qty = []
            for j in items:
                qty.append(ScannedBarcode.objects.filter(from_vendor=1,scanning_date__year=current_year,scanning_date__month=i,barcode__po_details__item_details__item=j,barcode__warehouse=warehouse).count())
            total_item_list.append(qty)
            data = {
                'month': MONTHS[i],
                'year': current_year,
                'datas': qty,
                'total': sum([i for i in qty]),
            }
            result.append(data)
            qty.insert(0,MONTHS[i]+"'"+str(current_year))
            total.append(qty)
        if(current_month < 12):
            previous_month = current_month - 12
            previous_year = current_year - 1
            for i in range(-1, previous_month-1, -1):
                index = MONTHS.index(MONTHS[i])
                qty = []
                for j in items:
                    qty.append(ScannedBarcode.objects.filter(from_vendor=1,scanning_date__year=previous_year,scanning_date__month=index,barcode__po_details__item_details__item=j,barcode__warehouse=warehouse).count())
                total_item_list.append(qty)
                data = {
                    'month': MONTHS[i],
                    'year': previous_year,
                    'datas': qty,
                    'total': sum([j for j in qty]),
                }
                result.insert(0, data)
                qty.insert(0,MONTHS[i]+"'"+str(previous_year))
                total.insert(0, qty)
    except Exception as e:
        print(e)
        pass
    context = {
        'result': result,
        'total': total,
        'item_name': item_name,
    }
    return HttpResponse(
        json.dumps(context),
        content_type="application/json"
    )
