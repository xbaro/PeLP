from django.db import models
import uuid

from .activity import Activity


def get_default_name():
    return uuid.uuid4().__str__()


class MailInbox(models.Model):
    """ Mail inbox model. """
    name = models.CharField(max_length=255, null=False, blank=False, unique=True, default=get_default_name)
    activity = models.ForeignKey(Activity, null=False, blank=False, on_delete=models.CASCADE, default=None)

    max_submissions = models.IntegerField(null=False, blank=False, default=10)
    max_submissions_day = models.IntegerField(null=False, blank=False, default=2)

    allow_user_replacement = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return self.name
