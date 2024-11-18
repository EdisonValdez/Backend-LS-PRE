from django.contrib.gis.geos import Point

from local_secrets.cities.models import City, Country
from local_secrets.core.tests.base_test_case import BaseTestCase
from local_secrets.sites.models import Site
from local_secrets.travels.models import Travel


class TestTravelSetup(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        user = cls.USER_MODEL_CLASS.objects.first()

        country1 = Country.objects.create(name='Portugal', code='PO')

        City.objects.create(
            name='TestCity', cp='123456', province='Test', description='Test', point=Point(0.0, 0.0), country=country1
        )

        Travel.objects.create(
            title='Test travel', type='solo', initial_date='2023-05-06', end_date='2023-05-10', user=user
        )

        old_trip = Travel.objects.create(
            title='Old trip', type='romantic', initial_date='2023-04-02', end_date='2023-04-10', user=user
        )

        site = Site.objects.create(title='Test Site', type='place', description='Desc')
        old_trip.stops.add(site)
