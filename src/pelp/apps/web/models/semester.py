from django.db import models
from django.utils import timezone


class Semester(models.Model):
    """ Semester model. """

    code = models.CharField(max_length=255, null=False, blank=False, unique=True)
    start = models.DateTimeField(null=False, blank=False)
    end = models.DateTimeField(null=False, blank=False)

    def __str__(self):
        return self.code

    @property
    def is_active(self):
        """
            Whether this semester is active or not
            :return: True if it is active or False otherwise
        """
        return (self.start is None or self.start <= timezone.now()) and (self.end is None or self.end >= timezone.now())
