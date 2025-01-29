from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from local_secrets.core.admin import admin_site
from local_secrets.languages.models import Language, TranslatedLanguage
from django.contrib import admin
from django.apps import apps

class LanguageResource(ModelResource):
    class Meta:
        model = Language
        fields = ('id', 'code', 'name')


class TranslatedLanguageInLine(admin.TabularInline):
    fk_name = 'language_from'
    model = TranslatedLanguage
    extra = 0


class LanguageAdmin(ImportExportModelAdmin):
    list_display = ('code', 'name')
    resource_class = LanguageResource
    inlines = [
        TranslatedLanguageInLine,
    ]
    search_fields = ['name', 'code']


class TranslationAdmin(admin.ModelAdmin):
    list_display = ('language', 'platform')


Language = apps.get_model('languages', 'Language')  # Dynamically fetch model

if not admin.site.is_registered(Language):
    admin.site.register(Language)
    
admin_site.register(Language, LanguageAdmin)
admin_site.register(TranslatedLanguage)
