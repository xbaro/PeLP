""" Module implementing submission management features """
import io
import datetime
import tarfile
import typing
import tempfile
import canvasapi.submission

from typing import List, Union, Optional, Literal
from rarfile import RarFile
from zipfile import ZipFile
from py7zr import SevenZipFile

from django.core.files.base import ContentFile, File
from django.utils import timezone
from django.db.models import Q
from django.db.models.fields.files import FieldFile
from django.db import transaction

from pelp.apps.web import models
from pelp.apps.web.models.utils import decode_json

from .execution import launch_submission_tests

from .utils import compute_diff
from .utils import get_submission_merge_structure
from .utils import get_structure_context
from .utils import get_makefile
from .utils import store_merged_code
from .utils import update_learner_result


def get_next_locked_status(submission: models.Submission) -> Optional[int]:
    """
        Get the next valid locked status for a submission
        :param submission: A submission object
        :return: The next status
    """
    next_status = None
    if submission.status == 1:  # CREATED
        if submission.repository is not None:
            next_status = 2  # CLONING
        elif len(submission.submission.name) > 0:
            next_status = 4  # MERGING
        else:
            next_status = 10  # INVALID
    elif submission.status == 3:  # CLONED
        next_status = 4  # MERGING
    elif submission.status == 5:  # MERGED
        next_status = 6  # WAITING

    return next_status


def get_next_submission(status: Union[int, List[int]]) -> Optional[models.Submission]:
    """
        Get the first submission with one of the provided status and move to the next valid locked status.

        :param status: The original status/statuses
        :return: A submission object with locked status
    """
    with transaction.atomic():
        # Filter for the first project in provided statuses
        if isinstance(status, int):
            submission = models.Submission.objects.filter(status=status).order_by('id').first()
        else:
            status_filter = None
            for s in status:
                if status_filter is None:
                    status_filter = Q(status=s)
                else:
                    status_filter |= Q(status=s)
            submission = models.Submission.objects.filter(status_filter).order_by('id').first()

        if submission is not None:
            next_status = get_next_locked_status(submission)

            if next_status is not None:
                submission.status = next_status
                submission.save()

                if submission.status == 9:  # INVALID
                    submission = None
            else:
                submission = None

    return submission


def clone_submission_files(submission: models.Submission) -> models.Submission:
    """
        Clone submission files from repository

        :param submission: The submission
        :return: The submission with updated status
    """
    raise NotImplemented("Not implemented method")


def merge_submission_files(submission: models.Submission) -> models.Submission:
    """
        Merge submission files

        :param submission: The submission
        :return: The submission with updated status
    """
    # Get the merge structure
    merge_structure = get_submission_merge_structure(submission)

    # Get the context structure for Makefile
    context = get_structure_context(submission.activity.project, merge_structure)

    # Get Makefile
    makefile = get_makefile(context)

    # Store merged code
    submission = store_merged_code(submission, merge_structure, makefile)

    submission.status = 5  # MERGED
    submission.save()

    # Compute files differences
    compute_diff(submission)

    return submission


def run_submission_tests(submission: models.Submission) -> models.Submission:
    """
        Run submission tests

        :param submission: The submission
    """
    work_id = launch_submission_tests(submission)

    if work_id is None:
        submission.status = 10  # ERROR
        submission.save()

        # Update the learner results related with this submission
        update_learner_result(learner=submission.learner, activity=submission.activity)

    return submission


def create_test_submission(project: models.Project, source: Literal[0, 1]) -> None:
    """
        Create a test submission with the code provided as part of the project description
        :param project: Project object
        :param source: Source for the submission: 0 for base code and 1 for test code
    """
    # Create a new test submission
    submission = models.TestSubmission.objects.create(
        status=0,
        activity=project.activity,
        learner=None,
        submitted_at=timezone.now(),
        source=source,
    )
    if source == 0:
        # Copy the base code as submission code
        base_code = ContentFile(project.code_base_zip.file.read())
        submission.submission.save(None, base_code)
        project.code_base_zip.file.close()
        project.code_base_result = submission
    else:
        # Copy the test code as submission code
        test_code = ContentFile(project.code_test_zip.file.read())
        submission.submission.save(None, test_code)
        project.code_test_zip.file.close()
        project.code_test_result = submission

    # Change status to created
    submission.status = 1
    submission.save()

    # Save project
    project.save()

    # Update the learner results related with this submission
    update_learner_result(learner=submission.learner, activity=submission.activity)


