from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    name = 'local_secrets.core'
    verbose_name = _('Application core')
