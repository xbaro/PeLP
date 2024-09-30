""" Tasks related to data importation management """
from pelp import celery_app
from pelp.apps.web import lib

from sentry_sdk import capture_exception


@celery_app.task
def load_session_data():
    """
        Load data from import session
    """
    # Get next created session
    session = lib.data_import.get_next_session(status=0)  # CREATED

    if session is not None:
        try:
            failed = False

            # Create a test submission
            session = lib.data_import.load_session_data(session)

            if session.status != 2:  # Loaded
                failed = True
        except Exception as ex:
            capture_exception(ex)
            session.status = 6  # ERROR
            session.error = ex.__str__()
            session.save()
            failed = True
        return {"failed": failed, "session_id": session.id, "status": session.get_status_display()}

    return None


@celery_app.task
def import_session_data():
    """
        Import loaded data from import session
    """
    # Get next loaded session
    session = lib.data_import.get_next_session(status=2)  # LOADED

    if session is not None:
        try:
            failed = False

            # Create a test submission
            session = lib.data_import.import_session_data(session)

            if session.status != 5:  # Imported
                failed = True
        except Exception as ex:
            capture_exception(ex)
            session.status = 6  # ERROR
            session.error = ex.__str__()
            session.save()
            failed = True

        return {"failed": failed, "session_id": session.id, "status": session.get_status_display()}

    return None
