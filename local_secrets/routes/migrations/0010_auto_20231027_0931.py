# Generated by Django 3.2.21 on 2023-10-27 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cities', '0022_auto_20231018_1259'),
        ('routes', '0009_auto_20231025_0813'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='route',
            name='city',
        ),
        migrations.AddField(
            model_name='route',
            name='cities',
            field=models.ManyToManyField(related_name='routes', to='cities.City', verbose_name='City'),
        ),
    ]
