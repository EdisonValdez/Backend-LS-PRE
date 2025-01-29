# Generated by Django 3.2.25 on 2025-01-29 08:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created by'),
        ),
        migrations.AddField(
            model_name='site',
            name='levels',
            field=models.ManyToManyField(related_name='sites', to='sites.Level', verbose_name='Levels'),
        ),
        migrations.AddField(
            model_name='site',
            name='subcategories',
            field=models.ManyToManyField(blank=True, related_name='sites', to='sites.SubCategory', verbose_name='Subcategories'),
        ),
        migrations.AddField(
            model_name='site',
            name='tags',
            field=models.ManyToManyField(related_name='site_tags', to='users.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='site',
            name='users',
            field=models.ManyToManyField(related_name='fav_sites', through='sites.FavoriteSites', to=settings.AUTH_USER_MODEL, verbose_name='Users'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='sites.site', verbose_name='Site'),
        ),
        migrations.AddField(
            model_name='hourrange',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opening_hours', to='sites.schedule', verbose_name='Schedule'),
        ),
        migrations.AddField(
            model_name='favoritesites',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sites.site', verbose_name='Site'),
        ),
        migrations.AddField(
            model_name='favoritesites',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='comment',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='sites.site', verbose_name='Site'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='category',
            name='level',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='categories', to='sites.level', verbose_name='Level'),
        ),
        migrations.AddIndex(
            model_name='translatedsubcategory',
            index=models.Index(fields=['title'], name='sites_trans_title_c4e31a_idx'),
        ),
        migrations.AddIndex(
            model_name='translatedsite',
            index=models.Index(fields=['title', 'description'], name='sites_trans_title_43620e_idx'),
        ),
        migrations.AddIndex(
            model_name='translatedlevel',
            index=models.Index(fields=['title'], name='sites_trans_title_bd2c2f_idx'),
        ),
        migrations.AddIndex(
            model_name='translatedcategory',
            index=models.Index(fields=['title'], name='sites_trans_title_30274e_idx'),
        ),
        migrations.AddIndex(
            model_name='site',
            index=models.Index(condition=models.Q(('type', 'event')), fields=['frequency'], name='frequency_idx'),
        ),
    ]
