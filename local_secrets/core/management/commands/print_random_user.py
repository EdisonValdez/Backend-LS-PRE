from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Prints an example random model from Users'

    def handle(self, *args, **options):
        return get_user_model().objects.order_by('?').first()
