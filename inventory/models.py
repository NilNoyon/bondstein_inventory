from django.db import models
from django.utils import timezone
from users.models import *

# Create your models here.

class Client(models.Model):
	name = models.CharField(max_length = 50, unique = True)
	contact = models.CharField(max_length = 150, null=True, blank=True)
	address = models.CharField(max_length = 150, null=True, blank=True)
	email  = models.EmailField(unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'clients'

class ResponsiblePerson(models.Model):
	name = models.CharField(max_length = 50)
	contact = models.CharField(max_length = 150, null=True, blank=True)
	address = models.CharField(max_length = 150, null=True, blank=True)
	email = models.EmailField(unique=True)
	client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'responsible_persons'
		