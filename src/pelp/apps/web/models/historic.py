from django.db import models
from .utils import JSONField


class HistoricActivity(models.Model):
    """ Historic Activity model. """
    code = models.CharField(max_length=255, null=False, blank=False, unique=True)

    def __str__(self):
        return "[{}] - Historic Activity".format(self.code)


class HistoricActivityData(models.Model):
    """ Historic Activity Data model. """
    code = models.ForeignKey(HistoricActivity, null=False, blank=False, on_delete=models.CASCADE)
    semester = models.CharField(max_length=50, null=False, blank=False)
    course = models.CharField(max_length=255, null=False, blank=False)
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
    metadata = models.TextField(null=True, blank=True, default=None)
    observations = models.TextField(null=True, blank=True, default=None)

    class Meta:
        unique_together = ['semester', 'course', 'code']

    def __str__(self):
        return "[{}] {} - {}".format(self.code, self.semester, self.course)

    def get_metadata(self):
        if self.metadata is not None:
            json_field = JSONField()
            return json_field.to_representation(self.metadata)
        return None


class HistoricActivityGroup(models.Model):
    """ Historic Activity Data model. """
    activity = models.ForeignKey(HistoricActivityData, null=False, blank=False, on_delete=models.CASCADE)
    group = models.CharField(max_length=255, null=False, blank=False)
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
    metadata = models.TextField(null=True, blank=True, default=None)
    observations = models.TextField(null=True, blank=True, default=None)

    class Meta:
        unique_together = ['activity', 'group']

    def __str__(self):
        return "[{}-{}] {} - {}".format(self.activity.course, self.activity.code, self.group, self.instructors)

    def get_metadata(self):
        if self.metadata is not None:
            json_field = JSONField()
            return json_field.to_representation(self.metadata)
        return None
