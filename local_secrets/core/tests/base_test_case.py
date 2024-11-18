from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient


class BaseTestCase(TestCase):
    USERNAME = 'userTest1'
    API_CLIENT_HEADERS = {'HTTP_AUTHORIZATION': 'Bearer token', 'USER_AGENT': 'ApiMockClient'}
    USER_MODEL_CLASS = get_user_model()

    def setUp(self):
        super(BaseTestCase, self).setUp()

        self.api_client = APIClient(**self.API_CLIENT_HEADERS)
        self.api_client.login(username=self.USERNAME, password='secret')
        # General mocked content goes here

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # General mocked data goes here
        u = cls.USER_MODEL_CLASS.objects.create(username=cls.USERNAME, email='user@test1.es')
        u.set_password('secret')
        u.save()

    @staticmethod
    def get_mocked_response(
        content, status_code: status = status.HTTP_200_OK, headers: dict = None, content_type: str = None
    ) -> Response:
        return Response(data=content, status=status_code, headers=headers, content_type=content_type)

    @classmethod
    def get_default_user(cls) -> USER_MODEL_CLASS:
        return cls.USER_MODEL_CLASS.objects.get(username=cls.USERNAME)