def _copy_data(source: typing.Union[File, canvasapi.submission.File], destination: FieldFile) -> bool:
    valid = True
    if isinstance(source, File):
        source_filename = source.name.lower()
    elif isinstance(source, canvasapi.submission.File):
        source_filename = source.filename.lower()
    else:
        return False

    if source_filename.endswith('.zip'):
        if isinstance(source, File):
            source_code = ContentFile(source.file.read())
        elif isinstance(source, canvasapi.submission.File):
            source_code = ContentFile(source.get_contents(binary=True))
        else:
            return False
        destination.save(source_filename, source_code)
        if isinstance(source, File):
            source.file.close()
    elif source_filename.endswith('.rar'):
        buffer = io.BytesIO()
        if isinstance(source, File):
            source_file = source
        elif isinstance(source, canvasapi.submission.File):
            # Create a temporal file
            source_file = tempfile.TemporaryFile()
            source_file.write(source.get_contents(binary=True))
            source_file.seek(0)
        else:
            return False
        with RarFile(source_file, 'r') as rar_file:
            with ZipFile(buffer, 'w') as zip_file:
                # Extract files
                for file in rar_file.namelist():
                    # Skip folders
                    if file.endswith('/') or file.endswith('\\'):
                        continue
                    content = rar_file.read(file)
                    zip_file.writestr(file, content)
            content = ContentFile(buffer.getvalue())
            destination.save(source_filename, content)
        if isinstance(source, canvasapi.submission.File):
            source_file.close()
    elif source_filename.endswith('.tar.gz'):
        buffer = io.BytesIO()
        if isinstance(source, File):
            tar_content = source.read()
        elif isinstance(source, canvasapi.submission.File):
            tar_content = source.get_contents(binary=True)
        else:
            return False
        input_buffer = io.BytesIO(tar_content)
        with tarfile.open(fileobj=input_buffer) as tar_file:
            with ZipFile(buffer, 'w') as zip_file:
                # Extract files
                for file in tar_file.getnames():
                    ext_file = tar_file.extractfile(file)
                    if ext_file is not None:
                        content = ext_file.read()
                        zip_file.writestr(file, content)
            content = ContentFile(buffer.getvalue())
            destination.save(None, content)
    elif source_filename.endswith('.7z'):
        buffer = io.BytesIO()
        if isinstance(source, File):
            sevenzip_content = source.read()
        elif isinstance(source, canvasapi.submission.File):
            sevenzip_content = source.get_contents(binary=True)
        else:
            return False
        input_buffer = io.BytesIO(sevenzip_content)
        with SevenZipFile(input_buffer, 'r') as sevenzip_file:
            with ZipFile(buffer, 'w') as zip_file:
                # Extract files
                for file in sevenzip_file.getnames():
                    sevenzip_file.reset()
                    # Skip folders
                    if file.endswith('/') or file.endswith('\\'):
                        continue
                    if '.codelite' in file or '.build-' in file:
                        continue
                    try:
                        content = sevenzip_file.read(file)
                    except Exception:
                        continue
                    if len(content.items()) > 0:
                        file_content = content[file].read()
                        zip_file.writestr(file, file_content)
            content = ContentFile(buffer.getvalue())
            destination.save(source_filename, content)
    else:
        valid = False
    return valid


def import_submission_entry(entry: models.ImportSessionEntry) -> Optional[models.Submission]:
    """
        Create a submission with the code provided as part of an import process
        :param entry: Imported submission entry
    """
    assert entry.session.activity is not None

    entry_data = decode_json(entry.data)

    assert entry_data is not None
    assert 'submission_date' in entry.data

    try:
        submission_date = timezone.make_aware(datetime.datetime.fromisoformat(entry_data['submission_date']))
    except Exception:
        submission_date = timezone.now()

    # Create the new submission
    submission = models.Submission.objects.create(
        status=0,
        activity=entry.session.activity,
        learner=entry.learner,
        submitted_at=submission_date,
        is_official=entry.session.set_official
    )
    # Copy the imported entry data
    if _copy_data(entry.entry_file, submission.submission):
        # Change status to created
        submission.status = 1
        submission.error = None
    else:
        # Change status to invalid
        submission.status = 9
        submission.error = "Invalid file format {}".format(entry.entry_file.name.lower().split('.')[-1])

    submission.save()

    # Update the learner results related with this submission
    update_learner_result(learner=submission.learner, activity=submission.activity)

    return submission


