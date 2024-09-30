from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.db import models
from django.db.models.signals import pre_delete, post_delete, post_save
from django.dispatch.dispatcher import receiver

from .activity import Activity
from .learner import Learner
from .instructor import Instructor
from .utils import JSONField


SUBMISSION_STATUS = (
    (0, 'CREATING'),
    (1, 'CREATED'),
    (2, 'CLONING'),
    (3, 'CLONED'),
    (4, 'MERGING'),
    (5, 'MERGED'),
    (6, 'WAITING'),
    (7, 'TESTING'),
    (8, 'PROCESSED'),
    (9, 'INVALID'),
    (10, 'ERROR'),
    (11, 'TIMEOUT'),
)


def get_submission_upload_path(instance, filename):
    """
        Build the path where the source code is stored

        :param instance: Submission instance
        :type instance: Submission
        :param filename: Name of the file
        :return: Path to store the file
    """
    if instance.is_test:
        return '{}/{}/{}/project/test/{}/test_code.zip'.format(
            instance.activity.course.semester.code.replace(' ', '_'),
            instance.activity.course.code.replace(' ', '_'),
            instance.activity.code.replace(' ', '_'),
            instance.id
        )
    return '{}/{}/{}/submissions/{}/{}/submission.zip'.format(
        instance.activity.course.semester.code.replace(' ', '_'),
        instance.activity.course.code.replace(' ', '_'),
        instance.activity.code.replace(' ', '_'),
        instance.learner.username.replace(' ', '_'),
        instance.id
    )


def get_merged_submission_upload_path(instance, filename):
    """
        Build the path where the merged code is stored

        :param instance: Submission instance
        :type instance: Submission
        :param filename: Name of the file
        :return: Path to store the file
    """
    if instance.is_test:
        return '{}/{}/{}/project/test/{}/merged_code.zip'.format(
            instance.activity.course.semester.code.replace(' ', '_'),
            instance.activity.course.code.replace(' ', '_'),
            instance.activity.code.replace(' ', '_'),
            instance.id
        )

    return '{}/{}/{}/submissions/{}/{}/merged_submission.zip'.format(
        instance.activity.course.semester.code.replace(' ', '_'),
        instance.activity.course.code.replace(' ', '_'),
        instance.activity.code.replace(' ', '_'),
        instance.learner.username.replace(' ', '_'),
        instance.id
    )


def get_logs_upload_path(instance, filename):
    """
        Build the path where the logs are stored

        :param instance: Submission instance
        :type instance: Submission
        :param filename: Name of the file
        :return: Path to store the file
    """
    if instance.is_test:
        return '{}/{}/{}/project/test/{}/logs/execution.log'.format(
            instance.activity.course.semester.code.replace(' ', '_'),
            instance.activity.course.code.replace(' ', '_'),
            instance.activity.code.replace(' ', '_'),
            instance.id
        )
    return '{}/{}/{}/submissions/{}/{}/logs/execution.log'.format(
        instance.activity.course.semester.code.replace(' ', '_'),
        instance.activity.course.code.replace(' ', '_'),
        instance.activity.code.replace(' ', '_'),
        instance.learner.username.replace(' ', '_'),
        instance.id
    )


def get_valgrind_upload_path(instance, filename):
    """
        Build the path where the valgrind report is stored

        :param instance: Submission instance
        :type instance: Submission
        :param filename: Name of the file
        :return: Path to store the file
    """
    if instance.is_test:
        return '{}/{}/{}/project/test/{}/tools/valgrind.xml'.format(
            instance.activity.course.semester.code.replace(' ', '_'),
            instance.activity.course.code.replace(' ', '_'),
            instance.activity.code.replace(' ', '_'),
            instance.id
        )
    return '{}/{}/{}/submissions/{}/{}/tools/valgrind.xml'.format(
        instance.activity.course.semester.code.replace(' ', '_'),
        instance.activity.course.code.replace(' ', '_'),
        instance.activity.code.replace(' ', '_'),
        instance.learner.username.replace(' ', '_'),
        instance.id
    )

def get_diff_upload_path(instance, filename):
    """
        Build the path where the diff report is stored

        :param instance: Submission instance
        :type instance: Submission
        :param filename: Name of the file
        :return: Path to store the file
    """
    if instance.is_test:
        return '{}/{}/{}/project/test/{}/tools/diff.json'.format(
            instance.activity.course.semester.code.replace(' ', '_'),
            instance.activity.course.code.replace(' ', '_'),
            instance.activity.code.replace(' ', '_'),
            instance.id
        )
    return '{}/{}/{}/submissions/{}/{}/tools/diff.json'.format(
        instance.activity.course.semester.code.replace(' ', '_'),
        instance.activity.course.code.replace(' ', '_'),
        instance.activity.code.replace(' ', '_'),
        instance.learner.username.replace(' ', '_'),
        instance.id
    )


