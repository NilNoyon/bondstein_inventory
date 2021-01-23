from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import *

# Create your views here.

#########################
## Clients
#########################

def clientList(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        clients = Clients.objects.all().select_related()
        context = {'clients': clients}
        return render(request, "clients/list.html", context)

def addClient(request):
    if not request.user.is_active:
        return redirect('users:index')
    else:
        if request.user.is_active:
            if request.method == 'POST':
                request.POST = request.POST.copy()

                form = SupplierForm(request.POST)
                if form.is_valid():
                    form.save()
                    message = 'Clients added successfully!'
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