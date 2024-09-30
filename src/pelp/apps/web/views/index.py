"""
    PeLP Index views
"""
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from pelp.apps.web import models


@login_required
def index_view(request):
    """
        Show PeLP index
        :param request: Current HTTP request
        :return: Rendered HTML content
    """
    if request.user.is_staff:
        courses = models.Course.objects.filter(
            Q(semester__start__isnull=True) | Q(semester__start__lte=timezone.now()),
            Q(semester__end__isnull=True) | Q(semester__end__gte=timezone.now())
        ).distinct()
        activities = models.Activity.objects.filter(
            Q(start__isnull=True) | Q(start__lte=timezone.now()),
            Q(end__isnull=True) | Q(end__gte=timezone.now())
        ).distinct()
    else:
        courses = models.Course.objects.filter(
            Q(coursegroup__instructor__user=request.user) | Q(coursegroup__learner__user=request.user),
            Q(semester__start__isnull=True) | Q(semester__start__lte=timezone.now()),
            Q(semester__end__isnull=True) | Q(semester__end__gte=timezone.now())
        ).distinct()
        activities = models.Activity.objects.filter(
            Q(course__coursegroup__instructor__user=request.user) | Q(course__coursegroup__learner__user=request.user),
            Q(start__isnull=True) | Q(start__lte=timezone.now()),
            Q(end__isnull=True) | Q(end__gte=timezone.now())
        ).distinct()
    context = {
        'page': _('Dashboard'),
        'active_menu': 'Dashboard',
        'show_breadcrum': False,
        'breadcrum_elems': [],
        'courses': courses,
        'activities': activities,
    }
    return render(request, 'web/index.html', context)
