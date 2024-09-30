from django.db import models

from .project import Project

MODULE_TYPE = (
    (0, 'STATIC LIBRARY'),
)


class ProjectModule(models.Model):
    """ Project Module model. """
    project = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
    type = models.SmallIntegerField(choices=MODULE_TYPE, null=False, blank=False, default=0)
    name = models.CharField(max_length=255, null=False, blank=False)
    base_path = models.CharField(max_length=255, null=False, blank=False)
    allowed_files_regex = models.CharField(max_length=255, null=True, blank=False, default=None)

    class Meta:
        unique_together = ['project', 'name']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

        self.project.status = 0
        self.project.save()

