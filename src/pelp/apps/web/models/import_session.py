from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.utils import timezone

from .course_group import CourseGroup
from .activity import Activity
from .learner import Learner
from .utils import JSONField


def get_input_file_upload_path(instance, filename):
    """
        Build the path where the input file is stored

        :param instance: Informed consent document
        :type instance: Enrolment
        :param filename: Name of the file
        :return: Path to store the file
    """
    return 'import/{}/uploaded/{}'.format(
        instance.id,
        filename
    )


def get_entry_file_upload_path(instance, filename):
    """
        Build the path where the session entry file is stored

        :param instance: Informed consent document
        :type instance: Enrolment
        :param filename: Name of the file
        :return: Path to store the file
    """
    return 'import/{}/files/{}/{}'.format(
        instance.session.id,
        instance.id,
        filename
    )


SESSION_TYPE = (
    (0, 'LEARNERS'),
    (1, 'SUBMISSIONS'),
)

SESSION_STATUS = (
    (0, 'CREATED'),
    (1, 'LOADING'),
    (2, 'LOADED'),
    (3, 'IMPORTING'),
    (4, 'IMPORTED'),
    (5, 'INVALID'),
    (6, 'ERROR'),
)


class ImportSession(models.Model):
    """ Import Session model. """
    status = models.SmallIntegerField(choices=SESSION_STATUS, null=False, blank=False, default=0)
    type = models.SmallIntegerField(choices=SESSION_TYPE, null=False, blank=False, default=0)
    course_group = models.ForeignKey(CourseGroup, null=False, blank=False, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=False, blank=False, default=timezone.now)
    input_file = models.FileField(max_length=250, null=True, blank=True, default=None,
                                  upload_to=get_input_file_upload_path)
    valid = models.BooleanField(null=False, blank=False, default=False)

    error = models.TextField(null=True, blank=True, default=None)

    set_official = models.BooleanField(null=False, blank=False, default=False)


@receiver(pre_delete, sender=ImportSession)
def _import_session_delete(sender, instance, **kwargs):
    instance.input_file.delete()


class ImportSessionEntry(models.Model):
    """ Import Session entry model. """
    session = models.ForeignKey(ImportSession, null=False, blank=False, on_delete=models.CASCADE)
    learner = models.ForeignKey(Learner, null=True, blank=True, on_delete=models.CASCADE)
    data = models.TextField(null=True, blank=True, default=None)
    is_valid = models.BooleanField(null=False, blank=False, default=True)
    entry_file = models.FileField(max_length=250, null=True, blank=True, default=None,
                                  upload_to=get_entry_file_upload_path)

    error = models.TextField(null=True, blank=True, default=None)

    def get_data(self):
        if self.data is not None:
            json_field = JSONField()
            return json_field.to_representation(self.data)
        return None


@receiver(pre_delete, sender=ImportSessionEntry)
def _import_session_entry_delete(sender, instance, **kwargs):
    instance.entry_file.delete()
