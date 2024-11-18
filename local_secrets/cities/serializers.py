from rest_framework import serializers

from local_secrets.cities.models import Address, City, Country
from local_secrets.core.serializers import ThumbnailJSONSerializer


class CountrySerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super(CountrySerializer, self).to_representation(instance)
        request = self.context.get('request')

        if request and request.headers.get('language'):
            language = request.headers.get('language')
        else:
            return representation

        for field in self.fields:
            if field in [
                'name',
            ]:
                representation[field] = instance.display_text(field, language)
        return representation

    class Meta:
        model = Country
        fields = '__all__'


class BaseCitySerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    def to_representation(self, instance):
        representation = super(BaseCitySerializer, self).to_representation(instance)
        request = self.context.get('request')

        if request and request.headers.get('language'):
            language = request.headers.get('language')
        else:
            return representation

        for field in self.fields:
            if field in ['name', 'province', 'description', 'slogan']:
                representation[field] = instance.display_text(field, language)
        return representation

    class Meta:
        model = City
        exclude = (
            'media',
            'point',
            'province',
            'description',
            'cp',
            'latitude',
            'longitude',
        )


class CitySerializer(BaseCitySerializer):
    images = ThumbnailJSONSerializer(alias='', read_only=True, many=True)
    num_of_routes = serializers.SerializerMethodField()

    def get_num_of_routes(self, obj):
        return obj.routes.count()

    class Meta:
        model = City
        fields = '__all__'


class AddressPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('latitude', 'longitude')


class AddressSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super(AddressSerializer, self).to_representation(instance)
        request = self.context.get('request')

        if request and request.headers.get('language'):
            language = request.headers.get('language')
        else:
            return representation

        for field in self.fields:
            if field in ['details', 'street']:
                representation[field] = instance.display_text(field, language)
        return representation

    class Meta:
        model = Address
        exclude = ('city',)
