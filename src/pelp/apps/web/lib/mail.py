""" Module implementing mail interaction """
import re
from typing import Optional, Union, List
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.core.files.base import ContentFile
from imap_tools import MailBox

from django.core.mail import EmailMessage
from django.template.loader import get_template

from sentry_sdk import capture_exception

from pelp.apps.web import models
from pelp.apps.web.models.task_lock import lock
from pelp.apps.web.models.task_lock import unlock


def get_next_locked_status(mail: models.MailSubmission) -> Optional[int]:
    """
        Get the next valid locked status for an email submission
        :param mail: An email submission object
        :return: The next status
    """
    next_status = None
    if mail.status == 1:  # CREATED
        next_status = 2  # IMPORTING

    return next_status


def get_next_mail(status: Union[int, List[int]]) -> Optional[models.MailSubmission]:
    """
        Get the first mail with one of the provided status and move to the next valid locked status.

        :param status: The original status/statuses
        :return: An email submission object with locked status
    """
    with transaction.atomic():
        # Filter for the first project in provided statuses
        if isinstance(status, int):
            mail = models.MailSubmission.objects.filter(status=status).order_by('id').first()
        else:
            status_filter = None
            for s in status:
                if status_filter is None:
                    status_filter = Q(status=s)
                else:
                    status_filter |= Q(status=s)
            mail = models.MailSubmission.objects.filter(status_filter).order_by('id').first()

        if mail is not None:
            next_status = get_next_locked_status(mail)

            if next_status is not None:
                mail.status = next_status
                mail.save()
            else:
                mail = None

    return mail


def _move_mail(mailbox: MailBox, uid: int, folder: str, activity: models.Activity = None):
    if activity is None:
        folder_name = 'PeLP/{}'.format(folder)
    else:
        folder_name = 'PeLP/{}/{}/{}/{}'.format(
            activity.course.semester.code,
            activity.course.code,
            activity.code,
            folder)

    # Check if the folder exists
    if not mailbox.folder.exists(folder_name):
        mailbox.folder.create(folder_name)

    # Move the message to the folder
    mailbox.move(uid_list=[uid], destination_folder=folder_name)


def _check_message(mailbox: MailBox, message):
    message_data = {
        'valid': False,
        'reason': None,
        'activity': None,
        'learner': None,
        'instructor': None,
        'inbox': None,
    }
    try:
        inbox = models.MailInbox.objects.get(name=message.subject)
        message_data['inbox'] = inbox
    except models.MailInbox.DoesNotExist:
        # No inbox for this subject, move to invalid messages folder
        _move_mail(mailbox, message.uid, 'Invalid')
        message_data['valid'] = False
        message_data['reason'] = 'Inbox not found'
        return message_data

    # Get the activity
    message_data['activity'] = inbox.activity

    # Check if sender is learner of the activity's course
    try:
        learner = inbox.activity.course.learners.get(email=message.from_)
        message_data['learner'] = learner
    except models.Learner.DoesNotExist:
        learner = None
        try:
            # Check if sender is instructor of the activity's course
            instructor = inbox.activity.course.instructors.get(email=message.from_)
            message_data['instructor'] = instructor
        except models.Instructor.DoesNotExist:
            instructor = None
    if learner is None and instructor is None:
        # No inbox for this subject, move to invalid messages folder
        _move_mail(mailbox, message.uid, 'Invalid', inbox.activity)
        message_data['valid'] = False
        message_data['reason'] = 'Invalid sender'
        return message_data

    message_data['valid'] = True
    message_data['reason'] = None

    return message_data


def _check_message_replacement(message, activity):
    replacement_data = {
        'valid': False,
        'has_replacement': False,
        'replacement_mail': None,
        'reason': None,
        'learner': None,
    }
    # Check if message body contains a learner email
    pattern = re.compile(r"user_replacement:\s.*[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\s")
    replacement = pattern.findall(message.text)

    if len(replacement) == 1:
        replacement_data['has_replacement'] = True
        learner_email = replacement[0].split(':')[1].strip()
        replacement_data['replacement_mail'] = learner_email
        try:
            replacement_data['learner'] = activity.course.learners.get(email=learner_email)
            replacement_data['valid'] = True
            replacement_data['reason'] = None
        except models.Learner.DoesNotExist:
            replacement_data['learner'] = None
            replacement_data['reason'] = 'No learner found with email {}.'.format(learner_email)
            replacement_data['valid'] = False
    elif len(replacement) > 1:
        replacement_data['valid'] = False
        replacement_data['has_replacement'] = True
        replacement_data['learner'] = None
        replacement_data['reason'] = 'Multiple replacement users found'
    else:
        replacement_data['has_replacement'] = False
        replacement_data['learner'] = None
        replacement_data['valid'] = True

    return replacement_data


