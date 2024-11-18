from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.core.validators import FileExtensionValidator, MaxValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils.timezone import localtime, now
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField

from local_secrets.cities.models import Address, City
from local_secrets.core.custom_exceptions import CustomApiException
from local_secrets.languages.models import Language
from local_secrets.sites.choices import Day, FrequencyChoices, SiteType
from local_secrets.sites.managers import ScheduleQueryset, SiteManager, SiteQueryset, SpecialScheduleQueryset, \
    AdminSiteManager, LevelManager, CategoryManager, SubcategoryManager, BaseManager
from local_secrets.users.models import CustomUser, Tag


class Site(models.Model):
    title = models.CharField(max_length=500, null=False, blank=False, verbose_name=_('Title'))

    levels = models.ManyToManyField('Level', verbose_name=_('Levels'), related_name='sites')
    categories = models.ManyToManyField('Category', verbose_name=_('Categories'), related_name='sites')
    subcategories = models.ManyToManyField('SubCategory', blank=True, verbose_name=_('Subcategories'), related_name='sites')
    type = models.CharField(max_length=100, choices=SiteType.choices, default=SiteType.PLACE, verbose_name=_('Type'))

    description = models.TextField(verbose_name=_('Description'))

    is_suggested = models.BooleanField(default=False)
    has_been_accepted = models.BooleanField(default=True)
    frequency = models.CharField(
        max_length=100, choices=FrequencyChoices.choices, default='never', verbose_name=_('Frequency')
    )
    media = models.FileField(
        upload_to='site_videos',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'webm', 'mkv'])],
        verbose_name=_('Video'),
    )
    url = models.CharField(max_length=500, verbose_name=_('Link'), null=True, blank=True)
    phone = models.CharField(max_length=500, verbose_name=_('Contact phone'), null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='site_tags', verbose_name=_('Tags'))
    users = models.ManyToManyField(
        CustomUser, related_name='fav_sites', through='FavoriteSites', verbose_name=_('Users')
    )
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, related_name='sites', null=True, blank=True)
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, related_name='sites', null=True, blank=True, verbose_name=_('City')
    )
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name=_('Created by'))
    always_open = models.BooleanField(default=False, verbose_name=_('Always open'))
    is_top_10 = models.BooleanField(default=False, verbose_name=_('Is top 10'))

    objects = SiteManager.from_queryset(SiteQueryset)()
    objects_for_admin = AdminSiteManager.from_queryset(SiteQueryset)()

    class Meta:
        verbose_name = _('Site')
        verbose_name_plural = _('Sites')
        indexes = [
            models.Index(fields=['frequency'], name='frequency_idx', condition=Q(type='event'))
        ]

    def __str__(self):
        return self.title

    def display_text(self, field, language='en'):
        value = None
        try:
            value = getattr(self, f"translated_{field}_{language}")
        except BaseException:
            value = getattr(self, field)
        if value is None:
            return getattr(self, field)
        return value

    def mark_as_fav(self, user):
        fav_site, created = FavoriteSites.objects.get_or_create(site=self, user=user)
        if not created:
            fav_site.delete()
        if created and user.fav_sites.count() > 50:
            fav_site.delete()
            raise CustomApiException(message=_('El usuario ya tiene más de 50 favoritos'), status_code=406)
        return created

    def is_open_by_schedule(self, current_time=now()):
        if self.always_open:
            return True
        days = dict(zip(range(0, 6), Day.choices))
        if self.type == SiteType.PLACE:  # The place Site uses only regular schedules from Mon-Sun.
            try:
                schedule = self.schedules.prefetch_related('opening_hours').get(day=days[current_time.weekday()][0])
                use_union = schedule.opening_hours.filter(initial_hour__gt=F('end_hour')).exists()
            except Schedule.DoesNotExist:
                print('There is no schedule for the specified day')
                return False
            except Exception:
                return False
        else:  # The event Site uses special schedules
            try:
                schedule = self.special_schedules.get(day=current_time.date())
                use_union = schedule.opening_hours.filter(initial_hour__gt=F('end_hour')).exists()
            except SpecialSchedule.DoesNotExist:
                print('There is no special schedule for the specified day')
                return False

        if not use_union:
            time_ranges = schedule.opening_hours.filter(
                initial_hour__lte=current_time.time(), end_hour__gte=current_time.time()
            )
        else:
            time_ranges = schedule.opening_hours.filter(
                Q(initial_hour__lte=current_time.time()) | Q(end_hour__gte=current_time.time())
            )
        return time_ranges.exists()

    def next_schedule(self):
        current_time = localtime()
        if self.type == SiteType.PLACE:
            schedule = self.schedules.annotate_day_order(current_time.weekday()).order_by('day_distance').first()
            return schedule
        else:
            if self.frequency in ['week', 'day', 'workday']:
                # This is meant to return a SpecialSchedule with the next week's day given the Schedule,
                # not the SpecialSchedule of the event.

                # Get the closest Schedule on the event
                next_schedule = self.schedules.annotate_day_order(current_time.weekday()).order_by('day_distance').first()
                if next_schedule:
                    # Calculate the difference for the next day on next_schedule on the next week
                    if next_schedule.day_order >= current_time.date().weekday():
                        # If the day is after today's weekday
                        days_until_next = next_schedule.day_order - current_time.date().weekday()
                    else:
                        # If the next_schedule's weekday is before or equal to today
                        days_until_next = 7 - (current_time.date().weekday() - next_schedule.day_order)
                    if days_until_next == 7:
                        next_schedule_datetime = current_time
                    else:
                        next_schedule_datetime = current_time + timedelta(days=days_until_next)
                    special_schedule = SpecialSchedule(
                        site=self,
                        day=next_schedule_datetime.date()
                    )
                    return special_schedule
                else:
                    return None

                # return self.schedules.annotate_day_order(current_time.weekday()).order_by('day_distance').first()
            else:
                special_schedules = self.special_schedules.annotate_day_distance(current_time.date())
                schedule = special_schedules.order_by('day_distance').first()
                if self.frequency in ['year',] and (schedule and schedule.day < current_time.date()):
                    schedule = special_schedules.order_by('-day_distance').first()
                    schedule = SpecialSchedule(
                        id=self.id,
                        site=self,
                        day=schedule.day.replace(year=current_time.date().year + 1),   # Add one year
                    )
                return schedule

    def check_frequency(self, is_open):
        current_date = localtime()

        if self.frequency == 'never':
            print(type(is_open))
            return True if is_open else False
        elif self.frequency == 'day':
            return True
        elif self.frequency == 'week':
            # Use the normal Schedule to check if today is applicable
            days = dict(zip(range(0, 6), Day.choices))
            res = self.schedules.filter(day=days[current_date.date().weekday()][0]).exists()
            return res

            # Old way of using the special_schedules
            # weekday = self.special_schedules.first().day.weekday()
            # if current_date.date().weekday() == weekday:
                # return True
        elif self.frequency == 'month':
            month_day = self.special_schedules.first().day
            if current_date.date().day == month_day:
                return True
        elif self.frequency == 'year':
            day = self.special_schedules.first().day
            if current_date.date() == day:
                return True
        elif self.frequency == 'workday':
            if current_date.weekday() < 5:
                return True
        return False

    def open_days(self):
        special_schedules = self.special_schedules.order_by('day')
        return special_schedules.first(), special_schedules.last()

    def add_comment(self, user, body, rating):
        comment = Comment.objects.create(user=user, site=self, body=body, rating=rating, created_at=now())
        return comment

    def create_address(self, location):
        geolocation = location.get('geolocation').split(',')
        point = Point((Decimal(geolocation[0]), Decimal(geolocation[1])), srid=4326)
        city = City.objects.filter(**location.get('city')).first()
        if city is None:
            self.save()
            return
        address = Address.objects.create(
            street=location.get('street_name'), city=city, point=point, details=location.get('link')
        )
        self.address = address
        self.city = city
        self.save()

    def add_schedules(self, schedules):
        for schedule in schedules:
            day = schedule.get('day')
            for hours in schedule.get('opening_hours'):
                initial_hour = hours.get('initial_hour')
                end_hour = hours.get('end_hour')

                db_schedule = Schedule.objects.create(site=self, day=day)
                HourRange.objects.create(initial_hour=initial_hour, end_hour=end_hour, schedule=db_schedule)

    def add_special_schedules(self, special_schedules):
        for special_schedule in special_schedules:
            initial_date = special_schedule.get('initial_date')
            end_date = special_schedule.get('end_date')
            initial_hour = special_schedule.get('initial_hour')
            end_hour = special_schedule.get('end_hour')

            date_format = '%Y-%m-%d'
            try:
                datetime.strptime(initial_date, date_format)
            except ValueError:
                date_format = '%I:%M %p'

            all_days = [
                datetime.strptime(initial_date, date_format).date() + timedelta(days=x)
                for x in range(
                    (
                        (datetime.strptime(end_date, date_format).date() + timedelta(days=1))
                        - datetime.strptime(initial_date, date_format).date()
                    ).days
                )
            ]
            for day in all_days:
                db_special_schedule = SpecialSchedule.objects.create(day=day, site=self)
                SpecialHourRange.objects.create(
                    schedule=db_special_schedule, initial_hour=initial_hour, end_hour=end_hour
                )


