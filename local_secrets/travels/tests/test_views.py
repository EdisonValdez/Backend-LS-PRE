from unittest.mock import ANY

from freezegun import freeze_time

from local_secrets.sites.models import Site
from local_secrets.travels.models import Travel
from local_secrets.travels.tests.test_setup import TestTravelSetup


class TestTravelViews(TestTravelSetup):
    def test_travels_returns_200(self):
        response = self.api_client.get('/travels/')
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": ANY,
                "title": "Test travel",
                "days_until_trip": None,
                "type": "solo",
                "cities": [],
                "initial_date": "2023-05-06",
                "end_date": "2023-05-10",
                "stops": [],
                'num_of_events': 0,
                'num_of_places': 0,
                'similar_stops': [],
            },
            {
                "id": ANY,
                "days_until_trip": None,
                "title": "Old trip",
                "type": "romantic",
                "cities": [],
                "initial_date": "2023-04-02",
                "end_date": "2023-04-10",
                "stops": ANY,
                'num_of_events': 0,
                'num_of_places': 1,
                'similar_stops': [],
            },
        ]

    def test_travels_detail_returns_200(self):
        response = self.api_client.get('/travels/1')
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "title": "Test travel",
            "days_until_trip": None,
            "type": "solo",
            "cities": [],
            "initial_date": "2023-05-06",
            "end_date": "2023-05-10",
            "stops": [],
            'num_of_events': 0,
            'num_of_places': 0,
            'similar_stops': [],
        }

    def test_patch_travel_returns_200(self):
        response = self.api_client.patch('/travels/1', data={'title': 'Test travel 1', 'type': 'romantic'})
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "days_until_trip": None,
            "title": "Test travel 1",
            "type": "romantic",
            "cities": [],
            "initial_date": "2023-05-06",
            "end_date": "2023-05-10",
            "stops": [],
            'num_of_events': 0,
            'num_of_places': 0,
            'similar_stops': [],
        }

    @freeze_time('2023-05-05 10:30:00')
    def test_history_returns_200(self):
        response = self.api_client.get('/travels/history')
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": ANY,
                "days_until_trip": None,
                "title": "Old trip",
                "type": "romantic",
                "cities": [],
                'num_of_events': 0,
                'num_of_places': 1,
                'similar_stops': [],
                "initial_date": "2023-04-02",
                "end_date": "2023-04-10",
                "stops": ANY,
            }
        ]

    @freeze_time('2023-05-05 10:30:00')
    def test_upcoming_returns_200(self):
        response = self.api_client.get('/travels/upcoming')
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": ANY,
                "days_until_trip": None,
                "title": "Test travel",
                "type": "solo",
                "cities": [],
                "initial_date": "2023-05-06",
                "end_date": "2023-05-10",
                "stops": [],
                'num_of_events': 0,
                'num_of_places': 0,
                'similar_stops': [],
            }
        ]

    def test_add_site_returns_200(self):
        travel = Travel.objects.get(id=1)
        assert travel.stops.count() == 0
        response = self.api_client.post('/travels/1/add_site', data={'id': Site.objects.first().id})
        travel.refresh_from_db()
        assert response.status_code == 200
        assert travel.stops.count() == 1

    def test_add_site_with_order_returns_200(self):
        travel = Travel.objects.get(id=1)
        assert travel.stops.count() == 0
        response = self.api_client.post('/travels/1/add_site', data={'id': Site.objects.first().id, 'order': 1})
        travel.refresh_from_db()
        assert response.status_code == 200
        assert travel.stops.count() == 1

    def test_remove_site_returns_200(self):
        travel = Travel.objects.get(id=1)
        travel.stops.add(Site.objects.get(id=1))
        assert travel.stops.count() == 1
        response = self.api_client.post('/travels/1/remove_site', data={'id': 1})
        travel.refresh_from_db()
        assert response.status_code == 200
        assert travel.stops.count() == 0

    @freeze_time('2023-05-24 10:30:00')
    def test_me_returns_correct_travel(self):
        response = self.api_client.get('/users/me')
        assert response.status_code == 200
        assert response.json() == {
            'id': ANY,
            'last_login': ANY,
            'username': 'userTest1',
            'first_name': '',
            'last_name': '',
            'email': 'user@test1.es',
            'date_joined': ANY,
            'tags': ANY,
            'phone': ANY,
            'device_id': ANY,
            'profile_picture': None,
            'next_trip': {
                "id": ANY,
                "days_until_trip": ANY,
                "title": "",
                "type": None,
                "cities": [],
                "initial_date": ANY,
                "end_date": ANY,
            },
            'current_trip': {'cities': [], 'end_date': None, 'initial_date': None, 'title': '', 'type': None},
            'is_on_trip': False,
            'num_of_upcoming_travels': 0,
            'num_of_past_travels': 2,
            'visited_events': 0,
            'visited_places': 1,
            'language': None,
            'groups': [],
        }

    def test_create_travel_returns_201(self):
        data = {'title': 'Travel test', 'initial_date': '2023-06-06', 'end_date': '2023-06-07', 'type': 'solo'}
        response = self.api_client.post('/travels/', data=data)
        assert response.status_code == 201
