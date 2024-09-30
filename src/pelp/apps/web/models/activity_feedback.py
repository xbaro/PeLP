from ckeditor.fields import RichTextField
from django.db import models

from .activity import Activity
from .learner import Learner
from .instructor import Instructor


class ActivityFeedback(models.Model):
    """ Learner result model. """
    activity = models.ForeignKey(Activity, null=False, default=None, blank=False, on_delete=models.CASCADE)
    learner = models.ForeignKey(Learner, null=False, default=None, blank=False, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, null=True, default=None, blank=True, on_delete=models.SET_NULL)
    general = RichTextField(null=True, blank=True, default=None)
    score = models.FloatField(null=True, blank=True, default=None)
    is_np = models.BooleanField(null=False, blank=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    public = models.BooleanField(null=False, blank=False, default=False)

    class Meta:
        unique_together = ['activity', 'learner']
