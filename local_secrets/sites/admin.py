from datetime import datetime

from dal import autocomplete, forward
from dal_admin_filters import AutocompleteFilter
from django import forms
from django.contrib import admin
from django.contrib.admin import TabularInline
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import ManyToManyWidget
from more_admin_filters import RelatedDropdownFilter
from nested_admin import nested


from .choices import Day
from .models import (
    Category,
    FavoriteSites,
    HourRange,
    Level,
    Schedule,
    Site,
    SiteImage,
    SpecialHourRange,
    SpecialSchedule,
    SubCategory,
    TranslatedCategory,
    TranslatedLevel,
    TranslatedSite,
    TranslatedSubCategory,
)
from .validators import video_size
from ..cities.models import City
from ..core.admin import admin_site
from ..users.models import Ambassador, Tag


class LevelFilter(AutocompleteFilter):
    title = _('Level')
    field_name = 'levels'
    autocomplete_url = 'level-autocomplete'

    def get_queryset_for_field(self, model, name):
        return Level.objects_for_admin.all()


class LevelFilterForCategory(LevelFilter):
    field_name = 'level'


class CategoryInLine(admin.TabularInline):
    model = Category
    extra = 0
    fields = ('id', 'title', 'type', 'order')
    readonly_fields = ('id',)

    def get_queryset(self, request):
        return Category.objects_for_admin.all()


class LevelResource(ModelResource):
    categories = Field(column_name='Categories')

    def dehydrate_categories(self, obj):
        return ", ".join(obj.categories.values_list('title', flat=True))

    class Meta:
        model = Level
        fields = ('id', 'title', 'categories', 'order')
        export_order = fields


class TranslatedLevelInLine(TabularInline):
    model = TranslatedLevel
    extra = 0


class LevelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = LevelResource
    list_display = ('title', 'type', 'order')
    search_fields = ('title',)
    inlines = [CategoryInLine, TranslatedLevelInLine]
    list_filter = ('type',)

    def get_queryset(self, request):
        return Level.objects_for_admin.all()

    def get_ordering(self, request):
        return ['order']

    def get_search_results(self, request, queryset, search_term):
        result_queryset, has_duplicates = super(LevelAdmin, self).get_search_results(request, queryset, search_term)
        return result_queryset, has_duplicates


class HiddenLevelAdmin(LevelAdmin):
    def has_module_permission(self, request):
        return False


class SubCategoryForm(forms.ModelForm):

    category = forms.ModelChoiceField(
        queryset=Category.objects_for_admin.all(), widget=autocomplete.Select2(url='category-autocomplete')
    )

    class Meta:
        model = SubCategory
        fields = ('id', 'title', 'category', 'order')


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    fk_name = 'category'
    extra = 0
    fields = ('title', 'type', 'order')


class CategoryResource(ModelResource):
    subcategories = Field(column_name='Subcategories')
    level_title = Field(column_name='Level')

    def dehydrate_level_title(self, obj):
        return obj.level.title

    def dehydrate_subcategories(self, obj):
        return ", ".join(obj.subcategories.values_list('title', flat=True))

    class Meta:
        model = Category
        fields = ('id', 'title', 'level_title', 'subcategories', 'order')
        export_order = fields


class TranslatedCategoryInLine(TabularInline):
    model = TranslatedCategory
    extra = 0


class CategoryForm(forms.ModelForm):
    level = forms.ModelChoiceField(
        queryset=Level.objects_for_admin.all(), widget=autocomplete.Select2(url='level-autocomplete')
    )

    class Meta:
        model = Category
        fields = ('level', 'title', 'type', 'order')


class CategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = CategoryResource
    form = CategoryForm
    inlines = [SubCategoryInline, TranslatedCategoryInLine]
    list_display = ('title', 'level', 'type', 'order')
    search_fields = ('title', 'level__title')
    autocomplete_fields = ('level',)
    list_filter = (
        LevelFilterForCategory,
        'type'
    )

    def get_ordering(self, request):
        return ['order']

    def get_queryset(self, request):
        return Category.objects_for_admin.all()

    def get_search_results(self, request, queryset, search_term):
        result_queryset, has_duplicates = super().get_search_results(request, queryset, search_term)
        return result_queryset, has_duplicates


class HiddenCategoryAdmin(CategoryAdmin):
    def has_module_permission(self, request):
        return False


