from datetime import datetime

from freezegun import freeze_time

from local_secrets.sites.models import Site
from local_secrets.sites.tests.tests_setup import TestSite
from local_secrets.users.models import CustomUser


class TestSiteModels(TestSite):
    def test_mark_as_fav(self):
        user = CustomUser.objects.first()
        site = Site.objects.get(title='TestSite1')
        assert site.users.count() == 0
        site.mark_as_fav(user)
        assert site.users.count() == 1

    def test_unmark_as_fav(self):
        user = CustomUser.objects.first()
        site = Site.objects.get(title='TestSite1')
        assert site.users.count() == 0
        site.mark_as_fav(user)
        site.mark_as_fav(user)
        assert site.users.count() == 0

    #   Places
    @freeze_time('2023-04-19 09:30:00')
    def test_next_schedule_weekday(self):
        site = Site.objects.get(title='TestSite1')
        schedule = site.next_schedule()
        assert schedule.day == 'thursday'

    @freeze_time('2023-04-21 09:30:00')
    def test_next_schedule_weekend(self):
        site = Site.objects.get(title='TestSite1')
        schedule = site.next_schedule()
        assert schedule.day == 'monday'

    @freeze_time('2023-04-20 09:30:00')
    def test_is_open(self):
        site = Site.objects.get(title='TestSite1')
        assert site.is_open_by_schedule()

    @freeze_time('2023-04-20 23:30:00')
    def test_is_not_open(self):
        site = Site.objects.get(title='TestSite1')
        assert site.is_open_by_schedule() is False

    @freeze_time('2023-04-18 21:30:00')
    def test_is_open_at_night(self):
        site = Site.objects.get(title='TestSite2')
        assert site.is_open_by_schedule()

    @freeze_time('2023-04-18 23:30:00')
    def test_is_open_late(self):
        site = Site.objects.get(title='TestSite2')
        assert site.is_open_by_schedule()

    #   Events
    @freeze_time('2023-04-21 09:30:00')
    def test_event_is_open(self):
        site = Site.objects.get(title='EventSite1')
        assert site.is_open_by_schedule()

    @freeze_time('2023-04-21 22:30:00')
    def test_event_is_not_open(self):
        site = Site.objects.get(title='EventSite1')
        assert site.is_open_by_schedule() is False

    @freeze_time('2023-04-20 10:30:00')
    def test_event_is_not_open_other_day(self):
        site = Site.objects.get(title='EventSite1')
        assert site.is_open_by_schedule() is False

    def test_open_days(self):
        site = Site.objects.get(title='EventSite1')
        first_date, second_date = site.open_days()
        assert first_date.day == datetime.strptime('2023-04-21', "%Y-%m-%d").date()
        assert second_date.day == datetime.strptime('2023-04-28', "%Y-%m-%d").date()

    def test_add_comment(self):
        site = Site.objects.first()
        user = CustomUser.objects.first()
        assert site.comments.count() == 0
        assert user.comments.count() == 0
        site.add_comment(user=user, body='Test', rating=5)
        assert site.comments.first().body == 'Test'
        assert user.comments.first().body == 'Test'
