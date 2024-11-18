from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from .choices import AppPlatform
from .managers import AppVersionManager


class AppVersion(models.Model):
    platform = models.CharField(max_length=50, choices=AppPlatform.choices, verbose_name=_('Platform'))
    version = models.CharField(max_length=150, verbose_name=_('Version'))
    required = models.BooleanField(default=False, verbose_name=_('Required'))

    objects = AppVersionManager()

    def __str__(self):
        return f'{self.get_platform_display()}: {self.version}'

    @property
    def platform_enum(self) -> AppPlatform:
        return AppPlatform.from_value(self.platform)


class UserAppVersion(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name='app_version', verbose_name=_('User')
    )
    version = models.ForeignKey(AppVersion, on_delete=models.CASCADE, related_name='users', verbose_name=_('Version'))

    @property
    def user_version(self) -> str:
        return self.version.version

    @property
    def user_platform(self) -> AppPlatform:
        return self.version.platform_enum


class Store(models.Model):
    platform = models.CharField(max_length=50, choices=AppPlatform.choices, unique=True, verbose_name=_('Platform'))
    url = models.CharField(max_length=200, verbose_name=_('Store url'))

    def __str__(self):
        return self.url
