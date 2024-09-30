""" Module implementing execution management features """
from pelp import celery_app
from pelp.apps.web import lib

from sentry_sdk import capture_exception

@celery_app.task
def prepare_created_execution():
    """
        Prepare a new created execution
    """
    # Get next created execution
    execution = lib.execution.get_next_execution(status=1)  # CREATED

    if execution is not None:
        try:
            failed = False

            # Check the status
            if execution.status == 2:  # PREPARING
                # Prepare the execution
                execution = lib.execution.prepare_execution(execution)
                if execution.status != 3:  # PREPARED
                    failed = True
            else:
                failed = True
        except Exception as ex:
            capture_exception(ex)
            execution.status = 7  # ERROR
            execution.error = ex.__str__()
            execution.save()
            execution.submission.status = 10  # ERROR
            execution.submission.error = ex.__str__()
            execution.submission.save()
            failed = True
            # Update the learner results related with this submission
            lib.execution.update_learner_result(
                learner=execution.submission.learner,
                activity=execution.submission.activity
            )

        return {"failed": failed, "execution_id": execution.id, "status": execution.get_status_display()}

    return None


@celery_app.task
def run_prepared_execution():
    """
        Prepare a new created execution
    """
    # Get next created execution
    execution = lib.execution.get_next_execution(status=3)  # PREPARED

    if execution is not None:
        try:
            failed = False

            # Check the status
            if execution.status == 4:  # RUNNING
                # Run the execution
                execution = lib.execution.run_execution(execution)
                # Check if execution is running
                if execution.container_id is None:
                    failed = True
            else:
                failed = True
        except Exception as ex:
            capture_exception(ex)
            execution.status = 7  # ERROR
            execution.error = ex.__str__()
            execution.save()
            execution.submission.status = 10  # ERROR
            execution.submission.error = ex.__str__()
            execution.submission.save()
            failed = True
            # Update the learner results related with this submission
            lib.execution.update_learner_result(
                learner=execution.submission.learner,
                activity=execution.submission.activity
            )

        return {"failed": failed, "execution_id": execution.id, "status": execution.get_status_display()}

    return None


@celery_app.task
def check_running_execution():
    """
        Check the status of running executions
    """
    lib.execution.check_running_executions()
