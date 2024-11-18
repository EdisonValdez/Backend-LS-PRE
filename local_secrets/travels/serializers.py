from django.db.models import OuterRef, Subquery
from rest_framework import serializers

from local_secrets.cities.serializers import CitySerializer
from local_secrets.sites.serializers import SiteForTravelSerializer
from local_secrets.travels.models import Stop, Travel


class TravelSerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True, required=False)
    days_until_trip = serializers.SerializerMethodField(read_only=True)
    num_of_places = serializers.SerializerMethodField()
    num_of_events = serializers.SerializerMethodField()
    stops = serializers.SerializerMethodField()

    def get_days_until_trip(self, obj):
        if hasattr(obj, 'days_until_trip'):
            return obj.days_until_trip.days
        return None

    def get_num_of_places(self, obj):
        return obj.stops.filter(type='place').count()

    def get_num_of_events(self, obj):
        return obj.stops.filter(type='event').count()

    def get_stops(self, obj):
        stops = obj.stops.all().annotate(
            order=Subquery(Stop.objects.filter(site__id=OuterRef('id'), travel__id=obj.id).values('order'))
        )
        return SiteForTravelSerializer(stops.order_by('order'), many=True, required=False, context=self.context).data

    class Meta:
        model = Travel
        exclude = ('user',)


class TravelListSerializer(TravelSerializer):
    similar_stops = None
    stops = None

    class Meta:
        model = Travel
        exclude = (
            'user',
            'stops',
        )


class TravelListLiteSerializer(TravelListSerializer):
    similar_stops = None
    stops = None
    num_of_events = None
    num_of_places = None
    days_until_trip = None
    cities = None

    class Meta:
        model = Travel
        exclude = (
            'user',
            'cities',
            'stops',
        )


class TravelExistsSerializer(serializers.Serializer):
    id = serializers.CharField()

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception)
        try:
            Travel.objects.get(id=self.validated_data.get('id'))
        except Travel.DoesNotExist:
            if raise_exception:
                raise serializers.ValidationError(detail='The travel does not exist', code=400)
            return False
        return is_valid
