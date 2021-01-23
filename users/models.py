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
