from lti_toolbox import backend
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from .consumer import get_consumer_from_request


class LTIBackend(backend.LTIBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user from a LTI request

        Args:
            request: django http request
            username: The (optional) username to authenticate
            password: The (optional) password of the user to authenticate
            kwargs: additional parameters

        Returns:
            An authenticated user or None
        """
        lti_request = kwargs.get("lti_request")
        if not lti_request:
            return None

        if not lti_request.is_valid:
            raise PermissionDenied()

        consumer = get_consumer_from_request(lti_request)
        if consumer is None:
            raise PermissionDenied('Invalid consumer')

        return consumer.get_user()
