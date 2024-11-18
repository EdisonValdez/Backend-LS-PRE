# Generated by Django 3.2.13 on 2023-07-25 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cities', '0010_auto_20230725_1326'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='city',
            name='slug_latitude',
        ),
        migrations.RemoveField(
            model_name='city',
            name='slug_longitude',
        ),
        migrations.AddField(
            model_name='city',
            name='latitude',
            field=models.DecimalField(decimal_places=28, default=0, max_digits=30, verbose_name='Latitude'),
        ),
        migrations.AddField(
            model_name='city',
            name='longitude',
            field=models.DecimalField(decimal_places=28, default=0, max_digits=30, verbose_name='Longitude'),
        ),
    ]
