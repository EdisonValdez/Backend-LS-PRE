# Generated by Django 3.2.25 on 2025-01-29 08:15

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import easy_thumbnails.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cities', '0001_initial'),
        ('languages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, verbose_name='Title')),
                ('type', models.CharField(choices=[('place', 'Place'), ('event', 'Event')], default='place', max_length=100, verbose_name='Type')),
                ('order', models.IntegerField(default=0, verbose_name='Order')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(verbose_name='Body')),
                ('rating', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5)], verbose_name='Rating')),
                ('created_at', models.DateTimeField(verbose_name='Created at')),
            ],
            options={
                'verbose_name': 'Review',
                'verbose_name_plural': 'Reviews',
            },
        ),
        migrations.CreateModel(
            name='DefaultImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('image', easy_thumbnails.fields.ThumbnailerImageField(upload_to='default_images')),
            ],
        ),
        migrations.CreateModel(
            name='FavoriteSites',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Favorite Site',
                'verbose_name_plural': 'Favorite Sites',
            },
        ),
        migrations.CreateModel(
            name='HourRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initial_hour', models.TimeField(default='08:00 AM')),
                ('end_hour', models.TimeField(default='11:00 PM')),
            ],
            options={
                'verbose_name': 'Hour Range',
                'verbose_name_plural': 'Hour Ranges',
            },
        ),
        migrations.CreateModel(
            name='ImageSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_width', models.IntegerField(default=512)),
                ('min_height', models.IntegerField(default=512)),
                ('max_width', models.IntegerField(default=4096)),
                ('max_height', models.IntegerField(default=2160)),
            ],
            options={
                'verbose_name': 'Image Size',
                'verbose_name_plural': 'Images Sizes',
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, verbose_name='Title')),
                ('type', models.CharField(choices=[('place', 'Place'), ('event', 'Event')], default='place', max_length=100, verbose_name='Type')),
                ('order', models.IntegerField(default=0, verbose_name='Order')),
            ],
            options={
                'verbose_name': 'Search level',
                'verbose_name_plural': 'Search levels',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], max_length=100)),
            ],
            options={
                'verbose_name': 'Schedule',
                'verbose_name_plural': 'Schedules',
            },
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, verbose_name='Title')),
                ('type', models.CharField(choices=[('place', 'Place'), ('event', 'Event')], default='place', max_length=100, verbose_name='Type')),
                ('description', models.TextField(verbose_name='Description')),
                ('is_suggested', models.BooleanField(default=False)),
                ('has_been_accepted', models.BooleanField(default=True)),
                ('frequency', models.CharField(choices=[('never', 'Does not repeat (Uses schedules)'), ('day', 'Every day'), ('week', 'Every week'), ('year', 'Every year'), ('workday', 'Every working day')], default='never', max_length=100, verbose_name='Frequency')),
                ('media', models.FileField(blank=True, null=True, upload_to='site_videos', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'webm', 'mkv'])], verbose_name='Video')),
                ('url', models.CharField(blank=True, max_length=500, null=True, verbose_name='Link')),
                ('phone', models.CharField(blank=True, max_length=500, null=True, verbose_name='Contact phone')),
                ('always_open', models.BooleanField(default=False, verbose_name='Always open')),
                ('is_top_10', models.BooleanField(default=False, verbose_name='Is top 10')),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sites', to='cities.address')),
                ('categories', models.ManyToManyField(related_name='sites', to='sites.Category', verbose_name='Categories')),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sites', to='cities.city', verbose_name='City')),
            ],
            options={
                'verbose_name': 'Site',
                'verbose_name_plural': 'Sites',
            },
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, verbose_name='Title')),
                ('type', models.CharField(choices=[('place', 'Place'), ('event', 'Event')], default='place', max_length=100, verbose_name='Type')),
                ('order', models.IntegerField(default=0, verbose_name='Order')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subcategories', to='sites.category', verbose_name='Category')),
            ],
            options={
                'verbose_name': 'Subcategory',
                'verbose_name_plural': 'Subcategories',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='VideoSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_size', models.IntegerField(default=512)),
                ('max_size', models.IntegerField(default=4096)),
            ],
            options={
                'verbose_name': 'Video Size',
                'verbose_name_plural': 'Videos Sizes',
            },
        ),
        migrations.CreateModel(
            name='TranslatedSubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, verbose_name='Title')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='languages.language')),
                ('subcategory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='sites.subcategory')),
            ],
        ),
        migrations.CreateModel(
            name='TranslatedSite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, verbose_name='Translated Title')),
                ('description', models.TextField(verbose_name='Translated Description')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='languages.language')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='sites.site')),
            ],
        ),
        migrations.CreateModel(
            name='TranslatedLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, verbose_name='Translated Title')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='languages.language')),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='sites.level')),
            ],
        ),
        migrations.CreateModel(
            name='TranslatedCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, verbose_name='Translated Title')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='sites.category')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='languages.language')),
            ],
        ),
        migrations.CreateModel(
            name='SpecialSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField()),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='special_schedules', to='sites.site', verbose_name='Site')),
            ],
            options={
                'verbose_name': 'Special Schedule',
                'verbose_name_plural': 'Special Schedules',
            },
        ),
        migrations.CreateModel(
            name='SpecialHourRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initial_hour', models.TimeField(default='08:00')),
                ('end_hour', models.TimeField(default='23:00')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opening_hours', to='sites.specialschedule', verbose_name='Schedule')),
            ],
        ),
        migrations.CreateModel(
            name='SiteImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', easy_thumbnails.fields.ThumbnailerImageField(upload_to='site_images')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='sites.site', verbose_name='Site')),
            ],
        ),
    ]
