# Generated by Django 3.2.20 on 2023-10-18 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cities', '0020_address_creation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='description_en',
            field=models.TextField(default='EN', verbose_name='Description EN'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='city',
            name='description_es',
            field=models.TextField(default='ES', verbose_name='Description ES'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='city',
            name='name_en',
            field=models.CharField(default='EN', max_length=500, verbose_name='Name EN'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='city',
            name='name_es',
            field=models.CharField(default='ES', max_length=500, verbose_name='Name ES'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='city',
            name='province_en',
            field=models.CharField(default='EN', max_length=100, verbose_name='Province EN'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='city',
            name='province_es',
            field=models.CharField(default='ES', max_length=100, verbose_name='Province ES'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='city',
            name='slogan_en',
            field=models.CharField(default='EN', max_length=100, verbose_name='Slogan EN'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='city',
            name='slogan_es',
            field=models.CharField(default='ES', max_length=100, verbose_name='Slogan ES'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='country',
            name='name_en',
            field=models.CharField(default='EN', max_length=500, verbose_name='Name EN'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='country',
            name='name_es',
            field=models.CharField(default='ES', max_length=500, verbose_name='Name ES'),
            preserve_default=False,
        ),
    ]
