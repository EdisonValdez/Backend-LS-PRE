# Generated by Django 3.2.13 on 2023-07-12 06:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0028_alter_level_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sites.site',),
        ),
    ]
