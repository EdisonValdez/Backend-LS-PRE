# Generated by Django 3.2.20 on 2023-08-03 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0033_delete_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hourrange',
            name='end_hour',
            field=models.TimeField(default='11:00 PM'),
        ),
        migrations.AlterField(
            model_name='hourrange',
            name='initial_hour',
            field=models.TimeField(default='08:00 AM'),
        ),
    ]
