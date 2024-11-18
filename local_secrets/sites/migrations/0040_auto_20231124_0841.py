# Generated by Django 3.2.21 on 2023-11-24 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0039_auto_20231018_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='type',
            field=models.CharField(choices=[('place', 'Place'), ('event', 'Event')], default='place', max_length=100, verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='level',
            name='type',
            field=models.CharField(choices=[('place', 'Place'), ('event', 'Event')], default='place', max_length=100, verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='type',
            field=models.CharField(choices=[('place', 'Place'), ('event', 'Event')], default='place', max_length=100, verbose_name='Type'),
        ),
    ]
