from unittest.mock import ANY, patch

from django.core.files.uploadedfile import SimpleUploadedFile

from local_secrets.core.tests.base_test_case import BaseTestCase
from local_secrets.users.models import CustomUser, Notification, Tag, UserNotification


class TestUserViews(BaseTestCase):
    user_response = {
        'id': ANY,
        'last_login': ANY,
        'username': 'test2@rudo.es',
        'first_name': 'test2',
        'last_name': 'rudo',
        'email': 'test2@rudo.es',
        'date_joined': ANY,
        'tags': ANY,
        'phone': ANY,
        'groups': [],
        'language': None,
        'device_id': ANY,
        'profile_picture': None,
        'next_trip': {"cities": [], "end_date": None, "initial_date": None, "title": "", "type": None},
        'current_trip': {"cities": [], "end_date": None, "initial_date": None, "title": "", "type": None},
        'is_on_trip': False,
        'num_of_upcoming_travels': 0,
        'num_of_past_travels': 0,
        'visited_events': 0,
        'visited_places': 0,
    }

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        user = CustomUser.objects.create(username='test@rudo.es')
        user.set_password('12345678A')
        user.save()

        Tag.objects.create(title='TestTag1')
        Tag.objects.create(title='TestTag2')

        notification = Notification.objects.create(title='Test', body='Test')
        UserNotification.objects.create(user=user, notification=notification)

    def test_create_returns_201(self):
        response = self.api_client.post(
            '/users/create',
            data={
                'username': 'test2@rudo.es',
                'first_name': 'test2',
                'last_name': 'rudo',
                'email': 'test2@rudo.es',
                'password': '12345678A#',
                'phone': '+34620687729',
            },
        )

        assert response.status_code == 201
        assert response.json() == self.user_response

        assert CustomUser.objects.get(id=response.json().get('id')).check_password('12345678A#')

    def test_select_preferences_returns_201(self):
        assert CustomUser.objects.get(username='userTest1').tags.all().count() == 0

        response = self.api_client.post(
            '/users/select_preferences',
            data={
                'tags': [
                    1,
                ]
            },
        )

        assert response.status_code == 201
        assert CustomUser.objects.get(username='userTest1').tags.first().id == 1

    def test_retrieve_preferences_returns_200(self):
        assert CustomUser.objects.get(username='userTest1').tags.all().count() == 0
        CustomUser.objects.get(username='userTest1').update_tags([1])

        response = self.api_client.get(
            '/users/preferences',
        )

        assert response.status_code == 200
        assert response.json() == [
            {'id': ANY, 'title': 'TestTag1', 'is_selected': True},
            {'id': ANY, 'title': 'TestTag2', 'is_selected': False},
        ]

    def test_me_returns_200(self):
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
            'next_trip': {"cities": [], "end_date": None, "initial_date": None, "title": "", "type": None},
            'current_trip': {"cities": [], "end_date": None, "initial_date": None, "title": "", "type": None},
            'is_on_trip': False,
            'num_of_upcoming_travels': 0,
            'num_of_past_travels': 0,
            'visited_events': 0,
            'visited_places': 0,
            'language': None,
            'groups': [],
        }

    def test_update_returns_200(self):
        response = self.api_client.patch(
            '/users/me',
            data={
                'username': 'test2@rudo.es',
                'first_name': 'test2',
                'last_name': 'rudo',
                'email': 'test2@rudo.es',
                'phone': '+34620687729',
            },
        )

        assert response.status_code == 200
        assert response.json() == self.user_response

    @patch.object(CustomUser, 'save')
    def test_update_pfp_returns_200(self, mock_save):
        pfp = SimpleUploadedFile('pfp.png', b'file_content', content_type='png')
        response = self.api_client.post('/users/1/update_pfp', data={'profile_picture': pfp})

        assert response.status_code == 200

    def test_list_notifications_returns_200(self):
        response = self.api_client.get('/users/notifications')
        assert response.status_code == 200

    def test_has_notifications_returns_200(self):
        response = self.api_client.get('/users/has_notifications')
        assert response.status_code == 200
        assert response.json() == {'detail': True}
