from django.db import models
from django.db import transaction
from django.utils import timezone


class TaskLock(models.Model):
    """ Task lock model. """
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    locked_at = models.DateTimeField(null=False, blank=False, default=timezone.now)

    def __str__(self):
        return self.name


def lock(task):
    assert task is not None
    with transaction.atomic():
        try:
            TaskLock.objects.get(name=task)
            task = None
        except TaskLock.DoesNotExist:
            task = TaskLock.objects.create(name=task)
    return task


def unlock(task):
    assert task is not None
    TaskLock.objects.filter(name=task).delete()


def unlock_expired():
    expiration_date = timezone.now() - timezone.timedelta(minutes=10)
    TaskLock.objects.filter(locked_at__lte=expiration_date).delete()
