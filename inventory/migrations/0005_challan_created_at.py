# Generated by Django 3.1.4 on 2021-01-23 22:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_challandetails_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='challan',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
