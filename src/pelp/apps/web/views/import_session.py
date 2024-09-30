"""
    PeLP Views related to Import Sessions
"""
from django.utils.translation import gettext as _
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

from pelp.apps.web import models


@login_required
@user_passes_test(lambda u: u.is_superuser)
def import_sessions(request):
    """
        Show the list of all available Import Sessions
        :param request:  Current HTTP request
        :return: Rendered HTML content
    """
    context = {
        'page': _('Import Sessions'),
        'active_menu': 'Import',
        'show_breadcrum': True,
        'breadcrum_elems': [],
    }

    return render(request, 'web/pages/import_sessions.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def import_session_detail(request, id):
    """
        Show the detail of an Import Session
        :param request: Current HTTP request
        :param id: Session ID
        :return: Rendered HTML content
    """
    session = get_object_or_404(models.ImportSession, id=id)
    context = {
        'page': '{} {}'.format(_('Session'), id),
        'show_breadcrum': True,
        'active_menu': 'Import',
        'breadcrum_elems': [
            {'name': _('Import Sessions'), 'url': '/import'}
        ],
        'session': session,
    }

    return render(request, 'web/pages/import_session_details.html', context)
