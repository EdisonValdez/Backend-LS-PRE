from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from local_secrets.languages.models import Language, Translation


class TranslationSerializer(serializers.Serializer):
    language_code = serializers.CharField()
    platform = serializers.CharField()

    def is_valid(self, raise_exception=False):
        is_valid = super(TranslationSerializer, self).is_valid(raise_exception)
        try:
            Translation.objects.get(
                language__code=self.initial_data.get('language_code'), platform=self.initial_data.get('platform')
            )
        except Translation.DoesNotExist:
            if raise_exception:
                raise ValidationError(detail='The translation does not exist', code=400)
            return False
        return is_valid

    class Meta:
        fields = (
            'language_code',
            'platform',
        )


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

    def to_representation(self, instance):
        representation = super(LanguageSerializer, self).to_representation(instance)
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