class HourRangeInLine(nested.NestedTabularInline):
    model = HourRange

    def get_extra(self, request, obj=None, **kwargs):
        extra = 1
        if obj and obj.id:
            extra = 0
        return extra


class SpecialHourRageInline(HourRangeInLine):
    model = SpecialHourRange


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('day', 'site')
    search_fields = ('day', 'site__title')
    list_filter = ('day',)
    inlines = [
        HourRangeInLine,
    ]


class ScheduleInLineForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(ScheduleInLineForm, self).__init__(*args, **kwargs)
        try:
            index = int(self.prefix.strip('schedules-'))
            self.fields['day'] = forms.ChoiceField(choices=Day.choices, initial=Day.choices[index])
        except Exception as e:
            print(e)


class ScheduleInLine(nested.NestedStackedInline):
    model = Schedule
    form = ScheduleInLineForm
    inlines = [
        HourRangeInLine,
    ]

    def get_extra(self, request, obj=None, **kwargs):
        extra = 7
        if obj:
            extra = 0
        return extra


class SpecialScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'site',
        'day',
    )
    search_fields = ('site__title', 'day', 'opening_hours__initial_hour', 'opening_hours__end_hour')
    list_filter = ('day',)


class SpecialScheduleInLine(nested.NestedTabularInline):
    model = SpecialSchedule
    extra = 0
    inlines = [
        SpecialHourRageInline,
    ]


class SiteImageInLine(nested.NestedTabularInline):
    model = SiteImage
    extra = 1


class SubCategoryResource(ModelResource):
    class Meta:
        model = SubCategory
        fields = ('id', 'title', 'category__id', 'category__title', 'category__level__id', 'category__level__title', 'order')


class TranslatedSubCategoryInLine(TabularInline):
    model = TranslatedSubCategory
    extra = 0


class CategorySearchFilter(AutocompleteFilter):
    title = _('Category')
    field_name = 'category'
    autocomplete_url = 'category-autocomplete'
    forwards = (
        forward.Field('level__id__exact', 'level'),
    )

    def get_queryset_for_field(self, model, name):
        return Category.objects_for_admin.all()


class SubCategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    form = SubCategoryForm
    resource_class = SubCategoryResource
    search_fields = ('title', 'category__title', 'category__level__title')
    list_display = ('title', 'category', 'type', 'order')
    list_filter = (
        CategorySearchFilter,
        'type'
    )
    autocomplete_fields = ('category',)
    inlines = [
        TranslatedSubCategoryInLine,
    ]

    def get_ordering(self, request):
        return ['order']

    def get_queryset(self, request):
        return SubCategory.objects_for_admin.all()

    def get_search_results(self, request, queryset, search_term):
        result_queryset, has_duplicates = super(SubCategoryAdmin, self).get_search_results(
            request, queryset, search_term
        )
        return result_queryset, has_duplicates


class HiddenSubcategoryAdmin(SubCategoryAdmin):
    def has_module_permission(self, request):
        return False


class CityFilter(AutocompleteFilter):
    title = _('City')
    field_name = 'city'
    autocomplete_url = 'city-autocomplete'
    forwards = (
        forward.Field('city__name', 'city'),
    )

    def get_queryset_for_field(self, model, name):
        return City.objects.all()


class CategoryFilter(AutocompleteFilter):
    title = _('Category')
    field_name = 'categories'
    autocomplete_url = 'category-autocomplete'
    forwards = (
        forward.Field('levels__id__exact', 'levels'),
    )

    def get_queryset_for_field(self, model, name):
        return Category.objects_for_admin.all()


class SubCategoryFilter(AutocompleteFilter):
    title = _('Subcategory')
    field_name = 'subcategories'
    autocomplete_url = 'subcategory-autocomplete'
    forwards = (
        forward.Field('categories__id__exact', 'categories'),
    )

    def get_queryset_for_field(self, model, name):
        return SubCategory.objects_for_admin.all()


