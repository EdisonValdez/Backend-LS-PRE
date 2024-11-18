from django.db import models
from django.utils import timezone

from local_secrets.core.managers import SoftDeletionManager

"""
TimeStampedModel can be added to auto-generate created and updated fields to all model with its automated expected
behavior.
> from django_extensions.db.models import TimeStampedModel

PD: Note that if you import this class, django_extensions library must be swapped from [dev-packages] to [packages]
section into Pipfile.
"""
__all__ = (
    "SoftDeletionModel",
    # "TimeStampedModel",
)


class SoftDeletionModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(with_deleted=True)

    class Meta:
        abstract = True

    def delete(self, **kwargs):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super(SoftDeletionModel, self).delete()
