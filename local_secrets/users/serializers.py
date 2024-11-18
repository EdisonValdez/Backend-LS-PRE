from django.contrib.auth.models import Group
from django.core.validators import RegexValidator
from django.db.models import DurationField, ExpressionWrapper, F
from django.utils import translation
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import CustomUser, GroupDescription, Notification, Tag
from ..core.custom_exceptions import CustomApiException
from ..core.serializers import ThumbnailJSONSerializer
from ..languages.serializers import LanguageSerializer
from ..operations.models import DefaultText


class TagOutputSerializer(serializers.ModelSerializer):
    is_selected = serializers.BooleanField()

    def to_representation(self, instance):
        representation = super(TagOutputSerializer, self).to_representation(instance)
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
        model = Tag
        fields = '__all__'


class TagOutputWithoutSelectionSerializer(TagOutputSerializer):
    is_selected = None


class TagSelectionInputSerializer(serializers.Serializer):
    tags = serializers.ListField(child=serializers.IntegerField())


class UserInputSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    password = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Z])*(?=.*\d)(?=.*[@$!%*#?&.])*(?=.*\d)[A-Z\d@$!%*#?&.]*(?=.*\d).{7,}$',
                message=_(
                    'The password must be 8 characters long, have an uppercase letter, a number and '
                    'a special character'
                ),
                code='invalid_password',
            )
        ],
        required=False,
    )
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{9,15}$',
                message=_('The phone must contain between 9 and 15 numbers'),
                code='invalid_phone',
            )
        ],
    )
    phone_prefix = serializers.CharField(required=False)

    def is_valid(self, raise_exception=False):
        #with translation.override(self.context.get('request').headers.get('language')):
        is_valid = super().is_valid(raise_exception)
        users = CustomUser.objects.all()
        if not self.context.get('request').user.is_anonymous:
            users = users.exclude(id=self.context.get('request').user.id)
        if users.filter(email=self.validated_data.get('email')).exists():
            if raise_exception:
                raise CustomApiException(message=_('There is an user with the same email'), status_code=400)
            return False
        if users.filter(username=self.validated_data.get('username')).exists():
            if raise_exception:
                raise CustomApiException(message=_('There is an user with the same username'), status_code=400)
            return False
        return is_valid

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'phone', 'phone_prefix')


class GroupSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super(GroupSerializer, self).to_representation(instance)
        request = self.context.get('request')

        if request and request.headers.get('language'):
            language = request.headers.get('language')
        else:
            return representation

        for field in self.fields:
            if field in ['description', 'name']:
                try:
                    representation[field] = GroupDescription.objects.get(group__id=instance.id).display_text(
                        field, language
                    )
                except BaseException as e:
                    print(e)
                    pass
        return representation

    description = serializers.SerializerMethodField()
    general_description = serializers.SerializerMethodField()

    def get_description(self, obj):
        try:
            return GroupDescription.objects.get(group__id=obj.id).description
        except GroupDescription.DoesNotExist:
            return ""

    def get_general_description(self, obj):
        try:
            return (
                DefaultText.objects.filter(title='group_description')
                .first()
                .display_text('text', self.context.get('request').headers.get('language'))
            )
        except Exception:
            return ''

    class Meta:
        model = Group
        fields = ('name', 'description', 'general_description')


class UserOutputSerializer(serializers.ModelSerializer):
    tags = TagOutputWithoutSelectionSerializer(many=True)
    profile_picture = ThumbnailJSONSerializer(alias='', read_only=True)
    next_trip = serializers.SerializerMethodField(allow_null=True)
    current_trip = serializers.SerializerMethodField(allow_null=True)
    is_on_trip = serializers.SerializerMethodField()
    num_of_past_travels = serializers.IntegerField()
    num_of_upcoming_travels = serializers.IntegerField()
    visited_places = serializers.IntegerField(default=0)
    visited_events = serializers.IntegerField(default=0)
    groups = GroupSerializer(many=True, read_only=True, allow_null=True)
    language = LanguageSerializer()

    def get_is_on_trip(self, obj):
        current_time = now()
        for travel in obj.travels.all():
            if travel.initial_date <= current_time.date() <= travel.end_date:
                return True
        return False

    def get_next_trip(self, obj):
        from ..travels.serializers import TravelListSerializer

        subquery = ExpressionWrapper((F('initial_date') - now().date()), output_field=DurationField())
        travels = obj.travels.filter(initial_date__gte=now().date())
        if not travels.exists():
            return None
        return TravelListSerializer(
            travels.annotate(days_until_trip=subquery).order_by('initial_date').first(),
            context=self.context,
        ).data

    def get_current_trip(self, obj):
        from ..travels.serializers import TravelListSerializer

        travels = obj.travels.filter(end_date__gte=now().date(), initial_date__lte=now().date())
        if not travels.exists():
            return None
        return TravelListSerializer(
            travels.annotate(
                days_until_trip=ExpressionWrapper((F('initial_date') - now().date()), output_field=DurationField())
            )
            .order_by('-initial_date')
            .first(),
            context=self.context,
        ).data

    class Meta:
        model = CustomUser
        exclude = (
            'password',
            'is_superuser',
            'is_staff',
            'is_active',
            'user_permissions',
        )


class UserCommentOutputSerializer(serializers.ModelSerializer):
    profile_picture = ThumbnailJSONSerializer(alias='', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'profile_picture')


# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    # Add extra fields
    has_been_seen = serializers.BooleanField()

    class Meta:
        model = Notification
        fields = ('id', 'title', 'body', 'link', 'site', 'has_been_seen', 'created_at')


# Notification Detail Serializer
class NotificationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        # fields = '__all__'
        fields = ('id', 'title', 'body', 'link', 'site', 'created_at')


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(allow_null=False)
    new_password = serializers.CharField(allow_null=False, allow_blank=False)

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception)
        old_password = self.validated_data['old_password']
        new_password = self.validated_data['new_password']
        if old_password == new_password:
            raise serializers.ValidationError(
                code=400, detail='The new password cannot be the same as the previous ' 'password'
            )
        return is_valid
