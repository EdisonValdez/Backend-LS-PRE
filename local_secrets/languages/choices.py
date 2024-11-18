from django.db import models


class TranslationPlatform(models.TextChoices):
    IOS = 'ios', 'iOS'
    ANDROID = 'android', 'Android'
    BACK = 'back', 'Back'


class FieldType(models.TextChoices):
    TITLE = 'title', 'Title'
    NAME = 'name', 'Name'
    DESCRIPTION = 'description', 'Description'
    TYPE = 'type', 'Type'
