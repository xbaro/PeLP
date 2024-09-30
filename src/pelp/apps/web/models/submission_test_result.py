from django.db import models

from .project_test import ProjectTest
from .submission import Submission


class SubmissionTestResult(models.Model):
    """ Project Test model. """
    submission = models.ForeignKey(Submission, null=False, on_delete=models.CASCADE)
    test = models.ForeignKey(ProjectTest, null=False, on_delete=models.CASCADE)

    passed = models.BooleanField(null=False, blank=False, default=False)
    num_passed = models.IntegerField(null=False, blank=False, default=0)
    num_failed = models.IntegerField(null=False, blank=False, default=0)
    num_tests = models.IntegerField(null=False, blank=False, default=0)
    total_weight = models.FloatField(null=False, blank=False, default=0.0)

    models.UniqueConstraint(fields = ['submission', 'test'], name = 'constraint_pk_submission_test')

    class Meta:
        unique_together = ['submission', 'test']
