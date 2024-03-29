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
	total_sell = models.IntegerField(default=0)
	total_return = models.IntegerField(default=0)

	class Meta:
		db_table = 'floating_sales_order'

	def get_total_item(self):
		return FloatingSalesDetails.objects.filter(floating_order=self.id).count()

	def get_total_sell(self):
		return FloatingSalesDetails.objects.filter(floating_order=self.id,is_sold=True).count()

class FloatingSalesDetails(models.Model):
	floating_order = models.ForeignKey(FloatingSalesOrder, on_delete=models.CASCADE, null=True, blank=True)
	item_details = models.ForeignKey(ItemDetails, on_delete=models.CASCADE, null=True)
	barcode 	= models.ForeignKey(Barcode, on_delete=models.CASCADE, null=True)
	is_sold		= models.BooleanField(default=0)
	updated_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'floating_sales_details'

class ChannelDemand(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)
	client_name = models.CharField(max_length=100, null=True, blank=True)
	month = models.IntegerField(default=0)
	year = models.IntegerField(default=2021)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True)
	warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True,blank=True)

	class Meta:
		db_table = 'channel_demands'

class ChannelDemandDetails(models.Model):
	channel = models.ForeignKey(ChannelDemand, on_delete=models.CASCADE, null=True, blank=True)
	device_type = models.ForeignKey(ItemDetails, on_delete=models.CASCADE, null=True)
	quantity = models.IntegerField(default=0)
	final_demand = models.IntegerField(default=0)
	order_probability = models.CharField(max_length=20, null=True, blank=True)
	weight = models.FloatField(default=0)
	warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True)

	class Meta:
		db_table = 'channel_demand_details'

class ForecastData(models.Model):
	MONTH_CHOICES = [
        ('January', '1'),
        ('February', '2'),
        ('March', '3'),
        ('April', '4'),
        ('May', '5'),
        ('June', '6'),
        ('July', '7'),
        ('August', '8'),
        ('September', '9'),
        ('October', '10'),
        ('November', '11'),
        ('December', '12'),
    ]
	month = models.CharField(max_length=10,choices=MONTH_CHOICES,default='0')
	year = models.IntegerField(default=timezone.now().year)
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'forecast_data'

	def total_idq(self):
		return sum([obj.id_quantity for obj in ForecastDetails.objects.filter(forecast=self.id)])

	def total_iq(self):
		return sum([obj.i_quantity for obj in ForecastDetails.objects.filter(forecast=self.id)])

class ForecastDetails(models.Model):
	forecast = models.ForeignKey(ForecastData, on_delete=models.CASCADE, null=True, blank=True)
	item_details = models.ForeignKey(ItemDetails, on_delete=models.CASCADE, null=True, blank=True)
	item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
	id_quantity = models.IntegerField(default=0)
	i_quantity = models.IntegerField(default=0)

	class Meta:
		db_table = 'forecast_details'