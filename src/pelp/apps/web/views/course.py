"""
    PeLP Views related to Courses
"""
from django.utils.translation import gettext as _, get_language
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from pelp.apps.web import models
from ..forms import ActivityForm


@login_required
def courses(request):
    """
        Show the list of courses
        :param request:  Current HTTP request
        :return: Rendered HTML content
    """
    context = {
        'page': _('Courses'),
        'active_menu': 'Courses',
        'show_breadcrum': True,
        'breadcrum_elems': [],
    }

    return render(request, 'web/pages/courses.html', context)


@login_required
def course_detail(request, id):
    """
        Manage the details of a Course
        :param request:  Current HTTP request
        :param id: Course ID
        :return: Rendered HTML content
    """
    if request.method == "POST":
        form_activity = ActivityForm(request.POST)
        if form_activity.is_valid():
            activity = form_activity.save()
            return redirect('activity_configuration', course_id=id, id=activity.id)

    course = get_object_or_404(models.Course, id=id)
    context = {
        'page': course.code,
        'show_breadcrum': True,
        'active_menu': 'Courses',
        'breadcrum_elems': [
            {'name': _('Courses'), 'url': '/course/'}
        ],
        'course': course,
        'form_activity': ActivityForm(initial={'course': id})
    }

    return render(request, 'web/pages/course_detail.html', context)

@login_required
def course_learners(request, course_id):
    """
        Import course learners
        :param request:  Current HTTP request
        :param id: Course ID
        :return: Rendered HTML content
    """
    course = get_object_or_404(models.Course, id=course_id)
    context = {
        'page': _('Learners'),
        'show_breadcrum': True,
        'active_menu': 'Courses',
        'breadcrum_elems': [
            {'name': _('Courses'), 'url': '/course/'},
            {'name': course.code, 'url': f'/course/{course_id}/'},
        ],
        'course': course,
        #'form_group': ActivityForm(initial={'course': id})
    }

    return render(request, 'web/pages/import_course_learners.html', context)
