import decimal

from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField

from local_secrets.languages.models import Language


class PhoneCode(models.Model):
    name = models.CharField(max_length=500, verbose_name=_('Name'))

    code = models.CharField(max_length=3, verbose_name=_('ISO Code'))
    phone_code = models.CharField(max_length=10, default=34, verbose_name=_('Phone code'))

    class Meta:
        verbose_name = _('Phone Code')
        verbose_name_plural = _('Phone Code')

    def __str__(self):
        return f'{self.name} - {self.code}'

    def display_text(self, field, language='en'):
        try:
            return getattr(self.translations.get(language__code=language), field)
        except BaseException:
            return getattr(self, field)


class TranslatedPhoneCode(models.Model):
    phone_code = models.ForeignKey(PhoneCode, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    name = models.CharField(max_length=500, verbose_name=_('Translated Name'))


class Country(models.Model):
    name = models.CharField(max_length=500, verbose_name=_('Name'))

    code = models.CharField(max_length=3, verbose_name=_('ISO Code'))
    phone_code = models.CharField(max_length=10, default=34, verbose_name=_('Phone code'))

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

    def __str__(self):
        return f'{self.name} - {self.code}'

    def display_text(self, field, language='en'):
        try:
            return getattr(self.translations.get(language__code=language), field)
        except BaseException:
            return getattr(self, field)


class TranslatedCountry(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    name = models.CharField(max_length=500, verbose_name=_('Translated Name'))


class City(models.Model):
    name = models.CharField(max_length=500, verbose_name=_('Name'))

    cp = models.CharField(max_length=12, verbose_name=_('CP'))

    province = models.CharField(max_length=100, verbose_name=_('Province'))

    point = PointField(blank=True, verbose_name=_('Geolocation'))

    description = models.TextField(verbose_name=_('Description'))

    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name=_('Country'))

    slogan = models.CharField(max_length=100, verbose_name=_('Slogan'))

    link = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Link'))
    media = models.FileField(
        upload_to='site_videos',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'webm', 'mkv'])],
        verbose_name=_('Video'),
    )
    latitude = models.DecimalField(max_digits=30, blank=True, decimal_places=27, default=0, verbose_name=_('Latitude'))
    longitude = models.DecimalField(
        max_digits=30, blank=True, decimal_places=27, default=0, verbose_name=_('Longitude')
    )
    activated = models.BooleanField(default=True, verbose_name=_('Is active?'))

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
        ordering = [
            Lower('name'),
        ]

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        if self.point:
            self.longitude = self.point.coords[0]
            self.latitude = self.point.coords[1]
        if decimal.Decimal(self.longitude).is_zero():
            self.longitude = decimal.Decimal(0.0)
        if decimal.Decimal(self.latitude).is_zero():
            self.longitude = decimal.Decimal(0.0)
        self.point = Point((decimal.Decimal(self.longitude), decimal.Decimal(self.latitude)), srid=4326)
        return super(City, self).save(*args, **kwargs)

    def display_text(self, field, language='en'):
        try:
            return getattr(self.translations.get(language__code=language), field)
        except BaseException:
            return getattr(self, field)


class TranslatedCity(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    name = models.CharField(max_length=500, verbose_name=_('Name'))
    province = models.CharField(max_length=100, verbose_name=_('Province'))
    description = models.TextField(verbose_name=_('Description'))
    slogan = models.CharField(max_length=100, verbose_name=_('Slogan'))


class CityImage(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='images', verbose_name=_('City'))
    image = ThumbnailerImageField(upload_to='city_images', verbose_name=_('Image'))


class Address(models.Model):
    street = models.CharField(max_length=250, verbose_name=_('Street'))
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='addresses')
    cp = models.CharField(max_length=12, verbose_name=_('CP'))
    point = PointField(blank=True, verbose_name=_('Geolocation'))

    latitude = models.DecimalField(max_digits=30, blank=True, decimal_places=27, default=0, verbose_name=_('Latitude'))
    longitude = models.DecimalField(
        max_digits=30, blank=True, decimal_places=27, default=0, verbose_name=_('Longitude')
    )

    google_place_id = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('Google Place Id'))
    details = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('Details'))
    number = models.CharField(max_length=6, null=True, blank=True, verbose_name=_('Number'))
    door = models.CharField(max_length=6, null=True, blank=True, verbose_name=_('Door'))
    floor = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Floor'))
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def __str__(self):
        return f'{self.street}, {self.city.name}'

    def save(self, *args, **kwargs):
        if self.point:
            self.longitude = self.point.coords[0]
            self.latitude = self.point.coords[1]

        if not self.longitude or decimal.Decimal(self.longitude).is_zero():
            self.longitude = decimal.Decimal(0.0)

        if not self.latitude or decimal.Decimal(self.latitude).is_zero():
            self.latitude = decimal.Decimal(0.0)

        self.point = Point((decimal.Decimal(self.longitude), decimal.Decimal(self.latitude)), srid=4326)
        return super(Address, self).save(*args, **kwargs)

    def display_text(self, field, language='en'):
        field_title = f'{field}_{language}'
        try:
            return getattr(self, field_title)
        except BaseException:
            return getattr(self, field)
