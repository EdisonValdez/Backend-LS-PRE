from typing import Optional

from local_secrets.app_version.choices import AppPlatform
from local_secrets.app_version.models import AppVersion, Store


class AppVersionProvider:
    @staticmethod
    def is_update_needed(version: str, platform: AppPlatform) -> (bool, bool):
        return AppVersion.objects.requires_update(version=version, platform=platform.value)

    @staticmethod
    def get_store_url(platform: AppPlatform) -> Optional[Store]:
        return Store.objects.filter(platform=platform.value).first()
