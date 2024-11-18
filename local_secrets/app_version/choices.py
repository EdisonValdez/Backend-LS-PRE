from django.db import models


class AppPlatform(models.TextChoices):
    IOS = 'ios', 'iOS'
    ANDROID = 'android', 'Android'

    @classmethod
    def values_dict(cls):
        # noinspection PyUnresolvedReferences
        return {platform.value: platform for platform in cls}

    @classmethod
    def from_value(cls, value: str):
        return cls.values_dict().get(value, None)