class TranslatedSite(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, null=False, blank=False, verbose_name=_('Translated Title'))
    description = models.TextField(verbose_name=_('Translated Description'))

    class Meta:
        indexes = [
            models.Index(fields=['title', 'description'])
        ]

class SiteImage(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='images', verbose_name=_('Site'))
    image = ThumbnailerImageField(upload_to='site_images')


class Level(models.Model):
    title = models.CharField(max_length=500, null=False, blank=False, verbose_name=_('Title'))
    type = models.CharField(max_length=100, choices=SiteType.choices, default=SiteType.PLACE, verbose_name=_('Type'))
    order = models.IntegerField(default=0, verbose_name=_('Order'))

    objects = BaseManager()
    objects_for_admin = BaseManager()
    objects_for_api = LevelManager()

    class Meta:
        verbose_name = _('Search level')
        verbose_name_plural = _('Search levels')
        ordering = ('title',)

    def display_text(self, field, language='en'):
        try:
            return getattr(self.translations.get(language__code=language), field)
        except BaseException:
            return getattr(self, field)

    def __str__(self):
        return f'{self.title} - ({self.type})'


class TranslatedLevel(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, null=False, blank=False, verbose_name=_('Translated Title'))

    class Meta:
        indexes = [
            models.Index(fields=['title',])
        ]