class SiteForm(forms.ModelForm):
    media = forms.FileField(required=False, validators=[video_size])

    def __init__(self, *args, **kwargs):
        super(SiteForm, self).__init__(*args, **kwargs)
        #self.fields['levels'].queryset = Level.objects_for_admin.all()
        #self.fields['categories'].queryset = Category.objects_for_admin.all()
        #self.fields['subcategories'].queryset = SubCategory.objects_for_admin.all()



    def clean(self):
        categories = self.cleaned_data.get('categories')
        subcategories = self.cleaned_data.get('subcategories')

        for level in self.cleaned_data.get('levels', []):
            if categories and level.id not in categories.values_list('level', flat=True):
                raise forms.ValidationError({'categories': _('The selected categories must be part of the level')})
            if subcategories:
                for subcategory in subcategories:
                    if subcategory.category not in categories:
                        raise forms.ValidationError(
                            {'subcategories': _('The selected subcategories must be part of a selected category')}
                        )

        return super(SiteForm, self).clean()

    class Meta:
        model = Site
        fields = '__all__'


class PlaceForm(SiteForm):
    levels = forms.ModelMultipleChoiceField(
        queryset=Level.objects_for_admin.filter(type='place'),
        widget=autocomplete.ModelSelect2Multiple(),
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects_for_admin.filter(type='place'),
        required=True,
        widget=autocomplete.ModelSelect2Multiple(
            url='category-autocomplete',
            forward=('levels',)
        )
    )
    subcategories = forms.ModelMultipleChoiceField(
        queryset=SubCategory.objects_for_admin.filter(type='place'),
        required=False,
        widget=autocomplete.ModelSelect2Multiple(
            url='subcategory-autocomplete',
            forward=('categories',)
        )
    )

    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)
        self.fields['levels'].queryset = Level.objects_for_admin.filter(type='place')
        self.fields['categories'].queryset = Category.objects_for_admin.filter(type='place')
        self.fields['subcategories'].queryset = SubCategory.objects_for_admin.filter(type='place')


class SiteResource(ModelResource):
    tags = fields.Field(column_name='tags', attribute='tags', widget=ManyToManyWidget(Tag))

    levels = fields.Field(column_name='levels', attribute='levels', widget=ManyToManyWidget(Level))

    categories = fields.Field(column_name='categories', attribute='categories', widget=ManyToManyWidget(Category))

    subcategories = fields.Field(
        column_name='subcategories', attribute='subcategories', widget=ManyToManyWidget(SubCategory)
    )

    formatted_schedules = fields.Field(column_name='formatted_schedules')

    class Meta:
        model = Site
        fields = (
            'id',
            'title',
            'city',
            'address',
            'tags',
            'levels',
            'categories',
            'subcategories',
            'description',
            'type',
            'is_suggested',
            'always_open',
            'url',
            'phone',
            # 'translation_title',
            # 'translation_description',
            'formatted_schedules',
        )
        export_order = fields
        import_id_fields = ('id',)

    def dehydrate_formatted_schedules(self, site):
        schedules = []
        for schedule in site.schedules.all():
            text = f'{schedule.day.lower()},'
            for hours in schedule.opening_hours.all():
                text += (
                    f'{hours.initial_hour.strftime(format="%I:%M %p")} to {hours.end_hour.strftime(format="%I:%M %p")}'
                )
            schedules.append(f'{text}')
        return ";".join(schedules)

    # def dehydrate_translation_title(self, site):
    #     if site.translations.filter(language__code='en').exists():
    #         return site.translations.get(language__code='en').title
    #     else:
    #         return ''
    #
    # def dehydrate_translation_description(self, site):
    #     if site.translations.filter(language__code='en').exists():
    #         return site.translations.get(language__code='en').description
    #     else:
    #         return ''


class TranslatedSiteInLine(nested.NestedTabularInline):
    model = TranslatedSite
    extra = 0


