from datetime import timedelta

from django.db.models import Avg
from django.utils.timezone import now, localtime
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from local_secrets.cities.models import City
from local_secrets.cities.serializers import AddressSerializer, BaseCitySerializer, CitySerializer, \
    AddressPointSerializer
from local_secrets.core.serializers import ThumbnailJSONSerializer
from local_secrets.sites.choices import Day
from local_secrets.sites.models import (
    Category,
    Comment,
    DefaultImage,
    Level,
    Schedule,
    Site,
    SpecialSchedule,
    SubCategory,
)
from local_secrets.users.serializers import TagOutputWithoutSelectionSerializer, UserCommentOutputSerializer


class SubCategorySerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super(SubCategorySerializer, self).to_representation(instance)
        request = self.context.get('request')

        if request and request.headers.get('language'):
            language = request.headers.get('language')
        else:
            return representation

        for field in self.fields:
            if field in ['title', 'description', 'type']:
                representation[field] = instance.display_text(field, language)
        return representation

    class Meta:
        model = SubCategory
        exclude = ('category',)


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    def get_subcategories(self, obj):
        return SubCategorySerializer(
            SubCategory.objects_for_api.filter(category__id=obj.id),
            many=True,
            context=self.context
        ).data

    def to_representation(self, instance):
        representation = super(CategorySerializer, self).to_representation(instance)
        request = self.context.get('request')
        if request and request.headers.get('language'):
            language = request.headers.get('language')
        else:
            return representation

        for field in self.fields:
            if field in ['title', 'description', 'type']:
                representation[field] = instance.display_text(field, language)
        return representation

    class Meta:
        model = Category
        fields = ['id', 'title', 'subcategories']


class CategoryListSerializer(CategorySerializer):
    subcategories = None

    class Meta:
        model = Category
        fields = ['id', 'title',]


class LevelSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    def get_categories(self, obj):
        return CategorySerializer(
            Category.objects_for_api.filter(level__id=obj.id),
            many=True,
            context=self.context
        ).data

    def to_representation(self, instance):
        representation = super(LevelSerializer, self).to_representation(instance)
        request = self.context.get('request')

        if request and request.headers.get('language'):
            language = request.headers.get('language')
        else:
            return representation

        for field in self.fields:
            if field in [
                'title',
            ]:
                representation[field] = instance.display_text(field, language)
        return representation

    class Meta:
        model = Level
        fields = ['id', 'title', 'categories']


class LevelListSerializer(LevelSerializer):
    categories = None

    class Meta:
        model = Level
        fields = ['id', 'title',]


class HourRangeSerializer(serializers.Serializer):
    id = serializers.IntegerField(default=0)
    initial_hour = serializers.TimeField(format='%I:%M %p')
    end_hour = serializers.TimeField(format='%I:%M %p')

    class Meta:
        fields = ('id', 'initial_hour', 'end_hour')


class ScheduleSerializer(serializers.ModelSerializer):
    opening_hours = HourRangeSerializer(many=True)

    class Meta:
        model = Schedule
        exclude = ('site',)


class SpecialScheduleSerializer(serializers.ModelSerializer):
    # initial_hour = serializers.TimeField(format='%I:%M %p')
    # end_hour = serializers.TimeField(format='%I:%M %p')
    opening_hours = serializers.SerializerMethodField()
    #opening_hours = HourRangeSerializer(many=True)

    def get_opening_hours(self, obj):
        days = dict(zip(range(0, 6), Day.choices))
        try:
            if obj.opening_hours.exists():
                return HourRangeSerializer(obj.opening_hours.all(), many=True).data
            if obj.site.schedules.filter(day=days[obj.day.weekday()][0]).exists():
                return HourRangeSerializer(obj.site.schedules.filter(day=days[obj.day.weekday()][0]).first().opening_hours.all(), many=True).data
        except Exception as e:
            print(e)
            return []
        return []

    class Meta:
        model = SpecialSchedule
        exclude = ('site',)


class SiteGeolocationSerializer(serializers.ModelSerializer):
    address = AddressPointSerializer()

    class Meta:
        model = Site
        fields = ('id', 'address')


