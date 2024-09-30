"""
    PeLP Web application URLs
"""
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('course/', views.courses, name='courses'),
    path('course/<int:id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/activity/<int:id>/', views.activity_detail, name='activity_detail'),
    path('course/<int:course_id>/activity/<int:id>/edit/', views.activity_configuration, name='activity_configuration'),
    path('course/<int:course_id>/activity/<int:id>/report/', views.activity_report, name='activity_report'),
    path('course/<int:course_id>/activity/<int:id>/statistics/', views.activity_statistics, name='activity_statistics'),
    path('course/<int:course_id>/activity/<int:activity_id>/report/<int:id>/', views.activity_report_detail,
         name='activity_report_detail'),
    path('projects', views.projects, name='projects'),
    path('project/<int:id>/', views.project_details, name='project_details'),

    path('import/', views.import_sessions, name='import_sessions'),
    path('import/<int:id>/', views.import_session_detail, name='import_sessions_detail'),

    path('course/<int:course_id>/activity/<int:activity_id>/submissions/', views.submissions, name='activity_submissions'),
    path('course/<int:course_id>/activity/<int:activity_id>/submissions/<int:id>/', views.submission_detail, name='activity_submissions_detail'),

    path('course/<int:course_id>/activity/<int:activity_id>/evaluate/', views.activity_evaluation, name='activity_evaluation'),
    path('course/<int:course_id>/activity/<int:activity_id>/evaluate/<int:group_id>/', views.activity_evaluation_group, name='activity_evaluation_group'),

    #path('course/<int:course_id>/group/', views.course_groups, name='course_groups'),
    #path('course/<int:course_id>/group/<int:id>/', views.course_group_info, name='course_group_detail'),
    path('course/<int:course_id>/learner/', views.course_learners, name='import_course_learners'),


    path('faq/', views.faq, name='faq_list'),
    path('faq/<int:faq_id>/', views.faq_view, name='faq_view'),
    path('faq/new/', views.faq_edit, name='faq_create'),
    path('faq/<int:faq_id>/edit/', views.faq_edit, name='faq_edit'),
    path('faq/<int:faq_id>/delete/', views.faq_delete, name='faq_delete'),
]
