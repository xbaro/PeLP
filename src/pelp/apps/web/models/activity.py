from django.db import models
from django.conf import settings
from django.utils import timezone

from .course import Course
from .rubric import Rubric
from .historic import HistoricActivity


class Activity(models.Model):
    """ Activity model. """
    code = models.CharField(max_length=255, null=False, blank=False)
    historic_code = models.ForeignKey(HistoricActivity, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    course = models.ForeignKey(Course, null=False, on_delete=models.CASCADE)
    start = models.DateTimeField(null=False, blank=False)
    end = models.DateTimeField(null=False, blank=False)
    rubric = models.ForeignKey(Rubric, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    enabled = models.BooleanField(null=False, blank=False, default=False)
    self_evaluation = models.BooleanField(null=False, blank=False, default=False)
    max_submissions = models.SmallIntegerField(null=True, blank=True, default=None)
    max_submissions_day = models.SmallIntegerField(null=True, blank=True, default=None)
    include_report = models.BooleanField(null=False, blank=False, default=False)
    report_name = models.CharField(max_length=255, null=True, blank=True, default=None)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['course', 'code']

    def __str__(self):
        return "[{} - {}] {}".format(self.course.semester, self.course.code, self.code)

    def get_translated_name(self, language):
        if language is None:
            return self.name
        try:
            return self.translateactivity_set.get(language=language).name
        except TranslateActivity.DoesNotExist:
            return self.name

    def get_translated_description(self, language):
        if language is None:
            return self.description
        try:
            return self.translateactivity_set.get(language=language).description
        except TranslateActivity.DoesNotExist:
            return self.description

    def num_learner_submissions(self, learner, start=None, end=None):
        qs = self.submission_set.filter(learner=learner, instructorsubmission__isnull=True)

        if start is not None:
            qs = qs.filter(submitted_at__gte=start)
        if end is not None:
            qs = qs.filter(submitted_at__lte=end)

        return qs.count()

    def num_learner_submissions_day(self, learner):
        end = timezone.now()
        start = end - timezone.timedelta(hours=24)

        return self.num_learner_submissions(learner, start, end)

    def num_pending_evaluations(self):
        return self.course.learners.filter(
            models.Q(activityfeedback__isnull=True) | models.Q(
                activityfeedback__isnull=False,
                activityfeedback__activity=self,
                activityfeedback__score__isnull=True
            ),
            submission__activity=self,
            id__gte=0
        ).distinct().count()

    @property
    def has_submissions(self):
        return self.submission_set.filter(learner_id__gte=0).count() > 0

    @property
    def is_active(self):
        """
            Whether this activity is active or not
            :return: True if it is active or False otherwise
        """
        if not self.enabled:
            return False
        return self.course.is_active and (
                self.start is None or self.start <= timezone.now()
        ) and (
                self.end is None or self.end >= timezone.now()
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.start = self.start.replace(hour=0, minute=0, second=0)
        self.end = self.end.replace(hour=23, minute=59, second=59)
        super().save(force_insert, force_update, using, update_fields)


class TranslateActivity(models.Model):
    """ Activity translation model. """
    activity = models.ForeignKey(Activity, null=False, on_delete=models.CASCADE)
    language = models.CharField(max_length=5, null=False, blank=False, choices=settings.LANGUAGES)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ['activity', 'language']
