# Generated by Django 3.2.21 on 2024-05-13 08:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0044_specialhourrange'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='specialschedule',
            name='end_hour',
        ),
        migrations.RemoveField(
            model_name='specialschedule',
            name='initial_hour',
        ),
    ]
