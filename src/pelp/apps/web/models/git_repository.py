from django.db import models


class GitRepository(models.Model):
    """ Git Repository model. """
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    base_url = models.CharField(max_length=255, null=False, blank=False)

    username = models.CharField(max_length=255, null=True, blank=False, default=None)
    token = models.CharField(max_length=255, null=True, blank=False, default=None)

    def __str__(self):
        return self.name
