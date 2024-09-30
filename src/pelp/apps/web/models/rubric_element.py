from django.conf import settings
from django.db import models

from .activity import Activity
from .learner import Learner
from .rubric import Rubric


RUBRIC_ELEMENT_TYPE = (
    (0, 'ADDITIVE'),
    (1, 'SUBTRACTIVE'),
)


class RubricElement(models.Model):
    """ Rubric element model. """
    rubric = models.ForeignKey(Rubric, null=False, blank=False, on_delete=models.CASCADE)
    type = models.SmallIntegerField(choices=RUBRIC_ELEMENT_TYPE, null=False, blank=False, default=0)
    description = models.TextField(null=False, blank=False)
    weight = models.FloatField(null=True, blank=True, default=None)

    def get_translated_description(self, language):
        if language is None:
            return self.description
        try:
            return self.translaterubricelement_set.get(language=language).description
        except TranslateRubricElement.DoesNotExist:
            return self.description


class RubricElementOption(models.Model):
    """ Rubric element option model. """
    rubric_element = models.ForeignKey(RubricElement, null=False, blank=False, on_delete=models.CASCADE)
    description = models.TextField(null=False, blank=False)
    value = models.FloatField(null=False, blank=False, default=1.0)

    def get_translated_description(self, language):
        if language is None:
            return self.description
        try:
            return self.translaterubricelementoption_set.get(language=language).description
        except TranslateRubricElementOption.DoesNotExist:
            return self.description


class RubricElementInstantiation(models.Model):
    """ Rubric element option instantiated for a learner and activity model. """
    activity = models.ForeignKey(Activity, null=False, blank=False, on_delete=models.CASCADE)
    learner = models.ForeignKey(Learner, null=False, blank=False, on_delete=models.CASCADE)
    rubric_element = models.ForeignKey(RubricElement, null=False, blank=False, on_delete=models.CASCADE)
    value = models.ForeignKey(RubricElementOption, null=False, blank=False, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['activity', 'learner', 'rubric_element']


class TranslateRubricElement(models.Model):
    """ Rubric element translation model. """
    rubric_element = models.ForeignKey(RubricElement, null=False, on_delete=models.CASCADE)
    language = models.CharField(max_length=5, null=False, blank=False, choices=settings.LANGUAGES)
    description = models.TextField(null=True, blank=True)


class TranslateRubricElementOption(models.Model):
    """ Rubric element option translation model. """
    rubric_element_option = models.ForeignKey(RubricElementOption, null=False, on_delete=models.CASCADE)
    language = models.CharField(max_length=5, null=False, blank=False, choices=settings.LANGUAGES)
    description = models.TextField(null=True, blank=True)
