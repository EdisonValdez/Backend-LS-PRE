from django.contrib.gis.geos import Point

from local_secrets.cities.models import Address, City, Country
from local_secrets.core.tests.base_test_case import BaseTestCase
from local_secrets.sites.models import Category, HourRange, Schedule, Site, SpecialSchedule, SubCategory


class TestSite(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        category1 = Category.objects.create(title='Category1')
        category2 = Category.objects.create(title='Category2')

        subcategory11 = SubCategory.objects.create(title='Subcategory11', category=category1)
        subcategory21 = SubCategory.objects.create(title='Subcategory21', category=category2)

        city1 = City.objects.create(
            name='TestCity',
            cp='123456',
            province='Test',
            description='Test',
            point=Point(0.0, 0.0),
            country=Country.objects.create(name='Portugal', code='PO'),
        )

        address1 = Address.objects.create(
            street='Calle de la piruleta',
            city=city1,
            point=Point(0.0, 0.0),
            google_place_id='',
            details='Test',
            number='1',
            door='1',
            floor=None,
        )

        site1 = Site.objects.create(
            title='TestSite1', type='place', description='Test place', address=address1, city=city1
        )

        site1.categories.add(category1)
        site1.subcategories.add(subcategory11)

        site2 = Site.objects.create(title='TestSite2', type='place', description='Test place')
        site2.categories.add(category2)
        site2.subcategories.add(subcategory21)

        schedule_monday = Schedule.objects.create(day='monday', site=site1)
        HourRange.objects.create(initial_hour='08:00', end_hour='23:00', schedule=schedule_monday)

        schedule_thursday = Schedule.objects.create(day='thursday', site=site1)
        HourRange.objects.create(initial_hour='08:00', end_hour='23:00', schedule=schedule_thursday)

        schedule_tuesday = Schedule.objects.create(day='tuesday', site=site2)
        HourRange.objects.create(initial_hour='10:00', end_hour='14:00', schedule=schedule_tuesday)
        HourRange.objects.create(initial_hour='20:00', end_hour='02:00', schedule=schedule_tuesday)

        event1 = Site.objects.create(title='EventSite1', type='event', description='Test Event')
        SpecialSchedule.objects.create(day='2023-04-21', initial_hour='09:00', end_hour='17:00', site=event1)
        SpecialSchedule.objects.create(day='2023-04-27', initial_hour='10:00', end_hour='12:00', site=event1)
        SpecialSchedule.objects.create(day='2023-04-28', initial_hour='10:00', end_hour='12:00', site=event1)
