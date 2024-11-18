import csv
import io

from local_secrets.languages.choices import FieldType


def duplicate_translated_fields():
    from local_secrets.routes.models import Route
    from local_secrets.users.models import Tag

    for tag in Tag.objects.all():
        tag.title_es = tag.title
        tag.title_en = tag.title
        tag.save()
    for route in Route.objects.all():
        route.title_es = route.title
        route.title_en = route.title
        route.save()


def generate_translations_from_models(queryset, type, language, field):
    from local_secrets.languages.models import TranslatedField

    for element in queryset:
        translated_field, created = TranslatedField.objects.get_or_create(
            fk=element.id, field=field, type=type, language=language
        )

        try:
            translated_field.translation = f'EN_{getattr(element, field)}'
            translated_field.save()
        except BaseException as e:
            print(e)
            continue


def generate_translated_models(file, language='ES'):
    from local_secrets.languages.models import TranslatedField
    from local_secrets.sites.models import Site

    file_r = file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(file_r))
    data = [line for line in reader]

    for element in data:
        type = element.get('type')
        object = None
        if type == 'site':
            try:
                object = Site.objects.get(id=element.get('id'))
            except BaseException:
                continue
        elif type == 'country':
            try:
                object = Site.objects.get(id=element.get('id'))
            except BaseException:
                continue

        if not object:
            continue

        for field in FieldType.choices:
            translated_field, created = TranslatedField.objects.get_or_create(
                fk=object.id, field=field, type=type, language=language
            )
            translated_field.translation = element.get(field, '')
            translated_field.save()


def find_translation(fk, field, language, type='site'):
    from local_secrets.languages.models import TranslatedField

    return TranslatedField.objects.get(fk=fk, field=field, language__code=language, type=type).translation
