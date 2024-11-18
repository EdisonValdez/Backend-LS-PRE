from unittest.mock import ANY

from django.contrib import auth
from django.utils.timezone import now
from freezegun import freeze_time

from local_secrets.sites.models import Comment, Site
from local_secrets.sites.tests.tests_setup import TestSite
from local_secrets.users.models import CustomUser, Tag


class TestSiteViews(TestSite):
    def test_suggest_site(self):
        response = self.api_client.post(
            '/sites/suggest_site',
            data={
                'title': 'Test',
                'type': 'place',
                'description': 'Test',
                'categories': [1, 2],
                'schedules': [
                    {'day': 'monday', 'opening_hours': [{'initial_hour': '08:00', 'end_hour': '12:00'}]},
                ],
                'location': {
                    "geolocation": "23.2, 23.3",
                    "street_name": "Test",
                    "link": "",
                    "city": {
                        "name": "Valencia",
                    },
                },
            },
            format='json',
        )
        assert response.status_code == 201

    def test_list_categories_returns_200(self):
        response = self.api_client.get('/sites/categories')

        assert response.status_code == 200
        assert response.json() == [
            {'id': ANY, 'title': 'Category1', 'subcategories': [{'id': ANY, 'title': 'Subcategory11'}]},
            {'id': ANY, 'title': 'Category2', 'subcategories': [{'id': ANY, 'title': 'Subcategory21'}]},
        ]

    def test_site_event_returns_200(self):
        site = Site.objects.get(id=3)
        response = self.api_client.get(f'/sites/{site.id}')
        assert response.status_code == 200

    def test_site_detail_returns_200(self):
        site = Site.objects.first()
        response = self.api_client.get(f'/sites/{site.id}')
        assert response.status_code == 200
        assert response.json() == {
            'id': site.id,
            'title': site.title,
            'description': site.description,
            'type': site.type,
            'categories': [
                {
                    'id': site.categories.first().id,
                    'title': site.categories.first().title,
                }
            ],
            'subcategories': [
                {
                    'id': site.subcategories.first().id,
                    'title': site.subcategories.first().title,
                }
            ],
            'images': [],
            'is_fav': False,
            'media': None,
            'tags': [],
            'address': ANY,
            'is_suggested': False,
            'has_been_accepted': True,
            'city': {
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
            },
            'next_schedule': {
                'id': ANY,
                'day': ANY,
                'opening_hours': [{'id': ANY, 'end_hour': ANY, 'initial_hour': ANY}],
            },
            'is_open': False,
            'schedules': [
                {
                    'id': ANY,
                    'day': 'monday',
                    'opening_hours': [{'id': ANY, 'end_hour': ANY, 'initial_hour': ANY}],
                },
                {
                    'id': ANY,
                    'day': 'thursday',
                    'opening_hours': [{'id': ANY, 'end_hour': ANY, 'initial_hour': ANY}],
                },
            ],
            'special_schedules': [],
            'rating': 0,
        }

    def test_site_list_returns_200(self):
        response = self.api_client.get('/sites/')
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': ANY,
                'city': {
                    'id': ANY,
                    'name': 'TestCity',
                    'country': {'id': ANY, 'name': 'Portugal', 'code': 'PO'},
                },
                'images': [],
                'is_fav': False,
                'title': 'TestSite1',
                'type': 'place',
                'is_suggested': False,
                'has_been_accepted': True,
                'media': None,
                'tags': [],
                'rating': 0,
            },
            {
                'id': ANY,
                'city': None,
                'images': [],
                'is_fav': False,
                'title': 'TestSite2',
                'type': 'place',
                'media': None,
                'is_suggested': False,
                'has_been_accepted': True,
                'tags': [],
                'rating': 0,
            },
            {
                'id': ANY,
                'city': None,
                'images': [],
                'is_fav': False,
                'title': 'EventSite1',
                'type': 'event',
                'media': None,
                'is_suggested': False,
                'has_been_accepted': True,
                'tags': [],
                'rating': 0,
            },
        ]

    def test_check_site_returns_200(self):
        assert auth.get_user(self.api_client).fav_sites.count() == 0
        site = Site.objects.first()
        response = self.api_client.post(f'/sites/{site.id}/check_fav')
        assert response.status_code == 200
        assert auth.get_user(self.api_client).fav_sites.count() == 1
        assert auth.get_user(self.api_client).fav_sites.first().id == site.id

    def test_favorite_sites_returns_200(self):
        site = Site.objects.first()
        site.mark_as_fav(auth.get_user(self.api_client))

        response = self.api_client.get('/sites/favorites')
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': site.id,
                'title': site.title,
                'type': site.type,
                'has_been_accepted': True,
                'is_suggested': False,
                'tags': [],
                'images': [],
                'is_fav': False,
                'media': None,
                'city': ANY,
                'rating': 0,
            }
        ]


class TestCommentViews(TestSite):
    @freeze_time('2023-04-20 10:30:00')
    def test_add_comment_to_site_returns_201(self):
        site = Site.objects.first()
        assert site.comments.count() == 0
        response = self.api_client.post(f'/sites/{site.id}/comment', data={'body': 'Test', 'rating': 5})
        assert response.status_code == 201
        assert site.comments.count() == 1
        assert site.comments.first().body == 'Test'
        assert site.comments.first().rating == 5
        assert site.comments.first().created_at == now()

    def test_list_comments_from_site_returns_200(self):
        site = Site.objects.first()
        user = CustomUser.objects.first()
        site.add_comment(user=user, body='Test', rating=5)
        response = self.api_client.get(f'/sites/{site.id}/comments')
        assert response.status_code == 200
        assert response.json() == [
            {'id': ANY, 'rating': 5, 'body': 'Test', 'created_at': ANY, 'user': {'username': 'userTest1'}},
        ]

    def test_update_comment_returns_200(self):
        comment = Comment.objects.create(
            user=CustomUser.objects.first(), site=Site.objects.first(), body='Test', rating=5, created_at=now()
        )
        data = {'body': 'Updated test'}
        response = self.api_client.patch(f'/sites/comments/{comment.id}', data=data)
        assert response.status_code == 200
        comment.refresh_from_db()
        assert comment.body == 'Updated test'

    def test_delete_comment_returns_204(self):
        site = Site.objects.first()
        assert site.comments.count() == 0
        comment = Comment.objects.create(
            user=CustomUser.objects.first(), site=site, body='Test', rating=5, created_at=now()
        )
        assert site.comments.count() == 1
        response = self.api_client.delete(f'/sites/comments/{comment.id}')
        assert response.status_code == 204
        assert site.comments.count() == 0

    def test_similar_returns_200(self):
        site = Site.objects.first()
        tag = Tag.objects.create(title='Test')
        site.tags.add(tag)
        site2 = Site.objects.last()
        site2.tags.add(tag)
        response = self.api_client.get(f'/sites/{site.id}/similar')
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': ANY,
                'city': None,
                'has_been_accepted': True,
                'images': [],
                'is_fav': False,
                'is_suggested': False,
                'media': None,
                'rating': 0,
                'tags': [{'id': ANY, 'title': 'Test'}],
                'title': 'EventSite1',
                'type': 'event',
            }
        ]
