from django.utils.translation import gettext_lazy as _

from local_secrets.sites.models import Site, TranslatedSite


class Event(Site):
    class Meta:
        proxy = True

        verbose_name = _('Event')
        verbose_name_plural = _('Events')


class TranslatedEvent(TranslatedSite):
    class Meta:
        proxy = True
