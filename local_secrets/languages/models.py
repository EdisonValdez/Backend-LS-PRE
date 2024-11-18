from django.db import models
from django.utils.translation import gettext_lazy as _

from local_secrets.core.utils.translations import generate_translated_models
from local_secrets.languages.choices import FieldType, TranslationPlatform


class Language(models.Model):
    code = models.CharField(max_length=10, verbose_name=_('Code'))
    name = models.CharField(max_length=100, verbose_name=_('Name'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')

    def display_text(self, field, language='en'):
        value = None
        try:
            value = getattr(self.translations.get(language__code=language), field)
        except BaseException:
            value = getattr(self, field)
        if value is None:
            return getattr(self, field)
        return value


class TranslatedLanguage(models.Model):
    language_from = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    name = models.CharField(max_length=500, null=False, blank=False, verbose_name=_('Translated Title'))


class Translation(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, verbose_name=_('Language'))
    platform = models.CharField(max_length=100, choices=TranslationPlatform.choices)
    translation = models.FileField(verbose_name=_('Translation'))

    def save(self, *args, **kwargs):
        generate_translated_models(self.translation.file, self)
        return super(Translation, self).save(*args, **kwargs)


class TranslatedField(models.Model):
    fk = models.IntegerField()
    type = models.CharField(max_length=100)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, verbose_name=_('Language'))
    field = models.CharField(max_length=100, choices=FieldType.choices)
    translation = models.CharField(max_length=5000, default='')
