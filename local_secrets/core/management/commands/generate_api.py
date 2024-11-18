import importlib
import os

from django.conf import settings
from django.core.management.base import BaseCommand

MODEL_TO_SERIALIZER = {
    'BigAutoField': 'IntegerField',
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        app_name = input('app name:')
        model_name = input('model:')
        try:
            models = importlib.import_module(f'local_secrets.{app_name}.models')
            getattr(models, model_name)
            os.chdir(f'{settings.PROJECT_NAME_SHORT.replace(" ", "_")}/{app_name}')
        except ModuleNotFoundError:
            #    Ask to create the app if it doesn't exist
            if input(f'Do you want to create the app {app_name}?').lower() in ['y', 'yes']:
                os.mkdir(f'{app_name}')
                os.chdir(f'./{app_name}')
                open('__init__.py', 'a').close()
            else:
                return

        # Create the serializers
        with open('serializers.py', 'w') as serializers:
            serializers.write('from rest_framework import serializers\n')
            serializers.write(f'from .models import {model_name}\n\n\n')
            serializers.write(f'class {model_name}Serializer(serializers.ModelSerializer):\n')
            serializers.write('    class Meta:\n')
            serializers.write(f'        model = {model_name}')

        #   Create the views
        with open('views.py', 'w') as views:
            views.write('from rest_framework import viewsets\n')
            views.write('from rest_framework.response import Response\n')
            views.write(f'from .models import {model_name}\n')
            views.write(f'from .serializers import {model_name}Serializer\n\n\n')

            views.write(f'class {model_name}ViewSet(viewsets.ViewSet):\n')
            views.write(f'    queryset = {model_name}.objects.all()\n')
            views.write(f'    serializer = {model_name}Serializer\n')

        #    Create the urls
        with open('urls.py', 'w') as urls:
            urls.write('from . import views\n')
            urls.write('from rest_framework import routers\n')
            urls.write('from django.conf.urls import include\n')
            urls.write('from django.urls import path\n')
            urls.write(f'from .models import {model_name}\n\n')

            urls.write('router = routers.DefaultRouter(trailing_slash=False)\n')
            urls.write(f'router.register("", views.{model_name}ViewSet, basename={model_name})\n')
            urls.write('urlpatterns = [path(r"", include(router.urls))]')

        return
