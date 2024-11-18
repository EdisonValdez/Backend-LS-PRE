import json
import logging
import os
import subprocess
import sys
from enum import Enum
from http.client import HTTPResponse
from pathlib import Path
from typing import Optional
from urllib import parse, request

from requests import Response
from rest_framework import status

logging.basicConfig(level=logging.NOTSET)


class Messages(Enum):
    AVAILABLE_ACTIONS = 'This script has the following actions:'
    CHOICE_DOWNLOAD_DESC = 'Perform a machines download if does not exists into local'
    CHOICE_LIST_DESC = 'Echoes a machines list saved into the cloud'
    CHOICE_SYNC_DESC = 'Perform a machines synchonization with the cloud'
    CHOICE_UPLOAD_DESC = 'Perform a machines upload if does not exists into the cloud'
    CLOUD_EXISTS_TXT = 'The given docker machine already exists into the cloud. Would you like to overwrite it?'
    CLOUD_NOT_EXISTS_TXT = 'The given docker machine does not exist into the cloud. Would you like to create it?'
    ERROR_CLOUD_DETAIL = 'There was an error requesting cloud machine detail ({machine_id_param})'
    ERROR_ENV_VAR_REQUIRED = 'Mandatory environment variable $TEAMCERTS_ACCESS_TOKEN not found'
    ERROR_GIVEN_ACTION = 'Specified option is not a valid choice'
    ERROR_LIST_CLOUD = 'There was an error requesting cloud machines list'
    ERROR_LIST_LOCAL = 'There was an error requesting local machines list'
    ERROR_MACHINE_DETAIL = 'There was an error requesting cloud machine detail'
    ERROR_MACHINE_NAME_REQUIRED = 'This action requires a machine name param to work'
    ERROR_MACHINE_NOT_AVAILABLE = 'Given machine name is not available to download'
    ERROR_SELECT_ACTION = 'Selected action is not a valid choice'
    ERROR_WRITING_FILES = 'There was an error writing machine files'
    GIVEN_MACHINE_NOT_FOUND = 'The given machine ({target_machine}) not found in local'
    INPUT_YES_NO = 'y/N\n'
    LOCAL_EXISTS_TXT = 'The given docker machine already exists into local. Would you like to overwrite it?'
    NO_ACTION_TAKEN = 'No action was taken'
    NO_DOWNLOAD_UPLOAD = "You don't have any machine to download nor upload"
    REQUIRED_FILE_NOT_FOUND = 'Docker machine required file not found'
    SELECT_ACTION = 'What action do you want to perform?'
    SELECT_ENV_FOR_ACTION = 'Which environment name do you want to {action}?'


class DockerMachineFile(Enum):
    CONFIG_FILE = 'config.json'
    PRIVATE_KEY = 'id_rsa'
    PUBLIC_KEY = 'id_rsa.pub'
    CA_CRT = 'ca.pem'
    CLIENT_CRT = 'cert.pem'
    CLIENT_KEY = 'key.pem'
    SERVER_CRT = 'server.pem'
    SERVER_KEY = 'server-key.pem'


