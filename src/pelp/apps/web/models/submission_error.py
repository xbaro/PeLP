from django.db import models

from .submission_file import SubmissionFile
from .submission import Submission

ERROR_TYPE = (
    (0, 'OTHER'),
    (1, 'MEMORY_OPERATION'),
    (2, 'MEMORY_LEAK'),
    (3, 'GENERATED'),
)

ERROR_SOURCE = (
    (0, 'INSTRUCTOR'),
    (1, 'VALGRIND'),
)


class SubmissionError(models.Model):
    """ Submission error model. """
    submission = models.ForeignKey(Submission, null=False, blank=None, on_delete=models.CASCADE)
    file = models.ForeignKey(SubmissionFile, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    type = models.SmallIntegerField(choices=ERROR_TYPE, null=False, default=0)
    source = models.SmallIntegerField(choices=ERROR_SOURCE, null=False, default=0)
    order = models.SmallIntegerField(null=True, blank=True, default=None)
    count = models.SmallIntegerField(null=True, blank=True, default=None)
    line = models.IntegerField(null=True, blank=True, default=None)
    function = models.CharField(max_length=250, null=True, blank=True, default=None)
    code = models.CharField(max_length=100, null=True, blank=True, default=None)
    description = models.TextField(null=True, blank=True, default=None)
    context = models.TextField(null=True, blank=True, default=None)
    value = models.FloatField(null=True, blank=True, default=None)
