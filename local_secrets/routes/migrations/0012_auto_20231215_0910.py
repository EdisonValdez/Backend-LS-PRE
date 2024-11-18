# Generated by Django 3.2.21 on 2023-12-15 08:10

from django.db import migrations


def create_through_relations(apps, schema_editor):
    Route = apps.get_model('routes', 'Route')
    RouteStop = apps.get_model('routes', 'RouteStop')
    for route in Route.objects.all():
        for stop in route.stops.all():
            RouteStop(
                route=route,
                site=stop,
                order=0
            ).save()


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0011_auto_20231215_0909'),
    ]

    operations = [
        migrations.RunPython(create_through_relations, reverse_code=migrations.RunPython.noop),
    ]
