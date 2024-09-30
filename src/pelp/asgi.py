"""
ASGI config for pelp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.urls import re_path
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pelp.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app  = get_asgi_application()

# pylint: disable=wrong-import-position
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from pelp.apps.web.consumers import activity, submission

asgi_app = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    # WebSocket event handler
    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path(r'^ws/activity/(?P<activity_id>\w+)/$', activity.ActivityEventConsumer.as_asgi()),
            re_path(r'^ws/activity/(?P<activity_id>\w+)/my_submissions/$', submission.SubmissionEventConsumer.as_asgi()),
        ])
    ),
})

# pylint: disable=wrong-import-order
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
application = SentryAsgiMiddleware(asgi_app)
