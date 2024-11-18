from unittest.mock import patch

import requests
from django.db import models
from django.http import HttpRequest
from django.template import RequestContext
from rest_framework.response import Response

from .base_test_case import BaseTestCase
from ..models import SoftDeletionModel
from ..serializers import DataSerializer, OutputSerializer
from ..storages import MediaStorage, StaticStorage
from ..templatetags import language_tags
from ...app_version.serializers import UpdateAppVersionSerializer


class TestStoragesBackends(BaseTestCase):
    def test_media_storage(self):
        backend = MediaStorage()
        self.assertTrue(backend)

    def test_static_storage(self):
        backend = StaticStorage()
        self.assertTrue(backend)


class TestGetMockedResponse(BaseTestCase):
    @patch('requests.get')
    def test_mocked_response(self, mock_get):
        expected_result = self.get_mocked_response('We make brutal apps!')
        mock_get.return_value = expected_result
        # This example may be in our django project code, but this is made as example
        response: Response = requests.get('https://www.rudo.es')
        self.assertEqual(expected_result.data, response.data)


class TestBaseOutputSerializer(BaseTestCase):
    def test_base_output_serializer(self):
        serializer = OutputSerializer({})
        serializer.create(None)
        serializer.update(None, None)

    def test_update_app_serializer_creation(self):
        serializer = UpdateAppVersionSerializer({})
        serializer.create(None)


class TestSoftDeleteModel(BaseTestCase):
    class DummySoftDeletableModel(SoftDeletionModel):
        title = models.CharField(max_length=10)

    def test_soft_deleted_model(self):
        self.DummySoftDeletableModel(title='empty').save()
        manager = self.DummySoftDeletableModel.objects
        unrestricted_manager = self.DummySoftDeletableModel.all_objects
        obj = manager.first()
        obj.delete()
        self.assertFalse(manager.exists())
        self.assertTrue(unrestricted_manager.exists())
        obj.hard_delete()
        self.assertFalse(unrestricted_manager.exists())

    def test_soft_delete_in_queryset(self):
        self.DummySoftDeletableModel(title='first').save()
        self.DummySoftDeletableModel(title='second').save()
        manager = self.DummySoftDeletableModel.objects
        unrestricted_manager = self.DummySoftDeletableModel.all_objects
        q1_s = manager.filter(title='first')
        q1_u = unrestricted_manager.filter(title='first')
        q1_s.delete()
        self.assertFalse(q1_s.exists())
        self.assertTrue(q1_u.exists())
        q2_s = manager.all()
        q2_u = unrestricted_manager.all()
        q2_s.hard_delete()
        self.assertFalse(q2_s.exists())
        self.assertEqual(q2_u.count(), 1)
        q3 = unrestricted_manager.all()
        self.assertTrue(q3.soft_deleted().count(), 1)
        q3.hard_delete()
        self.assertFalse(q3.exists())


class TestStuff(BaseTestCase):
    def test_language_template_tag(self):
        self.assertTrue(language_tags.get_languages())

    def test_localize_admin_template_tag(self):
        req = HttpRequest()
        req.path = '/admin/es'
        context = RequestContext(req)
        self.assertTrue(language_tags.get_localized_admin_url(context=context, lang='es'))

    def test_data_serializer(self):
        content = {'content': 'stuff'}
        expected_result = {'data': content}
        serializer = DataSerializer(content)
        self.assertTrue(serializer.data, expected_result)
