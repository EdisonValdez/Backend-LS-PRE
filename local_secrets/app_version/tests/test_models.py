from local_secrets.app_version.models import AppVersion, Store
from local_secrets.app_version.tests.test_manager import TestAppVersionManager
from local_secrets.core.tests.base_test_case import BaseTestCase


class TestAppVersionModels(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        TestAppVersionManager.create_app_version_test_data()

    def test_app_version_model_str(self):
        self.assertTrue(str(AppVersion.objects.first()))

    def test_store_model_str(self):
        self.assertTrue(str(Store.objects.first()))