def _apply_mail_restrictions(mail: models.MailSubmission) -> models.MailSubmission:

    if mail.instructor is None:
        stats = _get_learner_submissions(mail.learner, mail.inbox)
        if stats['submissions_last_day'] >= stats['max_day'] or stats['submissions_total'] >= stats['max_total']:
            mail.status = 7  # OVER_QUOTA
        elif not mail.inbox.activity.is_active:
            mail.status = 6  # OVER_DUE
    return mail


def check_mail_submissions():
    # Get a lock for this task
    task_lock = lock('check_mail_submissions')
    if task_lock is None:
        return

    try:
        with MailBox(settings.IMAP_SERVER).login(settings.IMAP_USER, settings.IMAP_PASSWORD, 'INBOX') as mailbox:
            for message in mailbox.fetch():
                # Check the message data
                message_data = _check_message(mailbox, message)
                if not message_data['valid']:
                    continue

                # Check if activity allow user replacement
                learner = message_data['learner']
                instructor = message_data['instructor']
                inbox = message_data['inbox']

                replacement = False
                if learner is None and instructor is not None and inbox.allow_user_replacement:
                    # Check replacement
                    replacement_data = _check_message_replacement(message, inbox.activity)

                    # If replacement data is not valid, move message to invalid folder and send a mail to instructor
                    if not replacement_data['valid']:
                        _move_mail(mailbox, message.uid, 'Invalid', inbox.activity)
                        models.InstructorMailSubmission.objects.create(
                            status=4,
                            inbox=inbox,
                            received_at=message.date,
                            message_id=message.uid,
                            instructor=instructor,
                            error=replacement_data['reason'],
                            replacement_mail=replacement_data['replacement_mail'],
                            from_mail=message.from_
                        )
                        continue

                    # If replacement is valid, take the learner data
                    if replacement_data['has_replacement']:
                        learner = replacement_data['learner']
                        replacement = True

                # Add the message to the database
                replacement_mail = None
                if replacement:
                    replacement_mail = replacement_data['replacement_mail']
                if instructor is not None and learner is None:
                    mail_submission = models.InstructorMailSubmission.objects.create(
                        status=0,
                        inbox=inbox,
                        received_at=message.date,
                        message_id=message.uid,
                        instructor=instructor,
                        replacement_mail=replacement_mail,
                        from_mail=message.from_
                    )
                else:
                    mail_submission = models.MailSubmission.objects.create(
                        status=0,
                        inbox=inbox,
                        received_at=message.date,
                        message_id=message.uid,
                        learner=learner,
                        instructor=instructor,
                        replacement_mail=replacement_mail,
                        from_mail=message.from_
                    )

                try:
                    valid_attachments = []
                    for attachment in message.attachments:
                        if attachment.filename.lower().endswith('.zip'):
                            valid_attachments.append(attachment)
                        elif attachment.filename.lower().endswith('.tar.gz'):
                            valid_attachments.append(attachment)
                        elif attachment.filename.lower().endswith('.rar'):
                            valid_attachments.append(attachment)
                        elif attachment.filename.lower().endswith('.7z'):
                            valid_attachments.append(attachment)
                    if len(valid_attachments) == 0:
                        mail_submission.error = "Missing attachment."
                        mail_submission.status = 4
                        mail_submission.save()
                        _move_mail(mailbox, message.uid, 'Invalid', inbox.activity)
                    elif len(valid_attachments) > 1:
                        mail_submission.error = "Too many attachments."
                        mail_submission.status = 4
                        mail_submission.save()
                        _move_mail(mailbox, message.uid, 'Invalid', inbox.activity)
                    else:
                        mail_submission.attachment.save(valid_attachments[0].filename,
                                                        ContentFile(valid_attachments[0].payload))
                        mail_submission.status = 1
                        mail_submission = _apply_mail_restrictions(mail_submission)
                        mail_submission.save()
                        _move_mail(mailbox, message.uid, 'Imported', inbox.activity)
                except Exception as ex:
                    capture_exception(ex)
                    mail_submission.error = ex.__str__()
                    mail_submission.status = 5
                    mail_submission.save()
                    _move_mail(mailbox, message.uid, 'Error', inbox.activity)

        # Unlock the task
        unlock('check_mail_submissions')
    except Exception as ex:
        capture_exception(ex)
        unlock('check_mail_submissions')


