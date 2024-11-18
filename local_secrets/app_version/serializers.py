from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .choices import AppPlatform
from .models import AppVersion, UserAppVersion
from ..core.serializers import OutputSerializer


class UpdateRequiredFilterSerializer(OutputSerializer):
    version = serializers.CharField()
    platform = serializers.ChoiceField(choices=AppPlatform.choices)

    def to_internal_value(self, data):
        data = super(UpdateRequiredFilterSerializer, self).to_internal_value(data)
        if 'platform' in data:
            data = data.copy()
            data['platform'] = AppPlatform.from_value(data['platform'])
        return data


class UpdateAppVersionSerializer(serializers.Serializer):
    version = serializers.CharField()
    platform = serializers.CharField()

    def create(self, validated_data):
        # No implementation needed as it is called always with an instance
        pass

    def update(self, instance, validated_data) -> UserAppVersion:
        app_version_qs = AppVersion.objects.filter(
            version=validated_data['version'], platform=validated_data['platform']
        )
        if not app_version_qs.exists():
            raise ValidationError(_("No existing version match with given params"))
        instance.version = app_version_qs.first()
        instance.save()
        return instance


class AppVersionOutputSerializer(OutputSerializer):
    update_available = serializers.BooleanField()
    update_required = serializers.BooleanField()
    store_url = serializers.CharField()
