from django.contrib import admin
from django.db.models import Count
from django.contrib.admin import TabularInline
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource
from nested_admin import NestedModelAdmin, NestedTabularInline
from .models import Ambassador, CustomUser, Notification, Tag, TranslatedTag, UserTags
from ..core.admin import admin_site
from ..core.utils.admin_actions import ExportCsvMixin


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)


class CustomUserAdmin(UserAdmin, ExportCsvMixin):
    filter_horizontal = ('groups',)


class AmbassadorAdmin(CustomUserAdmin):
    filter_horizontal = ('cities', 'groups')

###################EDISON IMPLEMENTATION##################
 
class TranslatedTagResource(ModelResource):
    class Meta:
        model = TranslatedTag
        fields = ('id', 'tag', 'language', 'title')


class TranslatedTagInLine(NestedTabularInline):
    """Inline to manage translations for each tag"""
    model = TranslatedTag
    extra = 0
    fields = ('language', 'title')
    autocomplete_fields = ('language',)


class TagResource(ModelResource):
    class Meta:
        model = Tag
        fields = ('id', 'title')


class TagAdmin(ImportExportModelAdmin, NestedModelAdmin):
    """Admin to manage Tags"""
    resource_class = TagResource

    def num_of_translations(self, obj):
        """Count the number of translations for a tag"""
        return obj.translations.count()

    num_of_translations.admin_order_field = 'num_of_translations'
    num_of_translations.short_description = 'Translations'

    def num_of_users(self, obj):
        """Count the number of users associated with a tag"""
        return obj.users.count()

    num_of_users.admin_order_field = 'num_of_users'
    num_of_users.short_description = 'Users'

    list_display = ('title', 'num_of_translations', 'num_of_users')
    search_fields = ('title', 'translations__title', 'translations__language__name')
    inlines = [TranslatedTagInLine]
    list_filter = ('translations__language',)


class TranslatedTagAdmin(ImportExportModelAdmin):
    """Admin to manage Translated Tags"""
    resource_class = TranslatedTagResource

    list_display = ('id', 'tag', 'language', 'title')
    search_fields = ('tag__title', 'title', 'language__name')
    list_filter = ('language', 'tag__title')


###################EDISON IMPLEMENTATION##################

#class TagResource(ModelResource):
    #class Meta:
        #model = Tag
        #fields = ('id', 'title')


#class TranslatedTagInLine(TabularInline):
    #model = TranslatedTag
    #extra = 0


#class TagAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    #resource_class = TagResource

    #def num_of_users(self, obj):
        #return obj.users.count()

    #list_display = ('title', 'num_of_users')
    #search_fields = ('title',)
    #inlines = [
        #TranslatedTagInLine,
    #]


admin_site.register(CustomUser, CustomUserAdmin)
admin_site.register(Ambassador, AmbassadorAdmin)
admin_site.register(Tag, TagAdmin)
admin_site.register(TranslatedTag, TranslatedTagAdmin)
admin_site.register(UserTags)
admin_site.register(Notification, NotificationAdmin)
# admin_site.register(UserNotification)