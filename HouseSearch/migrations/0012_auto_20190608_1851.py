# Generated by Django 2.1.2 on 2019-06-08 18:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('HouseSearch', '0011_booking'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='comment',
            field=models.TextField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name='booking',
            name='phone_num',
            field=models.CharField(blank=True, max_length=12),
        ),
    ]
