from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MessagingConfig(AppConfig):
    name = 'local_secrets.messaging'
    verbose_name = _('Firebase Cloud Messaging')
