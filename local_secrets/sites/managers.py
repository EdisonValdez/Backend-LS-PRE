from datetime import datetime, timedelta

from django.contrib.gis.geos import Point, MultiPoint, LineString, MultiLineString, Polygon
from django.db import models
from django.db.models import Case, Count, Exists, F, OuterRef, Q, Subquery, When, BooleanField, Value, IntegerField, \
    Max, ExpressionWrapper, DateField, DurationField
from django.db.models.functions import Abs, Coalesce, Cast
from django.utils.timezone import now, localtime
from rest_framework.exceptions import ValidationError

from local_secrets.core.utils.text import TextHelper as text
from local_secrets.languages.models import Language
from local_secrets.sites.choices import Day


class SiteManager(models.Manager):
    def get_queryset(self):
        # big_query = '''WITH translations AS ( SELECT ts.site_id, l.code, ts.title, ts.description FROM sites_translatedsite ts JOIN languages_language l ON ts.language_id = l.id WHERE l.code IN ('es', 'en-GB', 'en', 'fr', 'pt', 'de') ) SELECT s.id, s.title, s.type, s.description, s.is_suggested, s.has_been_accepted, s.frequency, s.media, s.url, s.phone, s.address_id, s.city_id, s.created_by_id, s.always_open, s.is_top_10, CASE WHEN s.always_open THEN TRUE WHEN s.frequency = 'never' THEN FALSE WHEN s.frequency = 'day' THEN TRUE WHEN s.frequency = 'week' THEN sched.day = 'tuesday' WHEN s.frequency = 'month' THEN EXTRACT(DAY FROM spec.day) = 15 WHEN s.frequency = 'year' THEN spec.day = DATE '2024-10-15' WHEN s.frequency = 'workday' THEN TRUE ELSE FALSE END AS is_open, MAX(t.title) FILTER (WHERE t.code = 'es') AS translated_title_es, MAX(t.description) FILTER (WHERE t.code = 'es') AS translated_description_es, MAX(t.title) FILTER (WHERE t.code = 'en-GB') AS translated_title_en_gb, MAX(t.description) FILTER (WHERE t.code = 'en-GB') AS translated_description_en_gb, MAX(t.title) FILTER (WHERE t.code = 'en') AS translated_title_en, MAX(t.description) FILTER (WHERE t.code = 'en') AS translated_description_en, MAX(t.title) FILTER (WHERE t.code = 'fr') AS translated_title_fr, MAX(t.description) FILTER (WHERE t.code = 'fr') AS translated_description_fr, MAX(t.title) FILTER (WHERE t.code = 'pt') AS translated_title_pt, MAX(t.description) FILTER (WHERE t.code = 'pt') AS translated_description_pt, MAX(t.title) FILTER (WHERE t.code = 'de') AS translated_title_de, MAX(t.description) FILTER (WHERE t.code = 'de') AS translated_description_de FROM sites_site s LEFT JOIN sites_schedule sched ON s.id = sched.site_id LEFT JOIN sites_specialschedule spec ON s.id = spec.site_id LEFT JOIN cities_city c ON s.city_id = c.id LEFT JOIN translations t ON t.site_id = s.id WHERE NOT ( ( (NOT c.activated AND c.activated IS NOT NULL) OR NOT s.has_been_accepted ) AND NOT ( s.frequency IN ('never') AND ( CASE WHEN s.always_open THEN TRUE WHEN s.frequency = 'never' THEN FALSE WHEN s.frequency = 'day' THEN TRUE WHEN s.frequency = 'week' THEN sched.day = 'tuesday' WHEN s.frequency = 'month' THEN EXTRACT(DAY FROM spec.day) = 15 WHEN s.frequency = 'year' THEN spec.day = DATE '2024-10-15' WHEN s.frequency = 'workday' THEN TRUE ELSE FALSE END ) AND s.type = 'event' ) AND NOT ( s.frequency IN ('never') AND EXISTS ( SELECT 1 FROM sites_specialschedule ss WHERE ss.day < DATE '2024-10-15' AND ss.site_id = s.id LIMIT 1 ) AND EXISTS ( SELECT 1 FROM sites_site U0 LEFT JOIN sites_specialschedule U1 ON U0.id = U1.site_id WHERE U1.id IS NULL AND U0.id = s.id ) AND s.type = 'event' ) ) GROUP BY s.id, s.title, s.type, s.description, s.is_suggested, s.has_been_accepted, s.frequency, s.media, s.url, s.phone, s.address_id, s.city_id, s.created_by_id, s.always_open, s.is_top_10, sched.day, spec.day, c.activated ;'''
        # from django.db import connection
        # cursor = connection.cursor()
        # return cursor.execute(big_query)

        return (
        #.exclude(
        #     Q(Q(city__activated=False) | Q(has_been_accepted=False)))
        # .exclude(
        #     Q(type='event', is_open=False, frequency__in=['never', ])
        # )
        # .exclude(
        #     type='event',
        #     frequency__in=['never', ],
        #     special_schedules__day__lt=now().date(),
        #     special_schedules__isnull=True,
        # )

            super(SiteManager, self).get_queryset().filter(
                city__activated=True, has_been_accepted=True
            )
            .filter(
                Q(type='place') |
                Q(frequency__in=['day', 'workday', 'week', 'year'], type='event') |
                Q(special_schedules__day__gte=now().date(), type='event', frequency='never')
            ).annotate_translated_fields()
        )


