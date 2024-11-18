import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    POSTGRESQL_TYPE_MAP = {
        'integer': 'IntegerField',
        'character varying': 'CharField',
        'text': 'TextField',
        'numeric': 'DecimalField',
        'bigint': 'IntegerField',
        'smallint': 'IntegerField',
        'timestamp with time zone': 'DateTimeField',
        'date': 'DateTimeField',
        'boolean': 'BooleanField',
        'jsonb': 'JSONField',
        'uuid': 'CharField',
    }

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', nargs='?', type=bool, default=False)

    def handle(self, *args, **options):
        schema_name = input('Specify th filename for the generated database schema:')
        with open(schema_name, 'r', encoding='utf-8') as md:
            app_name = input(
                'Specify an app_name to extract the data from the schema (leave blank to extract all '
                'models in one app):'
            )
            if app_name == '':
                app_name = 'test_app'

            os.chdir(settings.BASE_DIR.joinpath(f'{settings.PROJECT_NAME_SHORT.replace(" ", "_")}'))

            if not options.get('dry-run'):
                if not os.path.exists(f'{app_name}'):
                    os.mkdir(f'{app_name}')
                os.chdir(f'./{app_name}')

                if not os.path.exists('migrations'):
                    os.mkdir('migrations')
                os.chdir('./migrations')
                open('__init__.py', 'a').close()
                os.chdir('..')

                open('__init__.py', 'a').close()
                with open('apps.py', 'w') as apps:
                    apps.write('from django.apps import AppConfig\n')
                    apps.write(f'\n\nclass {app_name}Config(AppConfig):\n')
                    apps.write(f'    name="{settings.PROJECT_NAME_SHORT.replace(" ", "_").lower()}.{app_name.lower()}"')

            with open('models.py', 'w', encoding='utf-8') as mdpy:
                data = json.load(md)

                if not options.get('dry-run'):
                    mdpy.write('from django.db import models\n')
                    mdpy.write('\n')

                for table in data:
                    print(table)
                    if app_name == 'test_app' or app_name in table:
                        if not options.get('dry-run'):
                            mdpy.write(f'\nclass {table.replace(app_name, "").lstrip("_")}(models.Model):\n')

                        for field in data[table]:
                            field_name = field.get("name")
                            field_type = field.get("values").get("type")
                            is_null = field.get("values").get("nullable")
                            length = field.get("values").get("max_length")

                            print(f'{field.get("name")}: ({field.get("values")})')
                            if not options.get('dry-run'):
                                if length:
                                    mdpy.write(
                                        f'    {field_name} = models.{self.POSTGRESQL_TYPE_MAP.get(field_type)}'
                                        f'(max_length={length}, null={is_null})\n'
                                    )
                                else:
                                    mdpy.write(
                                        f'    {field_name} = models.{self.POSTGRESQL_TYPE_MAP.get(field_type)}'
                                        f'(null={is_null})\n'
                                    )

                        if not options.get('dry-run'):
                            mdpy.write('\n    class Meta:\n')
                            mdpy.write(f'        db_table = "{table}"\n')
                            mdpy.write(f'        app_label = "{app_name}"\n\n')

                        print('--------')
