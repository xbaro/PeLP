from django.db import models
from django.contrib.auth.models import User
from .course_group import CourseGroup


class Learner(models.Model):
    """ Learner model. """
    username = models.CharField(max_length=255, null=False, blank=False, unique=True)
    first_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(null=False, blank=False, unique=True)
    groups = models.ManyToManyField(CourseGroup)
    user = models.OneToOneField(User, null=True, blank=True, default=None, on_delete=models.SET_NULL)
