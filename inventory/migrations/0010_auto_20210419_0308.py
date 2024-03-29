# Generated by Django 3.1.4 on 2021-04-18 21:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '__first__'),
        ('pre_order', '0007_auto_20210203_0549'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0009_stcbarcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='delivery_person',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='stchallan',
            name='delivery_person',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='client',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='responsible_person',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.warehouse'),
        ),
        migrations.AlterField(
            model_name='sodetails',
            name='barcode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pre_order.barcode'),
        ),
        migrations.AlterField(
            model_name='sodetails',
            name='item_details',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pre_order.itemdetails'),
        ),
        migrations.AlterField(
            model_name='sodetails',
            name='so',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.salesorder'),
        ),
        migrations.AlterField(
            model_name='stcbarcode',
            name='barcode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pre_order.barcode'),
        ),
        migrations.AlterField(
            model_name='stcbarcode',
            name='stcd',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.stcdetails'),
        ),
        migrations.AlterField(
            model_name='stcdetails',
            name='barcode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pre_order.barcode'),
        ),
        migrations.AlterField(
            model_name='stcdetails',
            name='item_details',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pre_order.itemdetails'),
        ),
        migrations.AlterField(
            model_name='stcdetails',
            name='stc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.stchallan'),
        ),
        migrations.AlterField(
            model_name='stchallan',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='stchallan',
            name='from_warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='from_warehouse', to='users.warehouse'),
        ),
        migrations.AlterField(
            model_name='stchallan',
            name='to_warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_warehouse', to='users.warehouse'),
        ),
        migrations.CreateModel(
            name='FloatingSalesOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.CharField(max_length=30, unique=True)),
                ('takeover_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('remarks', models.CharField(blank=True, max_length=100, null=True)),
                ('is_stock_out', models.BooleanField(default=0)),
                ('is_warehouse_out', models.BooleanField(default=0)),
                ('is_deleted', models.BooleanField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('delivery_person', models.CharField(blank=True, max_length=200, null=True)),
                ('phone_no', models.CharField(blank=True, max_length=14, null=True)),
                ('total_item', models.IntegerField(default=0)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.warehouse')),
            ],
            options={
                'db_table': 'floating_sales_order',
            },
        ),
        migrations.CreateModel(
            name='FloatingSalesDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_sold', models.BooleanField(default=0)),
                ('barcode', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pre_order.barcode')),
                ('floating_order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.floatingsalesorder')),
                ('item_details', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pre_order.itemdetails')),
            ],
            options={
                'db_table': 'floating_sales_details',
            },
        ),
    ]
