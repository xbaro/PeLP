"""
    PeLP Views related to Frequently Asked Questions (FAQ)
"""
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.db.models import Q
from django.utils.translation import gettext as _, get_language_from_request
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from pelp.apps.web import models
from pelp.apps.web import lib as pelp_lib
from ..forms import FaqForm, FaqSearchForm


@login_required
@vary_on_headers('Content-Language')
#@cache_page(60 * 15)
def faq(request):
    """
        List and filter FAQ entries
        :param request:  Current HTTP request
        :return: Rendered HTML content
    """
    form_search = FaqSearchForm(request.GET)
    criteria = False
    if form_search.is_valid():
        search_result = models.TranslateFaq.objects
        if form_search.cleaned_data['search'] is not None:
            criteria = True
            search_result = search_result.search(form_search.cleaned_data['search']).order_by('-search_score')
        tag_filter = None
        for tag in form_search.cleaned_data['tags']:
            if tag_filter is None:
                tag_filter = Q(faq__tags=tag)
            else:
                tag_filter = tag_filter | Q(faq__tags=tag)
        if tag_filter is not None:
            criteria = True
            search_result = search_result.filter(tag_filter)
        lang_filter = None
        for lang in form_search.cleaned_data['language']:
            if lang_filter is None:
                lang_filter = Q(language=lang)
            else:
                lang_filter = lang_filter | Q(language=lang)
        if lang_filter is not None:
            criteria = True
            search_result = search_result.filter(lang_filter)
        if criteria:
            search_result = search_result.distinct().all()
        else:
            search_result = models.TranslateFaq.objects
            if 'filter' not in form_search.data:
                query_language = get_language_from_request(request)
                form_search = FaqSearchForm({'language': query_language})
                search_result = search_result.filter(language=query_language)
            search_result = search_result.distinct().order_by('-updated_at').all()

        # Hide not public FAQs
        if not request.user.is_staff:
            search_result = search_result.filter(faq__public=True)

        paginator = Paginator(search_result, 6)
        page = request.GET.get('page')
        try:
            search_result = paginator.get_page(page)
        except PageNotAnInteger:
            search_result = paginator.get_page(1)
        except InvalidPage:
            search_result = paginator.get_page(1)
        except EmptyPage:
            search_result = paginator.get_page(paginator.num_pages)

    context = {
        'page': _('FAQ'),
        'show_breadcrum': True,
        'active_menu': 'FAQ',
        'form_search': form_search,
        'search_result': search_result,
        'breadcrum_elems': [],
        'tags_list': pelp_lib.faq.get_tag_histogram(request.user.is_staff)
    }

    return render(request, 'web/pages/faq.html', context)


@login_required
def faq_view(request, faq_id):
    """
        Show the content of a FAQ entry
        :param request:  Current HTTP request
        :param faq_id: FAQ entry ID
        :return: Rendered HTML content
    """
    faq = get_object_or_404(models.Faq, id=faq_id)
    language = request.GET.get('language')
    if language is None:
        language = get_language_from_request(request)

    context = {
        'page': '{} {}'.format(_('FAQ'), faq_id),
        'show_breadcrum': True,
        'active_menu': 'FAQ',
        'faq': faq,
        'language': language,
        'breadcrum_elems': [{'name': _('FAQ'), 'url': '/faq'}],
    }

    return render(request, 'web/pages/faq.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def faq_edit(request, faq_id=None):
    """
        Edit or create the content of a FAQ entry
        :param request:  Current HTTP request
        :param faq_id: FAQ entry ID
        :return: Rendered HTML content
    """
    if faq_id is not None:
        faq = get_object_or_404(models.Faq, id=faq_id)
        form_faq = FaqForm(instance=faq)
    else:
        faq = None
        form_faq = FaqForm()

    context = {
        'page': _('Edit'),
        'active_menu': 'FAQ',
        'show_breadcrum': True,
        'faq': faq,
        'form_faq': form_faq,
        'breadcrum_elems': [
            {'name': _('FAQ'), 'url': '/faq'},
            {'name': '{} {}'.format(_('FAQ'), faq_id), 'url': '/faq/{}/'.format(faq_id)}
        ],
    }

    if faq is None:
        context['page'] = _('New')
        context['breadcrum_elems'].pop()

    if request.method == "POST":

        form_faq = FaqForm(request.POST, instance=faq)
        if form_faq.is_valid():
            context['faq'] = form_faq.save()
            if 'action_save_view' in form_faq.data:
                return redirect('faq_view', faq_id=context['faq'].id)
        context['form_faq'] = form_faq

    return render(request, 'web/pages/faq_editor.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def faq_delete(request, faq_id):
    """
        Delete a FAQ entry
        :param request:  Current HTTP request
        :param faq_id: FAQ entry ID
        :return: Redirection to the list of FAQ entries
    """
    faq = get_object_or_404(models.Faq, id=faq_id)
    faq.delete()
    return redirect('faq_list')
