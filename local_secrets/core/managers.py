from django.db import models
from django.utils import timezone


class SoftDeletionManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.with_deleted = kwargs.pop('with_deleted', False)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.with_deleted:
            return SoftDeletionQuerySet(self.model)
        return SoftDeletionQuerySet(self.model).shown()


class SoftDeletionQuerySet(models.QuerySet):
    def delete(self):
        return super(SoftDeletionQuerySet, self).update(deleted_at=timezone.now())

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

    def shown(self):
        return self.filter(deleted_at=None)

    def soft_deleted(self):
        return self.exclude(deleted_at=None)
