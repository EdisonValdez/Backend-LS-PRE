from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .base_test_case import BaseTestCase
from ..exception_handlers import exception_handler


class TestExceptionHandler(BaseTestCase):
    def test_api_exception(self):
        e = ValidationError()
        response = exception_handler(e, None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_exception(self):
        e = Http404
        response = exception_handler(e, None)
        self.assertIsNone(response)
