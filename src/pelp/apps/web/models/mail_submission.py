from django.db import models

from .learner import Learner
from .instructor import Instructor
from .mail_inbox import MailInbox
from .submission import Submission


def get_attachment_upload_path(instance, filename):
    """
        Build the path where the attachment is stored

        :param instance: Mail submission
        :type instance: MailSubmission
        :param filename: Name of the file
        :return: Path to store the file
    """
    return '{}/{}/{}/mail/{}/{}'.format(
        instance.inbox.activity.course.semester.code.replace(' ', '_'),
        instance.inbox.activity.course.code.replace(' ', '_'),
        instance.inbox.activity.code.replace(' ', '_'),
        instance.id,
        filename
    )


MAIL_SUBMISSION_STATUS = (
    (0, 'CREATING'),
    (1, 'CREATED'),
    (2, 'IMPORTING'),
    (3, 'IMPORTED'),
    (4, 'INVALID'),
    (5, 'ERROR'),
    (6, 'OVERDUE'),
    (7, 'OVER_QUOTA'),
)


class MailSubmission(models.Model):
    """ Mail submission model. """
    status = models.SmallIntegerField(choices=MAIL_SUBMISSION_STATUS, null=False, default=0)
    inbox = models.ForeignKey(MailInbox, null=False, blank=False, on_delete=models.CASCADE, default=None)
    learner = models.ForeignKey(Learner, null=False, blank=False, on_delete=models.CASCADE, default=None)
    received_at = models.DateTimeField(null=False, blank=False, default=None)
    processed_at = models.DateTimeField(null=True, blank=True, default=None)
    answered_at = models.DateTimeField(null=True, blank=True, default=None)
    attachment = models.FileField(null=True, blank=True, upload_to=get_attachment_upload_path)
    error = models.TextField(null=True, blank=True, default=None)

    message_id = models.IntegerField(null=False, blank=False, default=None, unique=True)

    replacement_mail = models.CharField(max_length=250, null=True, blank=True, default=None)
    from_mail = models.CharField(max_length=250, null=False, blank=False, default=None)
    instructor = models.ForeignKey(Instructor, null=True, blank=True, on_delete=models.CASCADE, default=None)
    submission = models.ForeignKey(Submission, null=True, blank=True, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.learner.username


class InstructorMailSubmission(MailSubmission):
    """ Instructor mail submission model. """

    def __str__(self):
        return self.instructor.username

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
