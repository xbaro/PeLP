""" Module implementing execution management features """
import os
import docker

import json

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Q
from django.utils import timezone, dateparse

from typing import Optional, Union, List, Tuple

from xml.etree import ElementTree

from zipfile import ZipFile

from sentry_sdk import capture_exception

from pelp.apps.web import models
from pelp.apps.web.models.utils import decode_json

from .utils import update_learner_result
from .utils import get_elapsed_time


def get_next_locked_status(execution: models.Execution) -> Optional[int]:
    """
        Get the next valid locked status for an execution
        :param execution: An execution object
        :return: The next status
    """
    next_status = None
    if execution.status == 1:  # CREATED
        next_status = 2  # PREPARING
    elif execution.status == 3 and models.Execution.objects.filter(status=4).count() < settings.MAX_PARALLEL_RUNS:
        # Only move from status 3 (PREPARED) to status 4 (RUNNING) if the maximum running executions is not met
        next_status = 4  # RUNNING

    return next_status


def get_next_execution(status: Union[int, List[int]]) -> Optional[models.Execution]:
    """
        Get the first execution with one of the provided status and move to the next valid locked status.

        :param status: The original status/statuses
        :return: An execution object with locked status
    """
    with transaction.atomic():
        # Filter for the first project in provided statuses
        if isinstance(status, int):
            execution = models.Execution.objects.filter(status=status).order_by('id').first()
        else:
            status_filter = None
            for s in status:
                if status_filter is None:
                    status_filter = Q(status=s)
                else:
                    status_filter |= Q(status=s)
            execution = models.Execution.objects.filter(status_filter).order_by('id').first()

        if execution is not None:
            next_status = get_next_locked_status(execution)

            if next_status is not None:
                execution.status = next_status
                execution.save()

                if execution.status == 6:  # INVALID
                    execution = None
            else:
                execution = None

    return execution


def launch_submission_tests(submission: models.Submission) -> Optional[int]:
    """
        Request submission tests execution
        :param submission: Submission object to be executed
        :return: The execution task ID
    """

    # Create an execution for this submission
    execution = create_execution(submission)

    if execution is None:
        return None

    return execution.id


def create_execution(submission: models.Submission):
    """
        Create an execution for given submission
        :param submission: Submission object
        :return: New execution object
    """

    # Create the execution path
    execution_path = os.path.join(submission.activity.course.semester.code,
                                  submission.activity.course.code,
                                  submission.activity.code,
                                  submission.learner.username,
                                  str(submission.id),
                                  '')

    # Create the execution
    execution = models.Execution.objects.create(
        status=0,  # CREATING
        project=submission.activity.project,
        submission=submission,
        execution_path=execution_path
    )

    # Change the status to created
    execution.status = 1  # CREATED
    execution.save()

    return execution


def prepare_execution(execution: models.Execution) -> models.Execution:
    """
        Prepare an execution to be executed
        :param execution: Execution object
        :return: New execution object
    """
    # Create the extraction path
    execution_path = os.path.join(settings.EXECUTION_PATH, execution.execution_path, '')

    # Create the path
    os.makedirs(execution_path)

    # Extract the submission
    with ZipFile(execution.submission.merged_submission, 'r') as merged_zip:
        merged_zip.extractall(execution_path)

    # Download the docker image
    client = docker.client.from_env()

    # Check image
    if execution.project.image not in client.images.list():
        client.images.pull(execution.project.image)

    # Update the status
    execution.status = 3  # PREPARED
    execution.save()

    return execution


