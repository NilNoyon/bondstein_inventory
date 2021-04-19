from django.db import models
from django.utils import timezone
from users.models import *
from pre_order.models import *

# Create your models here.

class Client(models.Model):
	name = models.CharField(max_length = 50, unique = True)
	contact = models.CharField(max_length = 150, null=True, blank=True)
	address = models.CharField(max_length = 150, null=True, blank=True)
	email  = models.EmailField(unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'clients'

	@property
	def responsibleperson_set(self):
	    return ResponsiblePerson.objects.filter(client=self.pk)

class ResponsiblePerson(models.Model):
	name = models.CharField(max_length = 50)
	contact = models.CharField(max_length = 150, null=True, blank=True)
	address = models.CharField(max_length = 150, null=True, blank=True)
	email = models.EmailField(unique=True)
	client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'responsible_persons'

class SalesOrder(models.Model):
	so_no = models.CharField(max_length=30, unique=True)
	client = models.CharField(max_length=200, null=True, blank=True)
	responsible_person = models.CharField(max_length=200, null=True, blank=True)
	so_amount = models.IntegerField(blank=True,null=True)
	so_date = models.DateTimeField(default=timezone.now)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True)
	warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True,blank=True)
	remarks = models.CharField(max_length=100, null=True, blank=True)
	is_stock_out = models.BooleanField(default=0)
	is_warehouse_out = models.BooleanField(default=0)
	is_deleted = models.BooleanField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	payment_status = models.BooleanField(default=0)
	delivery_person = models.CharField(max_length=200, null=True, blank=True)

	class Meta:
		db_table = 'sales_orders'

	def total_qty(self):
		return sum([obj.quantity for obj in SODetails.objects.filter(so=self.id)])

class SODetails(models.Model):
	so = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, null=True,blank=True)
	item_details = models.ForeignKey(ItemDetails, on_delete=models.CASCADE, null=True,blank=True)
	price = models.IntegerField(blank=True,null=True)
	quantity = models.IntegerField()
	barcode = models.ForeignKey(Barcode, on_delete=models.CASCADE, null=True,blank=True)
	remarks = models.CharField(max_length=100, null=True, blank=True)

	class Meta:
		db_table = 'sales_order_details'

class STChallan(models.Model):
	from_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True,blank=True, related_name='from_warehouse')
	to_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True,blank=True, related_name='to_warehouse')
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True)
	remarks = models.CharField(max_length=100, null=True, blank=True)
	challan_no = models.CharField(max_length=30, unique=True)
	is_warehouse_out = models.BooleanField(default=0)
	is_received = models.BooleanField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	delivery_person = models.CharField(max_length=200, null=True, blank=True)

	class Meta:
		db_table = 'stock_transfer_challans'

	def total_qty(self):
		return sum([obj.quantity for obj in STCDetails.objects.filter(stc=self.id)])

class STCDetails(models.Model):
	stc = models.ForeignKey(STChallan, on_delete=models.CASCADE, null=True,blank=True)
	item_details = models.ForeignKey(ItemDetails, on_delete=models.CASCADE, null=True,blank=True)
	quantity = models.IntegerField()
	barcode = models.ForeignKey(Barcode, on_delete=models.CASCADE, null=True,blank=True)
	remarks = models.CharField(max_length=100, null=True, blank=True)

	class Meta:
		db_table = 'stc_details' #stock transfer challan details

# scanned barcode for sepcific item...
class STCBarcode(models.Model):
	stcd 		= models.ForeignKey(STCDetails, on_delete=models.CASCADE, null=True,blank=True)
	barcode 	= models.ForeignKey(Barcode, on_delete=models.CASCADE, null=True,blank=True)
	created_at 	= models.DateTimeField(auto_now_add=True)
	class Meta:
		db_table = 'stc_barcodes' #stock transfer challan's scanned barcodes

# Handover to technician
class FloatingSalesOrder(models.Model):
	order_no = models.CharField(max_length=30, unique=True)
	warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True,blank=True)
	takeover_date = models.DateTimeField(default=timezone.now)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True)
	remarks = models.CharField(max_length=100, null=True, blank=True)
	is_stock_out = models.BooleanField(default=0)
	is_warehouse_out = models.BooleanField(default=0)
	is_deleted = models.BooleanField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	delivery_person = models.CharField(max_length=200, null=True, blank=True)
	phone_no = models.CharField(max_length=14, null=True, blank=True)
	total_item = models.IntegerField(default=0)

	class Meta:
		db_table = 'floating_sales_order'

class FloatingSalesDetails(models.Model):
	floating_order = models.ForeignKey(FloatingSalesOrder, on_delete=models.CASCADE, null=True, blank=True)
	item_details = models.ForeignKey(ItemDetails, on_delete=models.CASCADE, null=True)
	barcode 	= models.ForeignKey(Barcode, on_delete=models.CASCADE, null=True)
	is_sold		= models.BooleanField(default=0)

	class Meta:
		db_table = 'floating_sales_details'

	