from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length = 50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_roles'

class Warehouse(models.Model):
    name = models.CharField(max_length = 50, unique=True)
    address = models.CharField(max_length = 150, blank=True, null=True)
    contact = models.CharField(max_length = 20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'warehouses'


class User(AbstractUser):
    fullname = models.CharField(max_length = 100, null=True)
    email = models.EmailField(unique=True)
    designation = models.CharField(max_length = 50, null=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

class Status(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    status_class = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'status'

class ActivityLog(models.Model):
    activity = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class MenuList(models.Model):
    menu_name   = models.CharField(max_length=50)
    menu_url    = models.CharField(max_length=90)
    module_types = (
        ('Administration', 'Administration'),
        ('Order', 'Order'),
        ('Inventory', 'Inventory'),
    )
    module_name      = models.CharField(max_length=50, choices=module_types)
    is_sub_menu      = models.BooleanField(default=False)
    sub_menu_name    = models.CharField(max_length=50,blank=True,null=True)
    menu_order       = models.IntegerField(default=0)
    menu_icon        = models.CharField(max_length=50,blank=True)
    status           = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.menu_name

    class Meta:
        db_table = 'menu_list'
        verbose_name = "Menu"
        verbose_name_plural = "Menu List" 

class UserPermission(models.Model):
    user            = models.ForeignKey(User, on_delete = models.CASCADE) 
    menu            = models.ForeignKey(MenuList, on_delete = models.CASCADE)
    view_action     = models.BooleanField(default = False)      
    insert_action   = models.BooleanField(default = False)      
    update_action   = models.BooleanField(default = False)      
    delete_action   = models.BooleanField(default = False)   
    permission_date = models.DateTimeField(auto_now_add=True)
    permitted_by    = models.IntegerField(default=0) 
    status          = models.BooleanField(default=True)   
    
    def __str__(self):
        return str(self.user)   
        
    class Meta:
        db_table = 'user_permission'
        verbose_name = "User Permission"
        verbose_name_plural = "User Permissions" 