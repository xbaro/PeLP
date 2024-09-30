from django.db import models


class Rubric(models.Model):
    """ Rubric model. """
    code = models.CharField(max_length=255, null=False, blank=False, unique=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('Rubric', related_name='children', null=True,
                               blank=True, default=None, on_delete=models.SET_NULL)

    def get_elements_recursive(self):
        if self.parent is None:
            return self.rubricelement_set.order_by('id').all()
        return self.parent.get_elements_recursive() | self.rubricelement_set.order_by('id').all()

    def __str__(self):
        return '[' + self.code + '] ' + self.name
