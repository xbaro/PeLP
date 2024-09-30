import re
import sentry_sdk
import humanize
from django import template
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import gettext as _
from pelp.apps.web import models

register = template.Library()

@register.simple_tag()
def pelp_version():
    return settings.PELP_VERSION or "N/A"

@register.filter(name='increment')
def increment(value, arg=1):
    return value + arg


@register.filter(name='is_instructor')
def is_instructor(value, arg=None):
    if arg is None:
        return False
    if not isinstance(arg, User):
        return False
    if isinstance(value, models.Course) and models.Course.objects.filter(
            id=value.id,
            coursegroup__instructor__user=arg
    ).count() > 0:
        return True
    if isinstance(value, models.Activity) and models.Activity.objects.filter(
            id=value.id,
            course__coursegroup__instructor__user=arg
    ).count() > 0:
        return True
    if isinstance(value, models.CourseGroup) and models.CourseGroup.objects.filter(
        id=value.id,
        instructor__user=arg
    ).count() > 0:
        return True
    return False

@register.filter(name='is_learner')
def is_learner(value, arg=None):
    if arg is None:
        return False
    if not isinstance(arg, User):
        return False
    if isinstance(value, models.Course) and models.Course.objects.filter(
            id=value.id,
            coursegroup__learner__user=arg
    ).count() > 0:
        return True
    if isinstance(value, models.Activity) and models.Activity.objects.filter(
            id=value.id,
            course__coursegroup__learner__user=arg
    ).count() > 0:
        return True
    if isinstance(value, models.CourseGroup) and models.CourseGroup.objects.filter(
        id=value.id,
        learner__user=arg
    ).count() > 0:
        return True

    return False


@register.filter(name='mem_size')
def mem_size(value):
    if value is None:
        return 0
    if isinstance(value, str) and not value.isnumeric():
        return 0
    return humanize.naturalsize(value)


@register.simple_tag(takes_context=True)
def course_user_role(context):
    request = context.get('request')
    if request is not None:
        if request.user.is_staff:
            return _("Administrator")
        course_match = re.search(r'^/course/(\d+)/.*$', request.path)
        if course_match is not None:
            course_id = int(course_match.group(1))
            course = models.Course.objects.get(id=course_id)
            if course.is_instructor(request.user):
                return _("Instructor")
            elif course.is_learner(request.user):
                return _("Learner")
    return ''


@register.simple_tag(takes_context=True)
def update_request_with_query(context, **kwargs):
    request = context.get('request')
    if request is not None:
        updated = request.GET.copy()
        for k, v in kwargs.items():
            updated[k] = v
        return request.build_absolute_uri('?{}'.format(updated.urlencode()))
    return '#'


@register.filter(name='trans_name')
def trans_name(value, arg=None):
    if arg is None:
        return value.name
    return value.get_translated_name(arg)


@register.filter(name='trans_description')
def trans_description(value, arg=None):
    if arg is None:
        return value.description
    return value.get_translated_description(arg)


@register.filter(name='trans_title')
def trans_title(value, arg=None):
    return value.get_translated_title(arg)


@register.filter(name='trans_content')
def trans_content(value, arg=None):
    return value.get_translated_content(arg)


@register.filter(name='trans_tag')
def trans_tag(value, arg=None):
    if arg is None:
        return value.tag
    return value.get_translated_tag(arg)


@register.filter(name='total_submissions')
def total_submissions(value, arg=None):
    if arg is None:
        return '-'
    if not isinstance(arg, User) or not isinstance(value, models.Activity):
        return '-'
    try:
        learner = arg.learner
        return value.num_learner_submissions(learner)
    except models.Learner.DoesNotExist:
        return '-'

    return '-'


@register.filter(name='day_submissions')
def day_submissions(value, arg=None):
    if arg is None:
        return '-'
    if not isinstance(arg, User) or not isinstance(value, models.Activity):
        return '-'
    try:
        learner = arg.learner
        return value.num_learner_submissions_day(learner)
    except models.Learner.DoesNotExist:
        return '-'

    return '-'


@register.filter(name='list_pos')
def list_pos(value, arg=0):
    return value[arg]


@register.filter(name='lang_form_name_element')
def lang_form_name_element(form, language):
    return form.get_lang_field_element(language[0], 'name')


@register.filter(name='lang_form_description_element')
def lang_form_description_element(form, language):
    return form.get_lang_field_element(language[0], 'description')

@register.filter(name='lang_form_title_element')
def lang_form_title_element(form, language):
    return form.get_lang_field_element(language[0], 'title')

@register.filter(name='lang_form_content_element')
def lang_form_content_element(form, language):
    return form.get_lang_field_element(language[0], 'content')


@register.filter(name='lang_form_name_element_id')
def lang_form_name_element_id(form, language):
    return form.get_lang_field_element(language[0], 'name').id_for_label


@register.filter(name='lang_form_description_element_id')
def lang_form_description_element_id(form, language):
    return form.get_lang_field_element(language[0], 'description').id_for_label

@register.filter(name='lang_form_title_element_id')
def lang_form_title_element_id(form, language):
    return form.get_lang_field_element(language[0], 'title').id_for_label

@register.filter(name='lang_form_content_element_id')
def lang_form_content_element_id(form, language):
    return form.get_lang_field_element(language[0], 'content').id_for_label

@register.filter(name='num_pending_evaluations')
def num_pending_evaluations(value, arg=None):
    if isinstance(value, models.Course) or isinstance(value, models.Activity):
        return value.num_pending_evaluations()
    if isinstance(value, models.CourseGroup):
        if arg is not None:
            return value.num_pending_evaluations(arg)
        return True
    return None

@register.simple_tag(takes_context=False)
def get_sentry_config():
    debug = 'false'
    if settings.SENTRY_DEBUG:
        debug = 'true'
    return {
        'enabled': settings.SENTRY_ENABLED,
        'dsn': settings.SENTRY_DSN,
        'sample_rate': settings.SENTRY_SAMPLE_RATE,
        'debug': debug,
        'release': settings.SENTRY_RELEASE,
        'environment': settings.SENTRY_ENVIRONMENT,
        'server_name': settings.SENTRY_SERVER_NAME,
    }


@register.filter(name='faq_rating')
def faq_rating(value, arg=None):
    if arg is None:
        return 0
    if not isinstance(arg, User):
        return 0
    if isinstance(value, models.Faq):
        return value.get_learner_rating(arg)
    return 0
