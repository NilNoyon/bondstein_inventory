# Generated by Django 3.1.4 on 2021-04-23 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_auto_20210419_0308'),
    ]

    operations = [
        migrations.AddField(
            model_name='floatingsalesorder',
            name='total_return',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='floatingsalesorder',
            name='total_sell',
            field=models.IntegerField(default=0),
        ),
    ]
