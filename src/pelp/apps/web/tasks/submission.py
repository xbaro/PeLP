""" Tasks related to submission management """
from pelp import celery_app
from pelp.apps.web import lib
from pelp.apps.web import models
from sentry_sdk import capture_exception

@celery_app.task
def merge_submission_code():
    """
        Create a merge code from submission code and project code
    """
    # Get next created submission
    submission = lib.submission.get_next_submission(status=[1, 3])  # CREATED or CLONED

    if submission is not None:
        try:
            failed = False
            # Check if we need to obtain the files from repository
            if submission.status == 2:  # CLONING
                # Download code from repository
                submission = lib.submission.clone_submission_files(submission)
                if submission.status != 3:  # CLONED
                    failed = True
            elif submission.status == 4:  # MERGING
                # Merge code files
                submission = lib.submission.merge_submission_files(submission)
                if submission.status != 5:  # MERGED
                    failed = True
            else:
                failed = True
        except Exception as ex:
            capture_exception(ex)
            failed = True
            submission.status = 10  # ERROR
            submission.error = ex.__str__()
            submission.save()

        return {"failed": failed, "submission_id": submission.id, "status": submission.get_status_display()}

    return None


@celery_app.task
def test_submission_code():
    """
        Test submission
    """
    # Get next merged submission
    submission = lib.submission.get_next_submission(status=5)  # MERGED

    if submission is not None:
        try:
            # Test submission
            submission = lib.submission.run_submission_tests(submission)
            failed = False
            # If no error, status should be WAITING(6) or RUNNING(7) or PROCESSED(8), depending the worker status
            if submission.status < 6 or submission.status > 8:
                failed = True
        except Exception as ex:
            capture_exception(ex)
            failed = True
            submission.status = 10  # ERROR
            submission.error = ex.__str__()
            submission.save()

        return {"failed": failed, "submission_id": submission.id, "status": submission.get_status_display()}

    return None


@celery_app.task
def reweight_activity_submissions(activity_id, reload_results=False):
    """
        Re-weight all submissions from an activity
    """
    try:
        activity = models.Activity.objects.get(id=activity_id)
        for submission in activity.submission_set.all():
            if reload_results:
                lib.execution._store_test_results(submission)
            result = lib.execution._update_grouping_nodes(submission)
            submission.test_score = result['total_weight']
            submission.test_passed = result['passed']
            submission.num_tests = result['num_tests']
            submission.num_test_passed = result['num_passed']
            submission.num_test_failed = result['num_failed']
            submission.save()
            if submission.is_last:
                lib.submission.update_learner_result(submission.learner, submission.activity)

    except models.Activity.DoesNotExist:
        pass