class Category(models.Model):
    level = models.ForeignKey(
        Level, on_delete=models.SET_NULL, null=True, related_name='categories', verbose_name=_('Level')
    )
    title = models.CharField(max_length=500, null=False, blank=False, verbose_name=_('Title'))
    type = models.CharField(max_length=100, choices=SiteType.choices, default=SiteType.PLACE, verbose_name=_('Type'))
    order = models.IntegerField(default=0, verbose_name=_('Order'))

    objects = BaseManager()
    objects_for_admin = BaseManager()
    objects_for_api = CategoryManager()

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ('title',)

    def display_text(self, field, language='en'):
        try:
            return getattr(self.translations.get(language__code=language), field)
        except BaseException:
            return getattr(self, field)

    def __str__(self):
        return f'{self.title} - ({self.type})'


class TranslatedCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, null=False, blank=False, verbose_name=_('Translated Title'))

    class Meta:
        indexes = [
            models.Index(fields=['title',])
        ]


class SubCategory(models.Model):
    title = models.CharField(max_length=500, null=False, blank=False, verbose_name=_('Title'))
    type = models.CharField(max_length=100, choices=SiteType.choices, default=SiteType.PLACE, verbose_name=_('Type'))

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='subcategories', verbose_name=_('Category')
    )
    order = models.IntegerField(default=0, verbose_name=_('Order'))

    objects = BaseManager()
    objects_for_admin = BaseManager()
    objects_for_api = SubcategoryManager()

    class Meta:
        verbose_name = _('Subcategory')
        verbose_name_plural = _('Subcategories')
        ordering = ('title',)

    def display_text(self, field, language='en'):
        try:
            return getattr(self.translations.get(language__code=language), field)
        except BaseException:
            return getattr(self, field)

    def __str__(self):
        return f'{self.title} - ({self.type})'


