# Generated by Django 3.2.21 on 2023-12-20 10:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0015_alter_routestop_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='routestop',
            options={'ordering': ('-order',)},
        ),
    ]
