from django.db import models
from django.utils.translation import gettext_lazy as _

from local_secrets.cities.models import City
from local_secrets.core.utils.pdf import generate_pdf_response_xhtml2pdf
from local_secrets.sites.models import Site
from local_secrets.travels.choices import TravelType
from local_secrets.users.models import CustomUser


class Travel(models.Model):
    title = models.CharField(max_length=100, verbose_name=_('Title'))
    type = models.CharField(max_length=100, choices=TravelType.choices, verbose_name=_('Type'))
    cities = models.ManyToManyField(City, verbose_name=_('Cities'))
    initial_date = models.DateField(verbose_name=_('Initial Date'))
    end_date = models.DateField(verbose_name=_('End Date'))
    stops = models.ManyToManyField(Site, related_name='travels', verbose_name=_('Stops'), through='Stop')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='travels', verbose_name=_('User'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Travel')
        verbose_name_plural = _('Travels')

    def add_route(self, route):
        self.stops.add(*route.stops.all())
        self.cities.add(*route.cities.all())

    def reorder_stops(self, ordered_list):
        for element in ordered_list:
            site = Site.objects.get(id=element[0])
            stop, created = Stop.objects.get_or_create(travel=self, site=site)
            stop.order = element[1]
            stop.save()

    def generate_pdf(self, request):
        return generate_pdf_response_xhtml2pdf(self, request)


class Stop(models.Model):
    travel = models.ForeignKey(Travel, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
