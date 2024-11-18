from django.db import models


class SiteType(models.TextChoices):
    PLACE = 'place', 'Place'
    EVENT = 'event', 'Event'


class Day(models.TextChoices):
    MONDAY = 'monday', 'Monday'
    TUESDAY = 'tuesday', 'Tuesday'
    WEDNESDAY = 'wednesday', 'Wednesday'
    THURSDAY = 'thursday', 'Thursday'
    FRIDAY = 'friday', 'Friday'
    SATURDAY = 'saturday', 'Saturday'
    SUNDAY = 'sunday', 'Sunday'


class FrequencyChoices(models.TextChoices):
    NEVER = 'never', 'Does not repeat (Uses schedules)'
    DAY = 'day', 'Every day'
    WEEK = 'week', 'Every week'
    # MONTH = 'month', 'Every month'
    YEAR = 'year', 'Every year'
    WORKDAY = 'workday', 'Every working day'
