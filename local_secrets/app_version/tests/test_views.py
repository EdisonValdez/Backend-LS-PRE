from django.urls import reverse
from rest_framework import status

from local_secrets.app_version.choices import AppPlatform
from local_secrets.app_version.models import AppVersion
from local_secrets.core.tests.base_test_case import BaseTestCase


class TestAppVersionViews(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        AppVersion.objects.create(version='2.0.1', platform=AppPlatform.ANDROID, required=True)
        AppVersion.objects.create(version='2.0.1', platform=AppPlatform.IOS, required=True)

    def test_app_version_update_required(self):
        params = {'version': '2.0.0', 'platform': AppPlatform.IOS}
        response = self.api_client.get(reverse('AppVersion-list'), data=params)
        self.assertTrue(response.json().get('update_available'))

    def test_app_version_update(self):
        params = {'version': '2.0.1', 'platform': AppPlatform.IOS}
        response = self.api_client.put(reverse('AppVersion-update-version'), data=params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.json().get('update_available'))

    def test_app_version_update_not_existing(self):
        params = {'version': '2.0.2', 'platform': AppPlatform.IOS}
        response = self.api_client.put(reverse('AppVersion-update-version'), data=params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('error' in response.json())
