from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import UserAppVersion
from .providers import AppVersionProvider
from .serializers import AppVersionOutputSerializer, UpdateAppVersionSerializer, UpdateRequiredFilterSerializer


class AppVersionViewset(viewsets.ViewSet):
    app_version_provider = AppVersionProvider()

    def list(self, request):
        """
        Returns true if there's a new version that requires an update, false otherwise
        """

        serializer = UpdateRequiredFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        version = serializer.validated_data['version']
        platform = serializer.validated_data['platform']
        available, required = self.app_version_provider.is_update_needed(version=version, platform=platform)
        store = self.app_version_provider.get_store_url(platform=platform)

        output = AppVersionOutputSerializer(
            {
                'update_required': required,
                'update_available': available,
                'store_url': store.url if store else None,
            }
        )
        return Response(output.data)

    @action(detail=False, methods=['put'], url_path='update')
    def update_version(self, request):
        """
        Updates the app version the user is using
        """
        user = request.user
        instance = request.user.app_version if hasattr(user, 'app_version') else UserAppVersion(user=user)
        data = request.data.copy()
        data['user'] = user
        serializer = UpdateAppVersionSerializer(instance=instance, data=data, partial=False)
        serializer.is_valid(raise_exception=True)
        user_app_version: UserAppVersion = serializer.save()

        available, required = self.app_version_provider.is_update_needed(
            version=user_app_version.user_version, platform=user_app_version.user_platform
        )
        store = self.app_version_provider.get_store_url(platform=user_app_version.user_platform)

        output = AppVersionOutputSerializer(
            {
                'update_required': required,
                'update_available': available,
                'store_url': store.url if store else None,
            }
        )
        return Response(output.data)
