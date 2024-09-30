"""
    PeLP URL Configuration
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from django.utils import translation, timezone
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.views.decorators.http import last_modified
from django.views.i18n import JavaScriptCatalog

from rest_framework import routers, serializers, viewsets


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
        Users basic serializer
    """

    # pylint: disable=missing-class-docstring
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


class UserViewSet(viewsets.ModelViewSet):
    """
        Users view
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


def set_language_from_url(request, user_language):
    """
        Change the visualization language
    """
    translation.activate(user_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    response = redirect('index')
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
    return response


app_name = 'pelp'
last_modified_date = timezone.now()
urlpatterns = [
    # Internationalization
    re_path(r'set_language/(?P<user_language>\w+)/', set_language_from_url, name="set_language_from_url"),
    path('jsi18n/',
         last_modified(lambda req, **kw: last_modified_date)(JavaScriptCatalog.as_view()),
         name='javascript-catalog'),

    path('admin/', admin.site.urls),
    path('', include('pelp.apps.web.urls')),
    path('api/', include('pelp.apps.api.urls', namespace='api')),
    path('', include('pelp.apps.lti.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
    path('select2/', include("django_select2.urls")),
    path('', include('django_prometheus.urls')),
]
