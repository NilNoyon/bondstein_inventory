# Generated by Django 3.1.4 on 2021-09-05 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_channeldemand_channeldemanddetails_forecastdata_forecastdetails'),
    ]

    operations = [
        migrations.AddField(
            model_name='channeldemanddetails',
            name='final_demand',
            field=models.IntegerField(default=0),
        ),
    ]
