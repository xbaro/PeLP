"""
    PeLP Views related to Courses
"""
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from pelp.apps.web import models

from .utils import Http403, admin_or_instructor
from ..forms import ActivityForm, ProjectForm, ProjectModuleForm


@login_required
def activity_detail(request, course_id, id):
    """
        Show the detail of an Activity
        :param request:  Current HTTP request
        :param course_id: Course ID
        :param id: Activity ID
        :return: Rendered HTML content
    """
    activity = get_object_or_404(models.Activity, course_id=course_id, id=id)
    context = {
        'page': activity.code,
        'show_breadcrum': True,
        'active_menu': 'Courses',
        'breadcrum_elems': [
            {'name': _('Courses'), 'url': '/course/'},
            {'name': activity.course.code, 'url': '/course/{}/'.format(course_id)}
        ],
        'activity': activity
    }

    # If the user is instructor or admin, show activity detail
    if request.user.is_staff or activity.course.is_instructor(request.user):
        return render(request, 'web/pages/activity_report.html', context)
    elif not activity.course.is_learner(request.user):
        return redirect('index')

    try:
        activity_feedback = activity.activityfeedback_set.get(learner__user=request.user)
        if not activity_feedback.public:
            activity_feedback = None
    except models.ActivityFeedback.DoesNotExist:
        activity_feedback = None

    context['activity_feedback'] = activity_feedback
    context['activity_feedback_elements'] = activity.rubricelementinstantiation_set.filter(learner__user=request.user)
    try:
        context['last_submission'] = activity.submission_set.get(learner__user=request.user, is_last=True)
    except models.Submission.DoesNotExist:
        context['last_submission'] = None

    # Otherwise, go to submissions page
    return render(request, 'web/pages/submissions.html', context)


@login_required
def activity_configuration(request, course_id, id):
    """
        Manage activity configuration
        :param request:  Current HTTP request
        :param course_id: Course ID
        :param id: Activity ID
        :return: Rendered HTML content
    """
    activity = get_object_or_404(models.Activity, course_id=course_id, id=id)
    if not admin_or_instructor(request, activity):
        return Http403()

    if request.method == 'POST':
        if request.POST.get('src_form') == 'activity':
            form_activity = ActivityForm(request.POST, instance=activity)
            if form_activity.is_valid():
                form_activity.save()
                return JsonResponse({'success': True, 'error': None}, status=200)
            else:
                return JsonResponse({'success': False, 'error': form_activity.errors}, status=400)
        elif request.POST.get('src_form') == 'project':
            form_project = ProjectForm(request.POST, request.FILES, instance=activity.project)
            if form_project.is_valid():
                form_project.save()
                return JsonResponse({'success': True, 'error': None}, status=200)
            else:
                return JsonResponse({'success': False, 'error': form_project.errors}, status=400)
        elif request.POST.get('src_form') == 'project_module':
            form_project_module = ProjectModuleForm(request.POST)
            if form_project_module.data['id'] is not None and len(form_project_module.data['id'].strip()) > 0:
                project_module = activity.project.projectmodule_set.get(id=form_project_module.data['id'])
                form_project_module = ProjectModuleForm(request.POST, instance=project_module)
            if form_project_module.is_valid():
                form_project_module.save()
                return JsonResponse({'success': True, 'error': None}, status=200)
            else:
                return JsonResponse({'success': False, 'error': form_project_module.errors}, status=400)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid source'}, status=400)

    form_activity = ActivityForm(instance=activity)
    try:
        form_project = ProjectForm(instance=activity.project)
    except models.Project.DoesNotExist:
        activity.project = models.Project.objects.create(
            activity=activity
        )
        form_project = ProjectForm(instance=activity.project)
    form_project_module = ProjectModuleForm()
    context = {
        'page': activity.code,
        'show_breadcrum': True,
        'active_menu': 'Courses',
        'breadcrum_elems': [
            {'name': _('Courses'), 'url': '/course/'},
            {'name': activity.course.code, 'url': '/course/{}/'.format(course_id)}
        ],
        'activity': activity,
        'form_activity': form_activity,
        'form_project': form_project,
        'form_project_module': form_project_module,
    }

    return render(request, 'web/pages/activity_configuration.html', context)


@login_required
def activity_report(request, course_id, id):
    """
        Show the detail of an Activity
        :param request:  Current HTTP request
        :param course_id: Course ID
        :param id: Activity ID
        :return: Rendered HTML content
    """
    activity = get_object_or_404(models.Activity, course_id=course_id, id=id)
    if not admin_or_instructor(request, activity):
        return Http403()
    context = {
        'page': _('Report'),
        'show_breadcrum': True,
        'active_menu': 'Courses',
        'breadcrum_elems': [
            {'name': _('Courses'), 'url': '/course/'},
            {'name': activity.course.code, 'url': '/course/{}/'.format(course_id)},
            {'name': activity.code, 'url': '/course/{}/activity/{}/'.format(course_id, id)}
        ],
        'activity': activity
    }

    return render(request, 'web/pages/activity_report.html', context)


@login_required
def activity_report_detail(request, course_id, activity_id, id):
    """
        Show the report of an activity
        :param request:  Current HTTP request
        :param course_id: Course ID
        :param activity_id: Activity ID
        :param id: Activity's submission ID
        :return: Rendered HTML content
    """
    submission = get_object_or_404(models.Submission, activity__course_id=course_id, activity_id=activity_id, id=id)

    if not admin_or_instructor(request, submission.activity) and submission.learner.user != request.user:
        return Http403()

    context = {
        'page': '{} {}'.format(_('Submission'), id),
        'show_breadcrum': True,
        'active_menu': 'Courses',
        'breadcrum_elems': [
            {'name': _('Courses'), 'url': '/course/'},
            {'name': submission.activity.course.code, 'url': '/course/{}/'.format(course_id)},
            {'name': submission.activity.code, 'url': '/course/{}/activity/{}/'.format(course_id, activity_id)},
            {'name': _('Report'), 'url': '/course/{}/activity/{}/report/'.format(course_id, activity_id)}
        ],
        'submission': submission
    }

    return render(request, 'web/pages/activity_report_detail.html', context)


@login_required
def activity_statistics(request, course_id, id):
    """
        Show the statistic information for an activity
        :param request:  Current HTTP request
        :param course_id: Course ID
        :param id: Activity ID
        :return: Rendered HTML content
    """
    activity = get_object_or_404(models.Activity, course_id=course_id, id=id)
    if not admin_or_instructor(request, activity):
        return Http403()
    context = {
        'page': _('Results'),
        'show_breadcrum': True,
        'active_menu': 'Courses',
        'breadcrum_elems': [
            {'name': _('Courses'), 'url': '/course/'},
            {'name': activity.course.code, 'url': '/course/{}/'.format(course_id)},
            {'name': activity.code, 'url': '/course/{}/activity/{}/'.format(course_id, id)}
        ],
        'activity': activity
    }

    return render(request, 'web/pages/activity_statistics.html', context)