def _get_learner_submissions(learner: models.Learner, inbox: models.MailInbox):

    qs = models.MailSubmission.objects.filter(
        learner=learner,
        instructor__isnull=True,
        status__lt=7,  # OVER_QUOTA
        inbox=inbox
    )
    total_submissions = qs.count()
    last_day = qs.filter(received_at__gte=timezone.now()-timezone.timedelta(days=1)).count()

    return {
        'submissions_total': total_submissions,
        'submissions_last_day': last_day,
        'max_total': inbox.max_submissions,
        'max_day': inbox.max_submissions_day
    }


def send_result_mail(dest_email, submission, inbox):
    result = submission.get_result()
    result_detail = None
    if result is not None:
        result_detail = {
            'total': result['total'],
            'passed': result['passed'],
            'failed': result['failed'],
            'sections': [],
            'tests': [],
            'results': []
        }
        for section in result['sections']:
            result_detail['sections'].append({
                'code': section['code'],
                'title': section['title'],
                'num_tests': section['total'],
            })
            for test in section['tests']:
                result_detail['tests'].append({
                    'code': test['code'],
                    'description': test['description']
                })
                result_detail['results'].append({
                    'result': test['result'],
                    'passed': test['result'] == "OK"
                })

    message = get_template("web/emails/submission_result.html").render({
        'submission': submission,
        'results': result_detail,
        'execution_log': submission.execution_logs.read().decode(),
        'stats': _get_learner_submissions(submission.learner, inbox)
    })
    mail = EmailMessage(
        subject="Submission {} result".format(submission.id),
        body=message,
        from_email=settings.EMAIL_FROM,
        to=[dest_email],
    )
    mail.content_subtype = "html"
    return mail.send()


def send_error_mail(mail: models.MailSubmission):
    message = get_template("web/emails/submission_error.html").render({
        'mail': mail
    })
    mail = EmailMessage(
        subject="Failed mail submission {}".format(mail.id),
        body=message,
        from_email=settings.EMAIL_FROM,
        to=[mail.from_mail],
    )
    mail.content_subtype = "html"
    return mail.send()


def check_mail_submissions_status():

    # Check valid imported submissions
    for mail in models.MailSubmission.objects.filter(status=3, submission__status__gte=8, answered_at__isnull=True):
        mail.processed_at = mail.submission.executed_at
        mail.save()
        try:
            if send_result_mail(mail.from_mail, mail.submission, mail.inbox):
                mail.answered_at = timezone.now()
                mail.save()
            else:
                mail.status = 5  # ERROR
                mail.error = "Cannot send result detail"
                mail.save()
        except Exception as ex:
            capture_exception(ex)
            mail.status = 5  # ERROR
            mail.error = ex.__str__()
            mail.save()

    # Check not valid imported submissions from instructors
    for mail in models.MailSubmission.objects.filter(status__gt=3, instructor__isnull=False, answered_at__isnull=True):
        try:
            if send_error_mail(mail):
                mail.answered_at = timezone.now()
                mail.save()
            else:
                mail.status = 5  # ERROR
                mail.error = "Cannot send result detail"
                mail.answered_at = timezone.now()  # Set answer time to avoid multiple errors
                mail.save()
        except Exception as ex:
            capture_exception(ex)
            mail.status = 5  # ERROR
            mail.error = ex.__str__()
            mail.answered_at = timezone.now()  # Set answer time to avoid multiple errors
            mail.save()
