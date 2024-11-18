from django.contrib import admin
from django.contrib.admin import TabularInline
from django.contrib.gis.admin import OSMGeoAdmin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource
from more_admin_filters import RelatedDropdownFilter, DropdownFilter

from .models import Address, City, CityImage, Country, PhoneCode, TranslatedCity, TranslatedCountry, TranslatedPhoneCode
from ..core.admin import admin_site


class CityImageInLine(admin.TabularInline):
    model = CityImage
    extra = 1


class CityResource(ModelResource):
    class Meta:
        model = City
        fields = ('id', 'name', 'country', 'cp', 'province', 'description', 'slogan', 'link', 'latitude', 'longitude')
        import_id_fields = ('name',)


class TranslatedCityInLine(TabularInline):
    model = TranslatedCity
    extra = 0


class CityAdmin(ImportExportModelAdmin, OSMGeoAdmin):
    resource_class = CityResource

    def get_queryset(self, request):
        cities = City.objects.all()
        from local_secrets.users.models import Ambassador

        try:
            ambassador = Ambassador.objects.get(id=request.user.id)
            cities = cities.filter(id__in=ambassador.cities.values_list('id', flat=True))
        except Ambassador.DoesNotExist:
            pass
        return cities.order_by('name')

    list_display = (
        'name',
        'cp',
        'province',
        'activated',
    )
    list_filter = (
        ('name', DropdownFilter),
        ('country', RelatedDropdownFilter),
        'activated'
    )
    search_fields = ('name', 'cp', 'province')
    autocomplete_fields = ('country',)
    inlines = [CityImageInLine, TranslatedCityInLine]

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super(CityAdmin, self).get_form(request, obj, change, **kwargs)
        return form


class AddressResource(ModelResource):
    class Meta:
        model = Address

        fields = (
            'street',
            'city',
            'cp',
            'latitude',
            'longitude',
            'google_place_id',
            'details',
            'number',
            'door',
            'floor',
        )

        import_id_fields = ('street',)


class AddressResourceWithID(ModelResource):
    class Meta:
        model = Address

        fields = (
            'id',
            'street',
            'city',
            'cp',
            'latitude',
            'longitude',
            'google_place_id',
            'details',
            'number',
            'door',
            'floor',
        )


class AddressAdmin(ImportExportModelAdmin, OSMGeoAdmin):
    # resource_class = AddressResource
    list_display = (
        'street',
        'number',
        'city',
    )
    list_filter = (
        ('city__country__name', DropdownFilter),
        ('city__province', DropdownFilter)
    )
    search_fields = (
        'street',
        'city__name',
        'city__cp',
        'city__province',
        'city__country__name',
    )
    autocomplete_fields = ('city',)
    date_hierarchy = 'creation_date'

    def get_queryset(self, request):
        address = Address.objects.all()
        from local_secrets.users.models import Ambassador

        try:
            ambassador = Ambassador.objects.get(id=request.user.id)
            address = address.filter(city__id__in=ambassador.cities.values_list('id', flat=True))
        except Ambassador.DoesNotExist:
            pass
        return address

    def get_export_resource_classes(self):
        return [
            AddressResourceWithID(),
        ]

    def get_import_resource_classes(self):
        return [
            AddressResource(),
        ]


class CityInLine(admin.TabularInline):
    model = City
    exclude = ('point', 'description', 'media', 'images')


class TranslatedCountryInLine(TabularInline):
    model = TranslatedCountry
    extra = 0


class TranslatedPhoneCodeInLine(TabularInline):
    model = TranslatedPhoneCode
    extra = 0


class CountryResource(ModelResource):
    class Meta:
        model = Country
        fields = ('id', 'name', 'code', 'phone_code')
        import_id_fields = ('name',)


class CountryAdmin(ImportExportModelAdmin):
    resource_class = CountryResource

    def get_queryset(self, request):
        countries = Country.objects.all()
        from local_secrets.users.models import Ambassador

        try:
            ambassador = Ambassador.objects.get(id=request.user.id)
            countries = countries.filter(id__in=ambassador.cities.values_list('country__id', flat=True))
        except Ambassador.DoesNotExist:
            pass
        return countries

    list_display = ('name', 'code')
    list_filter = (('code', DropdownFilter),)
    search_fields = ('name', 'code')
    inlines = [CityInLine, TranslatedCountryInLine]


class PhoneCodeResource(ModelResource):
    class Meta:
        model = PhoneCode
        fields = ('id', 'name', 'code', 'phone_code')
        import_id_fields = ('name',)


class PhoneCodeAdmin(ImportExportModelAdmin):
    resource_class = PhoneCodeResource
    list_display = ('name', 'code')
    list_filter = (('code', DropdownFilter),)
    search_fields = ('name', 'code')
    inlines = [TranslatedPhoneCodeInLine]


admin_site.register(Country, CountryAdmin)
admin_site.register(PhoneCode, PhoneCodeAdmin)
admin_site.register(City, CityAdmin)
admin_site.register(Address, AddressAdmin)
