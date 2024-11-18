from django.db import models


class TravelType(models.TextChoices):
    SOLO = 'solo', 'Solo'
    FAMILIAR = 'familiar', 'Familiar'
    BUSINESS = 'business', 'Business'
    ROMANTIC = 'romantic', 'Romantic'
    GROUP = 'group', 'Group'
