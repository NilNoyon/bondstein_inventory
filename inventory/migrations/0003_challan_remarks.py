# Generated by Django 3.1.4 on 2021-01-23 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_challan_challandetails'),
    ]

    operations = [
        migrations.AddField(
            model_name='challan',
            name='remarks',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
