# Generated by Django 3.2.21 on 2023-12-15 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0012_auto_20231215_0910'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='route',
            name='stops',
        ),
    ]
