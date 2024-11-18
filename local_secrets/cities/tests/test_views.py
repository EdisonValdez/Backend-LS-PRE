from unittest.mock import ANY

from django.contrib.gis.geos import Point

from local_secrets.cities.models import Address, City, Country
from local_secrets.core.tests.base_test_case import BaseTestCase
from local_secrets.sites.models import Site


class TestCityViews(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        country1 = Country.objects.create(name='Portugal', code='PO')

        city1 = City.objects.create(
            name='TestCity', cp='123456', province='Test', description='Test', point=Point(0.0, 0.0), country=country1
        )

        address1 = Address.objects.create(
            street='Calle de la piruleta',
            city=city1,
            point=Point(0.0, 0.0),
            google_place_id='',
            details='Test',
            number='1',
            door='1',
            floor=None,
        )

        Site.objects.create(title='TestSite', type='place', description='Test place', address=address1, city=city1)
        Site.objects.create(title='TestEvent', type='event', description='Test event', address=address1, city=city1)

    def test_list_cities_returns_200(self):
        response = self.api_client.get('/cities/')

        assert response.status_code == 200
        assert response.json() == [
            {
                'id': ANY,
                'name': 'TestCity',
                'cp': '123456',
                'description': 'Test',
                'images': [],
                'media': None,
                'point': ANY,
                'province': 'Test',
                'country': {'id': ANY, 'name': 'Portugal', 'code': 'PO'},
            },
        ]

    def test_detail_city_returns_200(self):
        response = self.api_client.get('/cities/1')

        assert response.status_code == 200
        assert response.json() == {
            'id': 1,
            'name': 'TestCity',
            'cp': '123456',
            'description': 'Test',
            'images': [],
            'media': None,
            'point': ANY,
            'province': 'Test',
            'country': {
                'id': ANY,
                'name': 'Portugal',
                'code': 'PO',
            },
        }

    def test_city_events_returns_200(self):
        response = self.api_client.get('/cities/1/events')

        assert response.status_code == 200
        assert response.json() == [
            {
                'id': ANY,
                'type': 'event',
                'title': 'TestEvent',
                'tags': [],
                'media': None,
                'images': [],
                'rating': 0,
                'has_been_accepted': True,
                'is_suggested': False,
                'city': {
                    'id': 1,
                    'name': 'TestCity',
                    'country': {
                        'id': ANY,
                        'name': 'Portugal',
                        'code': 'PO',
                    },
                },
            },
        ]

    def test_city_places_returns_200(self):
        response = self.api_client.get('/cities/1/places')

        assert response.status_code == 200
        assert response.json() == [
            {
                'id': ANY,
                'type': 'place',
                'title': 'TestSite',
                'tags': [],
                'media': None,
                'images': [],
                'rating': 0,
                'has_been_accepted': True,
                'is_suggested': False,
                'city': {
                    'id': 1,
                    'name': 'TestCity',
                    'country': {
                        'id': ANY,
                        'name': 'Portugal',
                        'code': 'PO',
                    },
                },
            },
        ]
