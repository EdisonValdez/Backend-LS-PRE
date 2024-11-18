# Generated by Django 3.2.13 on 2023-05-19 09:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sites', '0019_defaultimage'),
        ('cities', '0004_auto_20230505_1125'),
    ]

    operations = [
        migrations.CreateModel(
            name='Travel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('type', models.CharField(choices=[('solo', 'Solo'), ('familiar', 'Familiar'), ('business', 'Business'), ('romantic', 'Romantic'), ('group', 'Group')], max_length=100, verbose_name='Type')),
                ('initial_date', models.DateField(verbose_name='Initial Date')),
                ('end_date', models.DateField(verbose_name='End Date')),
                ('cities', models.ManyToManyField(to='cities.City', verbose_name='Cities')),
                ('stops', models.ManyToManyField(to='sites.Site', verbose_name='Stops')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='travels', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Travel',
                'verbose_name_plural': 'Travels',
            },
        ),
    ]
