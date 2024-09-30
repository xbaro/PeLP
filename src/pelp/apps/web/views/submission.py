"""
    PeLP Views related to Submissions
"""
from django.utils.translation import gettext as _
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from pelp.apps.web import models

from .utils import Http403, admin_or_instructor


@login_required
def submissions(request, course_id, activity_id):
    """
        Show the list of submissions for a given activity
        :param request: Current HTTP request
        :param course_id: Course ID
        :param activity_id: Activity ID
        :return: Rendered HTML content
    """
    activity = get_object_or_404(models.Activity, id=activity_id, course_id=course_id)
    if not admin_or_instructor(request, activity):
        return Http403()
    context = {
        'page': _('Submissions'),
        'show_breadcrum': False,
        'activity': activity
    }

    return render(request, 'web/pages/submissions.html', context)


@login_required
def submission_detail(request, course_id, activity_id, id):
    """
        Show learner's submission details
        :param request: Current HTTP request
        :param course_id: Course ID
        :param activity_id: Activity ID
        :param id: Submission ID
        :return: Rendered HTML content
    """
    submission = get_object_or_404(models.Submission, activity__course_id=course_id, activity_id=activity_id, id=id)

    if admin_or_instructor(request, submission.activity):
        breadcum_elems = [
            {'name': _('Submissions'), 'url': '/course/{}/activity/{}/submissions/'.format(course_id, activity_id)}
        ]
    elif submission.learner.user == request.user:
        breadcum_elems = [
            {'name': _('Courses'), 'url': '/course/'},
            {'name': submission.activity.course.code, 'url': '/course/{}/'.format(course_id)},
            {'name': submission.activity.code, 'url': '/course/{}/activity/{}/'.format(course_id, activity_id)}
        ]
    else:
        return Http403()

    context = {
        'page': '{} {}'.format(_('Submission'), id),
        'show_breadcrum': True,
        'active_menu': 'Courses',
        'breadcrum_elems': breadcum_elems,
        'submission': submission
    }

    return render(request, 'web/pages/activity_report_detail.html', context)
