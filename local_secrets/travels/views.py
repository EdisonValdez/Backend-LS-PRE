from django.db.models import Count, Q
from django.shortcuts import redirect
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from local_secrets.cities.models import City
from local_secrets.core.utils.directions import get_directions
from local_secrets.core.utils.text import TextHelper as text
from local_secrets.sites.models import Site
from local_secrets.sites.serializers import CityExistsSerializer, SiteExistsSerializer, SiteListSerializer
from local_secrets.travels.models import Stop, Travel
from local_secrets.travels.serializers import TravelListLiteSerializer, TravelListSerializer, TravelSerializer


class TravelViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    permission_classes = (IsAuthenticated,)

    @property
    def paginator(self):
        self._paginator = super(TravelViewSet, self).paginator
        if not self.request.query_params.get('page'):
            self._paginator = None
        return self._paginator

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            travels = Travel.objects.all()
        else:
            travels = self.request.user.travels
        if self.request.query_params.get('city'):
            city = self.request.query_params.get('city').lower().rstrip(" ").lstrip(" ")
            _city = text.remove_all_accent_marks(city)
            has_accents = city != _city
            language = self.request.headers.get('Language')
            if language:
                if has_accents:
                    travels = travels.filter(cities__translations__name__icontains=city)
                else:
                    travels = travels.filter(cities__translations__name__unaccent__icontains=_city)
            else:
                if has_accents:
                    travels = travels.filter(cities__name__icontains=city)
                else:
                    travels = travels.filter(cities__name__unaccent__icontains=_city)

        if self.request.query_params.get('type'):
            travels = travels.filter(type=self.request.query_params.get('type'))

        if self.request.query_params.get('initial_date'):
            travels = travels.filter(initial_date__lte=self.request.query_params.get('initial_date'))

        if self.request.query_params.get('end_date'):
            travels = travels.filter(end_date__gte=self.request.query_params.get('end_date'))

        return travels.annotate(
            num_of_places=Count('stops', filter=Q(type='place')),
            num_of_events=Count('stops', filter=Q(type='event')),
        ).order_by('initial_date')

    def get_serializer_class(self):
        if self.action == 'list':
            return TravelListSerializer
        return TravelSerializer

    def create(self, request, *args, **kwargs):
        cities = None
        if 'cities' in request.data:
            cities = request.data.pop('cities')

        stops = None
        if 'stops' in request.data:
            stops = request.data.pop('stops')

        travel = Travel.objects.create(user=request.user, **request.data)
        if cities:
            travel.cities.set(cities)

        if stops:
            travel.stops.set(stops)

        return Response(TravelSerializer(travel, context={'request': request}).data, status=201)

    def destroy(self, request, *args, **kwargs):
        if self.get_object().user != self.request.user:
            return Response({'detail': _('You do not have permissions to delete this travel')}, status=402)
        super(TravelViewSet, self).destroy(request, *args, **kwargs)
        return Response({'detail': _('Travel deleted')}, status=200)

    @action(detail=True, methods=['get'], permission_classes=(AllowAny,))
    def directions(self, request, *args, **kwargs):
        origin = self.get_object().stops.first()
        origin_geolocation = (origin.address.latitude, origin.address.longitude)

        destination = self.get_object().stops.last()
        destination_geolocation = (destination.address.latitude, destination.address.longitude)

        stops = self.get_object().stops.exclude(id__in=[origin.id, destination.id])
        waypoints = list(map(lambda x: (x.address.latitude, x.address.longitude), stops))

        directions = get_directions(
            origin=origin_geolocation,
            destination=destination_geolocation,
            mode=request.query_params.get('mode'),
            waypoints=waypoints
        )

        return Response(directions, 200)

    @action(detail=False, methods=['get'])
    def history(self, request):
        travels = self.get_queryset().filter(end_date__lt=now()).order_by('initial_date')

        paginator = PageNumberPagination()
        paginator.page_size = 25
        paginate = request.query_params.get('page')

        if paginate:
            paginated_queryset = paginator.paginate_queryset(travels, request)
            output = TravelListSerializer(paginated_queryset, context={'request': request}, many=True).data
            return paginator.get_paginated_response(output)
        else:
            return Response(TravelListSerializer(travels, many=True, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        travels = (
            self.get_queryset().filter(Q(initial_date__gte=now()) | Q(end_date__gte=now())).order_by('initial_date')
        )

        paginator = PageNumberPagination()
        paginator.page_size = 25
        paginate = request.query_params.get('page')

        if paginate:
            paginated_queryset = paginator.paginate_queryset(travels, request)
            output = TravelListSerializer(paginated_queryset, context={'request': request}, many=True).data
            return paginator.get_paginated_response(output)
        else:
            return Response(TravelListSerializer(travels, many=True, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def list_lite(self, request):
        travels = (
            self.get_queryset().filter(Q(initial_date__gte=now()) | Q(end_date__gte=now())).order_by('initial_date')
        )
        return Response(TravelListLiteSerializer(travels, many=True, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def add_site(self, request, pk):
        serializer = SiteExistsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        site = Site.objects.get(id=serializer.validated_data.get('id'))
        self.get_object().stops.add(site)
        if serializer.validated_data.get('order'):
            stop = Stop.objects.get(site__id=site.id, travel__id=pk)
            stop.order = serializer.validated_data.get('order')
            stop.save()
        if site.city not in self.get_object().cities.all():
            self.get_object().cities.add(site.city)
        return Response({'detail': 'Site added successfully'})

    @action(detail=True, methods=['patch'])
    def update_stops(self, request, pk):
        ordered_list = list(zip(request.data.get('sites'), range(0, len(request.data.get('sites')))))
        sites = Site.objects.filter(id__in=request.data.get('sites'))
        if sites.count() != len(request.data.get('sites')):
            raise ValidationError('One of the stops does not exist', code=400)
        self.get_object().stops.set(sites)
        self.get_object().reorder_stops(ordered_list)

        for stop in sites:
            if stop.city not in self.get_object().cities.all():
                self.get_object().cities.add(stop.city)

        self.get_object().cities.remove(
            *self.get_object()
            .cities.exclude(id__in=self.get_object().stops.values_list('city', flat=True))
            .values_list('id', flat=True)
        )

        return Response({'detail': 'Stops updated successfully'})

    @action(detail=True, methods=['patch'])
    def update_cities(self, request, pk):
        cities = City.objects.filter(id__in=request.data.get('cities'))
        if cities.count() != len(request.data.get('cities')):
            raise ValidationError('One of the cities does not exist', code=400)
        self.get_object().cities.set(cities)
        travel = self.get_object()
        for stop in travel.stops.all():
            if stop.city not in travel.cities.all():
                stop.delete()
        return Response({'detail': 'Cities updated successfully'})

    @action(detail=True, methods=['post'])
    def remove_site(self, request, pk):
        serializer = SiteExistsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        site = self.get_object().stops.get(id=serializer.validated_data.get('id'))
        self.get_object().stops.remove(site)
        self.get_object().cities.set(
            self.get_object().cities.filter(id__in=self.get_object().stops.values_list('city', flat=True))
        )

        return Response({'detail': 'Site removed successfully'})

    @action(detail=True, methods=['post'])
    def add_city(self, request, pk):
        serializer = CityExistsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        city = City.objects.get(id=serializer.validated_data.get('id'))
        self.get_object().cities.add(city)
        return Response({'detail': 'City added'})

    @action(detail=True, methods=['get'], permission_classes=(AllowAny,))
    def pdf(self, request, pk):
        return Travel.objects.get(id=pk).generate_pdf(request)

    @action(detail=True, methods=['get'])
    def generate_link(self, request, pk):
        link = f'https://{request.get_host()}/travels/redirect_detail?id={pk}'
        return Response({'detail': link}, status=200)

    @action(detail=True, methods=['get'])
    def similar_stops(self, request, pk):
        paginator = PageNumberPagination()
        paginator.page_size = 25
        paginate = request.query_params.get('page')

        travel = self.get_object()
        tags = travel.stops.values_list('tags')
        if len(tags) <= 0:
            stops = Site.objects.filter(city__id__in=travel.cities.values_list('id'), is_suggested=True)
        else:
            stops = Site.objects.filter(tags__id__in=tags, city__id__in=travel.cities.values_list('id'))

        stops = stops.exclude(id__in=travel.stops.values_list('id', flat=True)).annotate_is_fav(self.request.user)
        if paginate:
            paginated_queryset = paginator.paginate_queryset(stops.distinct(), request)
            output = SiteListSerializer(paginated_queryset, context={'request': request}, many=True).data
            return paginator.get_paginated_response(output)
        else:
            return Response(
                SiteListSerializer(
                    stops.distinct(),
                    many=True,
                    required=False,
                    context={'request': request},
                ).data,
                status=200,
            )

    @action(detail=False, methods=['get'], permission_classes=(AllowAny,))
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

        travel_id = request.query_params.get('id')
        travel = Travel.objects.filter(id=travel_id).first()
        if not travel:
            return Response({'detail': f'There is no site with id: {travel_id}'}, status=404)
        return Response(TravelSerializer(travel, context={'request': request}).data, status=200)
