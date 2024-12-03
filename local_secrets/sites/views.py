import json
from itertools import chain
from operator import attrgetter

from dal import autocomplete
from django.contrib.gis.db.models.functions import Distance
from django.core.cache import cache
from django.core.files.images import get_image_dimensions
from django.db.models import Case, When, Max, Count, IntegerField, Prefetch
from django.db.models.functions import Random
from django.shortcuts import redirect
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from local_secrets.cities.models import City
from local_secrets.core.permissions import IsAuthenticatedForPost
from local_secrets.core.utils.text import TextHelper as text
from local_secrets.sites.models import DefaultImage, ImageSize, Level, Site, Category, SubCategory
from local_secrets.sites.serializers import (
    CommentInputSerializer,
    CommentSerializer,
    DefaultImageSerializer,
    FavoriteSitesFilterSerializer,
    LevelSerializer,
    SiteCreationSerializer,
    SiteListSerializer,
    SiteSerializer,
    SitestoDiscoverSerializer, SiteGeolocationSerializer, SiteRandomListSerializer, SiteLiteListSerializer,
)


class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    def get_queryset(self):
        levels = Level.objects_for_api.all()
        level_type = self.request.query_params.get('type')
        if level_type:
            levels = levels.filter(type=level_type)
        city = self.request.query_params.get('city')
        if city:
            levels = levels.filter(sites__city__id=city)

            # Prefetch related subcategories that have sites in the specified city
            filtered_subcategories = SubCategory.objects.filter(
                sites__city=city,
                sites__type=level_type
            ).distinct().annotate(
                site_count=Count('sites', output_field=IntegerField())
            ).filter(site_count__gt=0).order_by('order')

            # Prefetch related categories that have sites in the specified city
            filtered_categories = Category.objects.prefetch_related(
                Prefetch('subcategories', queryset=filtered_subcategories),
            ).filter(
                sites__city=city,
                sites__type=level_type
            ).distinct().annotate(
                site_count=Count('sites', output_field=IntegerField())
            ).filter(site_count__gt=0).order_by('order', '-site_count')

            # Prefetch filtered categories to avoid fetching unfiltered categories
            levels = levels.prefetch_related(
                Prefetch('categories', queryset=filtered_categories),
            )

        levels = levels.annotate(site_count=Count('sites', output_field=IntegerField())).filter(site_count__gt=0)
        return levels

    def get_serializer_class(self):
        return LevelSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    @property
    def paginator(self):
        self._paginator = super(CategoryViewSet, self).paginator
        if not self.request.query_params.get('page'):
            self._paginator = None
        return self._paginator


# This view is used only on the admin page to filter the categories. It should not be used on the api
class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        name = self.request.GET.get('q')
        levels = self.forwarded.get('levels')
        if levels:
            if type(levels) == list:
                categories = Category.objects_for_admin.filter(level__in=levels)
            else:
                levels_as_list = levels.split(',')
                categories = Category.objects_for_admin.filter(level__in=levels_as_list)
        else:
            level = self.forwarded.get('level')
            if level:
                categories = Category.objects_for_admin.filter(level=level)
            else:
                categories = Category.objects_for_admin.all()
        if name:
            categories = categories.filter(title__icontains=name)
        return categories


class SubCategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        categories = self.forwarded.get('categories')
        name = self.request.GET.get('q')
        if categories:
            if type(categories) == list:
                subcategories = SubCategory.objects_for_admin.filter(category__in=categories)
            else:
                categories_as_list = categories.split(',')
                subcategories = SubCategory.objects_for_admin.filter(category__in=categories_as_list)
        else:
            subcategories = SubCategory.objects_for_admin.all()
        if name:
            subcategories = subcategories.filter(title__icontains=name)
        return subcategories


class LevelAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        levels = Level.objects_for_admin.all()
        name = self.request.GET.get('q')
        if name:
            levels = levels.filter(title__icontains=name)
        return levels


class PlaceLevelAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        levels = Level.objects_for_admin.filter(type='place')
        name = self.request.GET.get('q')
        if name:
            levels = levels.filter(title__icontains=name)
        return levels


class EventLevelAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        levels = Level.objects_for_admin.filter(type='event')
        name = self.request.GET.get('q')
        if name:
            levels = levels.filter(title__icontains=name)
        return levels


class SiteViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    permission_classes = (AllowAny,)
    paginate_by = 2  # ¿?

    @property
    def paginator(self):
        # Get Paginator
        self._paginator = super(SiteViewSet, self).paginator
        # Set page size to 3
        # self._paginator.page_size = 3
        # If no page param, return no pagination
        if not self.request.query_params.get('page'):
            self._paginator = None
        # Return Pagination
        return self._paginator

    def get_queryset(self):
        sites = Site.objects.annotate_num_of_favs()
        queries = self.request.query_params
        language = self.request.headers.get('Language')

        # Handle points formation
        points = queries.getlist('points')
        if not points:
            points = [
                queries.get('topLeft'),
                queries.get('topRight'),
                queries.get('bottomRight'),
                queries.get('bottomLeft')
            ]

        sites = (
            sites.filter_type(queries.get('type'))
            .filter_keyword(queries.get('keyword'), language)
            .filter_categories(queries.get('categories'))
            .filter_levels(queries.get('levels'))
            .filter_subcategories(queries.get('subcategories'))
            .filter_city(queries.get('city'), language)
            .filter_city_id(queries.get('city_id'))
            .filter_tag(queries.get('tag'))
            .filter_country(queries.get('country'))
            .filter_hours(queries.get('day'), queries.get('hour'))
            .filter_suggested(queries.get('is_suggested'))
            .filter_special_schedule(queries.get('first_date'), queries.get('last_date'))
            .filter_polygon(points)
        )

        sites = (sites.filter(has_been_accepted=True, city__activated=True)
                 .annotate_is_fav(self.request.user).distinct())

        if self.request.query_params.get('preview'):
            sites = sites.only('id', 'title')

        if queries.get('type') == 'event':
            sites = sites
        else:
            sites = sites.order_by('-is_top_10')

        return sites

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if request.query_params.get('type') == 'event':
            new_results = sorted(response.data.get('results'), key=lambda k: k['next_schedule']['day'] if k['next_schedule'] else 'z')
            response.data['results'] = new_results
        return response

    def get_serializer_class(self):
        if self.action == 'list':
            if self.request.query_params.get('preview'):
                return SiteLiteListSerializer
            return SiteListSerializer
        return SiteSerializer



    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=False, methods=['get'], permission_classes=(IsAuthenticated,))
    def favorites(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 25
        paginate = request.query_params.get('page')
        output_serializer = SiteListSerializer
        if self.request.query_params.get('preview'):
            output_serializer = SiteLiteListSerializer

        serializer = FavoriteSitesFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        language = request.headers.get('language')

        fav_sites = ((
            request.user.fav_sites.filter_type(serializer.validated_data.get('type'))
            .filter_keyword(serializer.validated_data.get('keyword'), language=language)
            .filter_levels(serializer.validated_data.get('levels'))
            .filter_categories(request.query_params.get('categories'))
            .filter_subcategories(request.query_params.get('subcategories'))
            .filter_city(serializer.validated_data.get('city'), language=language)
            ).annotate_is_fav(self.request.user)
            .annotate_translated_fields()
            .order_by('-is_top_10')
            .distinct()
        )
        if self.request.query_params.get('preview'):
            fav_sites = fav_sites.only('id', 'title')

        if paginate:
            queryset = paginator.paginate_queryset(fav_sites, request)
            output = output_serializer(queryset, context={'request': request}, many=True).data
            return paginator.get_paginated_response(output)
        else:
            output = output_serializer(fav_sites, context={'request': request}, many=True).data
            return Response(output)

    @action(detail=True, methods=['post'], permission_classes=(IsAuthenticated,))
    def check_fav(self, request, pk):
        created = self.get_object().mark_as_fav(request.user)
        if created:
            detail = 'Marked as favorite'
        else:
            detail = 'Unmarked as favorite'
        return Response({'detail': detail})

    @action(detail=True, methods=['post'], permission_classes=(IsAuthenticated,))
    def comment(self, request, pk):
        serializer = CommentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.get_object().comments.filter(user__id=self.request.user.id).exists():
            raise ValidationError(detail='You have already posted a review', code=400)
        comment = self.get_object().add_comment(
            user=request.user,
            body=serializer.validated_data.get('body'),
            rating=serializer.validated_data.get('rating'),
        )
        return Response(CommentSerializer(comment, context={'request': request}).data, status=201)

    @action(detail=False, methods=['get'], permission_classes=(AllowAny,))
    def by_map(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 25
        paginate = request.query_params.get('page')

        sites = self.get_queryset().exclude(address__isnull=True)

        if paginate:
            queryset = paginator.paginate_queryset(sites, request)
            output = SiteListSerializer(queryset, context={'request': request}, many=True).data
            return paginator.get_paginated_response(output)
        else:
            output = SiteListSerializer(sites, context={'request': request}, many=True).data
            return Response(output)

    @action(detail=False, methods=['get'], permission_classes=(AllowAny,))
    def geolocations(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 25
        paginate = request.query_params.get('page')

        sites = self.get_queryset().exclude(address__isnull=True)

        if paginate:
            queryset = paginator.paginate_queryset(sites, request)
            output = SiteGeolocationSerializer(queryset, context={'request': request}, many=True).data
            return paginator.get_paginated_response(output)
        else:
            output = SiteGeolocationSerializer(sites, context={'request': request}, many=True).data
            return Response(output)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk):
        comments = (
            self.get_object()
            .comments.all()
            .annotate(is_from_user=Case(When(user__id=request.user.id, then=True), default=False))
        ).order_by('-created_at')

        paginator = PageNumberPagination()
        paginator.page_size = 25
        paginate = request.query_params.get('page')

        if paginate:
            paginated_queryset = paginator.paginate_queryset(comments, request)
            output = CommentSerializer(paginated_queryset, context={'request': request}, many=True).data
            return paginator.get_paginated_response(output)
        else:
            return Response(CommentSerializer(comments, context={'request': request}, many=True).data)

    @action(detail=True, methods=['get'])
    def similar(self, request, pk):
        tags = self.get_object().tags.all()
        sites = self.get_queryset().filter(tags__id__in=tags).exclude(id=self.get_object().id)
        return Response(SiteListSerializer(sites, context={'request': request}, many=True).data)

    @action(detail=False, methods=['post'])
    def suggest_site(self, request):
        serializer = SiteCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        location = serializer.validated_data.pop('location')

        schedules = []
        special_schedules = []
        if 'schedules' in serializer.validated_data:
            schedules = serializer.validated_data.pop('schedules')
        if 'special_schedules' in serializer.validated_data:
            special_schedules = serializer.validated_data.pop('special_schedules')

        site = Site.objects.create(has_been_accepted=False, created_by=request.user, **serializer.validated_data)

        site.create_address(location)
        site.add_schedules(schedules)
        site.add_special_schedules(special_schedules)

        return Response(SiteSerializer(site, context={'request': request}).data, status=201)

    @action(detail=True, methods=['post'])
    def add_images(self, request, pk):
        site = Site.objects.get(id=pk)
        if site.created_by.id != request.user.id:
            raise PermissionDenied(detail='You can only add images to your created sites', code=400)
        files = request.FILES.getlist('images')

        for file in files:
            img_sizes = ImageSize.objects.first()
            width, height = get_image_dimensions(file)
            print(f'Image size: {width}, {height}')
            if (
                not img_sizes.max_width > width > img_sizes.min_width
                or not img_sizes.max_height > height > img_sizes.min_height
            ):
                raise ValidationError(
                    detail=f'The given images must size between {img_sizes.min_width} - '
                    f'{img_sizes.min_height} and {img_sizes.max_width} - {img_sizes.max_height}',
                    code=400,
                )
            site.images.create(image=file)
        return Response({'detail': 'Images were added successfully'}, status=200)

    @action(detail=True, methods=['get'])
    def generate_link(self, request, pk):
        link = f'https://{request.get_host()}/sites/redirect_detail?id={pk}'
        return Response({'detail': link}, status=200)

    @action(detail=False, methods=['get'])
    def redirect_detail(self, request):
        user_agent = request.META['HTTP_USER_AGENT'].lower()
        if user_agent not in ['local-secrets']:
            if 'android' in user_agent:
                return redirect('https://play.google.com/store')
            elif (
                'ios' in user_agent
                or 'iphone' in user_agent
                or 'apple' in user_agent
                or 'darwin' in user_agent
                or 'mac' in user_agent
            ):
                return redirect('https://apps.apple.com/us/app/local-secrets/id6448513168')
            else:
                return redirect('https://play.google.com/store')

        site_id = request.query_params.get('id')
        site = self.get_queryset().filter(id=site_id).first()
        if not site:
            return Response({'detail': f'There is no site with id: {site_id}'}, status=404)
        return Response(SiteSerializer(site, context={'request': request}).data, status=200)

    @action(detail=False, methods=['get'])
    def sites_to_discover(self, request):
        cache_key = 'sites_to_discover'
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginate = request.query_params.get('page')
        serializer = SitestoDiscoverSerializer
        if request.query_params.get('preview'):
            serializer = SiteRandomListSerializer

        if cache.get(cache_key):
            result_list = cache.get(cache_key)
        else:
            sites = self.get_queryset().filter(type='place').annotate(order=Random() * 100)

            cities = City.objects.filter(activated=True).annotate(order=Random() * 100)

            language = self.request.headers.get('language')
            if 'city' in self.request.query_params:
                city = text.remove_all_accent_marks(self.request.query_params.get('city').lower())
                if language:
                    if language == 'es':
                        cities = cities.filter(name__icontains=city)
                    elif language != 'es':
                        cities = cities.filter(translations__name__icontains=city)
                else:
                    cities = cities.filter(name__icontains=city)

            result_list = sorted(chain(sites, cities), key=attrgetter('order'))[:100]
            cache.set(cache_key, result_list)

        if paginate:
            paginated_queryset = paginator.paginate_queryset(result_list, request)
            output = serializer(paginated_queryset, context={'request': request}, many=True).data
            return paginator.get_paginated_response(output)
        else:
            output = serializer(result_list, context={'request': request}, many=True).data
            return Response(output)

    @action(detail=False, methods=['get'])
    def suggested(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 25
        paginate = request.query_params.get('page')

        sites = self.get_queryset().filter_suggested(True)
        sites.order_by('?')

        if paginate:
            queryset = paginator.paginate_queryset(sites[:100], request)
            output = SiteListSerializer(queryset, context={'request': request}, many=True).data
            response = paginator.get_paginated_response(output)
        else:
            output = SiteListSerializer(sites[:100], many=True, context={'request': request}).data
            response = Response(output, status=200)
        return response

    @action(detail=True, methods=['get'])
    def nearby(self, request, pk):
        paginator = PageNumberPagination()
        paginator.page_size = 25
        paginate = request.query_params.get('page')

        is_cache_applicable = len(request.query_params) <= 1
        serializer = SiteListSerializer
        if self.request.query_params.get('preview'):
            serializer = SiteRandomListSerializer

        sites = None
        if is_cache_applicable:
            if cache.get(f'nearby_{pk}'):
                sites = cache.get(f'nearby_{pk}')
        if sites is None:
            site = Site.objects.get(id=pk)
            sites = self.get_queryset().filter_country_id(site.city.country.id)
            if site.address is None:
                point = site.city.point
            else:
                point = site.address.point
            if sites.count() > 0:
                sites = sites.exclude(id=pk).annotate(distance=Distance('address__point', point))
                sites = sites.filter(distance__lte=50000)  # 50 Km
                sites = sites.order_by('distance').distinct()
                if sites.count() > 50:
                    sites = sites[:50]
                if is_cache_applicable:
                    cache.set(f'nearby_{pk}', sites)

        if paginate:
            queryset = paginator.paginate_queryset(sites, request)
            output = serializer(queryset, context={'request': request}, many=True).data
            response = paginator.get_paginated_response(output)
        else:
            output = serializer(sites, many=True, context={'request': request}).data
            response = Response(output)
        return response

    @action(detail=False, methods=['get'])
    def random(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 25
        paginate = request.query_params.get('page')
        serializer = SiteListSerializer
        serializer = SiteRandomListSerializer

        if paginate:
            if cache.get('random_cache'):
                sites = cache.get('random_cache')
            else:
                sites = Site.objects.only('id', 'title').order_by('?', 'id')[:100]
                cache.set('random_cache', sites)
            queryset = paginator.paginate_queryset(sites[:100], request)
            output = serializer(queryset, context={'request': request}, many=True).data
            response = paginator.get_paginated_response(output)
            return response
        else:
            if cache.get('random_basic'):
                return Response(cache.get('random_basic'))
            sites = self.get_queryset().only('id', 'title').order_by('?', 'id')
            output = serializer(sites[:50], many=True, context={'request': request}).data
            cache.set('random_basic', output)
            response = Response(output, status=200)
            return response


class DefaultImageViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    def get_queryset(self):
        return DefaultImage.objects.all()

    def get_serializer_class(self):
        return DefaultImageSerializer


class CommentViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin
):
    permission_classes = (IsAuthenticatedForPost,)
    paginate_by = 35

    @property
    def paginator(self):
        self._paginator = super(CommentViewSet, self).paginator
        if not self.request.query_params.get('page'):
            self._paginator = None
        return self._paginator

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        paginator = PageNumberPagination()
        paginator.page_size = 25
        paginate = request.query_params.get('page')

        if paginate:
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            output = self.get_serializer_class()(paginated_queryset, context={'request': request}, many=True).data
            return paginator.get_paginated_response(output)
        else:
            return Response(self.get_serializer_class()(queryset).data)

    def update(self, request, *args, **kwargs):
        if self.get_object().user != self.request.user:
            return Response({'detail': 'You do not have permissions to modify this comment'}, status=402)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if self.get_object().user != self.request.user:
            return Response({'detail': 'You do not have permissions to delete this comment'}, status=402)
        super().destroy(request, *args, **kwargs)
        return Response({'detail': 'The comment was deleted'}, status=200)

    def get_queryset(self):
        return self.request.user.comments.all()

    def get_serializer_class(self):
        return CommentSerializer

    def get_serializer_context(self):
        return {'request': self.request}