def import_mail_submission(mail: models.MailSubmission) -> Optional[models.MailSubmission]:
    """
        Create a submission with the code provided as part of a mail submission
        :param entry: Mail submission
    """
    assert mail.status == 2

    # Check if submission can be accepted
    if mail.instructor is None and mail.inbox.activity.end is not None and mail.received_at > mail.inbox.activity.end:
        mail.status = 6  # OVERDUE
        mail.save()
        return None

    if mail.instructor is not None and mail.learner.id < 0:
        submission = models.InstructorSubmission.objects.create(
            status=0,
            activity=mail.inbox.activity,
            submitted_at=mail.received_at,
            instructor=mail.instructor
        )
    else:
        submission = models.Submission.objects.create(
            status=0,
            activity=mail.inbox.activity,
            submitted_at=mail.received_at,
            learner=mail.learner
        )
    mail.status = 3
    mail.submission = submission

    # Copy the mail attachment data
    if _copy_data(mail.attachment, submission.submission):
        # Change status to created
        submission.status = 1
        submission.error = None
    else:
        # Change status to invalid
        submission.status = 9
        submission.error = "Invalid file format {}".format(mail.attachment.name.lower().split('.')[-1])
        mail.error = submission.error
        mail.status = 5
    mail.save()
    submission.save()

    return mail


def create_submission(activity: models.Activity,
                      file: typing.Union[File, canvasapi.submission.File],
                      learner: Optional[models.Learner] = None,
                      instructor: Optional[models.Instructor] = None,
                      submission_date: Optional[timezone.datetime] = None,
                      is_official: bool = False
                      ) -> Optional[models.Submission]:
    """
        Create a submission
        :param activity: The activity where submission is created
        :param file: The submission file
        :param learner: The learner performing the submission
        :param instructor: The instructor performing the submission
        :param submission_date: Submission date to be assigned
    """
    assert activity is not None
    assert file is not None
    assert learner is not None or instructor is not None

    if submission_date is None:
        submission_date = timezone.now()

    # Create the new submission
    if instructor is None:
        submission = models.Submission.objects.create(
            status=0,
            activity=activity,
            learner=learner,
            submitted_at=submission_date,
            is_official=is_official
        )
    else:
        submission = models.InstructorSubmission.objects.create(
            status=0,
            activity=activity,
            instructor=instructor,
            submitted_at=submission_date,
            is_official=is_official
        )
        submission = submission.submission_ptr
        if learner is not None:
            submission.learner = learner
            submission.save()
    assert submission is not None

    # Copy the imported entry data
    if _copy_data(file, submission.submission):
        # Change status to created
        submission.status = 1
        submission.error = None
    else:
        # Change status to invalid
        submission.status = 9
        if isinstance(file, File):
            submission.error = "Invalid file format {}".format(file.name.lower().split('.')[-1])
        elif isinstance(file, canvasapi.submission.File):
            submission.error = "Invalid file format {}".format(file.filename.lower().split('.')[-1])
        else:
            submission.error = "Invalid file format and type"

    submission.save()

    # Update the learner results related with this submission
    update_learner_result(learner=submission.learner, activity=submission.activity)

    return submission


def import_canvas_submission(activity: models.Activity,
                      learner: models.Learner,
                      submission: canvasapi.submission.Submission,
                      is_official: bool = False
                      ) -> Optional[models.Submission]:
    """
        Create a submission
        :param activity: The activity where submission is created
        :param file: The submission file
        :param learner: The learner performing the submission
        :param instructor: The instructor performing the submission
        :param is_official: Whether this submission is an official submission or not.
    """
    assert activity is not None
    assert learner is not None
    assert submission is not None

    for file in submission.attachments:
        new_submission = create_submission(activity, file, learner, submission_date=file.modified_at_date, is_official=is_official)
        break

    return new_submission
