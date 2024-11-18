from django.contrib import admin
from django.contrib.admin import TabularInline
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource
from import_export.widgets import ManyToManyWidget
from more_admin_filters import RelatedDropdownFilter, MultiSelectRelatedDropdownFilter

from .models import Route, RouteStop, TranslatedRoute
from ..core.admin import admin_site
from ..sites.models import Site
from ..users.models import Ambassador, Tag


class StopInLine(admin.TabularInline):
    autocomplete_fields = [
        'site',
    ]
    model = RouteStop
    extra = 0


class RouteResource(ModelResource):
    tags = fields.Field(column_name='tags', attribute='tags', widget=ManyToManyWidget(Tag))

    stops = fields.Field(column_name='stops', attribute='stops', widget=ManyToManyWidget(Site))

    class Meta:
        model = Route
        fields = (
            'title',
            'cities',
            'tags',
            'stops',
        )
        import_id_fields = ('title',)


class TranslatedRouteInLine(TabularInline):
    model = TranslatedRoute
    extra = 0


class RouteAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = RouteResource

    def get_queryset(self, request):
        routes = Route.objects.all()
        try:
            ambassador = Ambassador.objects.get(id=request.user.id)
            routes = routes.filter(cities__id__in=ambassador.cities.values_list('id', flat=True))
        except Ambassador.DoesNotExist:
            pass
        return routes

    list_display = ('title', 'num_of_views')
    filter_horizontal = ('tags',)
    autocomplete_fields = ('tags', 'cities')
    search_fields = ('cities__name',)
    inlines = [TranslatedRouteInLine, StopInLine]
    list_filter = (
        ('cities', MultiSelectRelatedDropdownFilter),
        ('tags', MultiSelectRelatedDropdownFilter),
    )


admin_site.register(Route, RouteAdmin)
