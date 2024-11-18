from unittest.mock import ANY

from django.contrib.gis.geos import Point

from local_secrets.cities.models import Address, City, Country
from local_secrets.core.tests.base_test_case import BaseTestCase
from local_secrets.routes.models import Route
from local_secrets.sites.models import Site


class TestRoutesViews(BaseTestCase):
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

        site1 = Site.objects.create(
            title='TestSite1', type='place', description='Test place', address=address1, city=city1
        )

        route = Route.objects.create(
            title='TestRoute',
            city=city1,
        )

        route.stops.add(site1)

    def test_list_routes_returns_200(self):
        response = self.api_client.get('/routes/')
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': ANY,
                'city': {
                    'country': {'code': 'PO', 'id': ANY, 'name': 'Portugal'},
                    'cp': '123456',
                    'description': 'Test',
                    'id': ANY,
                    'images': [],
                    'media': None,
                    'name': 'TestCity',
                    'point': ANY,
                    'province': 'Test',
                },
                'stops': [
                    {
                        'id': ANY,
                        'has_been_accepted': True,
                        'images': [],
                        'city': {
                            'country': {'code': 'PO', 'id': ANY, 'name': 'Portugal'},
                            'id': ANY,
                            'name': 'TestCity',
                        },
                        'is_suggested': False,
                        'media': None,
                        'rating': 0,
                        'tags': [],
                        'title': 'TestSite1',
                        'type': 'place',
                    },
                ],
                'num_of_stops': 1,
                'num_of_views': 0,
                'is_top_ten': False,
                'tags': [],
                'title': 'TestRoute',
            },
        ]

    def test_retrieve_returns_200(self):
        response = self.api_client.get('/routes/1')
        assert response.status_code == 200
        assert response.json() == {
            'id': ANY,
            'city': {
                'country': {'code': 'PO', 'id': ANY, 'name': 'Portugal'},
                'cp': '123456',
                'description': 'Test',
                'id': ANY,
                'images': [],
                'media': None,
                'name': 'TestCity',
                'point': ANY,
                'province': 'Test',
            },
            'stops': [
                {
                    'id': ANY,
                    'has_been_accepted': True,
                    'images': [],
                    'city': {'country': {'code': 'PO', 'id': ANY, 'name': 'Portugal'}, 'id': ANY, 'name': 'TestCity'},
                    'is_suggested': False,
                    'media': None,
                    'rating': 0,
                    'tags': [],
                    'title': 'TestSite1',
                    'type': 'place',
                },
            ],
            'num_of_stops': 1,
            'num_of_views': 1,
            'is_top_ten': False,
            'tags': [],
            'title': 'TestRoute',
        }

    def test_by_city_returns_200(self):
        response = self.api_client.get('/routes/by_city')
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': ANY,
                'name': 'TestCity',
                'routes': [
                    {
                        'id': ANY,
                        'stops': [
                            {
                                'city': {
                                    'id': ANY,
                                    'name': 'TestCity',
                                    'country': {'id': ANY, 'code': 'PO', 'name': 'Portugal'},
                                },
                                'id': ANY,
                                'has_been_accepted': True,
                                'images': [],
                                'is_suggested': False,
                                'media': None,
                                'rating': 0,
                                'tags': [],
                                'title': 'TestSite1',
                                'type': 'place',
                            }
                        ],
                        'num_of_stops': 1,
                        'num_of_views': 0,
                        'is_top_ten': False,
                        'tags': [],
                        'title': 'TestRoute',
                    }
                ],
            }
        ]
