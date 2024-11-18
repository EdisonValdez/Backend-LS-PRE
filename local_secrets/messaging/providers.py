from .models import APNSConfig, AndroidConfig, FCMDevice, FCMDeviceQuerySet, FCMOptions, Message, Notification
from ..app_version.choices import AppPlatform


class FCMProvider:
    @staticmethod
    def create_device(token: str, platform: AppPlatform, device_id: str = None) -> FCMDevice:
        device = FCMDevice(registration_id=token, type=platform.value, device_id=device_id)
        device.save()
        return device

    # noinspection PyTypeChecker
    @staticmethod
    def get_devices(**kwargs) -> FCMDeviceQuerySet:
        if not kwargs or len(kwargs) == 0:
            return FCMDevice.objects.all()
        return FCMDevice.objects.filter(**kwargs)

    @staticmethod
    def create_message(
        data=None,
        notification: Notification = None,
        android: AndroidConfig = None,
        apns: APNSConfig = None,
        fcm_options: FCMOptions = None,
        token: str = None,
        topic: str = None,
    ) -> Message:
        return Message(
            data=data,
            notification=notification,
            android=android,
            apns=apns,
            fcm_options=fcm_options,
            token=token,
            topic=topic,
        )

    @classmethod
    def send_test_notification(
        cls, title='Test title', body='Test image', image='https://i.ebayimg.com/images/g/mrkAAOSwksRfgmko/s-l300.jpg'
    ):
        notif = Notification(title=title, body=body, image=image)
        return cls.get_devices().send_message(cls.create_message(notification=notif))

    @classmethod
    def send_notification_to_device(
        cls, title, body, device_id, image='https://i.ebayimg.com/images/g/mrkAAOSwksRfgmko/s-l300.jpg'
    ):
        notification = Notification(title=title, body=body, image=image)
        devices = cls.get_devices(device_id=device_id)
        response = devices.send_message(message=cls.create_message(notification=notification))
        return response
