# Generated by Django 3.2.21 on 2023-10-25 06:13

from django.db import migrations, models
import django.db.models.deletion

from local_secrets.cities.models import City


class Migration(migrations.Migration):

    dependencies = [
        #('cities', '0022_auto_20231018_1259'),
        ('cities', '0027_translatedphonecode'),
        ('routes', '0008_auto_20231024_0839'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='route',
            name='cities',
        ),
        migrations.AddField(
            model_name='route',
            name='city',
            field=models.ForeignKey(default=City.objects.first().id, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='routes',
                                    to='cities.city', verbose_name='City'),
            preserve_default=False,
        ),
    ]
