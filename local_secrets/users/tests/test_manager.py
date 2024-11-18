from local_secrets.core.tests.base_test_case import BaseTestCase
from local_secrets.users.models import CustomUser, Notification


class TestNotificationManager(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Notification.objects.create(title='Test', body='Test')

    def test_annotate_has_been_seen(self):
        user = CustomUser.objects.first()
        Notification.objects.first().mark_as_seen(user)
        notifications = Notification.objects.all().annotate_has_been_seen(user)
        assert notifications.first().has_been_seen

    def test_mark_as_seen(self):
        user = CustomUser.objects.first()
        Notification.objects.first().mark_as_seen(user)
        assert user.notifications.filter(has_been_seen=True).count() == 1
