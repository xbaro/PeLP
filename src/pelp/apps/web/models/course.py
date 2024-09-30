from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from .semester import Semester


class CourseTemplate(models.Model):
    """ Course Template model. """
    code = models.CharField(max_length=255, null=False, blank=False, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "[{}] {} - {}".format(self.id, self.code, self.description)


class CourseTemplateLanguage(models.Model):
    """ Course translation model. """
    template = models.ForeignKey(CourseTemplate, null=False, on_delete=models.CASCADE)
    code = models.CharField(max_length=255, null=False, blank=False)
    language = models.CharField(max_length=5, null=False, blank=False, choices=settings.LANGUAGES)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    is_lab = models.BooleanField(null=False, blank=False, default=False)


class Course(models.Model):
    """ Course model. """

    code = models.CharField(max_length=255, null=False, blank=False, unique=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    semester = models.ForeignKey(Semester, null=False, on_delete=models.CASCADE)
    template = models.ForeignKey(CourseTemplate, null=True, on_delete=models.SET_NULL, default=None)

    def __str__(self):
        return "[{}] {}".format(self.semester, self.code)

    @property
    def valid_activities(self):
        return self.activity_set.filter(project__status=9)

    @property
    def not_valid_activities(self):
        return self.activity_set.exclude(project__status=9)

    @property
    def learners(self):
        from .learner import Learner
        return Learner.objects.filter(groups__course=self).distinct()

    @property
    def instructors(self):
        from .instructor import Instructor
        return Instructor.objects.filter(groups__course=self).distinct()

    @property
    def is_active(self):
        """
            Whether this course is active or not
            :return: True if it is active or False otherwise
        """
        return self.semester.is_active

    def is_instructor(self, user: User) -> bool:
        """
            Whether provided user is instructor of this course
            :return: True if it is instructor or False otherwise
        """
        try:
            self.instructors.get(user_id=user.id)
            return True
        except Exception:
            return False

    def is_learner(self, user: User) -> bool:
        """
            Whether provided user is learner of this course
            :return: True if it is learner or False otherwise
        """
        try:
            self.learners.get(user_id=user.id)
            return True
        except Exception:
            return False

    def get_translated_name(self, language):
        if language is None:
            return self.name
        try:
            return self.translatecourse_set.get(language=language).name
        except TranslateCourse.DoesNotExist:
            return self.name

    def get_translated_description(self, language):
        if language is None:
            return self.description
        try:
            return self.translatecourse_set.get(language=language).description
        except TranslateCourse.DoesNotExist:
            return self.description

    def num_pending_evaluations(self):
        count = 0
        for activity in self.activity_set.all():
            count += activity.num_pending_evaluations()
        return count


class TranslateCourse(models.Model):
    """ Course translation model. """
    course = models.ForeignKey(Course, null=False, on_delete=models.CASCADE)
    language = models.CharField(max_length=5, null=False, blank=False, choices=settings.LANGUAGES)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    sis_code = models.CharField(max_length=255, null=True, blank=True, default=None)
