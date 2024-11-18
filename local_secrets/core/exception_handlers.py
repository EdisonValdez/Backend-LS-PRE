from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler as default_exception_handler

from local_secrets.core.custom_exceptions import CustomApiException


def exception_handler(exception, context):
    response_status = status.HTTP_400_BAD_REQUEST
    language = translation.get_language()
    with translation.override(language):
        if isinstance(exception, APIException):
            payload = {
                'error': 'An error ocurred',
            }

            if (
                isinstance(exception, PermissionDenied)
                or isinstance(exception, NotAuthenticated)
                or isinstance(exception, AuthenticationFailed)
            ):
                payload['error'] = 'invalid_grant'
                response_status = status.HTTP_401_UNAUTHORIZED
                if payload.get('error_description'):
                    payload['detail'] = payload.pop('error_description')

            if type(exception) == CustomApiException:
                payload['detail'] = exception.detail
                response_status = exception.status_code
            elif type(exception) == ValidationError:
                if type(exception.detail) == list:
                    payload['detail'] = ", ".join(exception.detail)
                else:
                    error_fields = ", ".join(list(exception.detail.keys()))
                    payload['detail'] = _('The fields ') + error_fields + _(' are required')
            else:
                if settings.DEBUG or settings.ENVIRONMENT == 'test':
                    payload['detail'] = exception.detail if isinstance(exception.detail, dict) else str(exception)
        else:
            return default_exception_handler(exception, context)
        return Response(data=payload, status=response_status)
