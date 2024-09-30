"""pelp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . import views


urlpatterns = [
    # Simple LTI launch request verification
    path(
        "lti/launch-verification/",
        views.SimpleLaunchURLVerification.as_view(),
        name="lti.launch-url-verification",
    ),
    # LTI launch request handler with authentication
    path(
        "lti/",
        views.LaunchURLWithAuth.as_view(),
        name='lti.authentication',
    ),
    path(
        "lti",
        views.LaunchURLWithAuth.as_view(),
        name='lti.authentication_uoc',
    ),

    # Dynamic LTI launch request handler with authentication and a custom parameter (uuid)
    #path(
    #    "lti/launch/<uuid:uuid>/",
    #    lti.LaunchURLWithAuth.as_view(),
    #    name="lti.launch-url-auth-with-params",
    #),
]
