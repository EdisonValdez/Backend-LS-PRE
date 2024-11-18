import csv

from django.contrib.admin import ModelAdmin
from django.db.models import ManyToManyRel, ManyToOneRel
from django.db.models.fields.related import ManyToManyField
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response

from local_secrets.core.utils.text import TextHelper


class ExportCsvMixin(ModelAdmin):
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        # noinspection PyProtectedMember
        _meta = self.model._meta
        meta_fields = _meta.get_fields()

        def get_names(field_elem):
            """Get field names. Special case where ManyToOneRel does not have a verbose_name"""
            return (
                field_elem.field.verbose_name
                if isinstance(field_elem, ManyToOneRel) or isinstance(field_elem, ManyToManyRel)
                else field_elem.verbose_name
            ).capitalize()

        field_names = map(get_names, meta_fields)

        response = Response(content_type='text/csv')
        file_name = TextHelper.normalize_str_file_path(str(_meta))
        response['Content-Disposition'] = f"attachment; filename={file_name}.csv"
        response['Content-Type'] = 'text/csv'
        writer = csv.writer(response)

        # Write header
        writer.writerow(field_names)

        # Write content
        for obj in queryset:
            values = []

            for field_obj in meta_fields:
                value = getattr(obj, field_obj.name) if hasattr(obj, field_obj.name) else None
                if value and isinstance(field_obj, (ManyToManyField, ManyToOneRel)):
                    value = [str(x) for x in value.all()]
                values.append(value)

            writer.writerow(values)

        return response

    export_as_csv.short_description = _("Export selected as CSV")
