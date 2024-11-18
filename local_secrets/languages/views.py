from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from local_secrets.languages.models import Language, Translation
from local_secrets.languages.serializers import LanguageSerializer, TranslationSerializer


class TranslationViewSet(
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        return Translation.objects.all()

    def get_serializer_class(self):
        return TranslationSerializer

    @action(detail=False, methods=['get'])
    def translation(self, request):
        serializer = TranslationSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        translation = self.get_queryset().get(
            language__code=serializer.validated_data.get('language_code'),
            platform=serializer.validated_data.get('platform'),
        )

        return FileResponse(open(translation.translation.path, 'rb'), content_type='application/txt')

    @action(detail=False, methods=['get'])
    def languages(self, request):
        languages = Language.objects.all()
        return Response(LanguageSerializer(languages, context={'request': request}, many=True).data, status=200)
