import abc

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils.translation import gettext
from faker import Faker
from oauth2_provider.models import Application

from local_secrets.app_version.choices import AppPlatform
from local_secrets.app_version.models import AppVersion, Store, UserAppVersion

# Seeding flags
SEED = {
    'version': True,
    'user': True,
    'user_version': True,
    'store': True,
    'oauth2': True,
}


class Seeder:
    enabled: bool = False
    requirements = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def seed(self) -> bool:
        return self._seed() if self.enabled else False

    @abc.abstractmethod
    def _seed(self) -> bool:
        raise NotImplementedError(gettext('No seeding method was declared'))

    @classmethod
    def requires_from(cls, another_seeder: 'Seeder') -> int:
        if another_seeder in cls.requirements:
            return 1
        elif cls in another_seeder.requirements:
            return -1
        else:
            return 0


class VersionSeeder(Seeder):
    def __init__(self, **kwargs):
        self.enabled = SEED['version']
        super(VersionSeeder, self).__init__(kwargs=kwargs)

    def _seed(self) -> bool:
        if not AppVersion.objects.exists():
            data = [
                AppVersion(platform=AppPlatform.ANDROID, version='2.0.0', required=True),
                AppVersion(platform=AppPlatform.ANDROID, version='2.1.0', required=False),
                AppVersion(platform=AppPlatform.IOS, version='2.0.0', required=True),
                AppVersion(platform=AppPlatform.IOS, version='2.2.0', required=False),
            ]
            AppVersion.objects.bulk_create(data)
            print(f'AppVersion table has been seeded with {len(data)} versions')
            return True
        else:
            return False


class UserSeeder(Seeder):
    SEED_USERS_AMOUNT = 10
    faker = Faker()

    def __init__(self, **kwargs):
        self.enabled = SEED['user']
        super(UserSeeder, self).__init__(**kwargs)

    def _seed(self) -> bool:
        user_manager = get_user_model().objects
        if self.kwargs.get('force_users', False) or not user_manager.exists():
            for _ in range(self.SEED_USERS_AMOUNT):
                user = user_manager.create(
                    username=self.faker.user_name(),
                    email=self.faker.email(),
                    first_name=self.faker.first_name(),
                    last_name=self.faker.last_name(),
                )
                user.set_password(self.faker.password())
                user.save()
            print(f'Users table has been seeded with {self.SEED_USERS_AMOUNT} users')
            return True
        return False


class UserVersionSeeder(Seeder):
    requirements = [VersionSeeder, UserSeeder]

    def __init__(self, **kwargs):
        self.enabled = SEED['user_version']
        super(UserVersionSeeder, self).__init__(kwargs=kwargs)

    def _seed(self) -> bool:
        if AppVersion.objects.exists() and get_user_model().objects.exists():
            user_manager = get_user_model().objects
            collection = user_manager.filter(is_superuser=False).exclude(app_version__isnull=False)
            if collection.exists():
                for user in list(collection):
                    UserAppVersion(user=user, version=AppVersion.objects.order_by('?').first()).save()
                print(f'UserAppVersion table has been seeded for {collection.count()} users')
                return True
        return False


class StoreSeeder(Seeder):
    requirements = []

    def __init__(self, **kwargs):
        self.enabled = SEED['store']
        super(StoreSeeder, self).__init__(kwargs=kwargs)

    def _seed(self) -> bool:
        if not Store.objects.filter(platform__in=[AppPlatform.ANDROID, AppPlatform.IOS]).exists():
            data = [
                Store(
                    platform=AppPlatform.ANDROID,
                    url="https://play.google.com/store/apps/details?id=com.google.android.googlequicksearchbox",
                ),
                Store(
                    platform=AppPlatform.IOS,
                    url="https://apps.apple.com/es/app/google/id284815942",
                ),
            ]
            Store.objects.bulk_create(data)
            print(f'Store table has been seeded with {len(data)} stores')
            return True
        else:
            return False


class OAuth2Seeder(Seeder):
    def __init__(self, **kwargs):
        self.enabled = SEED['oauth2']
        super(OAuth2Seeder, self).__init__(kwargs=kwargs)

    def _seed(self) -> bool:
        if not Application.objects.exists():
            call_command(
                'createapplication',
                'confidential',
                'client-credentials',
                name='oauth2-client',
            )
            call_command('createapplication', 'confidential', 'password', name='oauth2-app')
            print('Oauth2 Provider Application table has been seeded with client-credentials and password types')
            return True
        else:
            return False