class SyncWraper:
    logger = logging.getLogger(__name__)
    base_url = 'https://dashboard.rudo.es'
    list_create_machines_url = f'{base_url}/machines?flat=1'
    detail_machine_url = f'{base_url}/machines/' + '{machine_id}'
    local_machines_path = '.docker/machine/machines'
    local_machines_dir = Path.home().joinpath(local_machines_path)
    choices = {
        'list': {
            'desc': f'{Messages.CHOICE_LIST_DESC.value}',
            'method': 'list_cloud_machines',
        },
        'sync': {
            'desc': f'{Messages.CHOICE_SYNC_DESC.value}',
            'method': 'sync_machines',
        },
        'download': {
            'desc': f'{Messages.CHOICE_DOWNLOAD_DESC.value}',
            'method': 'download_machine',
        },
        'upload': {
            'desc': f'{Messages.CHOICE_UPLOAD_DESC.value}',
            'method': 'upload_machine',
        },
    }

    def main(self, argv):
        if self.is_auth_var_present():
            action = self.select_action(argv=argv)
            self.logger.info(f'Performing <{action}> action')
            success, result = getattr(self, self.choices[action]['method'])(argv=argv)
            log = self.logger.info if success else self.logger.error
            log(f'Success [{success}] - Result: {result}')
        else:
            self.logger.error(Messages.ERROR_ENV_VAR_REQUIRED.value)

    def select_action(self, argv):
        if len(argv) < 2 or argv[1] is None:
            self.logger.info(Messages.AVAILABLE_ACTIONS.value)
            [self.logger.info(f"<{action}>: {data['desc']}") for action, data in self.choices.items()]
            self.logger.info(Messages.SELECT_ACTION.value)
            rsp = input()
            if rsp not in self.choices:
                raise NotImplementedError(Messages.ERROR_SELECT_ACTION.value)
            argv.append(rsp)
            if argv[1] in ['download', 'upload']:
                self.logger.info(Messages.SELECT_ENV_FOR_ACTION.value.format(action=argv[1]))
                env_name = input()
                argv.append(env_name)
        action = argv[1]
        if action not in self.choices:
            raise NotImplementedError(Messages.ERROR_GIVEN_ACTION.value)
        return action

    # noinspection PyUnusedLocal
    def list_cloud_machines(self, argv=None) -> (bool, list):
        default_content = b'[]'
        status_ok = False
        try:
            self.logger.error(self.list_create_machines_url)
            req = request.Request(self.list_create_machines_url, headers=self.get_auth_headers())
            res: HTTPResponse = request.urlopen(req)
            contents = res.read()
            status_ok = res.status == status.HTTP_200_OK
        except Exception as e:
            self.logger.error(Messages.ERROR_LIST_CLOUD.value, exc_info=e)
            contents = default_content
        return contents != default_content or status_ok, json.loads(contents.decode('utf-8'))

    # noinspection PyUnusedLocal
    def sync_machines(self, argv=None) -> (bool, list):
        success, cloud_machines = self.list_cloud_machines()
        assert success is True, Messages.ERROR_LIST_CLOUD.value
        cloud_machines_dict = self.map_cloud_machines(machines_rsp=cloud_machines)
        success, local_machines = self.list_local_machines()
        assert success is True, Messages.ERROR_LIST_LOCAL.value
        arguments: list = argv.copy()
        arguments.append('machine-name')
        machines_to_download = [
            machine_name for machine_name in cloud_machines_dict.keys() if machine_name not in local_machines
        ]
        machines_to_upload = [
            machine_name for machine_name in local_machines if machine_name not in cloud_machines_dict
        ]
        success = True
        if not (len(machines_to_download) + len(machines_to_upload)):
            self.logger.info(Messages.NO_DOWNLOAD_UPLOAD.value)
            success = False
        else:
            for machine in machines_to_download:
                arguments[-1] = machine
                success, _ = self.download_machine(argv=arguments)
                success &= success
            for machine in machines_to_upload:
                arguments[-1] = machine
                success, _ = self.upload_machine(argv=arguments)
                success &= success
        return success, None

    def download_machine(self, argv=None) -> (bool, str):
        if len(argv) > 2 and argv[2] is not None:
            target_machine = argv[2]
            success, cloud_machines = self.list_cloud_machines()
            assert success is True, Messages.ERROR_LIST_CLOUD.value
            cloud_machines_dict = self.map_cloud_machines(machines_rsp=cloud_machines)
            machine_id = cloud_machines_dict[target_machine] if target_machine in cloud_machines_dict else None
            assert machine_id is not None, Messages.ERROR_MACHINE_NOT_AVAILABLE.value
            self.logger.info(f'Downloading <{target_machine}> docker machine')
            success, machine = self.get_machine_detail(machine_id=machine_id)
            assert success is True, Messages.ERROR_MACHINE_DETAIL.value
            success = self.save_machine(machine=machine)
            self.fix_certs_for_machine(machine.get('name'))
            return success, None
        else:
            self.logger.error(Messages.ERROR_MACHINE_NAME_REQUIRED.value)
            return False, None

    def upload_machine(self, argv=None):
        if len(argv) > 2 and argv[2] is not None:
            target_machine = argv[2]
            success, local_machines = self.list_local_machines()
            assert success is True, Messages.ERROR_LIST_LOCAL.value
            error_msg = Messages.GIVEN_MACHINE_NOT_FOUND.value.format(target_machine=target_machine)
            assert target_machine in local_machines, error_msg
            success, cloud_machines = self.list_cloud_machines()
            assert success is True, Messages.ERROR_LIST_CLOUD.value
            cloud_machines_dict = self.map_cloud_machines(machines_rsp=cloud_machines)
            self.logger.info(f'Uploading <{target_machine}> docker machine')
            success = False
            try:
                machine = self.get_local_machine(target_machine)
                fragment = '' if target_machine in cloud_machines_dict else 'NOT_'
                self.logger.info(Messages.__getitem__(f'CLOUD_{fragment}EXISTS_TXT').value)
                if input(Messages.INPUT_YES_NO.value) == 'y':
                    success = self.request_machine_upload(machine=machine)
                else:
                    self.logger.info(Messages.NO_ACTION_TAKEN.value)
            except FileNotFoundError as e:
                self.logger.error(Messages.REQUIRED_FILE_NOT_FOUND.value, exc_info=e)
            return success, None
        else:
            self.logger.error(Messages.ERROR_MACHINE_NAME_REQUIRED.value)
            return False, None

    # noinspection PyUnusedLocal
    def list_local_machines(self, argv=None) -> (bool, list):
        with self.local_machines_dir as machines_dir:
            success = machines_dir.is_dir() and machines_dir.exists()
            machines = self.clean_folders(directory=machines_dir)
        return success, machines

    def get_machine_detail(self, argv=None, machine_id: str = None, default_content=b'{}') -> (bool, dict):
        if argv and len(argv) > 2 and argv[2] is not None:
            contents = self.request_machine_detail(machine_id_param=argv[2], default_content=default_content)
        elif machine_id:
            contents = self.request_machine_detail(machine_id_param=machine_id, default_content=default_content)
        else:
            self.logger.error(Messages.ERROR_MACHINE_NAME_REQUIRED.value)
            contents = default_content
        return contents != default_content, json.loads(contents.decode('utf-8'))

    def request_machine_detail(self, machine_id_param, default_content):
        try:
            req = request.Request(
                self.detail_machine_url.format(machine_id=machine_id_param), headers=self.get_auth_headers()
            )
            contents = request.urlopen(req).read()
        except Exception as e:
            self.logger.error(Messages.ERROR_CLOUD_DETAIL.value.format(machine_id_param=machine_id_param), exc_info=e)
            contents = default_content
        return contents

    def get_local_machine(self, target_machine) -> dict:
        machine_dir = self.local_machines_dir.joinpath(target_machine)
        return {
            'name': target_machine,
            'config_file': self.read_file_content(
                machine_dir=machine_dir, file_path=DockerMachineFile.CONFIG_FILE.value
            ),
            'private_key': self.read_file_content(
                machine_dir=machine_dir, file_path=DockerMachineFile.PRIVATE_KEY.value
            ),
            'public_key': self.read_file_content(machine_dir=machine_dir, file_path=DockerMachineFile.PUBLIC_KEY.value),
            'ca_certificate': self.read_file_content(machine_dir=machine_dir, file_path=DockerMachineFile.CA_CRT.value),
            'client_certificate': self.read_file_content(
                machine_dir=machine_dir, file_path=DockerMachineFile.CLIENT_CRT.value
            ),
            'client_key': self.read_file_content(machine_dir=machine_dir, file_path=DockerMachineFile.CLIENT_KEY.value),
            'server_certificate': self.read_file_content(
                machine_dir=machine_dir, file_path=DockerMachineFile.SERVER_CRT.value
            ),
            'server_key': self.read_file_content(machine_dir=machine_dir, file_path=DockerMachineFile.SERVER_KEY.value),
        }

    def request_machine_upload(self, machine: dict) -> bool:
        response: Optional[HTTPResponse] = None
        try:
            data = parse.urlencode(machine).encode()
            req = request.Request(self.list_create_machines_url, data=data, headers=self.get_auth_headers())
            response = request.urlopen(req)
            status_code = response.status
        except Exception as e:
            self.logger.error(Messages.ERROR_LIST_CLOUD.value, exc_info=e)
            status_code = response.status if response and isinstance(response, Response) else 500
        self.logger.debug(f'POST Response Status Code: {status_code}')
        return status_code not in (status.HTTP_200_OK, status.HTTP_201_CREATED)

    def save_machine(self, machine: dict) -> bool:
        success = False
        machine_name = machine['name']
        with self.local_machines_dir as machines_dir:
            machine_path = machines_dir.joinpath(machine_name)
            if machine_path.exists():
                self.logger.info(Messages.LOCAL_EXISTS_TXT.value)
                if input(Messages.INPUT_YES_NO.value) == 'y':
                    success = self.save_machine_files(machine_dir=machine_path, machine=machine, overwrite=True)
                else:
                    self.logger.info(Messages.NO_ACTION_TAKEN.value)
            else:
                machine_path.mkdir()
                success = self.save_machine_files(machine_dir=machine_path, machine=machine)
        return success

    def save_machine_files(self, machine_dir: Path, machine: dict, overwrite: bool = False) -> bool:
        machine_config_file = machine['config_file']
        machine_priv_key = machine['private_key']
        machine_pub_key = machine['public_key']
        machine_ca_crt = machine['ca_certificate']
        machine_cli_crt = machine['client_certificate']
        machine_cli_key = machine['client_key']
        machine_srv_crt = machine['server_certificate']
        machine_srv_key = machine['server_key']
        mode = 'w' if overwrite else 'x'
        success = False
        docker_files = [
            {
                'file': self.get_docker_file(machine_dir=machine_dir, file=DockerMachineFile.CONFIG_FILE),
                'mode': mode,
                'content': machine_config_file,
            },
            {
                'file': self.get_docker_file(machine_dir=machine_dir, file=DockerMachineFile.PRIVATE_KEY),
                'mode': mode,
                'content': machine_priv_key,
                'chmod': True,
            },
            {
                'file': self.get_docker_file(machine_dir=machine_dir, file=DockerMachineFile.PUBLIC_KEY),
                'mode': mode,
                'content': machine_pub_key,
            },
            {
                'file': self.get_docker_file(machine_dir=machine_dir, file=DockerMachineFile.CA_CRT),
                'mode': mode,
                'content': machine_ca_crt,
            },
            {
                'file': self.get_docker_file(machine_dir=machine_dir, file=DockerMachineFile.CLIENT_CRT),
                'mode': mode,
                'content': machine_cli_crt,
            },
            {
                'file': self.get_docker_file(machine_dir=machine_dir, file=DockerMachineFile.CLIENT_KEY),
                'mode': mode,
                'content': machine_cli_key,
            },
            {
                'file': self.get_docker_file(machine_dir=machine_dir, file=DockerMachineFile.SERVER_CRT),
                'mode': mode,
                'content': machine_srv_crt,
            },
            {
                'file': self.get_docker_file(machine_dir=machine_dir, file=DockerMachineFile.SERVER_KEY),
                'mode': mode,
                'content': machine_srv_key,
            },
        ]
        try:
            written_files = [self.write_file_content(**file) for file in docker_files]
            success = len(written_files) == len(docker_files)
        except Exception as e:
            self.logger.error(Messages.ERROR_WRITING_FILES.value, exc_info=e)
        return success

    def fix_certs_for_machine(self, machine_name: str):
        self.logger.info(f'Configuring certificates of downloaded {machine_name} docker machine')
        subprocess.run(['docker-cloud', 'certs', machine_name, '--y'], stdout=subprocess.DEVNULL)

    @staticmethod
    def get_auth_headers() -> dict:
        return {'X-Api-Access-Token': os.environ.get('TEAMCERTS_ACCESS_TOKEN')}

    @staticmethod
    def is_auth_var_present() -> bool:
        return os.environ.get('TEAMCERTS_ACCESS_TOKEN') is not None

    @staticmethod
    def read_file_content(machine_dir: Path, file_path: str) -> str:
        dst = machine_dir.joinpath(file_path)
        if not dst.exists():
            raise FileNotFoundError(dst)
        return dst.open().read()

    @staticmethod
    def get_docker_file(machine_dir: Path, file: DockerMachineFile) -> Path:
        return machine_dir.joinpath(file.value)

    @staticmethod
    def clean_folders(directory: Path) -> list:
        machines = []
        if directory.is_dir() and directory.exists():
            machines = [machine.name for machine in directory.iterdir() if machine.is_dir()]
        return machines

    @staticmethod
    def map_cloud_machines(machines_rsp: list) -> dict:
        return {machine.get('name'): machine.get('id') for machine in machines_rsp}

    @staticmethod
    def write_file_content(file: Path, mode: str, content: any, chmod: bool = False):
        if chmod and mode == 'w':
            os.chmod(file, 0o600)
        with file.open(mode) as file_to_write:
            file_to_write.write(content)
            file_to_write.flush()
            file_to_write.close()
        if chmod:
            os.chmod(file, 0o400)


if __name__ == '__main__':
    SyncWraper().main(sys.argv)
