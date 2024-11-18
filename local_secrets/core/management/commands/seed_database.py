import functools
import inspect
import json

from django.core.management.base import BaseCommand

from ..seeders import seeding


class Command(BaseCommand):
    help = 'Seeds the database with Fake random models'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f', '--force-users', help='Indicates if the users have to been seeded', action='store_true'
        )

    def handle(self, *args, **options):
        seeded = {field: klass(**options).seed() for field, klass in self.inspect_seeders().items()}
        return json.dumps(seeded, indent=4)

    @staticmethod
    def is_seeder(cls) -> bool:
        return inspect.isclass(cls) and issubclass(cls, seeding.Seeder) and cls != seeding.Seeder

    @classmethod
    def inspect_seeders(cls) -> dict:
        sorted_seeders = sorted(inspect.getmembers(seeding, cls.is_seeder), key=functools.cmp_to_key(cls.sorting_func))
        return {seeder_name: getattr(seeding, seeder_name) for seeder_name, _ in sorted_seeders}

    @staticmethod
    def sorting_func(a, b) -> int:
        return a[1].requires_from(b[1])
