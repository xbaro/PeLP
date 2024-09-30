""" Module implementing data importation management features """
import pandas as pd
from typing import List, Union, Optional
from zipfile import ZipFile

from django.core.files.base import ContentFile

from django.db.models import Q
from django.db import transaction

from sentry_sdk import capture_exception

from pelp.apps.web import models

from .submission import import_submission_entry

def get_next_locked_status(session: models.ImportSession) -> Optional[int]:
    """
        Get the next valid locked status for an import session
        :param session: An import session object
        :return: The next status
    """
    next_status = None
    if session.status == 0:  # CREATED
        next_status = 1  # LOADING
    elif session.status == 2 and session.valid:  # LOADED
        next_status = 3  # IMPORTING

    return next_status


def get_next_session(status: Union[int, List[int]]) -> Optional[models.ImportSession]:
    """
        Get the first import session with one of the provided status and move to the next valid locked status.

        :param status: The original status/statuses
        :return: An import session object with locked status
    """
    with transaction.atomic():
        # Filter for the first import session in provided statuses
        if isinstance(status, int):
            session = models.ImportSession.objects.filter(status=status).order_by('id').first()
        else:
            status_filter = None
            for s in status:
                if status_filter is None:
                    status_filter = Q(status=s)
                else:
                    status_filter |= Q(status=s)
            session = models.ImportSession.objects.filter(status_filter).order_by('id').first()

        if session is not None:
            next_status = get_next_locked_status(session)

            if next_status is not None:
                session.status = next_status
                session.save()

                if session.status == 5:  # INVALID
                    session = None
            else:
                session = None

    return session


def load_session_data(session: models.ImportSession) -> models.ImportSession:

    if session.type == 0:  # LEARNERS
        session = load_learners_data(session)
    elif session.type == 1:  # SUBMISSIONS
        session = load_submissions_data(session)

    return session


def import_session_data(session: models.ImportSession) -> models.ImportSession:

    if session.type == 0:  # LEARNERS
        session = import_learners_data(session)
    elif session.type == 1:  # SUBMISSIONS
        session = import_submissions_data(session)

    return session


def split_name(full_name: str):

    full_name = full_name.replace("El ", "El__")
    full_name = full_name.replace("De ", "De__")
    name_parts = full_name.split()
    if len(name_parts) == 2:
        first_name = name_parts[0]
        last_name = name_parts[1]
    elif len(name_parts) == 3:
        first_name = name_parts[0]
        last_name = '{} {}'.format(name_parts[1], name_parts[2])
    elif len(name_parts) > 3:
        if name_parts[len(name_parts)-2].lower() == 'i':
            # Name SN1 i SN2
            first_name = ' '.join(name_parts[:len(name_parts) - 3])
            last_name = '{} {} {}'.format(name_parts[len(name_parts)-3], name_parts[len(name_parts)-2], name_parts[len(name_parts)-1])
        else:
            # N1 N2 Nn SN1 SN2
            first_name = ' '.join(name_parts[:len(name_parts) - 2])
            last_name = ' '.join(name_parts[len(name_parts) - 2:])

    first_name = first_name.replace("__", " ")
    last_name = last_name.replace("__", " ")

    return [first_name, last_name]


def load_learners_data(session: models.ImportSession) -> models.ImportSession:
    assert session.type == 0

    if session.input_file.name is None or \
            (not session.input_file.name.endswith('.xls') and not session.input_file.name.endswith('.xlsx')):
        session.status = 5  # INVALID
        session.save()
    else:
        data = pd.read_excel(session.input_file)
        session.importsessionentry_set.all().delete()
        for index, row in data.iterrows():
            # Check if this learner exists
            try:
                learner = models.Learner.objects.get(email=row['Correo'])
            except models.Learner.DoesNotExist:
                learner = None

            # Add entry to session
            [first_name, last_name] = split_name(row['Nombre'])
            models.ImportSessionEntry.objects.create(
                session=session,
                learner=learner,
                data={
                    "raw": {
                        "name": row['Nombre'],
                        "email": row['Correo'],
                    },
                    "email": row['Correo'],
                    "username": row['Correo'].split('@')[0],
                    "first_name": first_name,
                    "last_name": last_name
                },
                is_valid=False
            )
        session.status = 2
        session.save()

    return session