class SiteListSerializer(serializers.ModelSerializer):
    city = BaseCitySerializer()
    images = ThumbnailJSONSerializer(alias='', read_only=True, many=True)
    rating = serializers.SerializerMethodField()
    tags = TagOutputWithoutSelectionSerializer(many=True)
    is_fav = serializers.BooleanField(required=False, default=False)
    address = AddressSerializer()
    next_schedule = serializers.SerializerMethodField(required=False, allow_null=True)
    date_range = serializers.SerializerMethodField(required=False, allow_null=True)
    levels = LevelListSerializer(many=True)

    def get_next_schedule(self, obj):
        next = obj.next_schedule()
        if obj.type == 'place':
            return ScheduleSerializer(next, required=False, allow_null=True).data
        if not next:
            return None
        if type(next) == Schedule:
            return ScheduleSerializer(next, required=False, allow_null=True).data
        elif type(next) == SpecialSchedule:
            return SpecialScheduleSerializer(next, required=False, allow_null=True).data
        else:
            return None

    def get_date_range(self, obj):
        if obj.type == 'event':
            today = localtime().date()
            dates = [
                obj.special_schedules.annotate_day_distance(today).order_by('day_distance').first(),
                obj.special_schedules.annotate_day_distance(today).order_by('day_distance').last()
            ]
            dates.reverse()
            if len(dates) == 0 or not obj.special_schedules.exists():
                return []

            if obj.frequency == 'year' and dates[0].day < today:
                dates[0].day = dates[0].day.replace(year=today.year + 1)
                dates[1].day = dates[1].day.replace(year=today.year + 1)
            return SpecialScheduleSerializer(dates, many=True).data
        return []

    def get_rating(self, obj):
        return obj.comments.aggregate(average_rating=Avg('rating'))['average_rating'] or 0

    def to_representation(self, instance):
        representation = super(SiteListSerializer, self).to_representation(instance)
        request = self.context.get('request')

        if request and request.headers.get('language'):
            language = request.headers.get('language')
        else:
            return representation

        for field in self.fields:
            if field in [
                'title',
                'description',
            ]:
                representation[field] = instance.display_text(field, language)
        return representation

    class Meta:
        model = Site
        exclude = (
            'users',
            'categories',
            'subcategories',
            'description',
        )


class SiteRandomListSerializer(SiteListSerializer):
    city = None
    rating = None
    tags = None
    address = None
    date_range = None
    levels = None

    class Meta:
        model = Site
        fields = ('id', 'title', 'images', 'is_fav', 'next_schedule')


class SiteLiteListSerializer(SiteRandomListSerializer):
    city = None
    rating = None
    tags = None
    address = None
    levels = LevelListSerializer(many=True)
    date_range = serializers.SerializerMethodField(required=False, allow_null=True)

    class Meta:
        model = Site
        fields = ('id', 'title', 'images', 'is_fav', 'next_schedule', 'levels', 'date_range')


class SiteSerializer(SiteListSerializer):
    city = CitySerializer()
    levels = LevelListSerializer(many=True)
    categories = CategoryListSerializer(many=True)
    subcategories = SubCategorySerializer(many=True)
    schedules = ScheduleSerializer(many=True)
    special_schedules = SpecialScheduleSerializer(many=True)
    is_open = serializers.SerializerMethodField()
    tags = TagOutputWithoutSelectionSerializer(many=True)

    def get_is_open(self, obj):
        is_open = obj.is_open_by_schedule()
        if not is_open:
            is_open = obj.check_frequency(is_open)
            print(type(is_open))
        return is_open

    class Meta:
        model = Site
        exclude = ('users',)


class SiteWithoutCitySerializer(SiteSerializer):
    city = None
    levels = LevelListSerializer(many=True)
    categories = CategoryListSerializer(many=True)
    subcategories = SubCategorySerializer(many=True)

    class Meta:
        model = Site
        exclude = ('users', 'city')


class SiteForTravelSerializer(SiteWithoutCitySerializer):
    levels = None
    categories = None
    subcategories = None
    tags = None
    is_open = None
    special_schedules = None
    schedules = None
    next_schedule = None
    date_range = None
    city = CitySerializer()

    class Meta:
        model = Site
        exclude = (
            'users',
            'levels',
            'categories',
            'subcategories',
            'tags',
            'created_by',
            'has_been_accepted',
        )


