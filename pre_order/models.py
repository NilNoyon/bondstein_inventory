from django.db import models
from django.utils import timezone
from users.models import *

# Create your models here.

class Supplier(models.Model):
	name = models.CharField(max_length = 50, unique = True)
	contact = models.CharField(max_length = 150, null=True, blank=True)
	address = models.CharField(max_length = 150, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'suppliers'

class ItemCategory(models.Model):
	name = models.CharField(max_length=50, unique=True)
	description = models.CharField(max_length=250, null=True, blank=True)

	class Meta:
		db_table = 'item_categories'

class Item(models.Model):
	name = models.CharField(max_length=50, unique=True)
	description = models.CharField(max_length=250, null=True, blank=True)
	category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'items'

class ItemDetails(models.Model):
	name = models.CharField(max_length=50)
	item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
	unit = models.CharField(max_length=30, null=True, blank=True)
	unit_price = models.FloatField(default=0)
	quantity = models.IntegerField(default=0)
	supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)
	warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'item_details'

class PreOrder(models.Model):
    order_no = models.CharField(max_length = 50, unique = True)
    order_date = models.DateTimeField(default=timezone.now)
    quot = models.CharField(max_length=50, blank=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE,null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='pre_order_created_by')
    prepared_by = models.CharField(max_length = 50, blank=True, null=True)
    checked_by = models.CharField(max_length = 50, blank=True, null=True)
    order_grand_total = models.FloatField(default=0, blank=True, null=True)
    is_deleted = models.BooleanField(default=0)

    class Meta:
        db_table = 'pre_orders'

    @property
    def sum_quantity(self):
    	return sum([obj.quantity for obj in PreOrderDetails.objects.filter(pre_order=self.id)])
    
    @property
    def sum_amount(self):
    	return sum([obj.amount for obj in PreOrderDetails.objects.filter(pre_order=self.id)])

class PreOrderDetails(models.Model):
	pre_order = models.ForeignKey(PreOrder, on_delete=models.CASCADE, null=True)
	item_details = models.ForeignKey(ItemDetails, on_delete=models.CASCADE, null=True)
	quantity = models.IntegerField(default=0, blank=True, null=True)
	unit_price = models.IntegerField(default=0, blank=True, null=True)
	amount = models.IntegerField(default=0, blank=True)
	shipping_date = models.DateTimeField(default=timezone.now)
	status = models.ForeignKey(Status, on_delete=models.CASCADE,null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	is_deleted = models.BooleanField(default=0)

	class Meta:
		db_table = 'pre_order_details'

class Barcode(models.Model):
	barcode = models.CharField(max_length=20, blank=True, null=True, unique=True)
	sku = models.CharField(max_length=8, blank=True, null=True, unique=True)
	bst = models.CharField(max_length=8, blank=True, null=True, unique=True)
	po_details = models.ForeignKey(PreOrderDetails, on_delete=models.CASCADE, null=True, blank=True)
	warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True)
	created_date = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

	class Meta:
		db_table = 'barcodes'

class ScannedBarcode(models.Model):
	barcode = models.ForeignKey(Barcode, on_delete=models.CASCADE, null=True, blank=True)
	scanning_date = models.DateTimeField(default=timezone.now)
	from_vendor = models.BooleanField(default=0)
	to_client = models.BooleanField(default=0)
	to_technician = models.BooleanField(default=0)
	damage = models.BooleanField(default=0)

	class Meta:
		db_table = 'scanned_barcodes'

class Stock(models.Model):
	item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
	quantity = models.IntegerField(default=0, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)
	updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='updated_by')

	class Meta:
		db_table = 'stocks'

class StockLog(models.Model):
	item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
	quantity = models.IntegerField(default=0, null=True)
	activity = models.CharField(max_length=20, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='log_created_by')

	class Meta:
		db_table = 'stock_log'
