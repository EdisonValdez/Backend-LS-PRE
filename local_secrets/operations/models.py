from django.db import models
from django.utils.translation import gettext_lazy as _

from local_secrets.languages.models import Language
from local_secrets.sites.models import (
    Comment,
    DefaultImage,
    FavoriteSites,
    HourRange,
    ImageSize,
    Schedule,
    SpecialSchedule,
    VideoSize,
)


class FavoriteSitesForAdmin(FavoriteSites):
    class Meta:
        proxy = True

        verbose_name = _('Favorite Site')
        verbose_name_plural = _('Favorite Sites')


class ScheduleForAdmin(Schedule):
    class Meta:
        proxy = True
        verbose_name = _('Schedule')
        verbose_name_plural = _('Schedules')


class HourRangeForAdmin(HourRange):
    class Meta:
        proxy = True
        verbose_name = _('Hour Range')
        verbose_name_plural = _('Hour Ranges')


class SpecialScheduleForAdmin(SpecialSchedule):
    class Meta:
        proxy = True
        verbose_name = _('Special Schedule')
        verbose_name_plural = _('Special Schedules')


class CommentForAdmin(Comment):
    class Meta:
        proxy = True
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')


class DefaultImageForAdmin(DefaultImage):
    class Meta:
        proxy = True
        verbose_name = _('Default Image')
        verbose_name_plural = _('Default Images')


class ImageSizeForAdmin(ImageSize):
    class Meta:
        proxy = True
        verbose_name = _('Image Size')
        verbose_name_plural = _('Image Sizes')


class VideoSizeForAdmin(VideoSize):
    class Meta:
        proxy = True

        verbose_name = _('Video Size')
        verbose_name_plural = _('Video Sizes')


class DefaultText(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()

    def __str__(self):
        return self.title

    def display_text(self, field, language='en'):
        try:
            return getattr(self.translations.get(language__code=language), field)
        except BaseException:
            return getattr(self, field)


class TranslatedDefaultText(models.Model):
    defautl_text = models.ForeignKey(DefaultText, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    text = models.TextField(verbose_name=_('Translated Text'))


class PrivacyPolicies(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Privacy Policy')
        verbose_name_plural = _('Privacy Policies')
