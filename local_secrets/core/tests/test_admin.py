import re
from unittest.mock import patch

from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from requests import Request
from rest_framework import status

from .base_test_case import BaseTestCase
from ..admin import admin_site
from ..utils.custom_validators import phone_regex
from ...users.admin import CustomUserAdmin


class TestAdmin(BaseTestCase):
    def _get_request(self):
        request = Request()
        request.user = self.get_default_user()
        return request

    @patch.object(AdminSite, '_build_app_dict')
    def test_get_app_list(self, mock_build_app_dict):
        mock_build_app_dict.return_value = {
            'app_version': {'app_label': 'app_version'},
            'auth': {'app_label': 'auth'},
            'oauth2_provider': {'app_label': 'oauth2_provider'},
            'fake_app': {'app_label': 'fake_app'},
        }
        result = admin_site.get_app_list(request=self._get_request())
        self.assertTrue(type(result) == list)

    def test_csv_export(self):
        csv_admin = CustomUserAdmin(model=get_user_model(), admin_site=admin_site)
        req = self._get_request()
        response = csv_admin.export_as_csv(request=req, queryset=csv_admin.get_queryset(request=req))
        self.assertTrue(response.status_code, status.HTTP_200_OK)

    def test_regex_serializer(self):
        self.assertTrue(re.compile(phone_regex).match('+34666666666'))
