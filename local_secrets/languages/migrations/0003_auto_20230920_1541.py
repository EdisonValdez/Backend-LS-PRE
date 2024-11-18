# Generated by Django 3.2.21 on 2023-09-20 13:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('languages', '0002_translatedfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='translatedfield',
            name='language',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='languages.language', verbose_name='Language'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='translatedfield',
            name='type',
            field=models.CharField(default='title', max_length=100),
            preserve_default=False,
        ),
    ]
