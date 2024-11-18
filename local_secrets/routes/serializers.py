from django.core.cache import cache
from rest_framework import serializers

from local_secrets.cities.models import City
from local_secrets.cities.serializers import AddressSerializer, BaseCitySerializer, CitySerializer
from local_secrets.core.serializers import ThumbnailJSONSerializer
from local_secrets.routes.models import Route
from local_secrets.sites.models import Site
from local_secrets.sites.serializers import (
    CategoryListSerializer,
    LevelListSerializer,
    SiteListSerializer,
    SiteWithoutCitySerializer,
    SubCategorySerializer,
)
from local_secrets.users.serializers import TagOutputWithoutSelectionSerializer


class RouteListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    tags = serializers.SerializerMethodField()
    # stops = SiteListSerializer(many=True, read_only=True)
    num_of_stops = serializers.SerializerMethodField(read_only=True)
    num_of_views = serializers.IntegerField(read_only=True)
    is_top_ten = serializers.BooleanField(default=False, read_only=True)
    image = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return TagOutputWithoutSelectionSerializer(obj.tags.only('id', 'title').all(), many=True, read_only=True).data

    def get_image(self, obj):
        cache_key = f'route_image_{obj.id}'
        try:
            if cache.get(cache_key):
                return cache.get(cache_key)
            cache.set(cache_key, ThumbnailJSONSerializer(instance=obj.stops.first().images.first().image, alias="", context=self.context).data)
            return cache.get(cache_key)
        except BaseException as e:
            print(e)
            if cache.get(cache_key):
                return cache.get(cache_key)
            cache.set(cache_key, ThumbnailJSONSerializer(instance=obj.cities.first().images.first().image, alias="", context=self.context).data)
            return cache.get(cache_key)

    def get_num_of_stops(self, obj):
        return obj.stops.count()

    def to_representation(self, instance):
        representation = super(RouteListSerializer, self).to_representation(instance)
        request = self.context.get('request')

        if request and request.headers.get('language'):
            language = request.headers.get('language')
        else:
            return representation

        for field in self.fields:
            if field in [
                'title',
            ]:
                representation[field] = instance.display_text(field, language)
        return representation

    class Meta:
        fields = ('id', 'title', 'tags', 'num_of_stops', 'num_of_views', 'is_top_ten')


class RouteListWithCitiesSerializer(RouteListSerializer):
    cities = CitySerializer(many=True, read_only=True)

    class Meta:
        fields = ('id', 'title', 'tags', 'cities', 'num_of_stops', 'num_of_views', 'is_top_ten')


class RouteSerializer(RouteListSerializer):
    cities = CitySerializer(many=True, read_only=True)
    stops = serializers.SerializerMethodField()

    def get_stops(self, obj):
        return SiteListSerializer(
            Site.objects.filter(route_stops__route__id=obj.id).order_by('route_stops__order'),
            many=True,
            read_only=True,
            context=self.context,
        ).data

    class Meta:
        fields = ('id', 'title', 'tags', 'stops', 'num_of_stops', 'num_of_views', 'is_top_ten', 'cities')


class CityWithRoutesSerializer(BaseCitySerializer):
    routes = serializers.SerializerMethodField()
    num_of_routes = serializers.SerializerMethodField()

    def get_num_of_routes(self, obj):
        return obj.routes.count()

    def get_routes(self, obj):
        cache_key = f'routes_for_city_{obj.id}'
        if cache.get(cache_key):
            return cache.get(cache_key)
        output = RouteListSerializer(obj.routes.only('id', 'title', 'is_top_ten', 'num_of_views'), context=self.context, many=True).data
        cache.set(cache_key, output, timeout=3600)
        return output

    class Meta:
        model = City
        fields = ('id', 'name', 'routes', 'num_of_routes', 'slogan')


class RoutesAndSitesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    images = serializers.SerializerMethodField(required=False)
    type = serializers.SerializerMethodField()
    city = CitySerializer(required=False)
    cities = CitySerializer(many=True, required=False)
    tags = TagOutputWithoutSelectionSerializer(many=True, read_only=True)
    num_of_stops = serializers.SerializerMethodField()
    stops = SiteWithoutCitySerializer(many=True, required=False)
    is_fav = serializers.BooleanField(required=False)
    address = AddressSerializer(required=False)
    levels = LevelListSerializer(many=True, required=False)
    categories = CategoryListSerializer(many=True, required=False)
    subcategories = SubCategorySerializer(many=True, required=False)

    def get_images(self, obj):
        if type(obj) == Route:
            return ThumbnailJSONSerializer(instance=obj.stops.first().images, context=self.context, alias='', read_only=True, many=True).data
        else:
            return ThumbnailJSONSerializer(instance=obj.images, context=self.context, alias='', read_only=True, many=True).data

    def get_num_of_stops(self, obj):
        if type(obj) == Route:
            return obj.stops.count()
        return 0

    def get_type(self, obj):
        if type(obj) == Route:
            return 'route'
        else:
            return obj.type

    def to_representation(self, instance):
        representation = super(RoutesAndSitesSerializer, self).to_representation(instance)
        request = self.context.get('request')

        if request and request.headers.get('language'):
            language = request.headers.get('language')
        else:
            return representation

        if type(instance) == Route:
            fields_to_translate = ['title']
        else:
            fields_to_translate = ['title', 'description']

        for field in self.fields:
            if field in fields_to_translate:
                representation[field] = instance.display_text(field, language)
        return representation

    class Meta:
        fields = ('id', 'images', 'title', 'tags', 'num_of_stops', 'num_of_views', 'is_top_ten')
