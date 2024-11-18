from dal import autocomplete
from django import forms
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.utils.translation import gettext_lazy as _

from .models import Event, TranslatedEvent
from ..core.admin import admin_site
from ..sites.admin import SiteAdmin, TranslatedSiteAdmin, LevelAdmin, LevelFilter, CityFilter, CategoryFilter, \
    SubCategoryFilter
from ..sites.choices import SiteType
from ..sites.models import Level, Category, SubCategory
from ..sites.validators import video_size


class CustomAutocomplete(AutocompleteSelectMultiple):
    def get_context(self, name, value, attrs):
        context = super(CustomAutocomplete, self).get_context(name, value, attrs)
        context['is_event'] = True
        return context


class EventForm(forms.ModelForm):
    media = forms.FileField(required=False, validators=[video_size])
    type = forms.ChoiceField(choices=SiteType.choices, initial=SiteType.EVENT.value)
    levels = forms.ModelMultipleChoiceField(
        queryset=Level.objects.filter(type='event'),
        widget=autocomplete.ModelSelect2Multiple(),
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects_for_admin.filter(type='event'),
        required=True,
        widget=autocomplete.ModelSelect2Multiple(
            url='category-autocomplete',
            forward=('levels',)
        )
    )
    subcategories = forms.ModelMultipleChoiceField(
        queryset=SubCategory.objects_for_admin.filter(type='event'),
        required=False,
        widget=autocomplete.ModelSelect2Multiple(
            url='subcategory-autocomplete',
            forward=('categories',)
        )
    )


    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        #self.fields['levels'].queryset = Level.objects_for_admin.filter(type='event')
        #self.fields['categories'].queryset = Category.objects_for_admin.filter(type='event')
        #self.fields['subcategories'].queryset = SubCategory.objects_for_admin.filter(type='event')

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

        return super(EventForm, self).clean()

    class Meta:
        model = Event
        fields = '__all__'


class EventLevelFilter(LevelFilter):
    autocomplete_url = 'event-level-autocomplete'

    def get_queryset_for_field(self, model, name):
        return Level.objects_for_admin.filter(type='event')

class EventAdmin(SiteAdmin):
    form = EventForm

    list_filter = (
        'has_been_accepted',
        # ('city', RelatedDropdownFilter),
        CityFilter,
        EventLevelFilter,
        # ('categories', MultiSelectRelatedDropdownFilter),
        CategoryFilter,
        SubCategoryFilter,
    )

    def get_queryset(self, request):
        return super(EventAdmin, self).get_queryset(request).filter(type='event')


class TranslatedEventAdmin(TranslatedSiteAdmin):
    def get_queryset(self, request):
        return super(TranslatedEventAdmin, self).get_queryset(request).filter(site__type='event')


admin_site.register(Event, EventAdmin)
admin_site.register(TranslatedEvent, TranslatedEventAdmin)
