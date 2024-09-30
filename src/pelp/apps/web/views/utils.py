"""
    PeLP utility module for Views
"""
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.translation import gettext as _, get_language_from_request
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from pelp.apps.web import models
from pelp.apps.web import lib as pelp_lib
from ..forms import FeedbackForm, ActivityForm, ProjectForm, ProjectModuleForm, FaqForm, FaqSearchForm


class Http403(HttpResponse):
    """
        Standard 403 view
    """
    status_code = 403


def admin_or_instructor(request, activity):
    """
        Check whether the authenticated user is administrator or instructor for the course where the activity belongs to
        :param request: HTTP request with authentication information
        :param activity: Test activity
        :return: True if the current authenticated user is administrator or instructor. False otherwise.
    """
    if request.user is None or not request.user.is_authenticated:
        return False
    if request.user.is_staff:
        return True
    return models.Activity.objects.filter(
            id=activity.id,
            course__coursegroup__instructor__user=request.user
    ).count() > 0


def admin_or_learner(request, activity):
    """
        Check whether the authenticated user is administrator or learner for the course where the activity belongs to
        :param request: HTTP request with authentication information
        :param activity: Test activity
        :return: True if the current authenticated user is administrator or learner. False otherwise.
    """
    if request.user is None or not request.user.is_authenticated:
        return False
    if request.user.is_staff:
        return True
    return models.Activity.objects.filter(
            id=activity.id,
            course__coursegroup__learner__user=request.user
    ).count() > 0
