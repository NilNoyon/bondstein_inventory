from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import *
from .forms import *
from users.models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
import json
import datetime
import tabula
import re
import os
import pprint
import xlrd
from tika import parser
from django.core.files.storage import FileSystemStorage
from notifications.signals import notify

# Create your views here.
@login_required
def uploadPDF(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        suppliers = Supplier.objects.all()
        status = Status.objects.filter(name__icontains='In Transit')

        context = {
            'suppliers':suppliers,
            'status':status,
        }
        return render(request, 'preorder/upload_pdf.html',context)

def extract_information(file):
    response_data = []
    raw = parser.from_file(file)
    text = str(raw['content'])
    po = re.search("BONDS/.*", text)
    date = re.search("Date:.*", text)
    quot = re.search("Quot. :.*", text)

    po_no = po.group()
    shipping_date = date.group().split(": ")[1]
    quot = quot.group().split(":")[1]

    df = tabula.read_pdf(file, output_format="json", pages="all", lattice=True,)
    sl = []
    item_name = []
    item_details = []
    quantity = []
    amount = []
    unit_price = []
    for k in range(0,len(df)):
        for i in range(1,len(df[k]['data'])):
            for j in range(len(df[k]['data'][i])):
                if j == 0:
                    continue
                elif j == 1:
                    if len(df[k]['data'][i][j]['text']) > 0:
                        if df[k]['data'][i][j]['text'] == 'Item Name' or df[k]['data'][i][j]['text'] == 'GRAND  TOTAL':
                            continue
                        else:
                            item_name.append(df[k]['data'][i][j]['text'])
                    else:
                        continue
                elif j == 2:
                    if len(df[k]['data'][i][j]['text']) > 0:
                        item_details.append(df[k]['data'][i][j]['text'])
                    else:
                        continue
                elif j == 3:
                    if len(df[k]['data'][i][j]['text']) > 0:
                        if 'Quantity' in df[k]['data'][i][j]['text']:
                            continue
                        else:
                            quantity.append(df[k]['data'][i][j]['text'])
                    else:
                        continue
                elif j == 4:
                    if len(df[k]['data'][i][j]['text']) > 0:
                        if 'PURCHASE' in df[k]['data'][i][j]['text'] or 'Unit Price' in df[k]['data'][i][j]['text']:
                            continue
                        else:
                            unit_price.append(df[k]['data'][i][j]['text'])
                    else:
                        continue
                else:
                    if len(df[k]['data'][i][j]['text']) > 0:
                        if 'Amount' in df[k]['data'][i][j]['text']:
                            continue
                        else:
                            amount.append(df[k]['data'][i][j]['text'])
                    else:
                        continue
    data = {
        'po_no':po_no,
        'shipping_date':shipping_date,
        'quot':quot,
        'item_name':item_name[0:len(unit_price)],
        'quantity':quantity,
        'amount':amount,
        'unit_price':unit_price,
        'grand_total':item_details[-1],
    }
    pprint.pprint(data)
    response_data.append(data)
    return response_data

def savePDF(request):
    if request.method == 'POST':
        if request.FILES['pdf']:
            file = request.FILES['pdf']
            fs = FileSystemStorage()
            order_count = PreOrder.objects.all().count()
            po = 'PO-'+str(order_count+1)+'.pdf'
            filename = fs.save(po, file)
            uploaded_file_url = os.path.abspath("assets/uploads/%s" % filename)

            data = extract_information(uploaded_file_url)
            grand_total = data[0]['grand_total']
            pre_order_info = {
                'order_no': data[0]['po_no'],
                'order_date': request.POST.get('order_date'),
                'quot': 'N/a',
                'supplier': request.POST.get('supplier'),
                'status': request.POST.get('status'),
                'created_by': request.user.id,
                'prepared_by': request.POST.get('prepared_by'),
                'checked_by': request.POST.get('checked_by'),
                'order_grand_total': grand_total.replace(",",""),
            }
            order_form = PreOrderForm(pre_order_info)
            if order_form.is_valid():
                frm = order_form.save()
                item_details = []

                counter = 0
                for i in data[0]['item_name']:
                    itm, created = Item.objects.get_or_create(name=i,category_id=1)
                    itmd, created = ItemDetails.objects.get_or_create(name=i,item=itm,unit_price=data[0]['unit_price'][counter].replace(",",""),warehouse_id=1)
                    item_details.append(itmd.id)
                    counter += 1
                qty = data[0]['quantity']
                amount = data[0]['amount']
                zipped = zip(item_details,qty,amount)
                shipping_date = datetime.datetime.strptime(data[0]['shipping_date'], "%d-%b-%Y")
                for item_details,qty,amount in zipped:
                    try:
                        amount = int(float(amount.replace(",","")))
                    except:
                        amount = int(float(amount))
                    data = {
                        'pre_order':frm.id,
                        'item_details':item_details,
                        'quantity':qty,
                        'amount':amount,
                        'shipping_date':shipping_date,
                        'status':frm.status.id,
                        'created_by':request.user.id,
                    }
                    pform = PreOrderDetailsForm(data)
                    if pform.is_valid():
                        pform.save()
                    else:
                        for field in pform:
                            for error in field.errors:
                                messages.warning(request, "%s : %s" % (field.name, error))
            else:
                for field in order_form:
                    for error in field.errors:
                        messages.warning(request, "%s : %s" % (field.name, error))
            return redirect('pre_order_list')
        else:
            message = 'File no uploaded!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        message = 'Method is not allowed!'
        messages.warning(request, message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def add_manual_po(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        form = PreOrderForm()
        suppliers = Supplier.objects.all()
        status = Status.objects.filter(name__icontains='In Transit')
        items = Item.objects.all()
        item_details = ItemDetails.objects.all()
        context = {
            'form':form,
            'suppliers':suppliers,
            'status':status,
            'items':items,
            'item_details':item_details,
        }
        return render(request, 'preorder/manual_preorder_form.html',context)

@csrf_exempt
def getItemDetailsForItem(request):
    if not request.user.is_authenticated:
        return redirect('index')
    else:

        item_details = ItemDetails.objects.filter(item = request.POST.get('item'))

        response_data = []
        for i in item_details:
            data = {
                'id':i.id,
                'name':i.name,
            }
            response_data.append(data)
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

@login_required
def preOrderList(request):
	if not request.user.is_active:
		return redirect('users:index')
	else:
		preorders = PreOrder.objects.filter(is_deleted=False)

		return render(request, 'preorder/index.html',{'preorders':preorders})

@login_required
def preOrderDetailsList(request,id):
	if not request.user.is_active:
		return redirect('users:index')
	else:
		pre_order_details = PreOrderDetails.objects.filter(pre_order=id)
		return render(request, 'preorder/details_list.html',{'details':pre_order_details})

@login_required
def save_preorder(request):
    if request.method == 'POST':
        request.POST = request.POST.copy()
        request.POST['created_by'] = request.user.id
        form = PreOrderForm(request.POST)
        if form.is_valid():
            poform = form.save()
            item_details = request.POST.getlist('item_details')
            quantity = request.POST.getlist('quantity')
            amount = request.POST.getlist('amount')
            shipping_date = request.POST.get('shipping_date')
            status = request.POST.get('status')
            created_by = request.user.id

            zipped = zip(item_details,quantity,amount)
            for item_details,quantity,amount in zipped:
                data = {
                    'pre_order':poform.id,
                    'item_details':item_details,
                    'quantity':quantity,
                    'amount':amount,
                    'shipping_date':shipping_date,
                    'status':status,
                    'created_by':request.user.id,
                }
                pod_form = PreOrderDetailsForm(data)
                if pod_form.is_valid():
                    pod_form.save()
                else:
                    for field in pod_form:
                        for error in field.errors:
                            messages.warning(request, "%s : %s" % (field.name, error))
        else:
            for field in form:
                for error in field.errors:
                    messages.warning(request, "%s : %s" % (field.name, error))
        return redirect('pre_order_list')
    else:
        message = 'Method is not allowed!'
        messages.warning(request, message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def deletePO(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                order = PreOrder.objects.get(id=request.POST.get('id'))
                order_details = PreOrderDetails.objects.filter(pre_order=request.POST.get('id'))
                order_details.delete()
                order.delete()
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


def generateBarcode(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            item_details = PreOrderDetails.objects.get(id=request.POST.get('item'))
            bid = []
            for i in range(int(request.POST.get('quantity'))):
                counter = Barcode.objects.filter(po_details=item_details.id).count()
                sku_base = format(item_details.item_details.id+i+1, '04d')
                bst_base = format(item_details.item_details.item.id+i+1, '04d')

                barcode = str(sku_base) +"-"+str(bst_base)+"-"+str(counter+1)
                data = {
                    'barcode':barcode,
                    'sku':str(sku_base),
                    'bst':str(bst_base),
                    'po_details': item_details.id,
                    'warehouse': item_details.item_details.warehouse.id,
                    'created_by': request.user.id,
                }
                bform = BarcodeForm(data)
                if bform.is_valid():
                    bc = bform.save()
                    bid.append(bc.id)
            barcodes = Barcode.objects.filter(id__in=bid)
            return render(request,'barcode/barcode.html',{'barcodes':barcodes})
        else:
            pre_orders = PreOrder.objects.all()
            item_details = PreOrderDetails.objects.all()
            return render(request,'barcode/form.html',{'orders':pre_orders})

def generateManualBarcode(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            file = request.FILES['barcode_excel']
            fs = FileSystemStorage()
            xcel = 'B-'+str(datetime.datetime.now().date())+'.xls'
            filename = fs.save(xcel, file)
            xl_workbook = xlrd.open_workbook("assets/uploads/%s" % xcel)
            sheet = xl_workbook.sheet_by_index(0)
            sheet.cell_value(1, 0)
            number_of_rows = sheet.nrows # Extracting number of rows
            codes = []
            item_details = PreOrderDetails.objects.get(id=request.POST.get('item'))
            quantity = request.POST.get('quantity')
            bid = []

            for row in range(1, number_of_rows):
                codes.append(int(sheet.cell(row,0).value))

            if Barcode.objects.filter(barcode__in=codes).exists():
                message = 'Barcodes are already exist!'
                messages.warning(request, message)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            elif not len(codes) == int(quantity):
                message = messages.warning(request, "Quantity:%s and Total Barcode: %s not matched" % (quantity, len(codes)))
                messages.warning(request, message)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                for i in codes:
                    counter = Barcode.objects.filter(po_details=item_details.id).count()
                    data = {
                        'barcode':i,
                        'po_details': item_details.id,
                        'warehouse': item_details.item_details.warehouse.id,
                        'created_by': request.user.id,
                    }
                    bform = BarcodeForm(data)
                    if bform.is_valid():
                        bc = bform.save()
                        bid.append(bc.id)
            barcodes = Barcode.objects.filter(id__in=bid)
            return render(request,'barcode/barcode.html',{'barcodes':barcodes})
        else:
            pre_orders = PreOrder.objects.all()
            return render(request,'barcode/manual_form.html',{'orders':pre_orders})

@csrf_exempt
def getOrderWiseItem(request):
    response_data = []
    if request.POST.get('order'):
        pre_order_details = PreOrderDetails.objects.filter(pre_order=request.POST.get('order'))


        for i in pre_order_details:
            data = {
                'id':i.id,
                'name':i.item_details.name,
                'quantity':i.quantity,
            }
            response_data.append(data)
        return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
    else:
        return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )

@csrf_exempt
def getItemQuantity(request):
    response_data = {}
    if request.POST.get('item'):
        item_details = PreOrderDetails.objects.get(id=request.POST.get('item'))
        response_data['quantity'] = item_details.quantity
        return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
    else:
        return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
@csrf_exempt
def getItemBarcode(request):
    if request.POST.get('item') and request.POST.get('quantity'):
        item_details = PreOrderDetails.objects.get(item_details=request.POST.get('item'))
        sku_base = format(item_details.item_details.id, '04d')
        bst_base = format(item_details.item_details.item.id, '04d')
        bid = []
        for i in range(int(request.POST.get('quantity'))):
            counter = Barcode.objects.filter(po_details=item_details.id).count()

            data = {
                'barcode':barcode,
                'sku':sku_base + (counter + 1),
                'bst':bst_base + (counter + 1),
                'po_details_id': item_details.id,
                'warehouse_id': item_details.item_details.warehouse.id,
                'created_by_id': request.user.id,
            }
            bform = BarcodeForm(data)
            if bform.is_valid():
                bc = bform.save()
                bid.append(bc.id)
        barcodes = Barcode.objects.filter(id__in=bid)
        return render(request,'barcode/barcode.html',{'barcodes':barcodes})

@login_required
def scan(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        return redirect(request, 'scan/scan.html')

@login_required
def stockIn(request, id):
	if not request.user.is_active:
		return redirect('users:index')
	else:
		order_details = PreOrderDetails.objects.get(id=id)
		# total_item = order_details.quantity
		try:
			total_scanned = ScannedBarcode.objects.get(barcode__po_details=id,from_vendor=True).counter()
		except:
			total_scanned = 0
		context = {
			'order_details':order_details,
			'total_item':int(order_details.quantity),
			'total_scanned':int(total_scanned),
			'action':'stock in',
			'from_vendor':True,
			'to_client':False,
			'to_technician':False,
			'damage':False,
		}
		return render(request,'scan/scan.html',context)

@csrf_exempt
def scanBCB(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            pre_order_details = request.POST.get('pre_order_details')
            order_details = PreOrderDetails.objects.get(id=pre_order_details)
            code = request.POST.get('barcode')
            if not Barcode.objects.filter(barcode=code).exists(): # if barcode not exist in our system, barcode will store then return
                counter = Barcode.objects.filter(po_details=pre_order_details).count()
                data = {
                    'barcode':code,
                    'po_details': order_details,
                    'warehouse': order_details.item_details.warehouse.id,
                    'created_by': request.user.id,
                }
                bform = BarcodeForm(data)
                if bform.is_valid():
                    bc = bform.save()
                data = scanTask(bc, order_details)
            else:
                bc = Barcode.objects.get(barcode=code)
                data = scanTask(bc, order_details)
            return HttpResponse(
                json.dumps(data),
                content_type="application/json"
            )
        else:
            message = 'Method is not allowed!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def scanTask(barcode, prod_details):
    if ScannedBarcode.objects.filter(barcode=barcode).exists():
        status = 'Duplicate Barcode'
        bc_data = {}
    else:
        try:
            status = 'success'
            current_date = datetime.datetime.today()
            bc_data = {
                'bid': barcode.id,
                'barcode': barcode.barcode,
                'item_name': prod_details.item_details.name, 
                'unit': prod_details.item_details.unit, 
                'unit_price': prod_details.item_details.unit_price,
                'supplier': prod_details.pre_order.supplier.name,
                'warehouse': prod_details.item_details.warehouse.name,
                'stock_in_date': current_date.strftime("%Y-%m-%d"),
            }
        except ScannedBarcode.DoesNotExist:
            status = 'Not Found'
            bc_data = {}

    response_data = {'status': status, 'bc_data': bc_data}
    return response_data


def storeScanData(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.method == 'POST':
            saveScan(request)
            return redirect('pre_order_list')
        else:
            message = 'Method is not allowed!'
            messages.warning(request, message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def saveScan(request):
    request.POST = request.POST.copy()
    scan_user = request.user.id
    barcode = request.POST.getlist('barcode')
    scanning_date = request.POST.getlist('stock_in_date')
    pre_order_details = request.POST.get('pre_order_details')
    from_vendor = request.POST.get('from_vendor')
    to_client = request.POST.get('to_client')
    to_technician = request.POST.get('to_technician')
    damage = request.POST.get('damage')
    try:
        obj = PreOrderDetails.objects.get(id=pre_order_details)
        total_scanned_qty = len(barcode)
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
            else:
                for field in spForm:
                    for error in field.errors:
                        messages.warning(request, "%s : %s" % (field.name, error))

        try:
            last_stock_qty = Stock.objects.filter(item=obj.item_details.item.id).last().quantity
            order_qty = ScannedBarcode.objects.filter(barcode__barcode__po_details=obj.id).count()
        except:
            last_stock_qty = 0
            order_qty = total_scanned_qty

        if last_stock_qty > 0:
            Stock.objects.filter(item=obj.item_details.item.id).update(quantity=last_stock_qty + int(total_scanned_qty))
        else:
            data = {
                'item': obj.item_details.item.id,
                'quantity': last_stock_qty + int(total_scanned_qty),
                'updated_by': request.user.id,
            }
            sform = StockForm(data)
            if sform.is_valid():
                ms = sform.save()
                if obj.quantity == order_qty:
                    PreOrderDetails.objects.filter(id=obj.id).update(status=Status.objects.get(name='Complete').id)
                elif obj.quantity > order_qty:
                    PreOrderDetails.objects.filter(id=obj.id).update(status=Status.objects.get(name='In Complete').id)

                last_status = PreOrderDetails.objects.get(id=obj.id)
                PreOrder.objects.filter(id=obj.pre_order.id).update(status=last_status.status)
            else:
                for field in msform:
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


def stockList(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        stocks = Stock.objects.all().order_by('-created_at')

        return render(request,'stocks/list.html',{'stocks':stocks})
@login_required
def stockLog(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        stocks = StockLog.objects.all().order_by('-created_at')

        return render(request,'stocks/log_list.html',{'stocks':stocks})
@login_required
def scannedProductList(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_superuser:
            scanned_products = ScannedBarcode.objects.all().values_list('barcode__po_details__pre_order__order_no','barcode__po_details__item_details__name').distinct()
        else:
            scanned_products = ScannedBarcode.objects.all().values_list('barcode__po_details__pre_order__order_no','barcode__po_details__item_details__name').distinct()
        data = []
        for i in scanned_products:
            result = {
                'order_no':i[0],
                'item_name':i[1],
                'total_scanned':ScannedBarcode.objects.filter(barcode__po_details__pre_order__order_no=i[0],barcode__po_details__item_details__name=i[1]).count(),
            }
            data.append(result)

        pprint.pprint(data)
        return render(request,'stocks/scanned_product.html',{'scanned_products':data})


#########################
## Suppliers
#########################

def supplierList(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        suppliers = Supplier.objects.all()
        context = {'suppliers': suppliers}
        return render(request, "suppliers/list.html", context)

def addSupplier(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                request.POST = request.POST.copy()

                form = SupplierForm(request.POST)
                if form.is_valid():
                    form.save()
                    message = 'Supplier added successfully!'
                    messages.success(request, message)
                else:
                    for field in form:
                        for error in field.errors:
                            messages.warning(request, "%s : %s" % (field.name, error))
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('supplier_list')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def deleteSupplier(request):
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
def getSupplier(request):
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
def updateSupplier(request):
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
## Category and Item Head
#########################

def itemCategories(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        items = Item.objects.all()
        item_categories = ItemCategory.objects.all()
        context = {'items': items,'item_categories':item_categories}
        return render(request, "items/list.html", context)

def addCategory(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                request.POST = request.POST.copy()

                form = ItemCategoryForm(request.POST)
                if form.is_valid():
                    form.save()
                    message = 'Category added successfully!'
                    messages.success(request, message)
                else:
                    for field in form:
                        for error in field.errors:
                            messages.warning(request, "%s : %s" % (field.name, error))
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('item_categories')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def deleteCategory(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                category = ItemCategory.objects.get(id=request.POST.get('id'))
                category.delete()
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
def getCategory(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                category = ItemCategory.objects.get(id=request.POST.get('id'))
                response_data = {}
                response_data['name'] = category.name
                response_data['description'] = category.description
                print(response_data)
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def updateCategory(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                category = ItemCategory.objects.get(id=request.POST.get('id'))
                category.name = request.POST.get('name')
                category.description = request.POST.get('description')
                category.save()
                message = 'Category Updated successfully!'
                messages.success(request, message)
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('item_categories')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

## Item Head..
def addItem(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                request.POST = request.POST.copy()

                form = ItemHeadForm(request.POST)
                if form.is_valid():
                    form.save()
                    message = 'Item Head added successfully!'
                    messages.success(request, message)
                else:
                    for field in form:
                        for error in field.errors:
                            messages.warning(request, "%s : %s" % (field.name, error))
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('item_categories')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def deleteItem(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                item = Item.objects.get(id=request.POST.get('id'))
                item.delete()
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
def getItem(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                item = Item.objects.get(id=request.POST.get('id'))
                response_data = {}
                response_data['name'] = item.name
                response_data['category'] = item.category
                response_data['description'] = item.description

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def updateItem(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                item = Item.objects.get(id=request.POST.get('id'))
                item.name = request.POST.get('name')
                item.description = request.POST.get('description')
                item.category = request.POST.get('description')
                item.save()
                message = 'Item Head Updated successfully!'
                messages.success(request, message)
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('item_categories')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#########################
## Items
#########################

def itemList(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        item_heads = Item.objects.all()
        items = ItemDetails.objects.all()
        suppliers = Supplier.objects.all()
        warehouses = Warehouse.objects.all()
        context = {
            'items': items,
            'item_heads':item_heads,
            'suppliers':suppliers,
            'warehouses':warehouses,
            }
        return render(request, "items/details_list.html", context)

def addItemDetails(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                request.POST = request.POST.copy()
                request.POST['name'] = request.POST.get('name').title()
                form = ItemDetailsForm(request.POST)
                if form.is_valid():
                    item = form.save()
                    notify.send(request.user, recipient=User.objects.filter(is_superuser=True).first(),verb="has added a new item {0}".format(str(item.name)))
                    message = 'Item added successfully!'
                    messages.success(request, message)
                else:
                    for field in form:
                        for error in field.errors:
                            messages.warning(request, "%s : %s" % (field.name, error))
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('items')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def deleteItemDetails(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                item = ItemDetails.objects.get(id=request.POST.get('id'))
                item.delete()
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
def getItemDetails(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                item = ItemDetails.objects.get(id=request.POST.get('id'))
                response_data = {}
                response_data['name'] = item.name
                response_data['item'] = item.item.id
                response_data['unit'] = item.unit
                response_data['unit_price'] = item.unit_price
                response_data['supplier'] = item.supplier.id
                response_data['warehouse'] = item.warehouse.id

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def updateItemDetails(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                item = ItemDetails.objects.get(id=request.POST.get('id'))
                item.name = request.POST.get('name').title()
                item.item = request.POST.get('item')
                item.unit = request.POST.get('unit')
                item.unit_price = request.POST.get('unit_price')
                item.supplier = request.POST.get('supplier')
                item.warehouse = request.POST.get('warehouse')
                item.save()
                message = 'Item Updated successfully!'
                messages.success(request, message)
            else:
                message = 'Method is not allowed!'
                messages.warning(request, message)
            return redirect('item_categories')
        else:
            message = 'You are not authorised!'
            messages.warning(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
