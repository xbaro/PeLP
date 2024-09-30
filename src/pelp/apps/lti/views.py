import base64
import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from django.utils import translation

from lti_toolbox.exceptions import LTIException
from lti_toolbox.lti import LTI, LaunchParams
from lti_toolbox.views import BaseLTIAuthView, BaseLTIView

from oauthlib.common import CaseInsensitiveDict
from sentry_sdk import capture_message, capture_exception

from .consumer import get_consumer_from_request


class ExtendedBaseLTIView(BaseLTIView):

    def get(self, request, *args, **kwargs) -> HttpResponse:  # pylint: disable=W0613
        context = {
            'domain': self.request.META['HTTP_HOST'],
            'launch_url': self.request.build_absolute_uri(reverse('lti.authentication')),
        }

        return render(self.request, "lti/lti_cartidge.xml",
                      content_type='text/xml',
                      context=context,
                      )


class ExtendedBaseLTIAuthView(BaseLTIAuthView):

    def get(self, request, *args, **kwargs) -> HttpResponse:  # pylint: disable=W0613
        context = {
            'domain': self.request.META['HTTP_HOST'],
            'launch_url': self.request.build_absolute_uri(reverse('lti.authentication')),
        }

        return render(self.request, "lti/lti_cartidge.xml",
                      content_type='text/xml',
                      context=context,
                      )


class SimpleLaunchURLVerification(ExtendedBaseLTIView):
    """Example view to handle LTI launch request verification."""

    def _do_on_success(self, lti_request: LTI) -> HttpResponse:
        # Render a template with some debugging information
        context = {
            "message": "LTI request verified successfully",
        }
        return render(self.request, "lti/debug_infos.html", context)

    def _do_on_failure(self, request: HttpRequest, error: LTIException) -> HttpResponse:
        context = {
            "message": "INVALID LTI request (check your django logs for more details)",
            "message_class": "danger",
        }
        return render(self.request, "lti/debug_infos.html", context, status=403)


class LaunchURLWithAuth(ExtendedBaseLTIAuthView):
    """
    Example view to handle LTI launch request with user authentication.
    It relies on the `lti_toolbox.backend.LTIBackend` authentication backend that
    has been defined in the `AUTHENTICATION_BACKENDS` setting.
    """

    def _do_on_login(self, lti_request: LTI) -> HttpResponse:
        """Process the request when the user is logged in via LTI"""
        # Move to the course if it exists
        consumer = get_consumer_from_request(lti_request)
        response = redirect('index')
        if consumer is not None:
            course = consumer.get_course_profile()
            if course is not None and course.course is not None:
                response = redirect('course_detail', course.course.id)

        if lti_request.get_param('launch_presentation_locale'):
            user_language = lti_request.get_param('launch_presentation_locale')
            if lti_request.get_param('custom_lti_message_encoded_base64') == '1':
                user_language = base64.b64decode(user_language)
                if lti_request.get_param('custom_lti_message_encoded_utf8') == '1':
                    user_language = user_language.decode('utf-8')
                else:
                    user_language = user_language.decode()
            if '_' in user_language:
                user_language = user_language.split('_')[0]
            # UOC use a non standard language codification
            if '-' in user_language:
                user_language = user_language.split('-')[0]

            translation.activate(user_language)            

            self.request.session[translation.LANGUAGE_SESSION_KEY] = user_language
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)

        return response

    def _do_on_authentication_failure(self, lti_request: LTI) -> HttpResponse:
        """ Redirects user to an error page """
        capture_message('LTI: Authentication error')
        try:
            request = lti_request.request
            params = LaunchParams(request.POST)

            capture_message('LTI: Authentication error. {}'.format(json.dumps({
                "url": request.build_absolute_uri(),
                "body": params.urlencoded,
                "http_method": request.method,
                "headers": CaseInsensitiveDict(request.headers)
            })))
        except Exception as exc:
            capture_exception(exc)
        return super()._do_on_authentication_failure(lti_request)

    def _do_on_verification_failure(self, request: HttpRequest, error: LTIException) -> HttpResponse:
        capture_message('LTI: Verification failure')
        try:
            capture_message('LTI: Verification failure.\n {}\n{}\n'.format(error, json.dumps(request)))
        except Exception as exc:
            capture_exception(exc)
        return super()._do_on_verification_failure(request, error)
