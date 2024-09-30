import datetime
import json

from sentry_sdk import capture_message
from rest_framework import viewsets, status
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework_extensions.mixins import NestedViewSetMixin
from pelp.apps.web import models
from pelp.apps.web.lib.submission import create_submission
from pelp.apps.web.lib.utils import get_test_results_structure
from . import serializers
from . import utils
from . import permissions


class ProfileViewSet(viewsets.ViewSet):
    serializer_class = serializers.ProfileSerializer

    def retrieve(self, request, pk=None):
        pk = request.user.pk
        profile = models.Profile.objects.get(user_id=pk)
        serializer = serializers.ProfileSerializer(profile)
        return Response(serializer.data)


class CourseViewSet(viewsets.ModelViewSet):
    model = models.Course
    serializer_class = serializers.CourseSerializer
    permission_classes = [
        permissions.AdminOrReadOnlyPermission
    ]

    def get_queryset(self):
        qs = models.Course.objects

        if not self.request.user.is_staff:
            qs = qs.filter(
                Q(coursegroup__instructor__user=self.request.user) | Q(coursegroup__learner__user=self.request.user)
            ).distinct()

        return qs.all()

    @action(methods=['GET'],
            detail=True,
            serializer_class=serializers.ActivityStatisticsSerializer,
            permission_classes=[
                permissions.AdminPermission |
                permissions.CourseInstructorReadOnlyPermission
            ])
    def statistics(self, *args, **kwargs):
        return Response(self.serializer_class(
            self.get_queryset().get(pk=kwargs['pk']).activity_set.all(),
            context=self.get_serializer_context(), many=False).data)


class CourseActivityViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = models.Activity
    queryset = models.Activity.objects
    serializer_class = serializers.ActivitySerializer
    permission_classes = [
        permissions.AdminPermission |
        permissions.CourseInstructorPermission |
        permissions.CourseMemberReadOnlyPermission
    ]

    @action(methods=['GET'],
            detail=True,
            serializer_class=serializers.ActivityStatisticsSerializer,
            permission_classes=[
                permissions.AdminPermission |
                permissions.CourseInstructorReadOnlyPermission
            ])
    def statistics(self, *args, **kwargs):
        return Response(self.serializer_class(
            self.filter_queryset_by_parents_lookups(self.queryset).filter(pk=kwargs['pk']),
            context=self.get_serializer_context(), many=False).data)


class CourseActivityFileViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = models.ProjectFile
    serializer_class = serializers.ProjectFileSerializer
    queryset = models.ProjectFile.objects
    permission_classes = [
        permissions.AdminPermission |
        permissions.CourseInstructorPermission
    ]


class CourseActivityTestViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = models.ProjectTest
    serializer_class = serializers.ProjectTestSerializer
    queryset = models.ProjectTest.objects
    permission_classes = [
        permissions.AdminPermission |
        permissions.CourseInstructorPermission
    ]


class CourseActivitySubmissionViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.Submission
    serializer_class = serializers.SubmissionSerializer
    queryset = models.Submission.objects
    permission_classes = [
        permissions.AdminReadOnlyPermission |
        permissions.CourseInstructorReadOnlyPermission
    ]


class CourseActivityModuleViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.ProjectModule
    serializer_class = serializers.ProjectModuleSerializer
    queryset = models.ProjectModule.objects
    permission_classes = [
        permissions.AdminReadOnlyPermission |
        permissions.CourseInstructorReadOnlyPermission
    ]


class CourseActivityMySubmissionsViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.Submission
    serializer_class = serializers.MySubmissionSerializer
    permission_classes = [
        permissions.AdminReadOnlyPermission |
        permissions.CourseMemberReadOnlyPermission
    ]

    def get_queryset(self):
        course = get_object_or_404(
            models.Course.objects,
            id=self.kwargs['parent_lookup_activity__course_id']
        )
        if course.is_instructor(self.request.user) or self.request.user.is_staff:
            qs = models.Submission.objects.filter(
                instructorsubmission__instructor__user_id=self.request.user.id
            ).order_by('-submitted_at')
        elif course.is_learner(self.request.user):
            qs = models.Submission.objects.filter(learner__user_id=self.request.user.id).order_by('-submitted_at')
        else:
            capture_message('Permission denied to course')
            raise PermissionDenied('You have no access to this course. Error reported.')

        return self.filter_queryset_by_parents_lookups(qs)

    @action(methods=['POST'],
            detail=False,
            permission_classes=[
                permissions.AdminPermission |
                permissions.CourseMemberPermission
            ])
    def upload(self, *args, **kwargs):
        activity = get_object_or_404(
            models.Activity.objects,
            id=self.kwargs['parent_lookup_activity_id'],
            course_id=self.kwargs['parent_lookup_activity__course_id']
        )
        valid_file = None
        if len(self.request.FILES) == 1 and 'file' in self.request.FILES:
            file = self.request.FILES['file']
            if file.name.lower().endswith('.zip') or file.name.lower().endswith('.tar.gz') or \
                file.name.lower().endswith('.rar') or file.name.lower().endswith('.7z'):
                valid_file = file
        else:
            return HttpResponse('Invalid request format', status=status.HTTP_400_BAD_REQUEST)
        if valid_file is None:
            return HttpResponse('Invalid file extension', status=status.HTTP_400_BAD_REQUEST)

        learner = None
        instructor = None
        if activity.course.is_instructor(self.request.user):
            instructor = self.request.user.instructor
            if 'learner' in self.request.POST and self.request.POST['learner'] is not None and len(self.request.POST['learner'].strip()) > 0:
                learner = get_object_or_404(models.Learner.objects, id=self.request.POST['learner'])
        elif activity.course.is_learner(self.request.user):
            learner = self.request.user.learner
        else:
            capture_message('Permission denied to course submission upload')
            raise PermissionDenied('You have no access to upload submissions to this course. Error reported.')

        submission = create_submission(activity, valid_file, learner, instructor)

        if submission is None:
            return HttpResponse('Invalid submission', status=status.HTTP_400_BAD_REQUEST)

        return HttpResponse('Submission created', status=status.HTTP_201_CREATED)


class CourseActivitySubmissionFileViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.SubmissionFile
    serializer_class = serializers.SubmissionFileSerializer
    queryset = models.SubmissionFile.objects
    permission_classes = [
        permissions.AdminReadOnlyPermission |
        permissions.CourseInstructorReadOnlyPermission |
        permissions.SubmissionOwnerReadOnlyPermission
    ]

    @action(methods=['GET', 'POST'],
            detail=False,
            serializer_class=serializers.FilePathBodySerializer,
            permission_classes=[
                permissions.AdminPermission |
                permissions.CourseInstructorPermission |
                permissions.SubmissionOwnerPermission
            ])
    def getPath(self, *args, **kwargs):

        if self.request.method == 'POST':
            path = self.request.POST['path']
            files = models.SubmissionFile.objects.filter(
                submission__activity__course_id=kwargs['parent_lookup_submission__activity__course_id'],
                submission__activity_id=kwargs['parent_lookup_submission__activity_id'],
                submission_id=kwargs['parent_lookup_submission_id']
            )
            if path != '/':
                files = files.filter(filename__startswith=path[1:])

            data = utils.getPath(path, self.serializer_class(files, many=True).data)

            return HttpResponse(json.dumps(data))
        else:
            path = self.request.query_params['path']
            if path.startswith('/'):
                path = path[1:]
            file = get_object_or_404(
                models.SubmissionFile,
                submission__activity__course_id=kwargs['parent_lookup_submission__activity__course_id'],
                submission__activity_id=kwargs['parent_lookup_submission__activity_id'],
                submission_id=kwargs['parent_lookup_submission_id'],
                filename=path
            )
            return HttpResponse(file.file.url)


class CourseActivityReportViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.Learner
    serializer_class = serializers.LearnerResultSerializer
    permission_classes = [
        permissions.AdminReadOnlyPermission |
        permissions.CourseInstructorReadOnlyPermission
    ]

    def get_queryset(self):
        activity_id = self.kwargs['parent_lookup_activity_id']
        queryset = models.LearnerResult.objects.exclude(learner_id__lt=0).filter(activity_id=activity_id)
        group = self.request.query_params.get('group')
        if group is not None:
            queryset = queryset.filter(learner__groups__id=int(group))
        return queryset

    @action(methods=['GET'],
            detail=False,
            permission_classes=[
                permissions.AdminReadOnlyPermission |
                permissions.CourseInstructorReadOnlyPermission
            ])
    def download(self, request, parent_lookup_course_id, parent_lookup_activity_id):
        activity = get_object_or_404(models.Activity, id=parent_lookup_activity_id)

        if 'group' in self.request.query_params:
            group_id = self.request.query_params['group']
            group = get_object_or_404(models.CourseGroup, id=group_id)
            queryset = models.Learner.objects.filter(groups__course=parent_lookup_course_id, groups__id=group_id).distinct()
        else:
            group = None
            queryset = models.Learner.objects.filter(groups__course=parent_lookup_course_id).distinct()

        if queryset.count() == 0:
            return HttpResponse("No data to export", status=status.HTTP_204_NO_CONTENT)

        parent_tests = activity.project.projecttest_set.filter(parent__isnull=True)
        parent_tests_structure = serializers.ProjectTestSerializer(parent_tests, many=True).data

        file = utils.export_to_xlsx(queryset, serializer=serializers.LearnerCourseActivitySubmissionSerializer,
                                    context={'request': request, 'view': self},
                                    results_structure=parent_tests_structure)

        response = HttpResponse(file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        if group is None:
            response['Content-Disposition'] = 'attachment; filename={}_{}_{}_{}.xlsx'.format(
                activity.course.semester.code, activity.course.code, activity.code,
                datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            )
        else:
            response['Content-Disposition'] = 'attachment; filename={}_{}_{}_{}_{}.xlsx'.format(
                activity.course.semester.code, activity.course.code, group.code, activity.code,
                datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            )

        return response

    @action(methods=['GET'],
            detail=False,
            permission_classes=[
                permissions.AdminReadOnlyPermission |
                permissions.CourseInstructorReadOnlyPermission
            ])
    def download_feedback(self, request, parent_lookup_course_id, parent_lookup_activity_id):
        activity = get_object_or_404(models.Activity, id=parent_lookup_activity_id)

        if 'group' in self.request.query_params:
            group_id = self.request.query_params['group']
            group = get_object_or_404(models.CourseGroup, id=group_id)
            queryset = models.Learner.objects.filter(id__gte=0, groups__course=parent_lookup_course_id,
                                                     groups__id=group_id).distinct()
        else:
            group = None
            queryset = models.Learner.objects.filter(id__gte=0, groups__course=parent_lookup_course_id).distinct()

        if queryset.count() == 0:
            return HttpResponse("No data to export", status=status.HTTP_204_NO_CONTENT)

        file = utils.export_feedback_to_xlsx(queryset, serializer=serializers.LearnerCourseActivityFeedbackSerializer,
                                             context={'request': request, 'view': self})

        response = HttpResponse(file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        if group is None:
            response['Content-Disposition'] = 'attachment; filename={}_{}_{}_{}_feedback.xlsx'.format(
                activity.course.semester.code, activity.course.code, activity.code,
                datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            )
        else:
            response['Content-Disposition'] = 'attachment; filename={}_{}_{}_{}_{}_feedback.xlsx'.format(
                activity.course.semester.code, activity.course.code, group.code, activity.code,
                datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            )

        return response


class CourseActivityReportSubmissionViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.Submission
    serializer_class = serializers.SubmissionSerializer
    queryset = models.Submission.objects
    permission_classes = [
        permissions.AdminReadOnlyPermission |
        permissions.CourseInstructorReadOnlyPermission
    ]


class ImportSessionViewSet(viewsets.ModelViewSet):
    model = models.ImportSession
    queryset = models.ImportSession.objects
    serializer_class = serializers.ImportSessionSerializer
    permission_classes = [
        permissions.AdminPermission
    ]


class ImportSessionEntryViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = models.ImportSessionEntry
    serializer_class = serializers.ImportSessionEntrySerializer
    queryset = models.ImportSessionEntry.objects
    permission_classes = [
        permissions.AdminPermission
    ]


class CourseGroupViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.CourseGroup
    serializer_class = serializers.CourseGroupSerializer
    queryset = models.CourseGroup.objects
    permission_classes = [
        permissions.AdminReadOnlyPermission |
        permissions.CourseInstructorReadOnlyPermission
    ]


class CourseLearnersViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.Learner
    serializer_class = serializers.LearnerSerializer
    queryset = models.Learner.objects.order_by('last_name')
    filter_backends = [filters.SearchFilter]
    search_fields = ('username', 'email', 'first_name', 'last_name')
    permission_classes = [
        permissions.AdminReadOnlyPermission |
        permissions.CourseInstructorReadOnlyPermission
    ]


class CourseGroupLearnersViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.Learner
    serializer_class = serializers.LearnerSerializer
    queryset = models.Learner.objects
    permission_classes = [
        permissions.AdminReadOnlyPermission |
        permissions.CourseInstructorReadOnlyPermission
    ]


class CourseActivitySubmissionErrorViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.SubmissionError
    serializer_class = serializers.SubmissionErrorSerializer
    queryset = models.SubmissionError.objects.order_by('id')
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['type', 'code']
    search_fields = ('type', 'code', 'description', 'file', 'line', 'value', 'context')
    permission_classes = [
        permissions.AdminReadOnlyPermission |
        permissions.CourseInstructorReadOnlyPermission |
        permissions.SubmissionOwnerReadOnlyPermission
    ]


class CourseActivitySubmissionTestResultViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.SubmissionTestResult
    serializer_class = serializers.SubmissionTestResultSerializer
    queryset = models.SubmissionTestResult.objects.order_by('id')
    permission_classes = [
        permissions.AdminReadOnlyPermission |
        permissions.CourseInstructorReadOnlyPermission |
        permissions.SubmissionOwnerReadOnlyPermission
    ]

    @action(methods=['GET'],
            detail=False,
            permission_classes=[
                permissions.AdminReadOnlyPermission |
                permissions.CourseInstructorReadOnlyPermission |
                permissions.SubmissionOwnerReadOnlyPermission
            ])
    def summary(self, request, **kwargs):
        try:
            submission_id = int(kwargs['parent_lookup_submission_id'])
            submission = get_object_or_404(models.Submission, id=submission_id)
        except ValueError:
            return Response('Invalid submission ID', status=status.HTTP_400_BAD_REQUEST)

        return Response(get_test_results_structure(submission), status=status.HTTP_200_OK)


class CourseActivityProjectViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = models.Project
    queryset = models.Project.objects
    serializer_class = serializers.ProjectExtendedSerializer
    permission_classes = [
        permissions.AdminPermission |
        permissions.CourseInstructorPermission
    ]

    @action(methods=['GET'],
            detail=False,
            permission_classes=[
                permissions.AdminReadOnlyPermission |
                permissions.CourseInstructorReadOnlyPermission
            ])
    def submissions(self, request, **kwargs):

        project = get_object_or_404(self.filter_queryset_by_parents_lookups(self.get_queryset()))
        qs_submissions = project.activity.submission_set.filter(learner_id=-1).order_by('-id')
        qs_submissions = self.paginate_queryset(qs_submissions)

        return Response(serializers.ProjectSubmissionSerializer(qs_submissions, many=True).data, status=status.HTTP_200_OK)


class FaqViewSet(viewsets.ModelViewSet):
    model = models.Faq
    serializer_class = serializers.FaqSerializer
    permission_classes = [
        permissions.AdminOrReadOnlyPermission
    ]

    def get_queryset(self):
        qs = models.Faq.objects

        if not self.request.user.is_staff:
            qs = qs.filter(
                public=True
            ).distinct()

        return qs

    @action(methods=['POST'],
            detail=True,
            serializer_class=serializers.FaqRateSerializer,
            permission_classes=[
                permissions.LearnerPermission,
            ])
    def rate(self, *args, **kwargs):
        body_data = self.serializer_class(data=self.request.data)
        if body_data.is_valid():
            faq_obj = get_object_or_404(self.get_queryset(), pk=kwargs['pk'])
            rate_value = body_data.validated_data['rate']
            learner_obj = get_object_or_404(models.Learner, user=self.request.user)
            if rate_value > 0:
                faq_rate_obj = faq_obj.faqrating_set.get_or_create(learner=learner_obj)[0]
                old_value = faq_rate_obj.rating
                faq_rate_obj.rating = rate_value
                faq_rate_obj.save()
            else:
                try:
                    faq_rate_obj = faq_obj.faqrating_set.get(learner=learner_obj)
                    old_value = faq_rate_obj.rating
                    faq_rate_obj.delete()
                except Exception:
                    # If not found there is no need to perform any action
                    old_value = 0

            return Response({"old_value": old_value, "new_value": rate_value}, status=status.HTTP_200_OK)
        return Response(body_data.errors, status=status.HTTP_400_BAD_REQUEST)
