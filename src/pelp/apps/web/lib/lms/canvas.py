""" Implementation of LMS methods for Canvas """
import typing

from canvasapi import Canvas
from django.conf import settings
from pelp.apps.web.lib.submission import import_canvas_submission
from .base import LMSBase, models, LMSUserImportResult, LMSSubmissionImportResult



class LMSCanvas(LMSBase):

    def __init__(self) -> None:
        super().__init__()
        self._canvas: typing.Optional[Canvas] = None

    @property
    def canvas(self) -> Canvas:
        """ Access to Canvas API client """
        if self._canvas is None:
            self._canvas = Canvas(settings.CANVAS_API_URL, settings.CANVAS_API_TOKEN)
        return self._canvas

    def update_group_learners(self, course_group: models.CourseGroup) -> LMSUserImportResult:
        result = LMSUserImportResult()
        # Get students list
        lms_course_group = self.canvas.get_course(course_group.sis_code, use_sis_id=True)
        students = lms_course_group.get_users(enrollment_type=['student'])
        for student in students:
            try:
                learner = models.Learner.objects.get(username=student.login_id)
            except models.Learner.DoesNotExist:
                last_name, first_name = student.sortable_name.split(', ')
                learner = models.Learner.objects.create(
                    username=student.login_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=student.email,
                )
                result.num_created += 1
            if not course_group.learner_set.filter(id=learner.id).exists():
                course_group.learner_set.add(learner)
                result.num_assigned += 1
            result.num_total += 1

        return result

    def update_group_instructors(self, course_group: models.CourseGroup) -> LMSUserImportResult:
        result = LMSUserImportResult()
        # Get instructors list
        lms_course_group = self.canvas.get_course(course_group.sis_code, use_sis_id=True)
        teachers = lms_course_group.get_users(enrollment_type=['teacher', 'ta'])

        for teacher in teachers:
            try:
                instructor = models.Instructor.objects.get(username=teacher.login_id)
            except models.Instructor.DoesNotExist:
                last_name, first_name = teacher.sortable_name.split(', ')
                instructor = models.Instructor.objects.create(
                    username=teacher.login_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=teacher.email,
                )
                result.num_created += 1
            if not course_group.instructor_set.filter(id=instructor.id).exists():
                course_group.instructor_set.add(instructor)
                result.num_assigned += 1
            result.num_total += 1
        return result

    def import_group_activity_submissions(self, course_group: models.CourseGroup, activity: models.Activity, is_official: bool = False) -> LMSSubmissionImportResult:
        result = LMSSubmissionImportResult()

        # Get assignments
        lms_course_group = self.canvas.get_course(course_group.sis_code, use_sis_id=True)

        codes = list(activity.translateactivity_set.values_list('name', flat=True))

        lms_activity = None
        for code in codes:
            act_list = list(lms_course_group.get_assignments(search_term=code))
            if len(act_list) > 0:
                lms_activity = act_list[0]
                break

        if lms_activity is None:
            return result

        # Activity Submissions
        submissions = lms_activity.get_submissions()
        for submission in submissions:
            if submission.submitted_at is not None:
                profile = self.canvas.get_user(submission.user_id).get_profile()
                if 'primary_email' in profile:
                    learner = models.Learner.objects.get(email=profile['primary_email'])
                else:
                    learner = models.Learner.objects.get(username=profile['login_id'])
                if import_canvas_submission(activity, learner, submission, is_official):
                    result.num_created += 1
                result.num_total += 1

        return result
