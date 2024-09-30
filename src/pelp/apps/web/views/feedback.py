"""
    PeLP Views related to activity evaluation and feedback
"""
from django.db.models import Q
from django.utils.translation import gettext as _
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from pelp.apps.web import models

from .utils import Http403, admin_or_instructor
from ..forms import FeedbackForm


@login_required
def activity_evaluation(request, course_id, activity_id):
    """
        Show the list of groups with missing evaluations
        :param request: Current HTTP request
        :param course_id: Course ID
        :param activity_id: Activity ID
        :return: Rendered HTML content
    """
    activity = get_object_or_404(models.Activity, id=activity_id, course_id=course_id)
    if not admin_or_instructor(request, activity):
        return Http403()
    context = {
        'page': _('Evaluation'),
        'show_breadcrum': True,
        'activity': activity,
        'breadcrum_elems': [
            {'name': _('Courses'), 'url': '/course/'},
            {'name': activity.course.code, 'url': '/course/{}/'.format(course_id)},
            {'name': activity.code, 'url': '/course/{}/activity/{}/'.format(course_id, activity_id)}
        ],
    }
    return render(request, 'web/pages/evaluation.html', context)


def _get_next_evaluation_feedback_form(activity, results_qs, offset):
    """
        Instantiate the feedback form for the following learner in current course, activity and group
        :param activity: Activity object
        :param results_qs: QuerySet object with all submissions
        :param offset: Current offset in the results_qs
        :return: Instantiated Form object
    """
    learner_result = None
    feedback_object = None
    total = results_qs.count()
    if total > 0:
        learner_result = results_qs.order_by('learner__last_name', 'learner__first_name', 'learner_id')[offset]
        try:
            feedback_object = activity.activityfeedback_set.filter(learner=learner_result.learner).get()
        except models.ActivityFeedback.DoesNotExist:
            feedback_object = models.ActivityFeedback.objects.create(
                activity=activity,
                learner=learner_result.learner
            )
    if learner_result is not None:
        try:
            feedback_object = activity.activityfeedback_set.filter(learner=learner_result.learner).get()
        except models.ActivityFeedback.DoesNotExist:
            feedback_object = models.ActivityFeedback.objects.create(
                activity=activity,
                learner=learner_result.learner
            )
    return learner_result, FeedbackForm(instance=feedback_object)


@login_required
def activity_evaluation_group(request, course_id, activity_id, group_id):
    """
        Show the feedback information for a certain group
        :param request: Current HTTP request
        :param course_id: Course ID
        :param activity_id: Activity ID
        :param group_id: Course Group ID
        :return: Rendered HTML content
    """
    activity = get_object_or_404(models.Activity, id=activity_id, course_id=course_id)
    if not admin_or_instructor(request, activity):
        return Http403()

    group = get_object_or_404(models.CourseGroup, id=group_id, course_id=course_id)
    if not request.user.is_staff and group.instructor_set.filter(user=request.user).count() == 0:
        return Http403()

    results_qs = activity.learnerresult_set.filter(
        learner_id__gte=0,
        learner__groups=group
    )

    use_filter = int(request.GET.get('filter', 0))
    if use_filter == 1:
        results_qs = results_qs.filter(
            Q(
                learner__activityfeedback__isnull=True
            ) | Q(
                learner__activityfeedback__score__isnull=True,
                learner__activityfeedback__is_np=False,
                learner__activityfeedback__activity=activity
            ),
        )
    results_qs = results_qs.distinct()
    total = results_qs.count()
    offset = int(request.GET.get('offset', 0))
    prev_page = None
    next_page = None
    if offset > 0:
        prev_page = '?offset={}'.format(offset - 1)
    if offset < total - 1:
        next_page = '?offset={}'.format(offset + 1)
    if use_filter == 1:
        if prev_page is not None:
            prev_page += '&filter=1'
        if next_page is not None:
            next_page += '&filter=1'

    context = {
        'page': group.name,
        'show_breadcrum': True,
        'activity': activity,
        'group': group,
        'total': total,
        'current_page': offset,
        'next_page': next_page,
        'prev_page': prev_page,
        'learner_result': None,
        'feedback_form': None,
        'breadcrum_elems': [
            {'name': _('Courses'), 'url': '/course/'},
            {'name': activity.course.code, 'url': '/course/{}/'.format(course_id)},
            {'name': activity.code, 'url': '/course/{}/activity/{}/'.format(course_id, activity_id)},
            {'name': _('Evaluation'), 'url': '/course/{}/activity/{}/evaluate/'.format(course_id, activity_id)}
        ],
        'filter': use_filter
    }
    learner_result = None
    feedback_form = None
    if request.method == 'GET':
        learner_result, feedback_form = _get_next_evaluation_feedback_form(activity, results_qs, offset)
    elif request.method == 'POST':
        feedback_form = FeedbackForm(request.POST)
        learner_result = get_object_or_404(models.LearnerResult,
                                           learner_id=feedback_form.data['learner'],
                                           activity_id=feedback_form.data['activity'])
        feedback_object = get_object_or_404(models.ActivityFeedback,
                                            learner_id=feedback_form.data['learner'],
                                            activity_id=feedback_form.data['activity'])
        feedback_form = FeedbackForm(request.POST, instance=feedback_object)
        if feedback_form.is_valid():
            feedback_form.save()
            if use_filter == 1:
                learner_result, feedback_form = _get_next_evaluation_feedback_form(activity, results_qs, offset)

    context['feedback_form'] = feedback_form
    context['learner_result'] = learner_result

    return render(request, 'web/pages/evaluation_group.html', context)
