from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
# Create your models here.

class UserType(models.Model):
    type_name = models.CharField(max_length = 50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_types'


class User(AbstractUser):
    name = models.CharField(max_length = 100, null=True)
    email = models.EmailField(unique=True)
    designation = models.CharField(max_length = 50, null=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    department = models.CharField(max_length=20, null=True)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'