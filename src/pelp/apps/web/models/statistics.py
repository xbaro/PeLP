from django.db import models
from .activity import Activity
from .course_group import CourseGroup
from .utils import JSONField


class StatisticsActivity(models.Model):
    """ Statistics for an Activity model. """
    activity = models.OneToOneField(Activity, null=False, blank=False, on_delete=models.CASCADE)
    learners = models.IntegerField(null=False, blank=False)
    learners_with_submissions = models.IntegerField(null=False, blank=False, default=0)
    mean_submissions_learner = models.IntegerField(null=False, blank=False, default=0)
    total_submissions = models.IntegerField(null=False, blank=False, default=0)
    score_np = models.IntegerField(null=False, blank=False, default=0)
    score_a = models.IntegerField(null=False, blank=False, default=0)
    score_b = models.IntegerField(null=False, blank=False, default=0)
    score_cp = models.IntegerField(null=False, blank=False, default=0)
    score_cm = models.IntegerField(null=False, blank=False, default=0)
    score_d = models.IntegerField(null=False, blank=False, default=0)
    has_evaluation = models.BooleanField(null=False, blank=False, default=False)
    eval_np = models.IntegerField(null=False, blank=False, default=0)
    eval_a = models.IntegerField(null=False, blank=False, default=0)
    eval_b = models.IntegerField(null=False, blank=False, default=0)
    eval_cp = models.IntegerField(null=False, blank=False, default=0)
    eval_cm = models.IntegerField(null=False, blank=False, default=0)
    eval_d = models.IntegerField(null=False, blank=False, default=0)
    eval_pending = models.IntegerField(null=False, blank=False, default=0)
    metadata = models.TextField(null=True, blank=True, default=None)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "[{}] - {}".format(self.activity.course.code, self.activity.code)

    def get_metadata(self):
        if self.metadata is not None:
            json_field = JSONField()
            return json_field.to_representation(self.metadata)
        return None


class StatisticsGroup(models.Model):
    """ Group Statistics for an Activity model. """
    activity = models.ForeignKey(Activity, null=False, blank=False, on_delete=models.CASCADE)
    group = models.ForeignKey(CourseGroup, null=False, blank=False, on_delete=models.CASCADE)
    instructors = models.CharField(max_length=255, null=False, blank=False)
    locale = models.CharField(max_length=10, null=False, blank=False)
    learners = models.IntegerField(null=False, blank=False)
    learners_with_submissions = models.IntegerField(null=False, blank=False, default=0)
    mean_submissions_learner = models.IntegerField(null=False, blank=False, default=0)
    total_submissions = models.IntegerField(null=False, blank=False, default=0)
    score_np = models.IntegerField(null=False, blank=False, default=0)
    score_a = models.IntegerField(null=False, blank=False, default=0)
    score_b = models.IntegerField(null=False, blank=False, default=0)
    score_cp = models.IntegerField(null=False, blank=False, default=0)
    score_cm = models.IntegerField(null=False, blank=False, default=0)
    score_d = models.IntegerField(null=False, blank=False, default=0)
    has_evaluation = models.BooleanField(null=False, blank=False, default=False)
    eval_np = models.IntegerField(null=False, blank=False, default=0)
    eval_a = models.IntegerField(null=False, blank=False, default=0)
    eval_b = models.IntegerField(null=False, blank=False, default=0)
    eval_cp = models.IntegerField(null=False, blank=False, default=0)
    eval_cm = models.IntegerField(null=False, blank=False, default=0)
    eval_d = models.IntegerField(null=False, blank=False, default=0)
    eval_pending = models.IntegerField(null=False, blank=False, default=0)
    metadata = models.TextField(null=True, blank=True, default=None)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['activity', 'group']

    def __str__(self):
        return "[{}-{}] {} - {}".format(self.activity.course.code, self.activity.code, self.group.code, self.instructors)

    def get_metadata(self):
        if self.metadata is not None:
            json_field = JSONField()
            return json_field.to_representation(self.metadata)
        return None