class AdminSiteManager(models.Manager):
    def get_queryset(self):
        return super(AdminSiteManager, self).get_queryset().annotate_translated_fields()


class SiteQueryset(models.QuerySet):
    def get(self, *args, **kwargs):
        try:
            return super(SiteQueryset, self).get(*args, **kwargs)
        except self.model.MultipleObjectsReturned:
            return super(SiteQueryset, self).filter(id=kwargs.get('id')).first()

    def create(self, **kwargs):
        levels = None
        categories = None
        subcategories = None
        schedules = None

        if 'levels' in kwargs:
            levels = kwargs.pop('levels')

        if 'categories' in kwargs:
            categories = kwargs.pop('categories')

        if 'subcategories' in kwargs:
            subcategories = kwargs.pop('subcategories')

        if 'schedules' in kwargs:
            schedules = kwargs.pop('schedules')

        site = super(SiteQueryset, self).create(**kwargs)

        if levels:
            site.levels.set(levels)

        if categories:
            site.categories.set(categories)

        if subcategories:
            site.subcategories.set(subcategories)

        if schedules:
            from local_secrets.sites.models import HourRange, Schedule

            for schedule_json in schedules:
                schedule = Schedule.objects.create(day=schedule_json.get('day'), site=site)
                for opening_hours in schedule_json.get('opening_hours'):
                    HourRange.objects.create(
                        initial_hour=opening_hours.get('initial_hour'),
                        end_hour=opening_hours.get('end_hour'),
                        schedule=schedule,
                    )
                schedule.save()

        return site

    def favorites(self, user):
        return user.fav_sites.all()

    def filter_type(self, type):
        if type:
            return self.filter(type=type)
        return self

    def filter_keyword(self, keyword, language='es'):
        if keyword:
            print(keyword)
            keyword = keyword.lower().rstrip(" ").lstrip(" ")
            _keyword = text.remove_all_accent_marks(keyword)
            has_accents = keyword != _keyword
            print(_keyword)
            if language == 'es':
                if has_accents:
                    title_query = Q(title__icontains=keyword)
                else:
                    title_query = Q(title__unaccent__icontains=_keyword)
                # description_query = Q(description__icontains=keyword)
            elif language != 'es':
                if has_accents:
                    title_query = Q(translations__title__icontains=keyword)
                else:
                    title_query = Q(translations__title__unaccent__icontains=_keyword)
                # description_query = Q(translations__description__icontains=keyword)
            else:
                if has_accents:
                    title_query = Q(title__icontains=keyword)
                else:
                    title_query = Q(title__unaccent__icontains=_keyword)
                # description_query = Q(description__icontains=keyword)
            return self.filter(title_query)  # | description_query)
        return self

    def filter_levels(self, levels):
        sites = self
        if levels:
            if type(levels) == list:
                sites = sites.filter(levels__id__in=levels)
            else:
                splitted_levels_ids = levels.split(',')
                if len(splitted_levels_ids) > 1:
                    sites = sites.filter(levels__id__in=splitted_levels_ids)
                else:
                    sites = sites.filter(levels__id=levels)
        return sites

    def filter_categories(self, categories):
        sites = self
        if categories:
            if type(categories) == list:
                sites = sites.filter(categories__id__in=categories)
            else:
                splitted_categories_ids = categories.split(',')
                if len(splitted_categories_ids) > 1:
                    sites = sites.filter(categories__id__in=splitted_categories_ids)
                else:
                    sites = sites.filter(categories__id=categories)
        return sites

    def filter_subcategories(self, subcategories):
        sites = self
        if subcategories:
            if type(subcategories) == list:
                sites = sites.filter(subcategories__id__in=subcategories)
            else:
                splitted_subcategories_ids = subcategories.split(',')
                if len(splitted_subcategories_ids) > 1:
                    sites = sites.filter(subcategories__id__in=splitted_subcategories_ids)
                else:
                    sites = sites.filter(subcategories__id=subcategories)
        return sites

    def filter_hours(self, day, hour):
        sites = self
        if day:
            sites = sites.filter(schedules__day=day)
        if hour:
            try:
                hour = datetime.strptime(hour, '%H:%M')
            except ValueError:
                raise ValidationError(detail='The hour does not have a valid format', code=400)
            sites = sites.filter(
                schedules__opening_hours__initial_hour__lte=hour, schedules__opening_hours__end_hour__gte=hour
            )
        return sites

    def filter_special_schedule(self, first_date, last_date):
        sites = self
        if first_date:
            sites = sites.filter(special_schedules__day__gte=first_date)
        if last_date:
            sites = sites.filter(special_schedules__day__lte=last_date)
        return sites

    def filter_suggested(self, is_suggested):
        sites = self
        if is_suggested:
            sites = sites.filter(is_suggested=True)
        return sites

    def filter_city(self, city, language='es'):
        sites = self
        if city:
            city = city.rstrip(" ").lstrip(" ").lower()
            _city = text.remove_all_accent_marks(city)
            has_accents = city != _city
            if language == 'es':
                if has_accents:
                    sites = sites.filter(Q(city__name__icontains=city))
                else:
                    sites = sites.filter(Q(city__name__unaccent__icontains=_city))
            elif language != 'es':
                if has_accents:
                    sites = sites.filter(Q(city__translations__name__icontains=city))
                else:
                    sites = sites.filter(Q(city__translations__name__unaccent__icontains=_city))
            else:
                if has_accents:
                    sites = sites.filter(Q(city__name__icontains=city))
                else:
                    sites = sites.filter(Q(city__name__unaccent__icontains=_city))
        return sites

    def filter_city_id(self, city_id):
        sites = self
        if city_id:
            if type(city_id) == list:
                sites = sites.filter(city__id__in=city_id)
            else:
                splitted_cities_ids = city_id.split(',')
                if len(splitted_cities_ids) > 1:
                    sites = sites.filter(city__id__in=splitted_cities_ids)
                else:
                    sites = sites.filter(city__id=city_id)
        return sites

    def filter_tag(self, tag):
        sites = self
        if tag:
            sites = sites.filter(tags__id=tag)
        return sites

    def filter_country(self, country, language='es'):
        sites = self
        if country:
            country = country.rstrip(" ").lstrip(" ").lower()
            _country = text.remove_all_accent_marks(country)
            has_accents = country != _country
            if language == 'es':
                if has_accents:
                    sites = sites.filter(Q(city__country__name__icontains=country))
                else:
                    sites = sites.filter(Q(city__country__name__unaccent__icontains=_country))
            elif language != 'es':
                if has_accents:
                    sites = sites.filter(Q(city__country__translations__name__icontains=country))
                else:
                    sites = sites.filter(Q(city__country__translations__name__unaccent__icontains=_country))
            else:
                if has_accents:
                    sites = sites.filter(Q(city__country__name__icontains=country))
                else:
                    sites = sites.filter(Q(city__country__name__unaccent__icontains=country))
        return sites

    def filter_country_id(self, country_id):
        sites = self
        if country_id:
            sites = sites.filter(city__country__id=country_id)
        return sites

    def filter_by_datetime(self, current_datetime):
        sites = self
        if current_datetime:
            sites = sites.annotate(
                union=Case(When(schedules__opening_hours__initial_hour__gt=F('schedules__opening_hours__end_hour')))
            ).filter(
                Q(
                    schedules__opening_hours__initial__hour__lte=current_datetime,
                    schedules__opening_hours__end_hour__gte=current_datetime,
                    union=True,
                )
                | Q(
                    schedules__opening_hours__initial__hour__gte=current_datetime,
                    schedules__opening_hours__end_hour__lte=current_datetime,
                    union=False,
                )
            )
        return sites

    def annotate_num_of_favs(self):
        return self.annotate(num_of_favs=Count('users'))

    def annotate_is_fav(self, user):
        if user.is_anonymous:
            return self
        return self.annotate(is_fav=Exists(Subquery(user.fav_sites.filter(id=OuterRef('id')))))

    def annotate_translated_fields(self):
        queryset = self

        def get_annotation(key, language_code, field_name):
            from local_secrets.sites.models import TranslatedSite

            return {
                key: Subquery(
                    TranslatedSite.objects.filter(site__id=OuterRef('pk'), language__code=language_code).values(
                        field_name
                    )[:1]
                )
            }

        for language in Language.objects.all():
            key_title = f'translated_title_{language.code}'
            key_description = f'translated_description_{language.code}'
            queryset = queryset.annotate(**get_annotation(key_title, language.code, 'title'))
            queryset = queryset.annotate(**get_annotation(key_description, language.code, 'description'))

        return queryset

    def filter_polygon(self, points):
        if points and None not in points:
            print(points)
            mp = MultiPoint(
                *map(lambda x: Point(float(x.split(',')[1]), float(x.split(',')[0]), srid=4326), points),
                srid=4326
            )
            print(mp.coords)
            coords = list(mp.coords)
            coords.append(coords[0])
            polygon = Polygon(tuple(coords))
            return self.filter(address__point__within=polygon)
        else:
            return self

    def annotate_is_open(self):
        current_date = localtime()
        current_weekday = current_date.weekday() + 1  # Django utiliza 1 para domingo y 7 para sábado
        days = {2: 'monday', 3: 'tuesday', 4: 'wednesday', 5: 'thursday', 6: 'friday', 7: 'saturday', 1: 'sunday'}
        current_weekday_name = days[(current_weekday + 1) % 7]
        current_day = current_date.day

        return self.annotate(is_open=Case(
            When(always_open=True, then=Value(True, output_field=BooleanField())),
            When(frequency='never', then=Value(False, output_field=BooleanField())),
            When(frequency='day', then=Value(True, output_field=BooleanField())),
            When(
                frequency='week',
                then=Case(
                    When(schedules__day=current_weekday_name, then=Value(True)),
                    default=Value(False, output_field=BooleanField())
                )
            ),
            When(
                frequency='month',
                then=Case(
                    When(special_schedules__day__day=current_day, then=Value(True)),
                    default=Value(False, output_field=BooleanField())
                )
            ),
            When(
                frequency='year',
                then=Case(
                    When(special_schedules__day=current_date.date(), then=Value(True)),
                    default=Value(False, output_field=BooleanField())
                )
            ),
            When(
                frequency='workday',
                then=Value(current_weekday < 6, output_field=BooleanField())
            ),
            default=Value(False, output_field=BooleanField()),
        )
        )

    def with_next_schedule_date(self):
        current_time = localtime()

        # Annotate `day_order` based on `current_time.weekday()` for each schedule
        annotated_schedules = self.annotate(
            day_order=Case(
                *[When(schedules__day=day, then=Value(index)) for index, day in
                  enumerate(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])],
                output_field=IntegerField(),
            )
        )

        # Annotate `day_distance` using calculated `day_order` as a base for each Site instance
        annotated_sites = annotated_schedules.annotate(
            day_distance=Case(
                When(day_order__gte=current_time.weekday(), then=F('day_order') - (current_time.weekday())),
                When(day_order__lt=current_time.weekday(), then=7 - (current_time.weekday() - F('day_order'))),
                output_field=IntegerField()
            ),
            next_date=ExpressionWrapper(
                Cast(Value(current_time), DateField()) + Cast(F("day_distance"), output_field=IntegerField()),
                output_field=DateField()
            ),
            closest_day=Max('special_schedules__day')
        )

        # Order the schedules by `day_distance` to get the closest one
        #closest_schedule = annotated_sites.order_by('day_distance').first()

        # If there's a match, calculate the date of the next schedule
        #next_schedule_date = current_time + timedelta(days=closest_schedule.day_distance) if closest_schedule and closest_schedule.day_distance else None
        #next_schedule_date = closest_schedule.day_order if closest_schedule and closest_schedule.day_order else closest_schedule.closest_day

        return annotated_sites


