""" Module implementing project management features """
from typing import List, Union, Optional
from zipfile import ZipFile

from django.core.files.base import ContentFile

from django.db.models import Q
from django.db import transaction

from pelp.apps.web import models

from .utils import get_base_path
from .utils import get_module


def get_next_locked_status(project: models.Project) -> Optional[int]:
    """
        Get the next valid locked status for a project
        :param project: A project object
        :return: The next status
    """
    next_status = None
    if project.status == 1:  # CREATED
        if project.repository is not None:
            next_status = 2  # CLONING
        elif len(project.code_base_zip.name) > 0:
            next_status = 4  # UPLOADING
        else:
            next_status = 10  # INVALID
    elif project.status == 3 or project.status == 5:  # CLONED or UPLOADED
        next_status = 6  # VALIDATING
    elif project.status == 7:  # VALID
        next_status = 8  # TESTING

    return next_status


def get_next_project(status: Union[int, List[int]]) -> Optional[models.Project]:
    """
        Get the first project with one of the provided status and move to the next valid locked status.

        :param status: The original status/statuses
        :return: A project object with locked status
    """
    with transaction.atomic():
        # Filter for the first project in provided statuses
        if isinstance(status, int):
            project = models.Project.objects.filter(status=status).order_by('id').first()
        else:
            status_filter = None
            for s in status:
                if status_filter is None:
                    status_filter = Q(status=s)
                else:
                    status_filter |= Q(status=s)
            project = models.Project.objects.filter(status_filter).order_by('id').first()

        if project is not None:
            next_status = get_next_locked_status(project)

            if next_status is not None:
                project.status = next_status
                project.save()

                if project.status == 10:  # INVALID
                    project = None
            else:
                project = None

    return project


def clone_project_files(project: models.Project) -> models.Project:
    """
        Clone project files from repository

        :param project: The project
        :return: The project with updated status
    """
    raise NotImplemented("Not implemented method")


def upload_project_files(project: models.Project) -> models.Project:
    """
        Upload project files to the storage server

        :param project: The project
        :return: The project with updated status
    """
    with ZipFile(project.code_base_zip, 'r') as base_zip_obj:
        # Get the list of files
        files_list = base_zip_obj.namelist()

        # Get base path
        base_path = get_base_path(files_list, project.anchor_file)

        # Remove existing files
        models.ProjectFile.objects.filter(project=project).delete()

        # Get modules
        paths = models.ProjectModule.objects.filter(project=project).values_list('base_path', flat=True)

        # Check empty base path
        if base_path is not None and len(base_path.strip()) == 0:
            base_path = None

        # Extract files
        for file in files_list:
            # Skip folders
            if file.endswith('/') or file.endswith('\\'):
                continue
            # Apply base path
            dst_file = file
            if base_path is not None and file.startswith(base_path):
                dst_file = file[len(base_path) + 1:]

            # Get the module
            module = get_module(project, dst_file, paths)
            # Store the result
            file_object = models.ProjectFile.objects.create(
                project=project,
                module=module,
                original_filename=file,
                filename=dst_file
            )
            content = base_zip_obj.read(file)
            file_object.file.save(None, ContentFile(content))

    project.status = 5  # UPLOADED
    project.save()

    return project