def _get_learner(file_parts: List[str], activity_code: Optional[str]=None):
    username = None
    learner = None
    if len(file_parts) == 2:
        username = file_parts[1]
    try:
        learner = models.Learner.objects.get(username=username)
    except models.Learner.DoesNotExist:
        learner_options = models.Learner.objects.filter(username__endswith=file_parts[-1]).all()
        for option in learner_options:
            for i in range(len(file_parts)-2, 0, -1):
                if option.username.startswith(file_parts[i]):
                    learner = option
                    username = learner.username
                    break
                elif file_parts[i] not in option.username:
                    break
        if learner is None and len(learner_options) == 1:
            learner = learner_options[0]
            username = learner.username

    return learner, username


def load_submissions_data(session: models.ImportSession) -> models.ImportSession:
    assert session.type == 1
    if session.input_file.name is None or not session.input_file.name.endswith('.zip'):
        session.status = 5  # INVALID
        session.save()
    else:
        session.importsessionentry_set.all().delete()
        with ZipFile(session.input_file, 'r') as zip_file:
            activity_code = None
            pending_imports = []
            for file in zip_file.filelist:
                # Fix known file issues
                filename = file.filename
                if file.filename.endswith('_tar.gz'):
                    filename = file.filename.replace('_tar.gz', '.tar.gz')

                # Process the file
                file_parts = filename.split('_')
                if len(file_parts) < 9:
                    continue

                user_parts = file_parts[:-7]
                submission_date = file_parts[-6:]
                submission_date[-1] = submission_date[-1].split('.')[0]
                day = submission_date[0]
                submission_date[0] = submission_date[2]
                submission_date[2] = day

                if activity_code is None and len(file_parts) == 9:
                    activity_code = file_parts[-7]
                learner, username = _get_learner(user_parts, activity_code)

                # Read the file
                content = zip_file.read(file.filename)

                # Add entry to session
                entry = models.ImportSessionEntry.objects.create(
                    session=session,
                    learner=learner,
                    data={
                        "filename": filename,
                        "username": username,
                        "submission_date": '{}-{}-{}T{}:{}:{}'.format(*submission_date)
                    },
                    is_valid=False
                )
                # Save the file
                entry.entry_file.save(filename, ContentFile(content))

            session.status = 2
            session.save()

    return session


def import_learners_data(session: models.ImportSession) -> models.ImportSession:
    assert session.type == 0 and session.valid

    for entry in session.importsessionentry_set.all():
        try:
            entry_data = entry.get_data()
            try:
                learner = models.Learner.objects.get(username=entry_data['username'])
            except models.Learner.DoesNotExist:
                learner = models.Learner.objects.create(
                    username=entry_data['username'],
                    first_name=entry_data['first_name'],
                    last_name=entry_data['last_name'],
                    email=entry_data['email'],
                )
            entry.learner = learner
            entry.is_valid = True
            entry.error = None
            entry.save()
            session.course_group.learner_set.add(learner)
        except Exception as ex:
            capture_exception(ex)
            entry.is_valid = False
            entry.error = ex.__str__()
            entry.save()

    session.status = 4
    session.save()

    return session


def import_submissions_data(session: models.ImportSession) -> models.ImportSession:
    assert session.type == 1 and session.valid

    for entry in session.importsessionentry_set.all():
        try:
            submission = import_submission_entry(entry)
            if submission is not None:
                submission.is_official = session.set_official
                if submission.status == 1:
                    entry.is_valid = True
                    entry.error = None
                    entry.save()
                else:
                    entry.is_valid = False
                    entry.error = submission.error
                    entry.save()
            else:
                entry.is_valid = False
                entry.error = "Missing submission"
                entry.save()
        except Exception as ex:
            capture_exception(ex)
            entry.is_valid = False
            entry.error = ex.__str__()
            entry.save()

    session.status = 4
    session.save()

    return session
