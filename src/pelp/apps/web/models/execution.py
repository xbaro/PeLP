from django.db import models

from .project import Project
from .submission import Submission


EXECUTION_STATUS = (
    (0, 'CREATING'),
    (1, 'CREATED'),
    (2, 'PREPARING'),
    (3, 'PREPARED'),
    (4, 'RUNNING'),
    (5, 'FINISHED'),
    (6, 'INVALID'),
    (7, 'ERROR'),
    (8, 'TIMEOUT'),
)


class Execution(models.Model):
    """ Execution model. """
    status = models.SmallIntegerField(choices=EXECUTION_STATUS, null=False, default=0)
    container_id = models.CharField(max_length=255, null=True, blank=False, default=None)
    project = models.ForeignKey(Project, null=False, default=None, blank=False, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, null=False, default=None, blank=False, on_delete=models.CASCADE)
    started_at = models.DateTimeField(null=True, blank=False, default=None)
    execution_path = models.CharField(max_length=255, null=False, blank=False, default=None)

    error = models.TextField(null=True, blank=True, default=None)