def run_execution(execution: models.Execution) -> models.Execution:
    """
        Start running an execution
        :param execution: Execution object
        :return: The updated execution object
    """
    if execution.status != 4 or execution.container_id is not None:
        return execution

    # Mount Path
    mount_path = os.path.join(settings.DOCKER_MOUNT_ROOT_PATH, execution.execution_path, '').replace('\\', '/')

    # Run container
    client = docker.client.from_env()
    container = client.containers.run(execution.project.image,
                                      ["make", "clean", "test"],
                                      volumes={mount_path: {'bind': '/code', 'mode': 'rw'}},
                                      working_dir='/code',
                                      mem_limit=execution.project.mem_limit,
                                      detach=True)

    # Store the container ID
    execution.container_id = container.id
    execution.started_at = timezone.now()
    execution.save()

    return execution


def _update_grouping_nodes(submission: models.Submission, test: Optional[models.ProjectTest] = None) -> dict:
    passed = True
    num_tests = 0
    num_failed = 0
    num_passed = 0
    total_weight = 0

    if test is None:
        test = models.ProjectTest.objects.filter(project=submission.activity.project, parent__isnull=True).all()
        for top_test in test:
            test_result = _update_grouping_nodes(submission, top_test)
            passed = passed and test_result['passed']
            num_tests += test_result['num_tests']
            num_failed += test_result['num_failed']
            num_passed += test_result['num_passed']
            total_weight += test_result['total_weight']
    elif test.grouping_node:
        weight_sum = 0.0
        total_weight = 0.0
        for child in test.children.all():
            child_res = _update_grouping_nodes(submission, child)
            passed = passed and child_res['passed']
            num_tests += child_res['num_tests']
            num_failed += child_res['num_failed']
            num_passed += child_res['num_passed']
            weight_sum += child_res['total_weight']
            total_weight += child.weight
        final_weight = (weight_sum/total_weight) * test.weight

        try:
            result = models.SubmissionTestResult.objects.get(submission=submission, test=test)
            result.passed = passed
            result.num_tests = num_tests
            result.num_failed = num_failed
            result.num_passed = num_passed
            result.total_weight = final_weight
            result.save()
        except models.SubmissionTestResult.DoesNotExist:
            models.SubmissionTestResult.objects.create(
                submission=submission,
                test=test,
                passed=passed,
                num_tests=num_tests,
                num_failed=num_failed,
                num_passed=num_passed,
                total_weight=final_weight
            )
        total_weight = final_weight
    else:
        try:
            test_result = models.SubmissionTestResult.objects.get(
                submission=submission,
                test=test,
            )
        except models.SubmissionTestResult.DoesNotExist:
            test_result = models.SubmissionTestResult.objects.create(
                submission=submission,
                test=test,
                passed=False,
                num_tests=1,
                num_failed=1,
                num_passed=0,
                total_weight=0.0,
            )
        test_result.total_weight = (test_result.num_passed/test_result.num_tests) * test.weight
        test_result.save()

        passed = test_result.passed
        num_tests = test_result.num_tests
        num_failed = test_result.num_failed
        num_passed = test_result.num_passed
        total_weight = test_result.total_weight

    return {
        'passed': passed,
        'num_tests': num_tests,
        'num_failed': num_failed,
        'num_passed': num_passed,
        'total_weight': total_weight
    }


# Store test results
def _store_test_progress(submission: models.Submission) -> dict:
    ret_value = {
        'passed': 0,
        'total': 0
    }

    # Remove old results
    submission.submissiontestresult_set.all().delete()
    if submission.progress is not None:
        for line in submission.progress.split('\n'):
            test_progress_data = None
            mode = None
            if line.startswith('TEST:START') or line.startswith('TEST:END'):
                mode = line.split(':')[1]
                test_progress_data = decode_json(line.split('TEST:{}:'.format(mode))[1])

            if test_progress_data is None or 'test_code' not in test_progress_data or mode is None:
                continue

            try:
                test_obj = models.ProjectTest.objects.get(project=submission.activity.project,
                                                          code=test_progress_data['test_code'])
            except models.ProjectTest.DoesNotExist:
                continue
            if mode == "START":
                ret_value['total'] += 1
                models.SubmissionTestResult.objects.create(
                    submission=submission,
                    test=test_obj,
                    passed=False,
                    num_tests=1,
                    num_passed=0,
                    num_failed=1,
                    total_weight=0.0
                )
            elif mode == "END":
                try:
                    test_result = models.SubmissionTestResult.objects.get(
                            submission=submission,
                            test=test_obj
                    )
                    if 'result' in test_progress_data and test_progress_data['result'] == "OK":
                        test_result.passed = True
                        test_result.num_tests = 1
                        test_result.num_passed = 1
                        test_result.num_failed = 0
                        test_result.total_weight = test_obj.weight
                        ret_value['passed'] += 1
                    else:
                        test_result.passed = False
                        test_result.num_tests = 1
                        test_result.num_passed = 0
                        test_result.num_failed = 1
                        test_result.total_weight = 0.0
                    test_result.save()

                except models.SubmissionTestResult.DoesNotExist:
                    pass

    return ret_value


