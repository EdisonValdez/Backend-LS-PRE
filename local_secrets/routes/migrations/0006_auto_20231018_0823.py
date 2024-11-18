# Generated by Django 3.2.20 on 2023-10-18 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0005_alter_route_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='title_en',
            field=models.CharField(default='EN', max_length=500, verbose_name='Title EN'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='route',
            name='title_es',
            field=models.CharField(default='ES', max_length=500, verbose_name='Title ES'),
            preserve_default=False,
        ),
    ]
