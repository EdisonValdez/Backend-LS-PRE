from unittest.mock import patch

from local_secrets.app_version.choices import AppPlatform
from local_secrets.core.tests.base_test_case import BaseTestCase
from local_secrets.messaging.models import FCMDevice, FCMDeviceQuerySet
from local_secrets.messaging.providers import FCMProvider


class TestFCMProvider(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        FCMDevice(
            device_id='aDeviceId',
            registration_id='aDeviceToken',
            type=AppPlatform.ANDROID,
        ).save()

    def setUp(self):
        super(TestFCMProvider, self).setUp()
        self.provider = FCMProvider()

    def test_get_devices_by_platform(self):
        devices = self.provider.get_devices(type=AppPlatform.IOS.value)
        self.assertFalse(devices.exists())

    def test_create_device(self):
        device = self.provider.create_device('aNewDeviceToken', AppPlatform.IOS, 'aNewDeviceId')
        self.assertIsNotNone(device.pk)

    @patch.object(FCMDeviceQuerySet, 'send_message')
    def test_send_push_sample(self, mock_send_message):
        self.provider.send_test_notification()
        mock_send_message.assert_called()
