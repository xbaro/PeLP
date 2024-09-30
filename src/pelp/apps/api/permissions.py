""" PeLP API permissions module """
import re
import typing
from rest_framework import permissions

from pelp.apps.web.models import Course, Submission, Learner


class AdminPermission(permissions.BasePermission):
    """
        Admins have full permissions
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_staff


class AdminReadOnlyPermission(AdminPermission):
    """
        Admins have read only permissions
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)

        return False


class AdminOrReadOnlyPermission(AdminPermission):
    """
        Admins have full permissions, others only read permission
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        return request.method in permissions.SAFE_METHODS


class CourseMemberPermission(permissions.BasePermission):
    """
        Members of a course have full permissions
    """
    _course_pattern = re.compile(r'^/api/course/(\d+)/.*$')

    def __init__(self) -> None:
        super().__init__()
        self._course: typing.Optional[Course] = None

    def _get_course(self, request):
        course_match = self._course_pattern.search(request.path)
        if course_match is not None:
            course_id = int(course_match.group(1))
            try:
                return Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                return None
        return None

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        self._course = self._get_course(request)
        if self._course is not None:
            return self._course.is_instructor(request.user) or self._course.is_learner(request.user)
        return False


class CourseMemberReadOnlyPermission(CourseMemberPermission):
    """
        Members of a course have read only permissions
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False


class CourseInstructorPermission(CourseMemberPermission):
    """
        Instructors of a course have full permissions
    """
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return self._course.is_instructor(request.user)

        return False


class CourseInstructorReadOnlyPermission(CourseInstructorPermission):
    """
        Instructors of a course have read only permissions
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False


class CourseLearnerPermission(CourseMemberPermission):
    """
        Learners of a course have full permissions
    """
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return self._course.is_learner(request.user)

        return False


class CourseLearnerReadOnlyPermission(CourseLearnerPermission):
    """
        Learners of a course have read only permissions
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False


class SubmissionOwnerPermission(CourseMemberPermission):
    """
        Owners of a submission have full permissions
    """
    _submission_pattern = re.compile(r'^/api/course/(\d+)/activity/(\d+)/submission/(\d+)/.*$')
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            submission_match = self._submission_pattern.search(request.path)
            if submission_match is not None:
                course_id = int(submission_match.group(1))
                activity_id = int(submission_match.group(2))
                submission_id = int(submission_match.group(3))
                try:
                    submission = Submission.objects.get(id=submission_id,
                                                        activity_id=activity_id,
                                                        activity__course_id=course_id)
                except Submission.DoesNotExist:
                    return False
                if submission.learner.user == request.user:
                    return True

        return False


class SubmissionOwnerReadOnlyPermission(SubmissionOwnerPermission):
    """
        Owners of a submission have read only permissions
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False


class LearnerPermission(permissions.IsAuthenticated):
    """
        Learner of any course have full permissions
    """
    def has_permission(self, request, view):
        return Learner.objects.filter(user=request.user).count() > 0

class LearnerReadOnlyPermission(LearnerPermission):
    """
        Learners of any course have read only permissions
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False
