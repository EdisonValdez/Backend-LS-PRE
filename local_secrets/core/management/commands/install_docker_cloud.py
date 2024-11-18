import os
import shutil
import stat
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    script_path = Path(settings.BASE_DIR).joinpath('.scripts/docker_cloud.sh')
    destination_path = Path.home().joinpath("docker_cloud.sh")
    symlink_path = Path('/usr/local/bin/docker-cloud')

    def handle(self, *args, **options):
        if not self.symlink_path.exists():
            shutil.copy(settings.BASE_DIR.joinpath(self.script_path), self.destination_path)

            with open(self.symlink_path, 'w') as f:
                f.write(f'source {self.destination_path}')
                os.chmod(self.symlink_path, self.get_os_stat())

            print('The script has been installed successfully')
        else:
            print('The script is already installed')

    def get_os_stat(self):
        return os.stat(self.symlink_path).st_mode | stat.S_IEXEC
