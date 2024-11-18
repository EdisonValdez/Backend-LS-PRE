import json
import stat
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import mock_open, patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from ..management.commands.create_superuser import Command as CreateSuperUserCommand
from ..management.commands.install_docker_cloud import Command
from ..management.commands.seed_database import Command as SeedDatabaseCommand
from ..management.seeders import seeding


class TestCustomCommands(TestCase):
    def setUp(self):
        super(TestCustomCommands, self).setUp()
        # Supressing commands print output
        sys.stdout = StringIO()

    def tearDown(self):
        # Turning back output change
        sys.stdout = sys.__stdout__

    @patch('builtins.input')
    def test_create_superuser(self, input_mock):
        input_mock.side_effect = (False, 'y')
        call_command('create_superuser')
        self.assertTrue(get_user_model().objects.filter(username=CreateSuperUserCommand.ADMIN_USERNAME).exists())
        call_command('create_superuser')
        self.assertTrue(get_user_model().objects.filter(username=CreateSuperUserCommand.ADMIN_USERNAME).exists())
        call_command('create_superuser')
        self.assertTrue(get_user_model().objects.filter(username=CreateSuperUserCommand.ADMIN_USERNAME).exists())

    @patch('os.chmod')
    @patch.object(Command, 'get_os_stat')
    @patch('builtins.open')
    @patch('shutil.copy')
    @patch.object(Path, 'exists')
    def test_install_docker_cloud(self, path_exists_mock, copy_mock, open_mock, stat_mock, chmod_mock):
        path_exists_mock.return_value = False
        copy_mock.return_value = None
        open_mock.new_callable = mock_open()
        stat_mock.return_value = stat.S_IEXEC
        chmod_mock.return_value = None
        result = call_command('install_docker_cloud')
        self.assertIsNone(result)

    @patch.object(Path, 'exists')
    def test_install_docker_cloud_installed(self, path_exists_mock):
        path_exists_mock.return_value = True
        result = call_command('install_docker_cloud')
        self.assertIsNone(result)

    @patch('os.stat')
    def test_get_os_stat(self, stat_mock):
        stat_mock.return_value.st_mode = 1
        command = Command()

        result = command.get_os_stat()

        self.assertEqual(result, 65)

    def test_print_random_user(self):
        result = call_command('print_random_user')
        self.assertIsNone(result)

    def test_seed_database(self):
        result = call_command('seed_database')
        expected_result = {field: True for field in SeedDatabaseCommand.inspect_seeders().keys()}
        self.assertDictEqual(json.loads(result), expected_result)
        rerun_result = call_command('seed_database')
        rerun_expected_result = {field: False for field in SeedDatabaseCommand.inspect_seeders().keys()}
        self.assertDictEqual(json.loads(rerun_result), rerun_expected_result)

    def test_seed_database_abstract(self):
        with self.assertRaises(NotImplementedError):
            # noinspection PyAbstractClass
            class AbstractSeeder(seeding.Seeder):
                enabled = True

            setattr(seeding, 'AbstractSeeder', AbstractSeeder)
            call_command('seed_database')
