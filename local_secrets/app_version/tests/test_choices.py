from django.test import TestCase

from local_secrets.app_version.choices import AppPlatform


class TestAppPlatform(TestCase):
    expected_result = {'ios': AppPlatform.IOS, 'android': AppPlatform.ANDROID}

    def test_values_dict(self):
        self.assertDictEqual(AppPlatform.values_dict(), self.expected_result)

    def test_from_value(self):
        for key, value in self.expected_result.items():
            self.assertEqual(AppPlatform.from_value(key), value)
