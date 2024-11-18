from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppVersionConfig(AppConfig):
    name = 'local_secrets.app_version'
    verbose_name = _('App versions')