class TranslatedSubCategory(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, null=False, blank=False, verbose_name=_('Title'))

    class Meta:
        indexes = [
            models.Index(fields=['title',])
        ]


class FavoriteSites(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('User'))
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name=_('Site'))

    class Meta:
        verbose_name = _('Favorite Site')
        verbose_name_plural = _('Favorite Sites')

    def __str__(self):
        return f'{self.user.username} likes {self.site.title}'


class Schedule(models.Model):
    day = models.CharField(max_length=100, choices=Day.choices)
    site = models.ForeignKey(Site, related_name='schedules', on_delete=models.CASCADE, verbose_name=_('Site'))

    objects = ScheduleQueryset.as_manager()

    class Meta:
        verbose_name = _('Schedule')
        verbose_name_plural = _('Schedules')

    def __str__(self):
        try:
            return f'{self.site.title} - {self.day}'
        except Exception:
            return f'None - {self.day}'


class HourRange(models.Model):
    initial_hour = models.TimeField(default='08:00 AM')
    end_hour = models.TimeField(default='11:00 PM')
    schedule = models.ForeignKey(
        Schedule, related_name='opening_hours', on_delete=models.CASCADE, verbose_name=_('Schedule')
    )

    class Meta:
        verbose_name = _('Hour Range')
        verbose_name_plural = _('Hour Ranges')

    def __str__(self):
        return f'{self.schedule.day}: {self.initial_hour} - {self.end_hour}'


class SpecialSchedule(models.Model):
    day = models.DateField()
    site = models.ForeignKey(Site, related_name='special_schedules', on_delete=models.CASCADE, verbose_name=_('Site'))

    objects = SpecialScheduleQueryset.as_manager()

    class Meta:
        verbose_name = _('Special Schedule')
        verbose_name_plural = _('Special Schedules')

    def __str__(self):
        return f'{self.day}'


class SpecialHourRange(models.Model):
    initial_hour = models.TimeField(default='08:00')
    end_hour = models.TimeField(default='23:00')
    schedule = models.ForeignKey(
        SpecialSchedule, related_name='opening_hours', on_delete=models.CASCADE, verbose_name=_('Schedule')
    )

    def __str__(self):
        return f'{self.schedule.day}: {self.initial_hour} - {self.end_hour}'


class Comment(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='comments', verbose_name=_('User')
    )
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Site'))
    body = models.TextField(verbose_name=_('Body'))
    rating = models.IntegerField(verbose_name=_('Rating'), validators=[MaxValueValidator(5)])
    created_at = models.DateTimeField(verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')

    def __str__(self):
        return f'{self.user} - {self.site} - {self.rating}'


class DefaultImage(models.Model):
    title = models.CharField(max_length=100)
    image = ThumbnailerImageField(upload_to='default_images')

    def __str__(self):
        return self.title


class ImageSize(models.Model):
    min_width = models.IntegerField(default=512)
    min_height = models.IntegerField(default=512)
    max_width = models.IntegerField(default=4096)
    max_height = models.IntegerField(default=2160)

    def __str__(self):
        return 'ImageSize'

    class Meta:
        verbose_name = _('Image Size')
        verbose_name_plural = _('Images Sizes')


class VideoSize(models.Model):
    min_size = models.IntegerField(default=512)
    max_size = models.IntegerField(default=4096)

    def __str__(self):
        return 'VideoSize'

    class Meta:
        verbose_name = _('Video Size')
        verbose_name_plural = _('Videos Sizes')
