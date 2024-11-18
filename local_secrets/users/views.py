import random
import string
from datetime import timedelta
from itertools import chain
from operator import attrgetter

from django.contrib.auth.models import Group
from django.core.cache import cache
from django.core.files.images import get_image_dimensions
from django.db.models.functions import Random
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from oauth2_provider.models import Application, get_access_token_model, get_refresh_token_model
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from local_secrets.languages.models import Language
from local_secrets.routes.models import Route
from local_secrets.routes.serializers import RoutesAndSitesSerializer
from local_secrets.sites.models import ImageSize
from local_secrets.users.models import CustomUser, Notification, Tag
from local_secrets.users.serializers import (
    EmailSerializer,
    GroupSerializer,
    NotificationDetailSerializer,
    NotificationSerializer,
    ResetPasswordSerializer,
    TagOutputSerializer,
    TagSelectionInputSerializer,
    UserInputSerializer,
    UserOutputSerializer,
)


class UserViewSet(
    GenericViewSet,
):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return CustomUser.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ['post', 'update', 'patch', 'update_me']:
            return UserInputSerializer
        return UserOutputSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=False, methods=['get'], permission_classes=(IsAuthenticated,))
    def me(self, request):
        user = CustomUser.objects.all().annotate_travel_variables().get(id=request.user.id)
        return Response(UserOutputSerializer(user, context={'request': request}).data)

    @action(detail=False, methods=['post'], permission_classes=(IsAuthenticated,))
    def logout(self, request):
        get_access_token_model().objects.filter(user=request.user).delete()
        get_refresh_token_model().objects.filter(user=request.user).delete()
        user = CustomUser.objects.get(id=request.user.id)
        user.device_id = None
        user.save()
        if request.data.get('create_token'):
            allowed_chars = ''.join((string.ascii_letters, string.digits))

            access_unique_id = ''.join(random.choice(allowed_chars) for _ in range(30))
            access_token = get_access_token_model().objects.create(
                user=request.user, expires=now() + timedelta(minutes=1), token=access_unique_id, scope="read write"
            )
            print(access_token)

            refresh_unique_id = ''.join(random.choice(allowed_chars) for _ in range(30))
            new_refresh_token = get_refresh_token_model().objects.create(
                user=request.user,
                access_token=access_token,
                application=Application.objects.first(),
                token=refresh_unique_id,
            )
            print(new_refresh_token)
            return Response({'detail': new_refresh_token.token})

        return Response({'detail': _('The access and refresh tokens have been deleted successfully')})

    @action(detail=False, methods=['post'], permission_classes=(IsAuthenticated,))
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.validated_data['old_password']):
            raise ValidationError(code=400, detail='The given password does not match the old password')
        print(request.user)
        request.user.set_password(serializer.validated_data.get('new_password'))
        request.user.save()
        return Response({'detail': 'Password reset successfully'})

    @action(detail=False, methods=['get'], permission_classes=(IsAuthenticated,))
    def preferences(self, request):
        tags = Tag.objects.annotate_is_selected(request.user)
        return Response(TagOutputSerializer(tags, many=True, context={'user': request.user, 'request': request}).data)

    @action(detail=False, methods=['post'], permission_classes=(IsAuthenticated,))
    def select_preferences(self, request):
        serializer = TagSelectionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.update_tags(serializer.validated_data.get('tags'))
        return Response({'detail': 'Preferences updated'}, status=201)

    @me.mapping.delete
    def delete_me(self, request: Request):
        request.user.delete()
        return Response({'detail': 'The user was deleted'}, status=200)

    @me.mapping.patch
    @me.mapping.put
    def update_me(self, request: Request):
        user = CustomUser.objects.all().annotate_travel_variables().get(id=request.user.id)
        serializer = self.get_serializer(user, data=request.data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if 'password' in serializer.validated_data:
            user.set_password(serializer.validated_data.get('password'))
            user.save()

        return Response(UserOutputSerializer(user, context={'request': request}).data)

    #  Get All notifications
    @action(detail=False, methods=['get'])
    def notifications(self, request):
        #  Define Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginate = request.query_params.get('page')

        #  Get Notifications, order by created_at desc
        notifications = Notification.objects.all().annotate_has_been_seen(request.user).order_by('-created_at')

        #  If Page Query param exists
        if paginate:
            paginated_queryset = paginator.paginate_queryset(notifications, request)
            output = NotificationSerializer(paginated_queryset, context={'request': request}, many=True).data
            return paginator.get_paginated_response(output)
        else:
            return Response(NotificationSerializer(notifications, many=True).data)

    #  Mark notifications as seen
    @action(detail=False, methods=['post'])
    def notification(self, request):
        # Get user
        user = CustomUser.objects.get(id=request.user.id)
        #  Get Notification
        notification = Notification.objects.get(id=request.data.get('id'))
        #  Mark as seen for request user
        notification.mark_as_seen(user)
        #  Get a fresh instance from db
        notification.refresh_from_db()
        #  Return Notification Detail
        return Response(NotificationDetailSerializer(notification).data)

    # Check if user has notifications that has_been_seen = False
    @action(detail=False, methods=['get'])
    def has_notifications(self, request):
        #  Check has_been_seen=False
        user = CustomUser.objects.get(id=request.user.id)
        _has_notifications = user.notifications.count() < Notification.objects.count()
        if not _has_notifications:
            _has_notifications = user.notifications.filter(has_been_seen=False).count() > 0
        return Response({'detail': _has_notifications})

    @action(detail=False, methods=['post'])
    def update_pfp(self, request):
        file = request.FILES.getlist('profile_picture')
        img_sizes = ImageSize.objects.first()
        if len(file) == 0:
            raise ValidationError(detail='You need to pass at least one image', code=400)
        width, height = get_image_dimensions(file[0])
        print(f'File sizes: {width}, {height}')
        if (
            not img_sizes.max_width > width > img_sizes.min_width
            or not img_sizes.max_height > height > img_sizes.min_height
        ):
            raise ValidationError(
                detail=f'The given image must size between {img_sizes.min_width} - '
                f'{img_sizes.min_height} and {img_sizes.max_width} - {img_sizes.max_height}',
                code=400,
            )
        request.user.update_pfp(file)
        return Response({'detail': _('Profile picture updated')})

    @action(detail=False, methods=['post'])
    def language(self, request):
        user = CustomUser.objects.get(id=request.user.id)
        user.language = Language.objects.get(id=request.data.get('lang_id'))
        user.save()
        return Response({'detail': _('Language updated')}, status=200)

    @action(detail=False, methods=['get'])
    def groups(self, request):
        groups = Group.objects.all()
        return Response(GroupSerializer(groups, context={'request': request}, many=True).data)


class UserCreationViewSet(GenericViewSet, mixins.CreateModelMixin):
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        with translation.override(request.headers.get('language')):
            serializer = UserInputSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = CustomUser.objects.create_user(**serializer.validated_data)
            user = CustomUser.objects.all().annotate_travel_variables().get(id=user.id)
            user.groups.add(Group.objects.get(name='Viajero'))
            output = UserOutputSerializer(user, context={'request': request})
            return Response(output.data, status=201)

    @action(detail=False, methods=['post'])
    def restore_password(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(CustomUser, email=serializer.validated_data.get('email'))
        user.restore_password()
        return Response({'detail': 'Check your email inbox to restore your password'})


class TagViewSet(GenericViewSet):
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Tag.objects.all()

    def get_serializer_class(self):
        return TagOutputSerializer

    @action(detail=True, methods=['get'])
    def routes_and_sites(self, request, pk):
        #  Define Pagination
        cache_key = f'routes_and_sites_{pk}_{request.query_params.get("city_id")}'
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginate = request.query_params.get('page')

        tag = self.get_object()
        if cache.get(cache_key):
            result_list = cache.get(cache_key)
        else:
            routes = (
                Route.objects.filter(tags__id=tag.id).filter_by_city_id(request.query_params.get('city_id')).distinct()#.annotate(order=Random() * 100)
            ).distinct()

            sites = (
                tag.site_tags.all()
                .filter_city_id(request.query_params.get('city_id'))
                #.annotate(order=Random() * 100)
                .annotate_is_fav(self.request.user)
            ).distinct()

            result_list = list(chain(sites, routes))
            cache.set(cache_key, result_list)

        #  If Page Query param exists
        if paginate:
            paginated_queryset = paginator.paginate_queryset(result_list, request)
            output = RoutesAndSitesSerializer(paginated_queryset, context={'request': request}, many=True).data
            return paginator.get_paginated_response(output)
        else:
            output = RoutesAndSitesSerializer(result_list, context={'request': request}, many=True).data
            return Response(output)
