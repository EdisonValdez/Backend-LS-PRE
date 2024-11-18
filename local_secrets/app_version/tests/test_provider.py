from local_secrets.app_version.choices import AppPlatform
from local_secrets.app_version.providers import AppVersionProvider
from local_secrets.app_version.tests.test_manager import TestAppVersionManager
from local_secrets.core.tests.base_test_case import BaseTestCase


class TestAppVersionProvider(BaseTestCase):
    provider = AppVersionProvider()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        TestAppVersionManager.create_app_version_test_data()

    def test_requires_update_when_current_version_is_higher_or_update_is_not_required(
        self,
    ):
        available, required = self.provider.is_update_needed(version='2.0.2', platform=AppPlatform.IOS)
        self.assertFalse(available)
        self.assertFalse(required)

    def test_requires_update_when_update_is_not_required(self):
        available, required = self.provider.is_update_needed(version='2.0.1', platform=AppPlatform.IOS)
        self.assertFalse(available)
        self.assertFalse(required)

    def test_returns_true_when_current_version_is_lower(self):
        available, required = self.provider.is_update_needed(version='0.1.1', platform=AppPlatform.IOS)
        self.assertTrue(available)
        self.assertTrue(required)

    def test_returns_false_when_current_version_is_lower_but_not_necessary(self):
        available, required = self.provider.is_update_needed(version='1.1.1', platform=AppPlatform.ANDROID)
        self.assertTrue(available)
        self.assertFalse(required)
