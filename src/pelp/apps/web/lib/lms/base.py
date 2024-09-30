import typing
from abc import ABC, abstractmethod
from pelp.apps.web import models


class LMSBaseImportResult(ABC):
    """
        Base class for LMS data import
    """

    def __init__(self, valid=True, num_objects=0, exception=None, num_assigned=0, num_created=0, num_total=0) -> None:
        super().__init__()
        self.valid: bool = valid
        self.num_objects: typing.Optional[int] = num_objects
        self.exceptions: typing.List[Exception] = []
        self.num_assigned = num_assigned
        self.num_created = num_created
        self.num_total = num_total
        if exception is not None:
            if isinstance(exception, list):
                if len(self.exceptions) > 0:
                    self.valid = False
                self.exceptions = exception
            else:
                self.valid = False
                self.exceptions = [exception]

    def __str__(self) -> str:
        if self.exceptions is not None and len(self.exceptions) > 0:
            return '\n'.join(self.exceptions)
        return f'[valid={self.valid}] - {self.num_objects} objects imported'

    def __add__(self, other):

        return LMSBaseImportResult(
            valid=self.valid and other.valid,
            num_objects=self.num_objects + other.num_objects,
            exception=self.exceptions + other.exceptions,
            num_total=self.num_total + other.num_total,
            num_assigned=self.num_assigned + other.num_assigned,
            num_created=self.num_created + other.num_created
        )


class LMSUserImportResult(LMSBaseImportResult):
    """
        Base class for LMS users import
    """
    pass


class LMSSubmissionImportResult(LMSBaseImportResult):
    """
        Base class for LMS submissions import
    """
    pass


class LMSBase(ABC):
    """
        Base class for LMS data management
    """
    def update_course_learners(self, course: models.Course) -> LMSUserImportResult:
        """
            Update the learners of all groups of a Course
            :param course: Related course
        """
        result = LMSUserImportResult()
        groups = models.CourseGroup.objects.filter(course=course)

        for group in groups:
            result += self.update_group_learners(group)

        return result

    def update_course_instructors(self, course: models.Course) -> LMSUserImportResult:
        """
            Update the instructors of all groups of a Course
            :param course: Related course
        """
        result = LMSUserImportResult()
        groups = models.CourseGroup.objects.filter(course=course)
        for group in groups:
            result += self.update_group_instructors(group)

        return result

    def import_course_activity_submissions(self, course: models.Course, activity: models.Activity, is_official: bool = False) -> LMSSubmissionImportResult:
        """
            Import all activities delivered to any of the groups of a Course
            :param course: Related courseç
            :param activity: Related activity
            :param is_official: Whether this submission is an official submission or not.
        """
        result = LMSSubmissionImportResult()
        groups = models.CourseGroup.objects.filter(course=course)
        for group in groups:
            result += self.import_group_activity_submissions(group, activity, is_official)
        return result

    @abstractmethod
    def update_group_learners(self, course_group: models.CourseGroup) -> LMSUserImportResult:
        """
            Update the learners of given course group
            :param course_group: Related course group
        """
        pass

    @abstractmethod
    def update_group_instructors(self, course_group: models.CourseGroup) -> LMSUserImportResult:
        """
            Update the instructors of given course group
            :param course_group: Related course group
        """
        pass

    @abstractmethod
    def import_group_activity_submissions(self, course_group: models.CourseGroup, activity: models.Activity, is_official: bool = False) -> LMSSubmissionImportResult:
        """
            Import all activities delivered to a given course group
            :param course_group: Related course group
            :param activity: Related activity
            :param is_official: Whether this submission is an official submission or not.
        """
        pass
