# Generated by Django 3.2.20 on 2023-10-18 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_auto_20231018_0915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupdescription',
            name='description_en',
            field=models.TextField(verbose_name='Description EN'),
        ),
        migrations.AlterField(
            model_name='groupdescription',
            name='description_es',
            field=models.TextField(verbose_name='Description ES'),
        ),
    ]
