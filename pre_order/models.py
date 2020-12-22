from django.db import models

# Create your models here.
class PreOrder(models.Model):
    order_no = models.CharField(max_length = 50)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_types'
