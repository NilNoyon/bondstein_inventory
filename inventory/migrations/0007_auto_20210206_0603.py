# Generated by Django 3.1.4 on 2021-02-06 00:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pre_order', '0007_auto_20210203_0549'),
        ('users', '__first__'),
        ('inventory', '0006_auto_20210130_0306'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('so_no', models.CharField(max_length=30, unique=True)),
                ('so_amount', models.IntegerField(blank=True, null=True)),
                ('so_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('remarks', models.CharField(blank=True, max_length=100, null=True)),
                ('is_stock_out', models.BooleanField(default=0)),
                ('is_deleted', models.BooleanField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.client')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('responsible_person', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.responsibleperson')),
                ('warehouse', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.warehouse')),
            ],
            options={
                'db_table': 'sales_orders',
            },
        ),
        migrations.CreateModel(
            name='SODetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField(blank=True, null=True)),
                ('quantity', models.IntegerField()),
                ('remarks', models.CharField(blank=True, max_length=100, null=True)),
                ('item_details', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pre_order.itemdetails')),
                ('so', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.salesorder')),
            ],
            options={
                'db_table': 'sales_order_details',
            },
        ),
        migrations.RemoveField(
            model_name='challandetails',
            name='challan',
        ),
        migrations.RemoveField(
            model_name='challandetails',
            name='item_details',
        ),
        migrations.DeleteModel(
            name='Challan',
        ),
        migrations.DeleteModel(
            name='ChallanDetails',
        ),
    ]