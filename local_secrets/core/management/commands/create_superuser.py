import random
from string import ascii_letters, digits

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a new superuser in the database and allows superuser password change too'

    ADMIN_USERNAME = 'rudoadmin'
    PASSWORD_LENGTH = 8
    PASSWORD_AVAILABLE_CHARACTERS = ascii_letters + digits

    def handle(self, *args, **options):
        user_manager = get_user_model().objects
        lookup = {'username': self.ADMIN_USERNAME, 'email': 'admin@rudo.es'}
        if user_manager.filter(**lookup).exists():
            print(
                f"User with username: {lookup['username']} and email: {lookup['email']} already exists.\n"
                f"Do you want to reset its password? (y/N)"
            )
            if input() == 'y':
                superuser = user_manager.get(**lookup)
                pwd = self.generate_random_password(self.PASSWORD_LENGTH)
                superuser.is_staff = True
                superuser.is_superuser = True
            else:
                return
        else:
            superuser = user_manager.create(is_staff=True, is_superuser=True, **lookup)
            pwd = self.generate_random_password(self.PASSWORD_LENGTH)
        superuser.set_password(pwd)
        superuser.save()
        return self.inform_created(superuser, pwd)

    @classmethod
    def generate_random_password(cls, length):
        # Available character collection
        return ''.join(random.choice(cls.PASSWORD_AVAILABLE_CHARACTERS) for _ in range(length))

    @staticmethod
    def inform_created(superuser, pwd):
        return (
            f'SuperUser has been created with these information:\n'
            f'username: {superuser.username}, '
            f'email: {superuser.email}, '
            f'password: {pwd}'
        )
