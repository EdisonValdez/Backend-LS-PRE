from django.db import models
from django.utils.translation import gettext_lazy as _

from local_secrets.cities.models import City
from local_secrets.core.utils.pdf import generate_pdf_response_xhtml2pdf
from local_secrets.languages.models import Language
from local_secrets.routes.managers import RouteManager, RouteQueryset
from local_secrets.sites.models import Site
from local_secrets.users.models import Tag


class Route(models.Model):
    title = models.CharField(max_length=500, verbose_name=_('Title'))

    cities = models.ManyToManyField(City, verbose_name=_('City'), related_name='routes')
    tags = models.ManyToManyField(Tag, related_name='routes', verbose_name=_('Tags'))
    stops = models.ManyToManyField(Site, related_name='routes', verbose_name=_('Stops'), through='RouteStop')
    num_of_views = models.IntegerField(default=0, verbose_name=_('Number of times viewed'))
    is_top_ten = models.BooleanField(default=False, verbose_name=_('Is top 10'))

    objects = RouteManager.from_queryset(RouteQueryset)()

    class Meta:
        verbose_name = _('Route')
        verbose_name_plural = _('Routes')

        ordering = ('is_top_ten', 'num_of_views')

    def __str__(self):
        return self.title

    def add_view(self):
        self.num_of_views += 1
        self.save()

    def display_text(self, field, language='en'):
        value = None
        try:
            value = getattr(self, f"translated_{field}_{language}")
        except BaseException:
            value = getattr(self, field)
        if value is None:
            return getattr(self, field)
        return value

    def generate_pdf(self, request):
        return generate_pdf_response_xhtml2pdf(None, request, route=self)


class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='route_stops')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ("-order",)


class TranslatedRoute(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, verbose_name=_('Translated Title'))
