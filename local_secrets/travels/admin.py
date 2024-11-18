from django.contrib import admin

from .models import Stop, Travel
from ..core.admin import admin_site


class StopInLine(admin.TabularInline):
    autocomplete_fields = [
        'site',
    ]
    model = Stop
    extra = 0


class TravelAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'initial_date', 'end_date', 'user')
    search_fields = ('title', 'initial_date', 'end_date', 'cities__name', 'user__username')
    date_hierarchy = 'initial_date'
    list_filter = ('type',)
    filter_horizontal = ('cities', 'stops')

    inlines = [
        StopInLine,
    ]

    def get_search_results(self, request, queryset, search_term):
        # Add functionality to split the search_term and allow to search by ranges
        results = super(TravelAdmin, self).get_search_results(request, queryset, search_term)
        return results


admin_site.register(Travel, TravelAdmin)
