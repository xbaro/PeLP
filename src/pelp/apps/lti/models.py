from django.db import models
from django.contrib.auth.models import User
from lti_toolbox.models import LTIConsumer
from pelp.apps.web.models import Course, CourseGroup


LTI_SOURCE = (
    (0, 'UOC_CAMPUS'),
    (1, 'MOODLE'),
    (2, 'CANVAS'),
)


class LTIConsumerProperties(models.Model):
    source = models.SmallIntegerField(choices=LTI_SOURCE, null=False, default=0)
    consumer = models.OneToOneField(LTIConsumer, null=False, blank=False, default=None, related_name='+',
                                    on_delete=models.CASCADE)
    user_creation = models.BooleanField(null=False, blank=False, default=False)
    instructor_creation = models.BooleanField(null=False, blank=False, default=False)
    learner_creation = models.BooleanField(null=False, blank=False, default=False)
    course_creation = models.BooleanField(null=False, blank=False, default=False)
    group_creation = models.BooleanField(null=False, blank=False, default=False)

    user_username_field = models.CharField(max_length=250, blank=True, null=True, default=None)
    course_code_field = models.CharField(max_length=250, blank=True, null=True, default=None)
    group_code_field = models.CharField(max_length=250, blank=True, null=True, default=None)


class LTIProfile(models.Model):
    consumer = models.ForeignKey(LTIConsumer, null=False, blank=False, default=None, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, blank=False, default=None, on_delete=models.CASCADE)
    user_username = models.CharField(max_length=250, blank=False, null=False, default=None)

    custom_photo = models.CharField(max_length=250, blank=True, null=True, default=None)
    custom_firstname = models.CharField(max_length=250, blank=True, null=True, default=None)
    custom_surname = models.CharField(max_length=250, blank=True, null=True, default=None)
    custom_fullname = models.CharField(max_length=250, blank=True, null=True, default=None)
    custom_username = models.CharField(max_length=250, blank=True, null=True, default=None)
    custom_sessionid =  models.CharField(max_length=250, blank=True, null=True, default=None)

    ext_user_username = models.CharField(max_length=250, blank=True, null=True, default=None)
    lis_person_name_given = models.CharField(max_length=250, blank=True, null=True, default=None)
    lis_person_name_family = models.CharField(max_length=250, blank=True, null=True, default=None)
    lis_person_name_full = models.CharField(max_length=250, blank=True, null=True, default=None)
    lis_person_contact_email_primary = models.CharField(max_length=250, blank=True, null=True, default=None)

    class Meta:
        unique_together = [['consumer', 'user'], ['consumer', 'user_username']]


class LTICourse(models.Model):
    consumer = models.ForeignKey(LTIConsumer, null=False, blank=False, default=None, on_delete=models.CASCADE)
    course_code = models.CharField(max_length=250, blank=False, null=False, default=None)

    course = models.ForeignKey(Course, null=True, blank=True, default=None, on_delete=models.CASCADE)

    custom_domain_coditercers = models.CharField(max_length=10, blank=True, null=True, default=None)
    custom_domain_year = models.CharField(max_length=10, blank=True, null=True, default=None)
    custom_domain_semester = models.CharField(max_length=10, blank=True, null=True, default=None)
    custom_domain_pt_template = models.CharField(max_length=250, blank=True, null=True, default=None)

    context_id = models.CharField(max_length=250, blank=True, null=True, default=None)
    context_title = models.CharField(max_length=250, blank=True, null=True, default=None)
    context_label = models.CharField(max_length=250, blank=True, null=True, default=None)

    class Meta:
        unique_together = [['consumer', 'course_code'], ]


class LTIGroup(models.Model):
    consumer = models.ForeignKey(LTIConsumer, null=False, blank=False, default=None, on_delete=models.CASCADE)
    group_code = models.CharField(max_length=250, blank=False, null=False, default=None)

    group = models.ForeignKey(CourseGroup, null=True, blank=True, default=None, on_delete=models.CASCADE)

    context_id = models.CharField(max_length=50, blank=True, null=True, default=None)
    context_label = models.CharField(max_length=250, blank=True, null=True, default=None)
    context_title = models.CharField(max_length=250, blank=True, null=True, default=None)

    custom_domain_id = models.CharField(max_length=10, blank=True, null=True, default=None)
    custom_domain_code = models.CharField(max_length=50, blank=True, null=True, default=None)

    class Meta:
        unique_together = [['consumer', 'group_code']]

