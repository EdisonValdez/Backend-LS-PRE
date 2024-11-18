from .development import *  # noqa

ENVIRONMENT = 'test'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': BASE_DIR.joinpath('db.spatialite'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

LOGGING['loggers']['local_secrets'] = {
    'level': 'ERROR',
    'propagate': True,
    'handlers': ['console'],
}

# Deactivating SSL redirect spares having a redirection in each request
SECURE_SSL_REDIRECT = False
