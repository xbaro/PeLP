from django.db import models

from .activity import Activity
from .learner import Learner
from .submission import Submission


RESULT_STATUS = (
    (0, 'NO_DATA'),
    (1, 'PENDING'),
    (2, 'VALID'),
    (3, 'INVALID'),
    (4, 'ERROR'),
    (5, 'TIMEOUT'),
)


class LearnerResult(models.Model):
    """ Learner result model. """
    status = models.SmallIntegerField(choices=RESULT_STATUS, null=False, default=0)
    activity = models.ForeignKey(Activity, null=False, default=None, blank=False, on_delete=models.CASCADE)
    learner = models.ForeignKey(Learner, null=False, default=None, blank=False, on_delete=models.CASCADE)
    last_submission = models.ForeignKey(Submission, null=True, default=None, blank=True, on_delete=models.SET_NULL)
    num_submissions = models.IntegerField(null=False, blank=False, default=0)
    built = models.BooleanField(null=False, blank=False, default=False)
    test_passed = models.BooleanField(null=False, blank=False, default=False)
    test_score = models.FloatField(null=False, blank=False, default=0.0)
    num_tests = models.IntegerField(null=False, blank=False, default=0)
    num_test_passed = models.IntegerField(null=False, blank=False, default=0)
    num_test_failed = models.IntegerField(null=False, blank=False, default=0)
    error = models.TextField(null=True, blank=True, default=None)
    submitted_at = models.DateTimeField(null=True, blank=False, default=None)
    elapsed_time = models.IntegerField(null=True, default=None)
    memory_leak = models.IntegerField(null=True, default=None)

    class Meta:
        unique_together = ['activity', 'learner']
