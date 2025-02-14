# Generated by Django 3.2.25 on 2025-01-29 08:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_version', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='userappversion',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='app_version', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='userappversion',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='app_version.appversion', verbose_name='Version'),
        ),
    ]