# Store test results
def _store_test_results(submission: models.Submission) -> None:
    # Remove old results
    submission.submissiontestresult_set.all().delete()
    result = decode_json(submission.result)
    if result is not None and 'sections' in result:
        for section in result['sections']:
            # Add tests
            for test in section['tests']:
                # Get the test object
                try:
                    test_obj = models.ProjectTest.objects.get(project=submission.activity.project,
                                                              code=test['code'])
                    passed = test['result'] == "OK"
                    if passed:
                        n_passed = 1
                        n_failed = 0
                    else:
                        n_passed = 0
                        n_failed = 1
                    models.SubmissionTestResult.objects.create(
                        submission=submission,
                        test=test_obj,
                        passed=passed,
                        num_tests=1,
                        num_passed=n_passed,
                        num_failed=n_failed,
                        total_weight=test_obj.weight * n_passed
                    )
                except models.ProjectTest.DoesNotExist:
                    pass
        result = _update_grouping_nodes(submission)
        submission.test_score = result['total_weight']
        submission.test_passed = result['passed']
        submission.num_tests = result['num_tests']
        submission.num_test_passed = result['num_passed']
        submission.num_test_failed = result['num_failed']
        submission.save()

    elif submission.progress is not None:
        _store_test_progress(submission)
        result = _update_grouping_nodes(submission)
        submission.test_score = result['total_weight']
        submission.test_passed = result['passed']
        submission.num_tests = result['num_tests']
        submission.num_test_passed = result['num_passed']
        submission.num_test_failed = result['num_failed']
        submission.save()


def _create_tests(submission: models.Submission):
    # Remove old tests
    submission.activity.project.projecttest_set.all().delete()
    result = decode_json(submission.result)
    if result is not None and 'sections' in result:
        for section in result['sections']:
            # Add section
            try:
                section_test = models.ProjectTest.objects.get(project=submission.activity.project,
                                                              code=section['code'])
            except models.ProjectTest.DoesNotExist:
                section_test = models.ProjectTest.objects.create(
                    project=submission.activity.project,
                    code=section['code'],
                    description=section['title'],
                    internal_code=section['code'],
                    parent=None,
                    grouping_node=True
                )
            # Add tests
            for test in section['tests']:
                if len(test['code'].split('_')) == 3 and test['code'].startswith(section_test.code):
                    sub_section_code = '{}_{}'.format(test['code'].split('_')[0], test['code'].split('_')[1])
                    test_internal_code = test['code'].split('_')[2]
                    try:
                        sub_section_test = models.ProjectTest.objects.get(project=submission.activity.project,
                                                                          code=sub_section_code)
                    except models.ProjectTest.DoesNotExist:
                        sub_section_test = models.ProjectTest.objects.create(
                            project=submission.activity.project,
                            code=sub_section_code,
                            internal_code=sub_section_code,
                            description=sub_section_code + ' tests',
                            parent=section_test,
                            grouping_node=True
                        )
                    try:
                        models.ProjectTest.objects.get(project=submission.activity.project, code=test['code'])
                    except models.ProjectTest.DoesNotExist:
                        models.ProjectTest.objects.create(
                            project=submission.activity.project,
                            code=test['code'],
                            internal_code=test_internal_code,
                            parent=sub_section_test,
                            description=test['description'],
                            grouping_node=False
                        )
                else:
                    try:
                        models.ProjectTest.objects.get(project=submission.activity.project, code=test['code'])
                    except models.ProjectTest.DoesNotExist:
                        models.ProjectTest.objects.create(
                            project=submission.activity.project,
                            code=test['code'],
                            internal_code=test['code'],
                            parent=section_test,
                            description=test['description'],
                            grouping_node=False
                        )


