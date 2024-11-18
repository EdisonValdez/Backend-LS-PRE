from django.core.validators import RegexValidator
from django.utils.translation import gettext as _

phone_regex = r'^\+?1?\d{9,15}$'
phone_validator = RegexValidator(regex=phone_regex, message=_("The phone must fit with format: '+999999999'"))
