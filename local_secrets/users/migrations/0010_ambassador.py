# Generated by Django 3.2.13 on 2023-07-14 08:20

from django.db import migrations, models
import django.db.models.deletion
import local_secrets.users.managers


class Migration(migrations.Migration):

    dependencies = [
        ('cities', '0005_alter_city_cp'),
        ('users', '0009_auto_20230621_1248'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ambassador',
            fields=[
                ('customuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='users.customuser')),
                ('cities', models.ManyToManyField(to='cities.City')),
            ],
            options={
                'verbose_name': 'Ambassador',
                'verbose_name_plural': 'Ambassadors',
            },
            bases=('users.customuser',),
            managers=[
                ('objects', local_secrets.users.managers.CustomUserManager()),
            ],
        ),
    ]