def _parse_stack_files(submission: models.Submission,
                       stack: ElementTree.Element,
                       base_dir: str) -> Tuple[Optional[models.SubmissionFile],
                                               Optional[int],
                                               Optional[str],
                                               Optional[list]]:
    if base_dir[-1] != '/' and base_dir[-1] != '\\':
        base_dir = '{}/'.format(base_dir)
    submission_file: Optional[models.SubmissionFile] = None
    file_line: Optional[int] = None
    file_function: Optional[str] = None
    ret_stack = []
    for frame in stack:
        frame_obj = {
            'ip': frame.find('ip').text,
            'obj': frame.find('obj').text,
            'fn': frame.find('fn').text,
            'dir': frame.find('dir'),
            'file': frame.find('file'),
            'line': frame.find('line'),
            'file_id': None,
        }
        if frame_obj['file'] is not None:
            frame_obj['file'] = frame_obj['file'].text
        if frame_obj['line'] is not None:
            frame_obj['line'] = int(frame_obj['line'].text)
        if frame_obj['dir'] is not None:
            frame_obj['dir'] = frame_obj['dir'].text
            if frame_obj['dir'].startswith(base_dir):
                frame_obj['dir'] = frame_obj['dir'][len(base_dir):]
                file_path = os.path.join(frame_obj['dir'], frame_obj['file']).replace('\\', '/')
                try:
                    sub_file = submission.submissionfile_set.get(filename=file_path)
                    if submission_file is None:
                        submission_file = sub_file
                        file_line = frame_obj['line']
                        file_function = frame_obj['fn']
                    frame_obj['file_id'] = sub_file.id
                except models.SubmissionFile.DoesNotExist:
                    pass
        ret_stack.append(frame_obj)

    return submission_file, file_line, file_function, ret_stack


