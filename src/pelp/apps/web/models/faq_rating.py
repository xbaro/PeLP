from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .faq import Faq
from .learner import Learner


class FaqRating(models.Model):
    """ FAQ Rating model. """
    faq = models.ForeignKey(Faq, on_delete=models.CASCADE)
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(
        default=None,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        unique_together = ['faq', 'learner']

