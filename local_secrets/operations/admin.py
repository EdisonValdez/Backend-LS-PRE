from django.contrib import admin

from local_secrets.sites.admin import CommentAdmin, FavoriteSiteAdmin, ScheduleAdmin, SpecialScheduleAdmin
from .models import (
    CommentForAdmin,
    DefaultImageForAdmin,
    DefaultText,
    FavoriteSitesForAdmin,
    ImageSizeForAdmin,
    PrivacyPolicies,
    ScheduleForAdmin,
    SpecialScheduleForAdmin,
    TranslatedDefaultText,
    VideoSizeForAdmin,
)
from ..core.admin import admin_site


class TranslatedDefaultTextInLine(admin.TabularInline):
    model = TranslatedDefaultText
    extra = 0


class DefaultTextAdmin(admin.ModelAdmin):
    inlines = [
        TranslatedDefaultTextInLine,
    ]


admin_site.register(ScheduleForAdmin, ScheduleAdmin)
admin_site.register(FavoriteSitesForAdmin, FavoriteSiteAdmin)
admin_site.register(SpecialScheduleForAdmin, SpecialScheduleAdmin)
admin_site.register(ImageSizeForAdmin)
admin_site.register(VideoSizeForAdmin)
admin_site.register(CommentForAdmin, CommentAdmin)
admin_site.register(DefaultImageForAdmin)
admin_site.register(DefaultText, DefaultTextAdmin)
admin_site.register(PrivacyPolicies)
