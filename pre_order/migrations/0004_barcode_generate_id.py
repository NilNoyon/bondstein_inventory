# Generated by Django 3.1.4 on 2021-01-28 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pre_order', '0003_auto_20210118_0327'),
    ]

    operations = [
        migrations.AddField(
            model_name='barcode',
            name='generate_id',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
