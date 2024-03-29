# Generated by Django 3.1.4 on 2021-05-22 21:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pre_order', '0009_stocklog_warehouse'),
        ('users', '__first__'),
        ('inventory', '0012_floatingsalesdetails_updated_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelDemand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('client_name', models.CharField(blank=True, max_length=100, null=True)),
                ('final_demand', models.IntegerField(default=0)),
                ('month', models.IntegerField(default=0)),
                ('year', models.IntegerField(default=2021)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.warehouse')),
            ],
            options={
                'db_table': 'channel_demands',
            },
        ),
        migrations.CreateModel(
            name='ForecastData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.CharField(choices=[('January', '1'), ('February', '2'), ('March', '3'), ('April', '4'), ('May', '5'), ('June', '6'), ('July', '7'), ('August', '8'), ('September', '9'), ('October', '10'), ('November', '11'), ('December', '12')], default='0', max_length=10)),
                ('year', models.IntegerField(default=2021)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'forecast_data',
            },
        ),
        migrations.CreateModel(
            name='ForecastDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_quantity', models.IntegerField(default=0)),
                ('i_quantity', models.IntegerField(default=0)),
                ('forecast', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.forecastdata')),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pre_order.item')),
                ('item_details', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pre_order.itemdetails')),
            ],
            options={
                'db_table': 'forecast_details',
            },
        ),
        migrations.CreateModel(
            name='ChannelDemandDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('order_probability', models.CharField(blank=True, max_length=20, null=True)),
                ('weight', models.FloatField(default=0)),
                ('channel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.channeldemand')),
                ('device_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pre_order.itemdetails')),
                ('warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.warehouse')),
            ],
            options={
                'db_table': 'channel_demand_details',
            },
        ),
    ]
