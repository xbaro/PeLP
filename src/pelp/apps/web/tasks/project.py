""" Tasks related to project management """
from pelp import celery_app
from pelp.apps.web import lib


@celery_app.task
def upload_project_files():
    """
        Upload provided project files to the storage
    """

    # Get next created project
    project = lib.project.get_next_project(status=[1, 3])  # CREATED or CLONED

    if project is not None:
        failed = False
        # Check if we need to obtain the files from repository
        if project.status == 2:  # CLONING
            # Download code from repository
            project = lib.project.clone_project_files(project)
            if project.status != 3: # CLONED
                failed = True
        elif project.status == 4:  # UPLOADING
            # Upload code files
            project = lib.project.upload_project_files(project)
            if project.status != 5:  # UPLOADED
                failed = True
        else:
            failed = True

        return {"failed": failed, "project_id": project.id, "status": project.get_status_display()}

    return None


@celery_app.task
def validate_project_files():
    """
        Validate base code with project definition
    """
    # Get next uploaded project
    project = lib.project.get_next_project(status=5)  # UPLOADED

    if project is not None:
        # Create a test submission
        lib.submission.create_test_submission(project, source=0)

        return {"failed": False, "project_id": project.id, "status": project.get_status_display()}

    return None


@celery_app.task
def test_project_files():
    """
        Run tests on project test submission
    """
    # Get next validated project
    project = lib.project.get_next_project(status=7)  # VALID

    if project is not None:
        # Create a test submission
        lib.submission.create_test_submission(project, source=1)

        return {"failed": False, "project_id": project.id, "status": project.get_status_display()}

    return None
