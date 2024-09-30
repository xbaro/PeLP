from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.db import models
from django.db.models import Sum
from django.db.models.signals import pre_delete, post_save
from django.dispatch.dispatcher import receiver

from .activity import Activity
from .git_repository import GitRepository
from .submission import TestSubmission


def get_base_code_upload_path(instance, filename):
    """
        Build the path where the base code is stored

        :param instance: Informed consent document
        :type instance: Enrolment
        :param filename: Name of the file
        :return: Path to store the file
    """
    return '{}/{}/{}/project/base_code.zip'.format(
        instance.activity.course.semester.code.replace(' ', '_'),
        instance.activity.course.code.replace(' ', '_'),
        instance.activity.code.replace(' ', '_')
    )


def get_test_code_upload_path(instance, filename):
    """
        Build the path where the test code is stored

        :param instance: Informed consent document
        :type instance: Enrolment
        :param filename: Name of the file
        :return: Path to store the file
    """
    return '{}/{}/{}/project/test_code.zip'.format(
        instance.activity.course.semester.code.replace(' ', '_'),
        instance.activity.course.code.replace(' ', '_'),
        instance.activity.code.replace(' ', '_')
    )


PROJECT_STATUS = (
    (0, 'CREATING'),
    (1, 'CREATED'),
    (2, 'CLONING'),
    (3, 'CLONED'),
    (4, 'UPLOADING'),
    (5, 'UPLOADED'),
    (6, 'VALIDATING'),
    (7, 'VALID'),
    (8, 'TESTING'),
    (9, 'PROCESSED'),
    (10, 'INVALID'),
    (11, 'ERROR'),
    (12, 'TIMEOUT'),
    (13, 'FAILED_TEST'),
)

PROJECT_TYPE = (
    (0, 'ANSI_C'),
)


class Project(models.Model):
    """ Project model. """
    status = models.SmallIntegerField(choices=PROJECT_STATUS, null=False, default=0)
    type = models.SmallIntegerField(choices=PROJECT_TYPE, null=False, default=0)
    activity = models.OneToOneField(Activity, null=False, on_delete=models.CASCADE)
    executable_name = models.CharField(max_length=255, null=False, blank=False)
    test_arguments = models.CharField(max_length=255, null=False, blank=False)
    results_path = models.CharField(max_length=255, null=False, blank=False)
    progress_path = models.CharField(max_length=255, null=True, blank=True, default=None)
    image = models.CharField(max_length=255, null=False, blank=False)
    anchor_file = models.CharField(max_length=255, null=True, blank=False, default=None)
    allowed_files_regex = models.CharField(max_length=255, null=True, blank=True, default=None)
    use_valgrind = models.BooleanField(null=False, blank=False, default=False)
    valgrind_report_path = models.CharField(max_length=255, null=True, blank=True, default=None)

    allow_base_failure = models.BooleanField(null=False, blank=False, default=False)

    repository = models.ForeignKey(GitRepository, null=True, default=None, blank=True, on_delete=models.SET_NULL)
    repository_url = models.CharField(max_length=255, null=True, blank=True, default=None)
    repository_base_branch = models.CharField(max_length=255, null=True, blank=True, default=None)
    repository_test_branch = models.CharField(max_length=255, null=True, blank=True, default=None)

    code_base_zip = models.FileField(max_length=250, null=True, blank=True, default=None,
                                     upload_to=get_base_code_upload_path)
    code_test_zip = models.FileField(max_length=250, null=True, blank=True, default=None,
                                     upload_to=get_test_code_upload_path)

    code_base_result = models.ForeignKey(TestSubmission, null=True, default=None, blank=True,
                                         on_delete=models.SET_NULL, related_name='base_submission')
    code_test_result = models.ForeignKey(TestSubmission, null=True, default=None, blank=True,
                                         on_delete=models.SET_NULL, related_name='test_submission')

    max_execution_time = models.IntegerField(null=False, blank=False, default=120)
    mem_limit = models.CharField(max_length=15, null=False, blank=False, default='10m')

    error = models.TextField(null=True, blank=True, default=None)

    def __str__(self):
        return "[{} - {} - {}] {}".format(self.activity.course.semester, self.activity.course.code,
                                          self.activity.code, self.executable_name)

    def get_total_weight(self):
        return self.projecttest_set.filter(parent__isnull=True).aggregate(Sum('weight')).get('weight__sum', 0.00)


@receiver(pre_delete, sender=Project)
def _project_delete(sender, instance, **kwargs):
    instance.code_base_zip.delete()
    instance.code_test_zip.delete()


@receiver(post_save, sender=Project)
def _project_post_save(sender, instance, **kwargs):
    # if kwargs[]
    try:
        from pelp.apps.web.consumers.activity import ActivityEventConsumer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            ActivityEventConsumer.get_activity_channel_name(instance.id),
            {
                'type': 'send_message',
                'message': instance.get_status_display(),
                "event": 'STATUS_CHANGE'
        })
    except Exception:
        # Avoid failing due to messaging errors
        pass