def _store_valgrind_results(submission: models.Submission) -> Optional[int]:
    total_leaked_bytes: Optional[int] = None
    if submission.activity.project.use_valgrind and submission.valgrind_report is not None:
        valgrind_report_xml = submission.valgrind_report.read()
        report = ElementTree.fromstring(valgrind_report_xml)
        base_path = '/code'
        for error in report.findall('error'):
            kind = error.find('kind').text
            stack = error.find('stack')
            file, line, function, parsed_stack = _parse_stack_files(submission, stack, base_path)

            if kind.startswith('Leak_'):
                description = error.find('xwhat/text').text
                errs = models.SubmissionError.objects.filter(
                    submission=submission,
                    type=2,  # MEMORY_LEAK
                    source=1,  # VALGRIND
                    file=file,
                    line=line,
                    function=function,
                    description=description
                )
                if errs.count() == 1:
                    err_object = errs.first()
                    err_object.count += 1
                    err_object.save()
                else:
                    models.SubmissionError.objects.create(
                        submission=submission,
                        type=2,   # MEMORY_LEAK
                        source=1,  # VALGRIND
                        file=file,
                        line=line,
                        function=function,
                        order=None,
                        count=1,
                        code=kind,
                        description=description,
                        context=json.dumps({'stack': parsed_stack}),
                        value=int(error.find('xwhat/leakedbytes').text)
                    )
                if total_leaked_bytes is None:
                    total_leaked_bytes = 0
                total_leaked_bytes += int(error.find('xwhat/leakedbytes').text)
            elif kind.startswith('Uninit') or kind.startswith('Invalid'):
                description = error.find('what').text
                errs = models.SubmissionError.objects.filter(
                    submission=submission,
                    type=1,  # MEMORY_OPERATION
                    source=1,  # VALGRIND
                    file=file,
                    line=line,
                    function=function,
                    description=description
                )
                if errs.count() == 1:
                    err_object = errs.first()
                    err_object.count += 1
                    err_object.save()
                else:
                    models.SubmissionError.objects.create(
                        submission=submission,
                        type=1,  # MEMORY_OPERATION
                        source=1,  # VALGRIND
                        file=file,
                        line=line,
                        function=function,
                        order=None,
                        count=1,
                        code=kind,
                        description=description,
                        context=json.dumps({'stack': parsed_stack}),
                        value=None
                    )
            else:
                desc = None
                if error.find('what') is not None:
                    desc = error.find('what').text
                elif error.find('xwhat') is not None:
                    desc = error.find('xwhat').text
                errs = models.SubmissionError.objects.filter(
                    submission=submission,
                    type=0,  # OTHER
                    source=1,  # VALGRIND
                    file=file,
                    line=line,
                    function=function,
                    description=desc
                )
                if errs.count() == 1:
                    err_object = errs.first()
                    err_object.count += 1
                    err_object.save()
                else:
                    models.SubmissionError.objects.create(
                        submission=submission,
                        type=0,  # OTHER
                        source=1,  # VALGRIND
                        file=file,
                        line=line,
                        function=function,
                        order=None,
                        count=1,
                        code=kind,
                        description=desc,
                        context=json.dumps({'stack': parsed_stack}),
                        value=None
                    )
    return total_leaked_bytes


