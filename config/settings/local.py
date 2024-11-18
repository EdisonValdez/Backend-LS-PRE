from .base import *  # noqa

ENVIRONMENT = 'local'
INSTALLED_APPS += ['django_extensions']

# Custom logging flags
DATABASE_LOGS = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += ('rest_framework.renderers.BrowsableAPIRenderer',)

if DATABASE_LOGS:
    LOGGING['loggers']['django.db'] = {
        'level': 'DEBUG',
        'propagate': True,
        'handlers': ['console'],
    }

SHOW_DJDT = False
SECURE_SSL_REDIRECT = False
