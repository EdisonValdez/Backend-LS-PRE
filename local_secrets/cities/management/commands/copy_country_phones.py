from django.core.management.base import BaseCommand

from local_secrets.cities.models import Country, PhoneCode, TranslatedPhoneCode


class Command(BaseCommand):
    help = 'Creates Phone codes from the countries on the database'

    def handle(self, *args, **options):
        for country in Country.objects.all():
            phone_code, created = PhoneCode.objects.get_or_create(code=country.code)
            phone_code.phone_code = country.phone_code
            phone_code.name = country.name
            phone_code.save()

            for translation in country.translations.all():
                phone_code_translation, created = TranslatedPhoneCode.objects.get_or_create(
                    language=translation.language, phone_code=phone_code, name=translation.name
                )

        return