def _store_container_data(container, execution):
    # Check output binary exists
    app_bin = os.path.join(settings.EXECUTION_PATH, execution.execution_path, 'bin', execution.project.executable_name)
    execution.submission.built = False
    if os.path.exists(app_bin):
        execution.submission.built = True

    # Define the progress path
    progress_path = None
    if execution.project.progress_path is not None and len(execution.project.progress_path) > 0:
        progress_path = os.path.join(settings.EXECUTION_PATH, execution.execution_path, execution.project.progress_path)
    # Define the results path
    result_path = os.path.join(settings.EXECUTION_PATH, execution.execution_path, execution.project.results_path)

    # Store the progress
    if progress_path is not None and os.path.exists(progress_path):
        execution.submission.progress = open(progress_path, 'r').read()

    # Store Valgrind report
    if execution.project.use_valgrind:
        valgrind_report_path = None
        if execution.project.valgrind_report_path is not None and len(execution.project.valgrind_report_path) > 0:
            valgrind_report_path = os.path.join(settings.EXECUTION_PATH, execution.execution_path, execution.project.valgrind_report_path)
        if valgrind_report_path is not None and os.path.exists(valgrind_report_path):
            try:
                valgrind_report = open(valgrind_report_path, 'r', encoding='utf-8').read()
                execution.submission.valgrind_report.save(None, ContentFile(valgrind_report.encode('utf-8')))
                execution.submission.leaked_bytes = _store_valgrind_results(execution.submission)
            except Exception as ex:
                execution.submission.status = 10  # ERROR
                execution.submission.error = ex.__str__()
                execution.submission.result = None
                capture_exception(ex)

    # Store the results
    execution.submission.correct_execution = False
    if os.path.exists(result_path):
        try:
            execution.submission.result = open(result_path, 'r').read()
        except UnicodeDecodeError:
            try:
                execution.submission.result = open(result_path, 'r', encoding='iso-8859-1').read()
            except Exception as ex:
                execution.submission.status = 10  # ERROR
                execution.submission.error = ex.__str__()
                execution.submission.result = None
                capture_exception(ex)

        execution.submission.correct_execution = True

    # Store the logs
    execution.submission.execution_logs.save(None, ContentFile(container.logs()))

    # Store execution times
    started_at = dateparse.parse_datetime(container.attrs.get('State')['StartedAt'])
    finished_at = dateparse.parse_datetime(container.attrs.get('State')['FinishedAt'])
    execution.submission.executed_at = started_at
    execution.submission.elapsed_time = int((finished_at - started_at).microseconds / 1000)

    # Store results summary
    try:
        if execution.submission.result is not None:
            result = json.loads(execution.submission.result)
            execution.submission.test_passed = result['failed'] == 0
            execution.submission.test_percentage = float(result['passed']) / float(result['total'])
            execution.submission.status = 8  # PROCESSED
        elif execution.submission.progress is not None:
            progress_result = _store_test_progress(execution.submission)
            execution.submission.test_passed = False
            if progress_result['total'] > 0:
                execution.submission.test_percentage = float(progress_result['passed']) / float(progress_result['total'])
            else:
                execution.submission.test_percentage = 0
            execution.submission.status = 8  # PROCESSED
        else:
            execution.submission.test_passed = False
            execution.submission.test_percentage = 0.0
            if execution.status == 8:  # TIMEOUT
                execution.submission.status = 11  # TIMEOUT
                execution.submission.error = 'Execution does not end in allowed time.'
            else:
                execution.submission.status = 10  # ERROR
                execution.submission.error = 'Output file not found.'
    except Exception as ex:
        capture_exception(ex)
        execution.submission.status = 10
        execution.submission.error = ex.__str__()

    execution.submission.save()
    execution.save()

    # If this is a test submission, update project
    if execution.submission.is_test:
        if execution.submission.testsubmission.source == 0:
            # Base code
            if execution.submission.status == 8:  # PROCESSED
                execution.project.status = 7  # VALID
            elif execution.project.allow_base_failure:
                # If failure is allowed, set final status as valid
                execution.project.status = 7  # VALID
                execution.project.error = execution.submission.error
            else:
                execution.project.status = 10  # INVALID
                execution.project.error = execution.submission.error
        else:
            # Test Code
            if execution.submission.status == 8:  # PROCESSED
                if execution.submission.test_passed:
                    # Generate the test structure
                    _create_tests(execution.submission)
                    # Store test results
                    _store_test_results(execution.submission)
                    # Set final status
                    execution.project.status = 9  # PROCESSED
                else:
                    execution.project.status = 13  # TEST_FAILED
                    execution.project.error = execution.submission.error
            else:
                execution.project.status = 13  # TEST_FAILED
        execution.project.save()
    else:
        # Store test results
        _store_test_results(execution.submission)


def check_running_executions():
    # Get the Docker client
    client = docker.client.from_env()

    # Get running executions
    for execution in models.Execution.objects.filter(status=4, container_id__isnull=False).all():
        container = client.containers.get(execution.container_id)

        if container is None:
            execution.status = 7  # ERROR
            execution.save()
            execution.submission.status = 10
            execution.submission.error = 'Invalid container ID on submission execution task'
            execution.submission.save()
            # Update the learner results related with this submission
            update_learner_result(learner=execution.submission.learner, activity=execution.submission.activity)
        else:
            if container.status == 'exited':
                _store_container_data(container, execution)
                execution.status = 5  # FINISHED
                execution.save()
                # Update the learner results related with this submission
                update_learner_result(learner=execution.submission.learner, activity=execution.submission.activity)
                # Remove the container
                container.remove()
            elif get_elapsed_time(execution.started_at) > execution.project.max_execution_time:
                container.stop()
                _store_container_data(container, execution)
                execution.status = 8  # TIMEOUT
                execution.save()
                # Update the learner results related with this submission
                update_learner_result(learner=execution.submission.learner, activity=execution.submission.activity)
                # Remove the container
                container.remove()
