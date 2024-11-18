from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from local_secrets.core.admin import admin_site
from local_secrets.languages.models import Language, TranslatedLanguage


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


class TranslationAdmin(admin.ModelAdmin):
    list_display = ('language', 'platform')


admin_site.register(Language, LanguageAdmin)
admin_site.register(TranslatedLanguage)
