""" Tasks related to mail submissions management """
from pelp import celery_app
from pelp.apps.web import lib
from pelp.apps.web.models.task_lock import unlock_expired


@celery_app.task
def unlock_expired_tasks():
    """
        Unlock expired task locks
    """
    unlock_expired()


@celery_app.task
def check_mail_submissions():
    """
        Check inbox for mail submissions
    """
    lib.mail.check_mail_submissions()


@celery_app.task
def import_mail_submissions():
    """
        Import mail submissions to be processed
    """
    mail = lib.mail.get_next_mail(1)

    if mail is not None:
        failed = False

        # Import the mail
        try:
            updated_mail = lib.submission.import_mail_submission(mail)
        except Exception as ex:
            mail.status = 5
            mail.error = ex.__str__()
            mail.save()

        if updated_mail is None or updated_mail.status != 3:
            failed = True

        return {"failed": failed, "mail_id": mail.id, "status": mail.get_status_display()}

    return None


@celery_app.task
def update_mail_submissions_status():

    lib.mail.check_mail_submissions_status()

