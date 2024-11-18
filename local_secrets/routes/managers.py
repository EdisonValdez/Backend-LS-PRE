from django.db import models
from django.db.models import Count, OuterRef, Subquery

from local_secrets.core.utils.text import TextHelper as text
from local_secrets.languages.models import Language


class RouteManager(models.Manager):
    def get_queryset(self):
        return (
            super(RouteManager, self)
            .get_queryset()
            .annotate_translated_fields()
            .annotate(stops_count=Count('stops'))
            .filter(stops_count__gt=0)
        )


class RouteQueryset(models.QuerySet):
    def filter_by_title(self, title, language='es'):
        if title:
            title = title.lower().rstrip(" ").lstrip(" ")
            _title = text.remove_all_accent_marks(title)
            has_accents = title != _title
            if language == 'es':
                if has_accents:
                    return self.filter(title__icontains=title)
                else:
                    return self.filter(title__unaccent__icontains=_title)
            elif language != 'es':
                if has_accents:
                    return self.filter(title__icontains=title)
                else:
                    return self.filter(translations__title__unaccent__icontains=_title)
            else:
                if has_accents:
                    return self.filter(title__icontains=title)
                else:
                    return self.filter(title__unaccent__icontains=_title)
        return self

    def filter_by_city(self, city_name, language='es'):
        if city_name:
            city_name = city_name.lower().rstrip(" ").lstrip(" ")
            _city_name = text.remove_all_accent_marks(city_name)
            has_accents = city_name != _city_name
            if language == 'es':
                if has_accents:
                    return self.filter(cities__name__icontains=city_name)
                else:
                    return self.filter(cities__name__unaccent__icontains=_city_name)
            elif language != 'es':
                if has_accents:
                    return self.filter(cities__translations__name__icontains=city_name)
                else:
                    return self.filter(cities__translations__name__unaccent__icontains=_city_name)
            else:
                if has_accents:
                    return self.filter(cities__name__icontains=city_name)
                else:
                    return self.filter(cities__name__unaccent__icontains=_city_name)
        return self

    def filter_by_city_id(self, city_id):
        cities = self
        if city_id:
            cities_ids = city_id.split(',')
            if len(cities_ids) > 1:
                cities = self.filter(cities__id__in=cities_ids)
            else:
                cities = self.filter(cities__id=city_id)
        return cities

    def filter_by_tag(self, tag):
        if tag:
            return self.filter(tags__id=tag)
        return self

    def annotate_translated_fields(self):
        queryset = self

        def get_annotation(key, language_code, field_name):
            # return {
            #     key: Case(
            #         When(translations__language__code=language_code, then=F(f'translations__{field_name}')),
            #         default=F(f'{field_name}'),
            #     )
            # }
            from local_secrets.routes.models import TranslatedRoute

            return {
                key: Subquery(
                    TranslatedRoute.objects.filter(route__id=OuterRef('pk'), language__code=language_code).values(
                        field_name
                    )[:1]
                )
            }

        for language in Language.objects.all():
            key_title = f'translated_title_{language.code}'
            queryset = queryset.annotate(**get_annotation(key_title, language.code, 'title'))

        return queryset
