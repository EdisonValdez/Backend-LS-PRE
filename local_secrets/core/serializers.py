from django.conf import settings
from django.db.models import ImageField
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import ThumbnailerImageFieldFile, get_thumbnailer
from rest_framework import serializers
from rest_framework.serializers import BaseSerializer
from rest_framework.serializers import ImageField as ImageFieldSerializer

from local_secrets.cities.models import CityImage
from local_secrets.sites.models import DefaultImage, SiteImage


class OutputSerializer(serializers.Serializer):
    def create(self, validated_data):
        return None

    def update(self, instance, validated_data):
        return None


class DataSerializer(OutputSerializer):
    def to_representation(self, instance):
        return {'data': instance}


class ThumbnailJSONSerializer(ImageFieldSerializer, BaseSerializer):
    def __init__(self, **kwargs):
        self.alias = kwargs.pop('alias', None)
        self.alias_obj = kwargs.pop('alias_obj', settings.THUMBNAIL_ALIASES)
        kwargs.pop('many', None)
        super(ThumbnailJSONSerializer, self).__init__(**kwargs)

    def to_representation(self, instance):
        try:
            if type(instance) in [SiteImage, CityImage]:
                instance = instance.image
            elif type(instance) == str:
                instance = get_url(self.context['request'], instance, alias="")
            instance['thumbnail'].url

            if self.alias or self.alias == '':
                return image_sizes(self.context['request'], instance, self.alias_obj, self.alias)
        except InvalidImageFormatError:
            image = DefaultImage.objects.get(title='site_default').image
            return image_sizes(self.context.get('request'), image, self.alias_obj, self.alias)


def get_url(request, instance, alias=None):
    if not instance:
        return None
    if alias is not None:
        if isinstance(instance, ThumbnailerImageFieldFile):
            return request.build_absolute_uri(instance[alias].url)
        elif isinstance(instance, ImageField):
            return request.build_absolute_uri(get_thumbnailer(instance)[alias].url)
    elif alias is None:
        return request.build_absolute_uri(instance.url)
    else:
        raise TypeError('Unsupported field type')


def image_sizes(request, instance, alias_obj, alias_key):
    if alias_key not in alias_obj:
        raise KeyError('Key %s not found in dict thumbnail aliases' % alias_key)
    i_sizes = list(alias_obj[alias_key].keys())

    return {'original': get_url(request, instance), **{k: get_url(request, instance, k) for k in i_sizes}}
