from django.db import models


class AppVersionManager(models.Manager):
    def requires_update(self, version: str, platform: str) -> (bool, bool):
        qs = self.filter(version__gt=version, platform=platform)
        return qs.exists(), qs.filter(required=True).exists()
