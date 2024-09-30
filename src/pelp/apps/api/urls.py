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
from django.conf.urls import include
from django.urls import re_path
from rest_framework_extensions.routers import ExtendedSimpleRouter
from rest_framework_simplejwt import views as jwt_views

from . import views
from . import apps

# Create the base router
router = ExtendedSimpleRouter()

import_router = router.register(r'import_session', views.ImportSessionViewSet)
import_entry_router = import_router.register(r'entry', views.ImportSessionEntryViewSet,
                                             basename='import-session-entry',
                                             parents_query_lookups=['session_id']
                                             )

course_router = router.register(r'course', views.CourseViewSet, basename='course')
course_activity_router = course_router.register(r'activity',
                                                views.CourseActivityViewSet,
                                                basename='course-activity',
                                                parents_query_lookups=['course_id']
                                                )
course_learner = course_router.register(r'learner',
                                        views.CourseLearnersViewSet,
                                        basename='course-learner',
                                        parents_query_lookups=['groups__course_id']
                                        )
course_group_router = course_router.register(r'group',
                                             views.CourseGroupViewSet,
                                             basename='course-group',
                                             parents_query_lookups=['course_id']
                                             )

course_group_learner_router = course_group_router.register(r'learner',
                                                           views.CourseGroupLearnersViewSet,
                                                           basename='course-group-learner',
                                                           parents_query_lookups=['groups__course_id', 'groups__id']
                                                           )

course_activity_file_router = course_activity_router.register(r'file',
                                                              views.CourseActivityFileViewSet,
                                                              basename='course-activity-file',
                                                              parents_query_lookups=['project__activity__course_id',
                                                                                     'project__activity_id']
                                                              )

course_activity_test_router = course_activity_router.register(r'test',
                                                              views.CourseActivityTestViewSet,
                                                              basename='course-activity-test',
                                                              parents_query_lookups=['project__activity__course_id',
                                                                                     'project__activity_id']
                                                              )

course_activity_project_router = course_activity_router.register(r'project',
                                                                 views.CourseActivityProjectViewSet,
                                                                 basename='course-activity-project',
                                                                 parents_query_lookups=['activity__course_id',
                                                                                        'activity_id']
                                                                 )


course_activity_submission_router = course_activity_router.register(r'submission',
                                                                    views.CourseActivitySubmissionViewSet,
                                                                    basename='course-activity-submission',
                                                                    parents_query_lookups=['activity__course_id',
                                                                                           'activity_id']
                                                                    )

course_activity_my_submissions_router = course_activity_router.register(r'my_submissions',
                                                                        views.CourseActivityMySubmissionsViewSet,
                                                                        basename='course-activity-my-submissions',
                                                                        parents_query_lookups=['activity__course_id',
                                                                                               'activity_id']
                                                                        )

course_activity_submission_file_router = course_activity_submission_router.register(
    r'file',
    views.CourseActivitySubmissionFileViewSet,
    basename='course-activity-submission-file',
    parents_query_lookups=['submission__activity__course_id', 'submission__activity_id', 'submission_id']
)

course_activity_submission_error_router = course_activity_submission_router.register(
    r'error',
    views.CourseActivitySubmissionErrorViewSet,
    basename='course-activity-submission-error',
    parents_query_lookups=['submission__activity__course_id', 'submission__activity_id', 'submission_id']
)

course_activity_submission_test_result_router = course_activity_submission_router.register(
    r'test',
    views.CourseActivitySubmissionTestResultViewSet,
    basename='course-activity-submission-test-result',
    parents_query_lookups=['submission__activity__course_id', 'submission__activity_id', 'submission_id']
)

course_activity_report_router = course_activity_router.register(r'report',
                                                                    views.CourseActivityReportViewSet,
                                                                    basename='course-activity-report',
                                                                    parents_query_lookups=['course_id',
                                                                                           'activity_id']
                                                                    )

course_activity_module_router = course_activity_router.register(r'module',
                                                                views.CourseActivityModuleViewSet,
                                                                basename='course-activity-module',
                                                                parents_query_lookups=['project__activity__course_id',
                                                                                       'project__activity_id']
                                                                )

faq_router = router.register(r'faq', views.FaqViewSet, basename='faq')

app_name = apps.ApiConfig.name
urlpatterns = [
    re_path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    re_path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path('profile/', views.ProfileViewSet.as_view({'get': 'retrieve'}), name='profile'),
    re_path('', include(router.urls)),
]
