# Generated by Django 3.2.13 on 2023-07-07 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cities', '0004_auto_20230505_1125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='cp',
            field=models.CharField(max_length=12, verbose_name='CP'),
        ),
    ]
