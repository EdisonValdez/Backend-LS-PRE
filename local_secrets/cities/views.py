from dal import autocomplete
from django.core.cache import cache
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from local_secrets.cities.models import City, Country, PhoneCode
from local_secrets.cities.serializers import CitySerializer, CountrySerializer
from local_secrets.core.utils.text import TextHelper as text
from local_secrets.sites.choices import SiteType
from local_secrets.sites.serializers import SiteListSerializer


class CountryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    @property
    def paginator(self):
        self._paginator = super(CountryViewSet, self).paginator
        self._paginator.page_size = 15
        if not self.request.query_params.get('page'):
            self._paginator = None
        return self._paginator

    def get_queryset(self):
        countries = Country.objects.all()
        language = self.request.headers.get('language')
        if self.request.query_params.get('name'):
            name = self.request.query_params.get('name').lower().rstrip(" ").lstrip(" ")
            _name = text.remove_all_accent_marks(name)
            has_accents = name != self.request.query_params.get('name').lower()
            if language:
                if language == 'es':
                    if has_accents:
                        countries = countries.filter(name__icontains=name)
                    else:
                        countries = countries.filter(name__unaccent__icontains=_name)
                elif language != 'es':
                    if has_accents:
                        countries = countries.filter(translations__name__icontains=name)
                    else:
                        countries = countries.filter(translations__name__unaccent__icontains=_name)
            else:
                if has_accents:
                    countries = countries.filter(name__icontains=name)
                else:
                    countries = countries.filter(name__unaccent__icontains=_name)
        return countries

    def get_serializer_class(self):
        return CountrySerializer

    @action(detail=False, methods=['get'])
    def phone_codes(self, request):
        phone_codes = PhoneCode.objects.all()

        language = self.request.headers.get('language')
        if self.request.query_params.get('name'):
            name = self.request.query_params.get('name').lower().rstrip(" ").lstrip(" ")
            _name = text.remove_all_accent_marks(name)
            has_accents = name != _name
            if language:
                if language == 'es':
                    if has_accents:
                        phone_codes = phone_codes.filter(name__icontains=name)
                    else:
                        phone_codes = phone_codes.filter(name__unaccent__icontains=_name)
                elif language != 'es':
                    if has_accents:
                        phone_codes = phone_codes.filter(translations__name__icontains=name)
                    else:
                        phone_codes = phone_codes.filter(translations__name__unaccent__icontains=_name)
            else:
                if has_accents:
                    phone_codes = phone_codes.filter(name__icontains=name)
                else:
                    phone_codes = phone_codes.filter(name__unaccent__icontains=_name)

        return Response(
            CountrySerializer(
                phone_codes.distinct().order_by('phone_code'), many=True, context={'request': request}
            ).data,
            status=200,
        )


class CityViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    permission_classes = (AllowAny,)

    @property
    def paginator(self):
        self._paginator = super(CityViewSet, self).paginator
        if not self.request.query_params.get('page'):
            self._paginator = None
        return self._paginator

    def get_queryset(self):
        cities = City.objects.all().filter(activated=True).select_related('country')
        language = self.request.headers.get('language')
        if 'name' in self.request.query_params:
            name = self.request.query_params.get('name').lower().rstrip(" ").lstrip(" ")
            _name = text.remove_all_accent_marks(name)
            has_accents = name != _name
            if language:
                if language == 'es':
                    if has_accents:
                        cities = cities.filter(name__icontains=name)
                    else:
                        cities = cities.filter(name__unaccent__icontains=_name)
                elif language != 'es':
                    if has_accents:
                        cities = cities.filter(translations__name__icontains=name)
                    else:
                        cities = cities.filter(translations__name__unaccent__icontains=_name)
            else:
                if has_accents:
                    cities = cities.filter(name__icontains=name)
                else:
                    cities = cities.filter(name__unaccent__icontains=_name)
        return cities.distinct().order_by('name')

    def get_serializer_class(self):
        return CitySerializer

    @action(detail=True, methods=['get'])
    def events(self, request, pk):
        if cache.get(f'city_events_{pk}'):
            return Response(cache.get(f'city_events_{pk}'))
        places = self.get_object().sites.filter(type=SiteType.EVENT).order_by('is_top_10')
        output = SiteListSerializer(places, many=True, context={'request': request}).data
        cache.set(f'city_events_{pk}', output)
        return Response(output)

    @action(detail=True, methods=['get'])
    def places(self, request, pk):
        if cache.get(f'city_places_{pk}'):
            return Response(cache.get(f'city_places_{pk}'))
        places = self.get_object().sites.filter(type=SiteType.PLACE).order_by('is_top_10')
        output = SiteListSerializer(places, many=True, context={'request': request}).data
        cache.set(f'city_places_{pk}', output)
        return Response(output)


class CityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        name = self.request.GET.get('q')
        if name:
            return City.objects.filter(name__icontains=name).distinct()
        else:
            return City.objects.all()
