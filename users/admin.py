from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(MenuList)
admin.site.register(UserPermission)
admin.site.register(Warehouse)