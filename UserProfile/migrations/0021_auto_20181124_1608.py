# Generated by Django 2.1.2 on 2018-11-24 16:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('UserProfile', '0020_auto_20181124_0840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='status',
            field=models.CharField(
                choices=[('TR', 'Travelling'), ('SH', 'Find house'), ('HH', 'Rent a house'), ('UF', 'Undefined')],
                default='UF', max_length=2),
        ),
    ]
