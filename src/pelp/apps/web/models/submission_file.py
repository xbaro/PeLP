from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from .project_module import ProjectModule
from .submission import Submission

FILE_STATUS = (
    (0, 'ADDED'),
    (1, 'SKIPPED'),
    (2, 'FILTERED'),
    (3, 'GENERATED'),
)


def get_submission_file_upload_path(instance, filename):
    """
        Build the path where the test code is stored

        :param instance: Informed consent document
        :type instance: Enrolment
        :param filename: Name of the file
        :return: Path to store the file
    """
    return '{}/{}/{}/submissions/{}/{}/code/{}'.format(
        instance.submission.activity.course.semester.code.replace(' ', '_'),
        instance.submission.activity.course.code.replace(' ', '_'),
        instance.submission.activity.code.replace(' ', '_'),
        instance.submission.learner.username.replace(' ', '_'),
        instance.submission.id,
        instance.filename
    )


class SubmissionFile(models.Model):
    """ Submission file model. """
    submission = models.ForeignKey(Submission, null=False, on_delete=models.CASCADE)
    module = models.ForeignKey(ProjectModule, null=True, on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=FILE_STATUS, null=False, default=0)
    filename = models.CharField(max_length=255, null=True, blank=False, default=None)
    original_filename = models.CharField(max_length=255, null=True, blank=False, default=None)
    file = models.FileField(null=False, blank=False, upload_to=get_submission_file_upload_path)
    is_report = models.BooleanField(null=False, blank=False, default=False)


@receiver(pre_delete, sender=SubmissionFile)
def _submission_file_delete(sender, instance, **kwargs):
    instance.file.delete()