class SiteAdmin(ImportExportModelAdmin, nested.NestedModelAdmin):
    form = SiteForm
    resource_class = SiteResource

    def get_queryset(self, request):
        sites = Site.objects_for_admin.all().annotate(num_of_favs=Count('users'), num_of_travels=Count('travels'))
        try:
            ambassador = Ambassador.objects.get(id=request.user.id)
            sites = sites.filter(city__id__in=ambassador.cities.values_list('id', flat=True))
        except Ambassador.DoesNotExist:
            pass
        return sites

    def num_of_favs(self, obj):
        return FavoriteSites.objects.filter(site__id=obj.id).count()

    num_of_favs.admin_order_field = 'num_of_favs'

    def num_of_travels(self, obj):
        return obj.num_of_travels

    num_of_travels.admin_order_field = 'num_of_travels'

    list_per_page = 50

    list_display = ('title', 'type', 'num_of_favs', 'num_of_travels', 'has_been_accepted')
    filter_horizontal = ('levels', 'categories', 'subcategories', 'tags')

    list_filter = (
        'has_been_accepted',
        #('city', RelatedDropdownFilter),
        CityFilter,
        LevelFilter,
        #('categories', MultiSelectRelatedDropdownFilter),
        CategoryFilter,
        SubCategoryFilter,
    )
    search_fields = (
        'title',
        'city__country__name',
    )
    autocomplete_fields = (
        'levels',
        #'categories',
        #'subcategories',
        'city',
        'address',
    )
    readonly_fields = ('created_by',)

    inlines = [ScheduleInLine, SpecialScheduleInLine, SiteImageInLine, TranslatedSiteInLine]

    def save_model(self, request, obj, form, change):
        if request.user.id in Ambassador.objects.all().values_list('id', flat=True):
            obj.created_by = request.user
        return super(SiteAdmin, self).save_model(request, obj, form, change)

    def process_dataset(self, dataset, confirm_form, request, *args, rollback_on_validation_errors=False, **kwargs):
        dataset.headers.pop()

        result = super(SiteAdmin, self).process_dataset(
            dataset, confirm_form, request, *args, rollback_on_validation_errors=False, **kwargs
        )
        for i, data_row in enumerate(dataset, 1):
            site = Site.objects.get(id=data_row[0])
            schedules = data_row[-1]
            if schedules is None:
                continue
            schedules_by_day = schedules.split(';')
            for schedule in schedules_by_day:
                print(schedule)
                try:
                    day, hours = schedule.split(',')

                    try:
                        schedule_db, created = Schedule.objects.get_or_create(day=day, site=site)
                    except Schedule.MultipleObjectsReturned:
                        schedule_db = Schedule.objects.filter(day=day, site=site).first()
                    hours = hours.split(' to ')
                    print(hours)
                    initial_datetime_in_hhmm = datetime.strptime(hours[0], "%I:%M %p")
                    end_datetime_in_hhmm = datetime.strptime(hours[1], "%I:%M %p")
                    print(initial_datetime_in_hhmm)
                    print(end_datetime_in_hhmm)
                    HourRange.objects.get_or_create(
                        initial_hour=initial_datetime_in_hhmm, end_hour=end_datetime_in_hhmm, schedule=schedule_db
                    )
                except BaseException as e:
                    print(e)
                    continue

        return result


class TranslatedSiteResource(ModelResource):
    class Meta:
        model = TranslatedSite
        fields = ('id', 'site', 'language', 'title', 'description')


class TranslatedSiteAdmin(ImportExportModelAdmin):
    resource_class = TranslatedSiteResource

    list_display = ('id', 'site', 'language', 'title')

    list_filter = (
        'site__type',
        'site__has_been_accepted',
        ('site__city', RelatedDropdownFilter),

        'language'
    )
    search_fields = (
        'site__title',
        'site__city__name',
        'site__city__country__name',
        'site__categories__title',
        'site__subcategories__title',
    )


class PlaceLevelFilter(LevelFilter):
    autocomplete_url = 'place-level-autocomplete'
    def get_queryset_for_field(self, model, name):
        return Level.objects_for_admin.filter(type='place')


class PlaceAdmin(SiteAdmin):
    form = PlaceForm

    readonly_fields = (
        'created_by',
        'frequency',
    )

    list_filter = (
        'has_been_accepted',
        # ('city', RelatedDropdownFilter),
        CityFilter,
        PlaceLevelFilter,
        # ('categories', MultiSelectRelatedDropdownFilter),
        CategoryFilter,
        SubCategoryFilter,
    )

    def get_queryset(self, request):
        return super(PlaceAdmin, self).get_queryset(request).filter(type='place')


class FavoriteSiteAdmin(admin.ModelAdmin):
    list_display = ('user', 'site')
    search_fields = ('user__username', 'site__title')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'site', 'rating')
    search_fields = ('user__username', 'site__title', 'site__city__name')


admin_site.register(Site, PlaceAdmin)
admin_site.register(TranslatedSite, TranslatedSiteAdmin)
admin_site.register(Category, HiddenCategoryAdmin)
admin_site.register(SubCategory, HiddenSubcategoryAdmin)
admin_site.register(Level, HiddenLevelAdmin)
