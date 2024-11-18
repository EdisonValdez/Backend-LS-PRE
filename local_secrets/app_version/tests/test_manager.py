from local_secrets.app_version.choices import AppPlatform
from local_secrets.app_version.models import AppVersion, Store
from local_secrets.core.tests.base_test_case import BaseTestCase


class TestAppVersionManager(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_app_version_test_data()

    @staticmethod
    def create_app_version_test_data():
        AppVersion.objects.create(version='1.0.0', platform=AppPlatform.IOS, required=True)
        AppVersion.objects.create(version='1.0.0', platform=AppPlatform.ANDROID, required=True)
        AppVersion.objects.create(version='2.0.0', platform=AppPlatform.IOS, required=True)
        AppVersion.objects.create(version='2.0.1', platform=AppPlatform.IOS, required=True)
        AppVersion.objects.create(version='2.0.0', platform=AppPlatform.ANDROID, required=False)
        Store.objects.create(platform=AppPlatform.ANDROID, url='link.to')

    def test_returns_false_when_no_version(self):
        available, required = AppVersion.objects.requires_update(version='0.0.1', platform='iosx')
        self.assertFalse(available)
        self.assertFalse(required)

    def test_requires_update_when_current_version_is_higher_or_update_is_not_required(
        self,
    ):
        available, required = AppVersion.objects.requires_update(version='2.0.2', platform=AppPlatform.IOS)
        self.assertFalse(available)
        self.assertFalse(required)

    def test_requires_update_when_update_is_not_required(self):
        available, required = AppVersion.objects.requires_update(version='2.0.1', platform=AppPlatform.IOS)
        self.assertFalse(available)
        self.assertFalse(required)

    def test_returns_true_when_current_version_is_lower(self):
        available, required = AppVersion.objects.requires_update(version='0.1.1', platform=AppPlatform.IOS)
        self.assertTrue(available)
        self.assertTrue(required)

    def test_returns_false_when_current_version_is_lower_but_not_necessary(self):
        available, required = AppVersion.objects.requires_update(version='1.1.1', platform=AppPlatform.ANDROID)
        self.assertTrue(available)
        self.assertFalse(required)
