from django.contrib import admin
from django.contrib.admin import TabularInline
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from .models import Ambassador, CustomUser, Notification, Tag, TranslatedTag, UserTags
from ..core.admin import admin_site
from ..core.utils.admin_actions import ExportCsvMixin


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)


class CustomUserAdmin(UserAdmin, ExportCsvMixin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'language', 'profile_picture')}),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone'),
            },
        ),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    filter_horizontal = ('groups',)


class AmbassadorAdmin(CustomUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone'),
            },
        ),
        ('Cities', {'classes': ('filter_horizontal',), 'fields': ('cities',)}),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'language')}),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Cities'), {'fields': ('cities',)}),
    )

    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'cities__name', 'cities__country__name')
    filter_horizontal = ('cities', 'groups')


class TagResource(ModelResource):
    class Meta:
        model = Tag
        fields = ('id', 'title')


class TranslatedTagInLine(TabularInline):
    model = TranslatedTag
    extra = 0


class TagAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TagResource

    def num_of_users(self, obj):
        return obj.users.count()

    list_display = ('title', 'num_of_users')
    search_fields = ('title',)
    inlines = [
        TranslatedTagInLine,
    ]


admin_site.register(CustomUser, CustomUserAdmin)
admin_site.register(Ambassador, AmbassadorAdmin)
admin_site.register(Tag, TagAdmin)
admin_site.register(UserTags)
admin_site.register(Notification, NotificationAdmin)
# admin_site.register(UserNotification)
