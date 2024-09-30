from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from .project import Project
from .project_module import ProjectModule


def get_project_file_upload_path(instance, filename):
    """
        Build the path where the test code is stored

        :param instance: Informed consent document
        :type instance: Enrolment
        :param filename: Name of the file
        :return: Path to store the file
    """
    return '{}/{}/{}/project/code/{}'.format(
        instance.project.activity.course.semester.code.replace(' ', '_'),
        instance.project.activity.course.code.replace(' ', '_'),
        instance.project.activity.code.replace(' ', '_'),
        instance.filename
    )


class ProjectFile(models.Model):
    """ Project file model. """
    project = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
    module = models.ForeignKey(ProjectModule, null=True, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255, null=True, blank=False, default=None)
    original_filename = models.CharField(max_length=255, null=True, blank=False, default=None)
    file = models.FileField(null=False, blank=False, upload_to=get_project_file_upload_path)
    locked = models.BooleanField(null=False, default=True)


@receiver(pre_delete, sender=ProjectFile)
def _project_file_delete(sender, instance, **kwargs):
    instance.file.delete()
