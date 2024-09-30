from django.db import models

from .course import Course


class CourseGroup(models.Model):
    """ Learner model. """
    code = models.CharField(max_length=255, null=False, blank=False)
    locale = models.CharField(max_length=10, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    course = models.ForeignKey(Course, null=False, blank=False, on_delete=models.CASCADE)
    is_lab = models.BooleanField(null=False, blank=False, default=False)
    sis_code = models.CharField(max_length=255, null=True, blank=True, default=None)

    def __str__(self):
        return "[{} - {}] {}".format(self.course.semester, self.course.code, self.code)

    def num_pending_evaluations(self, activity):
        return self.learner_set.filter(
            models.Q(activityfeedback__isnull=True) | models.Q(
                activityfeedback__isnull=False,
                activityfeedback__activity=activity,
                activityfeedback__score__isnull=True
            ),
            submission__activity=activity,
            id__gte=0
        ).distinct().count()

    @property
    def num_learners(self):
        return self.learner_set.distinct().count()
