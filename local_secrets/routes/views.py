from django.db.models import Count
from django.shortcuts import redirect
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from local_secrets.cities.models import City
from local_secrets.core.utils.directions import get_directions
from local_secrets.core.utils.text import TextHelper as text
from local_secrets.routes.models import Route, RouteStop
from local_secrets.routes.serializers import CityWithRoutesSerializer, RouteListWithCitiesSerializer, RouteSerializer
from local_secrets.travels.models import Travel
from local_secrets.travels.serializers import TravelExistsSerializer


class RouteViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    permission_classes = (AllowAny,)

    @property
    def paginator(self):
        self._paginator = super(RouteViewSet, self).paginator
        if not self.request.query_params.get('page'):
            self._paginator = None
        return self._paginator

    def get_queryset(self):
        language = self.request.headers.get('Language')
        return (
            Route.objects.all()
            .filter_by_city(self.request.query_params.get('city'), language=language)
            .filter_by_title(self.request.query_params.get('title'), language=language)
            .filter_by_city_id(self.request.query_params.get('city_id'))
            .filter_by_tag(self.request.query_params.get('tag'))
            .order_by('is_top_ten', 'num_of_views', 'id')
            .distinct()
            .annotate_translated_fields()
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return RouteListWithCitiesSerializer
        return RouteSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def retrieve(self, request, *args, **kwargs):
        try:
            return super(RouteViewSet, self).retrieve(request, *args, **kwargs)
        except Route.MultipleObjectsReturned:
            route = self.get_queryset().filter(id=kwargs.get('pk')).first()
            route.add_view()
            return Response(self.get_serializer_class()(route, context={'request': request}).data)

    @action(detail=True, methods=['get'])
    def directions(self, request, *args, **kwargs):
        origin = self.get_object().stops.first()
        origin_geolocation = (origin.address.latitude, origin.address.longitude)

        destination = self.get_object().stops.last()
        destination_geolocation = (destination.address.latitude, destination.address.longitude)

        stops = RouteStop.objects.filter(route__id=self.get_object().id).order_by('order').exclude(id__in=[origin.id, destination.id])
        waypoints = list(map(lambda x: (x.site.address.latitude, x.site.address.longitude), stops.filter(site__address__isnull=False)))

        directions = get_directions(
            origin=origin_geolocation,
            destination=destination_geolocation,
            mode=request.query_params.get('mode'),
            waypoints=waypoints
        )

        return Response(directions, 200)

    @action(detail=False, methods=['get'])
    def by_city(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 20
        paginate = request.query_params.get('page')
        cities = City.objects.only('id', 'name', 'slogan',).annotate(num_of_routes=Count('routes')).filter(num_of_routes__gt=0, activated=True)
        language = request.headers.get('Language')
        if request.query_params.get('city'):
            city = request.query_params.get('city').lower().rstrip(" ").lstrip(" ")
            _city = text.remove_all_accent_marks(city)
            has_accents = city != _city
            if language:
                if has_accents:
                    cities = cities.filter(translations__name__icontains=city)
                else:
                    cities = cities.filter(translations__name__unaccent__icontains=_city)
            else:
                if has_accents:
                    cities = cities.filter(name__icontains=city)
                else:
                    cities = cities.filter(name__unaccent__icontains=_city)

        if request.query_params.get('title'):
            title = request.query_params.get('title').lower().rstrip(" ").lstrip(" ")
            _title = text.remove_all_accent_marks(title)
            has_accents = title != _title
            if language:
                if has_accents:
                    cities = cities.filter(routes__translations__title__icontains=title)
                else:
                    cities = cities.filter(routes__translations__title__unaccent__icontains=_title)
            else:
                if has_accents:
                    cities = cities.filter(routes__title__icontains=title)
                else:
                    cities = cities.filter(routes__title__unaccent__icontains=_title)
        cities = cities.order_by('name')
        if paginate:
            queryset = paginator.paginate_queryset(cities, request)
            output = CityWithRoutesSerializer(queryset, context={'request': request}, many=True).data
            return paginator.get_paginated_response(output)
        else:
            return Response(CityWithRoutesSerializer(cities, many=True, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=(IsAuthenticated,))
    def add_to_travel(self, request, pk):
        route = self.get_object()
        serializer = TravelExistsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            travel = request.user.travels.get(id=serializer.validated_data.get('id'))
        except Travel.DoesNotExist:
            raise ValidationError(detail='The selected Travel is not yours', code=400)
        travel.add_route(route)
        return Response({'detail': 'The route stops have been added to the travel'}, status=201)

    @action(detail=True, methods=['get'])
    def generate_link(self, request, pk):
        link = f'https://{request.get_host()}/routes/redirect_detail?id={pk}'
        return Response({'detail': link}, status=200)

    @action(detail=False, methods=['get'], permission_classes=(AllowAny,))
    def redirect_detail(self, request):
        user_agent = request.META['HTTP_USER_AGENT'].lower()
        if user_agent not in ['local-secrets']:
            if 'android' in user_agent:
                return redirect('https://play.google.com/store')
            elif 'ios' in user_agent or 'iphone' in user_agent or 'apple' in user_agent:
                return redirect('https://apps.apple.com/us/app/local-secrets/id6448513168')
            else:
                return redirect('https://play.google.com/store')

        route_id = request.query_params.get('id')
        route = self.get_queryset().filter(id=route_id).first()
        if not route:
            return Response({'detail': f'There is no route with id: {route_id}'}, status=404)
        return Response(RouteSerializer(route, context={'request': request}).data, status=200)

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk):
        return self.get_object().generate_pdf(request)