class SiteCreationSerializer(serializers.ModelSerializer):
    schedules = serializers.ListField(child=serializers.JSONField(), required=False)
    special_schedules = serializers.ListField(child=serializers.JSONField(), required=False)
    levels = serializers.ListField(child=serializers.IntegerField(), required=True)
    categories = serializers.ListField(child=serializers.IntegerField(), required=True)
    subcategories = serializers.ListField(child=serializers.IntegerField(), required=True)
    location = serializers.JSONField()
    frequency = serializers.CharField(required=False)

    class Meta:
        model = Site
        fields = (
            'title',
            'type',
            'levels',
            'categories',
            'subcategories',
            'description',
            'schedules',
            'special_schedules',
            'location',
            'url',
            'phone',
            'frequency',
        )

    def is_valid(self, raise_exception=False):
        is_valid = super(SiteCreationSerializer, self).is_valid(raise_exception)

        levels = self.initial_data.get('levels')
        if Level.objects.filter(id__in=levels).count() != len(levels):
            if raise_exception:
                raise ValidationError(detail='Some of the selected levels does not exist', code=400)
            return False

        categories = self.initial_data.get('categories')
        if Category.objects.filter(id__in=categories).count() != len(categories):
            if raise_exception:
                raise ValidationError(detail='The selected category does not exist', code=400)
            return False

        subcategories = self.initial_data.get('subcategories')
        if SubCategory.objects.filter(id__in=subcategories).count() != len(subcategories):
            if raise_exception:
                raise ValidationError(detail='The selected subcategory does not exist', code=400)
            return False

        return is_valid


class FavoriteSitesFilterSerializer(serializers.Serializer):
    type = serializers.CharField(required=False)
    levels = serializers.ListField(required=False)
    categories = serializers.ListField(required=False)
    subcategories = serializers.ListField(required=False)
    keyword = serializers.CharField(required=False)
    city = serializers.CharField(required=False)


class CommentInputSerializer(serializers.Serializer):
    body = serializers.CharField(allow_blank=True)
    rating = serializers.IntegerField()

    def is_valid(self, raise_exception=False):
        is_valid = super(CommentInputSerializer, self).is_valid(raise_exception)
        if self.validated_data.get('rating') >= 1:
            return is_valid
        if raise_exception:
            raise ValidationError(_('The review must have at least 1 star'), code=400)
        return False


class CommentSerializer(serializers.ModelSerializer):
    user = UserCommentOutputSerializer()
    body = serializers.CharField(allow_blank=True)

    class Meta:
        model = Comment
        exclude = [
            'site',
        ]


class DefaultImageSerializer(serializers.ModelSerializer):
    image = ThumbnailJSONSerializer(alias='', read_only=True)

    class Meta:
        model = DefaultImage
        fields = "__all__"


class SiteExistsSerializer(serializers.Serializer):
    id = serializers.CharField()
    order = serializers.IntegerField(required=False)

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception)
        try:
            Site.objects.get(id=self.validated_data.get('id'))
        except Site.DoesNotExist:
            if raise_exception:
                raise serializers.ValidationError(detail='The site does not exist', code=400)
            return False
        return is_valid


class CityExistsSerializer(serializers.Serializer):
    id = serializers.CharField()

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception)
        try:
            City.objects.get(id=self.validated_data.get('id'))
        except City.DoesNotExist:
            if raise_exception:
                raise serializers.ValidationError(detail='The city does not exist', code=400)
            return False
        return is_valid


class SitestoDiscoverSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    display_text = serializers.SerializerMethodField(read_only=True)
    images = ThumbnailJSONSerializer(alias='', read_only=True, many=True)
    type = serializers.SerializerMethodField(read_only=True)
    slogan = serializers.CharField(required=False, read_only=True)
    num_of_routes = serializers.SerializerMethodField(read_only=True)
    city = CitySerializer(required=False, read_only=True)
    date_range = serializers.SerializerMethodField(required=False, read_only=True)
    address = AddressSerializer(required=False, read_only=True)
    categories = CategoryListSerializer(many=True, required=False, read_only=True)
    always_open = serializers.BooleanField(required=False, read_only=True)

    def get_type(self, obj):
        if type(obj) == City:
            return 'city'
        else:
            return obj.type

    def get_num_of_routes(self, obj):
        if type(obj) == City:
            return obj.routes.count()
        return 0

    def get_date_range(self, obj):
        if type(obj) == Site:
            if obj.type == 'event':
                dates = []
                dates.append(obj.special_schedules.first())
                dates.append(obj.special_schedules.last())
                return SpecialScheduleSerializer(dates, many=True).data
        return []

    def get_display_text(self, obj):
        try:
            getattr(obj, 'title')
            return obj.display_text('title', language=self.context.get('request').headers.get('Language'))
        except Exception:
            pass

        try:
            getattr(obj, 'name')
            return obj.display_text('name', language=self.context.get('request').headers.get('Language'))
        except Exception:
            pass
        return None