class ScheduleQueryset(models.QuerySet):
    def annotate_day_order(self, current_day_integer):
        return self.annotate(
            day_order=Case(
                When(day=Day.MONDAY, then=0),
                When(day=Day.TUESDAY, then=1),
                When(day=Day.WEDNESDAY, then=2),
                When(day=Day.THURSDAY, then=3),
                When(day=Day.FRIDAY, then=4),
                When(day=Day.SATURDAY, then=5),
                When(day=Day.SUNDAY, then=6),
                output_field=models.IntegerField(),
                default=-1,
            ),
            day_distance=Case(
                When(day_order__lt=current_day_integer, then=7 - (current_day_integer - F('day_order'))),
                When(day_order__gte=current_day_integer, then=Abs(current_day_integer - F('day_order'))),
            ),
        )


class SpecialScheduleQueryset(models.QuerySet):
    def annotate_day_distance(self, current_day):
        return self.annotate(day_distance=current_day - F('day'))


class BaseManager(models.Manager):  # Base manager for Level, Category and SubCategory models
    def get_queryset(self):
        return super(BaseManager, self).get_queryset().order_by('order')


class LevelManager(models.Manager):
    def get_queryset(self):
        return (super(LevelManager, self).get_queryset()).annotate(
            site_count=Count('sites', output_field=IntegerField())
        ).filter(site_count__gt=0).order_by('order')


class CategoryManager(models.Manager):
    def get_queryset(self):
        return (super(CategoryManager, self).get_queryset()).annotate(
            site_count=Count('sites', output_field=IntegerField())
        ).filter(site_count__gt=0).order_by('order')


class SubcategoryManager(models.Manager):
    def get_queryset(self):
        return (super(SubcategoryManager, self).get_queryset()).annotate(
            site_count=Count('sites', output_field=IntegerField())
        ).filter(site_count__gt=0).order_by('order')
