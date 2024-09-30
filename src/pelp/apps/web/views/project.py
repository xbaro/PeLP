"""
    PeLP Views related to activity project management
"""
from django.utils.translation import gettext as _
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def projects(request):
    """
        Show the list of projects
        :param request: Current HTTP request
        :return: Rendered HTML content
    """
    context = {
        'page': _('Projects'),
        'active_menu': 'Projects',
        'show_breadcrum': True,
        'breadcrum_elems': [],
    }

    return render(request, 'web/pages/projects.html', context)


@login_required
def project_details(request, id):
    """
        Show the details of a project
        :param request: Current HTTP request
        :param id: Project ID
        :return: Rendered HTML content
    """
    context = {
        'page': '{} {}'.format(_('Project'), id),
        'show_breadcrum': True,
        'breadcrum_elems': [
            {'name': _('Projects'), 'url': '/projects'}
        ],
    }

    return render(request, 'web/pages/project_details.html', context)
