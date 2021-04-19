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
		pprint.pprint(response_data)
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
	                'client': prod_details.so.client.name,
	                'warehouse': prod_details.so.warehouse.name,
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
        if Stock.objects.filter(item=obj.item_details.item.id).last().quantity < int(total_scanned_qty):
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

        last_stock_qty = Stock.objects.filter(item=obj.item_details.item.id).last().quantity
        print(last_stock_qty)
        if last_stock_qty > 0:
            Stock.objects.filter(item=obj.item_details.item.id).update(quantity=last_stock_qty - int(total_scanned_qty),updated_at=datetime.datetime.now())

        data = {
            'item': obj.item_details.item.id,
            'quantity': int(total_scanned_qty),
            'activity': request.POST.get('action'),
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
                warehouses = Warehouse.objects.exclude(id=request.user.warehouse.id).all()
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

@login_required
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
                last_stock_qty = Stock.objects.filter(item=obj.item_details.item.id).last().quantity
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

                data = {
                    'item': obj.item_details.item.id,
                    'quantity': int(total_scanned_qty),
                    'activity': request.POST.get('action'),
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
            print(code)
            for i in code:
                barcode = Barcode.objects.get(id=i)
                barcode.warehouse = order_details.to_warehouse
                barcode.save()
                print('hello')

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
