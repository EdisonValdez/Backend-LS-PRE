# Generated by Django 3.2.20 on 2023-10-18 09:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('languages', '0004_alter_translatedfield_translation'),
        ('users', '0017_auto_20231018_1009'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='title_en',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='title_es',
        ),
        migrations.CreateModel(
            name='TranslatedTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='Translated Tag')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='languages.language')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='users.tag')),
            ],
        ),
    ]
