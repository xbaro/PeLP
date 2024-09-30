from django.db import models
from django.conf import settings

from ckeditor_uploader.fields import RichTextUploadingField

from .full_text_search import SearchManager
from .learner import Learner, User


class FaqCollection(models.Model):
    """ FAQ Collection model. """
    title = models.CharField(max_length=255, null=False, blank=False)
    items = models.ManyToManyField('Faq')


class Faq(models.Model):
    """ FAQ model. """
    tags = models.ManyToManyField('FaqTag')
    public = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return "FAQ {}".format(self.id)

    @property
    def language(self):
        return settings.LANGUAGE_CODE.split('-')[0].split('_')[0]

    @property
    def available_languages(self):
        return self.translatefaq_set.filter(
            title__isnull=False, content__isnull=False
        ).values_list('language', flat=True)

    @property
    def title(self):
        return self.get_translated_title()

    @property
    def content(self):
        return self.get_translated_content()

    @property
    def num_rates(self):
        return self.faqrating_set.count()

    @property
    def average_rate(self):
        return self.faqrating_set.aggregate(models.Avg('rating'))['rating__avg'] or 0.0

    def get_translated_title(self, language=None):
        try:
            if language is None:
                language = self.language
            return self.translatefaq_set.get(language=language).title
        except TranslateFaq.DoesNotExist:
            return None

    def get_translated_content(self, language=None):
        try:
            if language is None:
                language = self.language
            return self.translatefaq_set.get(language=language).content
        except TranslateFaq.DoesNotExist:
            return None

    def get_learner_rating(self, learner=None):
        learner_obj = None
        rate = 0
        if isinstance(learner, Learner):
            learner_obj = learner
        elif isinstance(learner, User):
            try:
                learner_obj = Learner.objects.get(user=learner)
            except Learner.DoesNotExist:
                learner_obj = None
        if learner_obj is not None:
            try:
                rate_obj = self.faqrating_set.get(learner=learner_obj)
                rate = rate_obj.rating
            except Exception:
                # In case not found, use default zero value
                pass
        return rate


class FaqTag(models.Model):
    """ FAQ Tag translation model. """
    tag = models.CharField(max_length=255, null=False, blank=False, unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.tag)

    def get_translated_tag(self, language):
        if language is None:
            return self.tag
        try:
            return self.translatefaqtag_set.get(language=language).tag
        except TranslateFaqTag.DoesNotExist:
            return self.tag

    def get_translated_last_update(self, language):
        if language is None:
            return self.updated_at
        try:
            return self.translatefaqtag_set.get(language=language).updated_at
        except TranslateFaqTag.DoesNotExist:
            return self.updated_at


class TranslateFaq(models.Model):
    """ FAQ translation model. """

    faq = models.ForeignKey(Faq, null=False, on_delete=models.CASCADE)
    language = models.CharField(max_length=5, null=False, blank=False, choices=settings.LANGUAGES)
    title = models.CharField(max_length=255, null=False, blank=False)
    content = RichTextUploadingField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Enable full-text search support for title and content.
    objects = SearchManager(['title', 'content'])

    class Meta:
        unique_together = ['faq', 'language']


class TranslateFaqTag(models.Model):
    """ FAQ Tag translation model. """
    
    faqtag = models.ForeignKey(FaqTag, null=False, on_delete=models.CASCADE)
    language = models.CharField(max_length=5, null=False, blank=False, choices=settings.LANGUAGES)
    tag = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        unique_together = ['faqtag', 'language']