class Submission(models.Model):
    """ Submission model. """
    activity = models.ForeignKey(Activity, null=False, on_delete=models.CASCADE)
    learner = models.ForeignKey(Learner, null=False, on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=SUBMISSION_STATUS, null=False, default=0)
    repository = models.CharField(max_length=255, null=True, blank=False, default=None)
    submitted_at = models.DateTimeField(null=True, blank=False, default=None)
    executed_at = models.DateTimeField(null=True, blank=False, default=None)
    elapsed_time = models.IntegerField(null=True, default=None)
    built = models.BooleanField(null=False, blank=False, default=False)
    metadata = models.TextField(null=True, blank=True, default=None)
    result = models.TextField(null=True, blank=True, default=None)
    progress = models.TextField(null=True, blank=True, default=None)
    test_passed = models.BooleanField(null=True, default=None)
    correct_execution = models.BooleanField(null=True, default=None)
    test_percentage = models.FloatField(null=True, default=None)
    submission = models.FileField(null=True, blank=True, upload_to=get_submission_upload_path)
    test_score = models.FloatField(null=True, blank=True, default=None)
    num_test_passed = models.IntegerField(null=True, blank=True, default=None)
    num_test_failed = models.IntegerField(null=True, blank=True, default=None)
    num_tests = models.IntegerField(null=True, blank=True, default=None)

    merged_submission = models.FileField(null=True, blank=True, upload_to=get_merged_submission_upload_path)
    execution_logs = models.FileField(null=True, blank=True, upload_to=get_logs_upload_path)

    valgrind_report = models.FileField(null=True, blank=True, upload_to=get_valgrind_upload_path)
    leaked_bytes = models.IntegerField(null=True, blank=True, default=None)

    diff_report = models.FileField(null=True, blank=True, upload_to=get_diff_upload_path)

    error = models.TextField(null=True, blank=True, default=None)
    is_last = models.BooleanField(null=False, default=False)

    is_official = models.BooleanField(null=False, default=False)
    result_summary = models.TextField(null=True, blank=True, default=None)

    def get_result(self):
        if self.result is not None:
            json_field = JSONField()
            return json_field.to_representation(self.result)
        return None

    def get_result_summary(self):
        if self.result_summary is not None:
            json_field = JSONField()
            return json_field.to_representation(self.result_summary)
        return None

    def get_metadata(self):
        if self.metadata is not None:
            json_field = JSONField()
            return json_field.to_representation(self.metadata)
        return None

    @property
    def report_files(self):
        reports = None
        if self.activity.include_report:
            reports = self.submissionfile_set.filter(is_report=True).all()
        return reports

    @property
    def is_test(self):
        try:
            test_submission = self.testsubmission
        except Exception:
            test_submission = None
        return test_submission is not None

    @property
    def is_mail_submission(self):
        return self.mailsubmission_set.all().count() > 0

    @property
    def is_instructor_submission(self):
        try:
            if self.is_mail_submission:
                return self.mailsubmission_set.get().instructor is not None
            else:
                instructor_submission = self.instructorsubmission
        except Exception:
            instructor_submission = None
        return instructor_submission is not None

    @property
    def submitted_by(self):
        if self.is_instructor_submission:
            return self.instructorsubmission.instructor.email
        return None


@receiver(pre_delete, sender=Submission)
def _submission_delete(sender, instance, **kwargs):
    instance.submission.delete()
    instance.merged_submission.delete()
    instance.execution_logs.delete()


@receiver(post_delete, sender=Submission)
def _submission_delete_post(sender, instance, **kwargs):
    from pelp.apps.web.lib.submission import update_learner_result

    update_learner_result(learner=instance.learner, activity=instance.activity)


TEST_SUBMISSION_SOURCE = (
    (0, 'BASE_CODE'),
    (1, 'TEST_CODE'),
)


class TestSubmission(Submission):
    """ Test Submission model. """
    source = models.SmallIntegerField(choices=TEST_SUBMISSION_SOURCE, null=False, default=0)

    @property
    def is_test(self):
        return True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # Check that test learner exists
        try:
            learner = Learner.objects.get(id=-1)
        except Learner.DoesNotExist:
            learner = Learner.objects.create(id=-1, username='test_learner', first_name='Test', last_name='Learner',
                                             email='test_learner@pelp.sunai.uoc.edu')
        # Assign the test learner
        self.learner = learner
        super().save(force_insert, force_update, using, update_fields)


class InstructorSubmission(Submission):
    """ Instructor Submission model. """
    instructor = models.ForeignKey(Instructor, null=False, on_delete=models.CASCADE)


    @property
    def is_test(self):
        return False

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # Check that instructor learner exists
        try:
            learner = Learner.objects.get(id=-2)
        except Learner.DoesNotExist:
            learner = Learner.objects.create(id=-2, username='instructor', first_name='Generic', last_name='Instructor',
                                             email='instructor@pelp.sunai.uoc.edu')
        # Assign the test learner
        self.learner = learner
        super().save(force_insert, force_update, using, update_fields)


@receiver(post_save, sender=Submission)
def _submission_post_save(sender, instance, **kwargs):
    try:
        from pelp.apps.web.consumers.submission import SubmissionEventConsumer
        user = None
        if instance.is_instructor_submission:
            user = instance.instructorsubmission.instructor.user
        elif instance.learner is not None:
            user = instance.learner.user

        if kwargs.get('created', False):
            event = "NEW_SUBMISSION"
        else:
            event = "SUBMISSION_NEW_STATE"

        if user is not None:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                SubmissionEventConsumer.get_activity_submissions_channel_name(instance.activity.id, user),
                {
                    'type': 'send_message',
                    'message': instance.id,
                    "event": event
            })
    except Exception:
        # Avoid failing execution due to messaging errors
        pass
