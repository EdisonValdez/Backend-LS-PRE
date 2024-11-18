from .base import *  # noqa

ENVIRONMENT = 'dev'
INSTALLED_APPS += ['django_extensions']

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += ('rest_framework.renderers.BrowsableAPIRenderer',)

SHOW_DJDT = False
