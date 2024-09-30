import json
import os
import re
import io
import difflib

from django.db import transaction
from django.db.models import F, Value, Count, Q, Subquery
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils import timezone

import pelp.apps.web.models
from pelp.apps.web import models
from pelp.apps.web.lib.exception import PelpProjectException
from typing import Optional, List
from zipfile import ZipFile


def get_base_path(files_list: List[str], anchor_file: str):
    """
        Get the path to the anchor file
        :param files_list: List of files
        :param anchor_file: The name of the anchor file
        :return: Path to the anchor file or None if not found
        :rtype: str
    """
    if anchor_file is None:
        return None

    # Build the pattern to find the anchor_file
    r = re.compile(r"^(.*[/\\])?{}$".format(anchor_file))

    # Get anchor instances
    anchor_list = list(filter(r.match, files_list))

    # Check that anchor_file exists
    if len(anchor_list) == 0:
        return None

    # Ensure no multiple instances of anchor file
    if len(anchor_list) > 1:
        raise PelpProjectException('Multiple instances of project anchor file [{}]. '.format(anchor_file))

    return os.path.dirname(anchor_list[0])


def get_module(project: models.Project, path: str,
               allowed_paths: Optional[List[str]] = None
               ) -> Optional[models.ProjectModule]:
    """
        Find the module containing given path
        :param project: The project
        :param path: The file path
        :param allowed_paths: Allowed module paths
        :return: The module object
    """
    module = None
    if allowed_paths is None:
        allowed_paths = models.ProjectModule.objects.filter(project=project).values_list('base_path', flat=True)

    for module_str in allowed_paths:
        if path.startswith(module_str):
            try:
                module = models.ProjectModule.objects.get(project=project, base_path=module_str)
            except models.ProjectModule.DoesNotExist:
                module = None
            except models.ProjectModule.MultipleObjectsReturned:
                module = None
            break

    return module


def get_merge_structure(project: models.Project, code: Optional[ZipFile] = None):
    structure = {}

    # Add project files
    for file in project.projectfile_set.all():
        # Exclude Makefile
        if file.filename == "Makefile":
            continue
        # Store the file
        module = None
        if file.module is not None:
            module = file.module.name
        structure[file.filename] = {
            'module': module,
            'locked': file.locked,
            'source': 'project',
            'original_file': file.original_filename
        }
    # Get modules
    paths = models.ProjectModule.objects.filter(project=project).values_list('base_path', flat=True)
    # Add code files
    code_files = []
    if code is not None:
        code_files = code.namelist()
    # Get base path
    base_path = get_base_path(code_files, project.anchor_file)
    if base_path is None:
        # TODO: Perform smart alignment if anchor file is not found (dict with filename as key and list of paths)
        base_path = smart_alignment(code_files, project)

    accepted_files_pattern = None
    if project.allowed_files_regex is not None and len(project.allowed_files_regex.strip()) > 0:
        accepted_files_pattern = re.compile(project.allowed_files_regex)
    if base_path is not None and len(base_path.strip()) == 0:
        base_path = None
    for file in code_files:
        # Skip folders
        if file.endswith('/') or file.endswith('\\'):
            continue
        # Skip Codelite folders
        if '.codelite' in file or '.build-' in file:
            continue
        # Skip MACOS ZIP hidden file
        if '__MACOSX' in file:
            continue
        # Skip files not matching accepted files
        if accepted_files_pattern is not None and not accepted_files_pattern.match(file):
            # Include report
            include = False
            if project.activity.include_report:
                if project.activity.report_name is None and file.lower().endswith('.pdf'):
                    include = True
                elif project.activity.report_name is not None and file.lower() == project.activity.report_name.lower():
                    include = True
            if not include:
                continue
        # Apply base path
        dst_file = file
        if base_path is not None and file.startswith(base_path) and len(base_path) > 0:
            dst_file = file[len(base_path) + 1:]
        # Skip Makefile
        if dst_file == 'Makefile':
            continue
        # Skip output folders
        if dst_file.startswith('bin/') or dst_file.startswith('bin\\') or dst_file.startswith('lib/') or dst_file.startswith('lib\\'):
            continue
        # Get the module
        if dst_file not in structure:
            module = get_module(project, dst_file, paths)
            if module is not None:
                module = module.name
            structure[dst_file] = {
                'module': module,
                'source': 'code',
                'original_file': file
            }
        elif not structure[dst_file]['locked']:
            structure[dst_file]['source'] = 'code'
            structure[dst_file]['original_file'] = file
    return structure


def get_structure_context(project: models.Project, structure: dict):
    context = {
        'app_name': project.executable_name,
        'app': {
            'sources': [],
            'include': [],
        },
        'libs': {},
        'test_args': project.test_arguments,
        'use_valgrind': project.use_valgrind,
        'valgrind_report': project.valgrind_report_path,
    }
    for file in structure.keys():
        if file.endswith('.c'):
            src_dir = os.path.dirname(file)
            if structure[file]['module'] is None:
                if src_dir not in context['app']['sources']:
                    context['app']['sources'].append(src_dir)
            else:
                if structure[file]['module'] not in context['libs']:
                    context['libs'][structure[file]['module']] = {
                        'sources': [],
                        'include': [],
                    }
                if src_dir not in context['libs'][structure[file]['module']]['sources']:
                    context['libs'][structure[file]['module']]['sources'].append(src_dir)
        elif file.endswith('.h'):
            inc_dir = os.path.dirname(file)
            if structure[file]['module'] is None:
                if inc_dir not in context['app']['include']:
                    context['app']['include'].append(inc_dir)
            else:
                if structure[file]['module'] not in context['libs']:
                    context['libs'][structure[file]['module']] = {
                        'sources': [],
                        'include': [],
                    }
                if inc_dir not in context['libs'][structure[file]['module']]['include']:
                    context['libs'][structure[file]['module']]['include'].append(inc_dir)
    return context


def get_project_context(project):
    context = {
        'app_name': project.executable_name,
        'app': {
            'sources': [],
            'include': [],
        },
        'libs': {},
        'test_args': project.test_arguments
    }

    for file in project.projectfile_set.all():
        if file.filename.endswith('.c'):
            src_dir = os.path.dirname(file.filename)
            if file.module is None:
                if src_dir not in context['app']['sources']:
                    context['app']['sources'].append(src_dir)
            else:
                if file.module.name not in context['libs']:
                    context['libs'][file.module.name] = {
                        'sources': [],
                        'include': [],
                    }
                if src_dir not in context['libs'][file.module.name]['sources']:
                    context['libs'][file.module.name]['sources'].append(src_dir)
        elif file.filename.endswith('.h'):
            inc_dir = os.path.dirname(file.filename)
            if file.module is None:
                if inc_dir not in context['app']['include']:
                    context['app']['include'].append(inc_dir)
            else:
                if file.module.name not in context['libs']:
                    context['libs'][file.module.name] = {
                        'sources': [],
                        'include': [],
                    }
                if inc_dir not in context['libs'][file.module.name]['include']:
                    context['libs'][file.module.name]['include'].append(inc_dir)
    return context

def _solve_root_path(paths):
    return list(map(lambda x: x if len(x.strip()) > 0 else '.', paths))

def get_makefile(context):
    libs = []
    for lib in context['libs']:
        libs.append( {
            'name': lib,
            'sources': _solve_root_path(context['libs'][lib]['sources']),
            'include': _solve_root_path(context['libs'][lib]['include'])
        })
    context['libs'] = libs

    # Fix main app paths
    context['app']['sources'] = _solve_root_path(context['app']['sources'])
    context['app']['include'] = _solve_root_path(context['app']['include'])

    result = render_to_string('web/makefile/Makefile', context=context)
    result = result.replace('        ', '\t')
    return result


def get_submission_merge_structure(submission: models.Submission):
    if submission.is_test:
        test_submission: models.TestSubmission = submission.testsubmission
        if test_submission.source == 0:
            # Get the merge structure from project
            merge_structure = get_merge_structure(test_submission.activity.project)
        else:
            with ZipFile(test_submission.submission, 'r') as test_zip_obj:
                # Get the merge structure from project and test code
                merge_structure = get_merge_structure(test_submission.activity.project, test_zip_obj)
    else:
        with ZipFile(submission.submission, 'r') as submission_zip_obj:
            # Get the merge structure from project and submitted code
            merge_structure = get_merge_structure(submission.activity.project, submission_zip_obj)
    return merge_structure


def store_merged_code(submission, merge_structure, makefile):

    # Remove existing files
    models.SubmissionFile.objects.filter(submission=submission).delete()

    # Create a temporal memory stream
    zip_buffer = io.BytesIO()

    # Create the output Zip File
    with ZipFile(zip_buffer, 'w') as merged_code:
        # Add merged files
        with ZipFile(submission.submission, 'r') as submission_code, \
             ZipFile(submission.activity.project.code_base_zip, 'r') as project_code:

            # Add files from merged structure
            for file in merge_structure:
                original_filename = merge_structure[file]['original_file']
                module = None
                if merge_structure[file]['module'] is not None:
                    module = models.ProjectModule.objects.get(project=submission.activity.project,
                                                              name=merge_structure[file]['module'])
                is_report = False
                if merge_structure[file]['source'] == 'project':
                    file_status = 1  # SKIPPED
                    content = project_code.read(original_filename)
                else:
                    file_status = 0  # ADDED
                    content = submission_code.read(original_filename)
                    if submission.activity.include_report:
                        if submission.activity.report_name is not None:
                            if original_filename == submission.activity.report_name:
                                is_report = True
                        else:
                            if original_filename.lower().endswith('.pdf'):
                                is_report = True

                # Create the file
                file_object = models.SubmissionFile.objects.create(
                    submission=submission,
                    module=module,
                    original_filename=original_filename,
                    filename=file,
                    status=file_status,
                    is_report=is_report
                )
                file_object.file.save(None, ContentFile(content))

                # Add file to merged ZIP
                merged_code.writestr(file, content)

            # Add Makefile
            file_object = models.SubmissionFile.objects.create(
                submission=submission,
                module=None,
                original_filename='Makefile',
                filename='Makefile',
                status=3
            )
            file_object.file.save(None, ContentFile(makefile.encode('UTF-8')))
            merged_code.writestr('Makefile', makefile)

    # Store the resulting ZIP file
    submission.merged_submission.save(None, ContentFile(zip_buffer.getbuffer()))

    return submission


def get_elapsed_time(start_time, units='s'):

    time_diff = timezone.now() - start_time

    if units == 's':
        return time_diff.seconds

    return time_diff


def smart_alignment(code_files, project):

    # Get modifiable files and main.c as reference files
    modifiable_files = project.projectfile_set.filter(locked=False).values_list('filename', flat=True)
    main_file = project.projectfile_set.filter(filename__endswith='main.c').values_list('filename', flat=True)
    reference_files = list(main_file) + list(modifiable_files)

    # Extract folders for reference files
    ref_file_paths = {}
    for ref_file in reference_files:
        filename = os.path.basename(ref_file)
        if filename not in ref_file_paths:
            ref_file_paths[filename] = {
                'ref_paths': [],
                'candidates': []
            }
        ref_file_paths[filename]['ref_paths'].append(os.path.dirname(ref_file))

    # Find reference files in submission files
    for file in code_files:
        # Skip folders
        if file.endswith('/') or file.endswith('\\'):
            continue
        filename = os.path.basename(file)
        if filename in ref_file_paths:
            ref_file_paths[filename]['candidates'].append(os.path.dirname(file))

    # Find a candidate that fits the maximum number of reference files. Start with main
    base = None
    if 'main.c' in ref_file_paths and len(ref_file_paths['main.c']['ref_paths']) == 1 and len(ref_file_paths['main.c']['candidates']) == 1:
        ref_path = ref_file_paths['main.c']['ref_paths'][0].replace('\\', '/')
        cand_path = ref_file_paths['main.c']['candidates'][0].replace('\\', '/')

        if cand_path.endswith(ref_path):
            base = cand_path[:-len(ref_path)]

    if base is None:
        # TODO: Find other candidates
        pass

    if base is not None and (base.endswith('/') or base.endswith('\\')):
        base = base[:-1]

    return base


def update_learner_result(learner, activity) -> None:
    # Check the list of submissions
    with transaction.atomic():
        # Set all submissions are not last
        learner.submission_set.filter(activity=activity).update(is_last=False)

        # Get the last submission
        last_submission = learner.submission_set.filter(activity=activity).order_by('-submitted_at', '-id').first()

        # Get the learner results
        try:
            results = models.LearnerResult.objects.get(activity=activity, learner=learner)
        except models.LearnerResult.DoesNotExist:
            results = None
        try:
            models.ActivityFeedback.objects.get(activity=activity, learner=learner)
        except models.ActivityFeedback.DoesNotExist:
            models.ActivityFeedback.objects.create(activity=activity, learner=learner)

        # Set the submission as last
        if last_submission is not None:
            last_submission.is_last = True
            last_submission.save()

            built = last_submission.built
            if last_submission.status < 8:
                status = 1
                test_passed = False
                test_score = 0.0
                num_tests = 0
                num_test_passed = 0
                num_test_failed = 0
                memory_leak = None
            else:
                status = last_submission.status - 6
                test_passed = last_submission.test_passed
                test_score = last_submission.test_score or 0.0
                num_test_passed = last_submission.num_test_passed or 0
                num_test_failed = last_submission.num_test_failed
                if num_test_failed is None:
                    num_test_failed = last_submission.activity.project.projecttest_set.filter(grouping_node=False).count()
                num_tests = last_submission.num_tests
                if num_tests is None:
                    num_tests = last_submission.activity.project.projecttest_set.filter(grouping_node=False).count()
                memory_leak = last_submission.leaked_bytes

            if results is None:
                results = models.LearnerResult.objects.create(
                    status=status,
                    learner=learner,
                    activity=activity,
                    last_submission=last_submission,
                    num_submissions=learner.submission_set.filter(activity=activity).count(),
                    test_passed=test_passed or False,
                    num_tests=num_tests,
                    num_test_passed=num_test_passed,
                    num_test_failed=num_test_failed,
                    error=last_submission.error,
                    submitted_at=last_submission.submitted_at,
                    elapsed_time=last_submission.elapsed_time,
                    built=built,
                    test_score=test_score,
                    memory_leak=memory_leak
                )
            else:
                results.status = status
                results.last_submission = last_submission
                results.num_submissions = learner.submission_set.filter(activity=activity).count()
                results.test_passed = test_passed or False
                results.num_tests = num_tests
                results.num_test_passed = num_test_passed
                results.num_test_failed = num_test_failed
                results.error = last_submission.error
                results.submitted_at = last_submission.submitted_at
                results.elapsed_time = last_submission.elapsed_time
                results.built = built
                results.test_score = test_score
                results.memory_leak = memory_leak
                results.save()

        if last_submission is None and results is not None:
            results.status = 0
            results.last_submission = None
            results.num_submissions = 0
            results.test_passed = False
            results.num_tests = 0
            results.num_test_passed = 0
            results.num_test_failed = 0
            results.error = None
            results.submitted_at = None
            results.elapsed_time = None
            results.built = False
            results.test_score = 0.0
            results.save()


def compute_diff(submission: models.Submission) -> None:
    """
        Compute the difference file for a submission
        :param submission:
        :return:
    """
    differences = {}

    for file in submission.submissionfile_set.filter(status=0).all().order_by('filename'):
        try:
            original_file_obj = submission.activity.project.projectfile_set.filter(filename=file.filename).get()
            original_file = original_file_obj.file.readlines()
            original_filename = original_file_obj.filename
        except models.ProjectFile.DoesNotExist:
            original_file = []
            original_filename = ''
        submission_file = file.file.readlines()

        try:
            original_file2 = [s.decode() for s in original_file]
            submission_file2 = [s.decode() for s in submission_file]

            htmldiff = difflib.HtmlDiff()
            differences[file.filename] = htmldiff.make_table(original_file2, submission_file2, original_filename, file.filename, context=True)
        except UnicodeDecodeError:
            pass

    submission.diff_report.save(None, ContentFile(json.dumps(differences).encode('utf-8')))
    # submission.save()


def get_recursive_test_structure(test: pelp.apps.web.models.ProjectTest,
                                 submission: Optional[pelp.apps.web.models.Submission]=None) -> dict:
    result = {
        'id': test.id,
        'count': 0,
        'passed': 0,
        'children': {},
        'children_count': 0,
        'children_codes': [],
        'children_ids': [],
        'code': test.code,
        'description': test.description
    }
    if test.children.count() == 0:
        result['count'] = 1
        if submission is not None:
            try:
                test_result = submission.submissiontestresult_set.get(test=test)
                if test_result.passed:
                    result['passed'] = 1
                else:
                    result['passed'] = 0
            except models.SubmissionTestResult.DoesNotExist:
                result['passed'] = 0
        return result

    for children in test.children.filter(parent=test).all().order_by('code'):
        child_structure = get_recursive_test_structure(children, submission)
        result['children'][children.code] = child_structure
        result['children_count'] += 1
        result['children_codes'].append(children.code)
        result['children_ids'].append(children.id)
        result['count'] += child_structure['count']
        result['passed'] += child_structure['passed']

    return result


def get_test_results_structure(submission: pelp.apps.web.models.Submission) -> dict:
    result = {
        'score': submission.test_score,
        'submission_id': submission.id,
        'count': 0,
        'tests': {},
        'tests_count': 0,
        'tests_codes': [],
        'tests_ids': [],
        'passed': 0
    }
    for top_result in submission.submissiontestresult_set.filter(
            test__parent__isnull=True
    ).all().order_by('test__code'):
        test_structure = get_recursive_test_structure(top_result.test, submission)
        result['tests'][top_result.test.code] = test_structure
        result['tests_count'] += 1
        result['count'] += test_structure['count']
        result['passed'] += test_structure['passed']
        result['tests_codes'].append(top_result.test.code)
        result['tests_ids'].append(top_result.test.id)

    return result

def _get_score_group_summary(activity: models.Activity,
                             qualification: str,
                             lower: Optional[int]=None,
                             upper: Optional[int]=None):
    if lower is not None and upper is not None:
        query = activity.learnerresult_set.filter(
            learner_id__gte=0,
            test_score__gte=lower,
            test_score__lt=upper,
            learner__groups__course = activity.course
        )
    elif lower is not None:
        query = activity.learnerresult_set.filter(
            learner_id__gte=0,
            test_score__gte=lower,
            learner__groups__course=activity.course
        )
    elif upper is not None:
        query = activity.learnerresult_set.filter(
            learner_id__gte=0,
            test_score__lt=upper,
            learner__groups__course=activity.course
        )
    else:
        query = activity.learnerresult_set.filter(
            learner_id__gte=0,
            learner__groups__course=activity.course
        )

    return query.values(
        'learner__groups',
        'learner__groups__code'
    ).annotate(
        group=F('learner__groups'),
        group__code=F('learner__groups__code'),
        qualification=Value(qualification),
        count=Count('pk')
    ).values('group', 'group__code', 'qualification', 'count')

def _get_score_summary(activity: models.Activity,
                       qualification: str,
                       lower: Optional[int]=None,
                       upper: Optional[int]=None):
    if lower is not None and upper is not None:
        query = activity.learnerresult_set.filter(
            learner_id__gte=0,
            test_score__gte=lower,
            test_score__lt=upper
        )
    elif lower is not None:
        query = activity.learnerresult_set.filter(
            learner_id__gte=0,
            test_score__gte=lower
        )
    elif upper is not None:
        query = activity.learnerresult_set.filter(
            learner_id__gte=0,
            test_score__lt=upper
        )
    else:
        query = activity.learnerresult_set.filter(
            learner_id__gte=0
        )

    return [
        {
            'qualification': qualification,
            'count': query.distinct().count()
        }
    ]

def _get_qualification_group_summary(activity: models.Activity,
                                     qualification: str,
                                     lower: Optional[int] = None,
                                     upper: Optional[int] = None):
    if lower is not None and upper is not None:
        query = activity.learnerresult_set.filter(
            Q(
                activity__activityfeedback__isnull=True
            ) | Q(
                activity__activityfeedback__activity=activity,
                activity__activityfeedback__is_np=False,
                activity__activityfeedback__score__gte=lower,
                activity__activityfeedback__score__lt=upper
            ),
            learner_id__gte = 0,
            learner__groups__course = activity.course)
    elif lower is not None:
        query = activity.learnerresult_set.filter(
            Q(
                activity__activityfeedback__isnull=True
            ) | Q(
                activity__activityfeedback__activity=activity,
                activity__activityfeedback__is_np=False,
                activity__activityfeedback__score__gte=lower
            ),
            learner_id__gte=0,
            learner__groups__course=activity.course)
    elif upper is not None:
        query = activity.learnerresult_set.filter(
            Q(
                activity__activityfeedback__isnull=True
            ) | Q(
                activity__activityfeedback__activity=activity,
                activity__activityfeedback__is_np=False,
                activity__activityfeedback__score__lt=upper
            ),
            learner_id__gte=0,
            learner__groups__course=activity.course)
    else:
        query = activity.learnerresult_set.filter(
            Q(
                activity__activityfeedback__isnull=True
            ) | Q(
                activity__activityfeedback__activity=activity,
                activity__activityfeedback__is_np=False
            ),
            learner_id__gte=0,
            learner__groups__course=activity.course)

    return query.values(
        'learner__groups',
        'learner__groups__code'
    ).annotate(
        group=F('learner__groups'),
        group__code=F('learner__groups__code'),
        qualification=Value(qualification),
        count=Count('pk')
    ).values('group', 'group__code', 'qualification', 'count')


def _get_qualification_summary(activity: models.Activity,
                               qualification: str,
                               lower: Optional[int] = None,
                               upper: Optional[int] = None):
    if lower is not None and upper is not None:
        query = activity.learnerresult_set.filter(
            Q(
                activity__activityfeedback__isnull=True
            ) | Q(
                activity__activityfeedback__activity=activity,
                activity__activityfeedback__is_np=False,
                activity__activityfeedback__score__gte=lower,
                activity__activityfeedback__score__lt=upper
            ),
            learner_id__gte = 0)
    elif lower is not None:
        query = activity.learnerresult_set.filter(
            Q(
                activity__activityfeedback__isnull=True
            ) | Q(
                activity__activityfeedback__activity=activity,
                activity__activityfeedback__is_np=False,
                activity__activityfeedback__score__gte=lower
            ),
            learner_id__gte=0)
    elif upper is not None:
        query = activity.learnerresult_set.filter(
            Q(
                activity__activityfeedback__isnull=True
            ) | Q(
                activity__activityfeedback__activity=activity,
                activity__activityfeedback__is_np=False,
                activity__activityfeedback__score__lt=upper
            ),
            learner_id__gte=0)
    else:
        query = activity.learnerresult_set.filter(
            Q(
                activity__activityfeedback__isnull=True
            ) | Q(
                activity__activityfeedback__activity=activity,
                activity__activityfeedback__is_np=False
            ),
            learner_id__gte=0)

    return query.annotate(
        qualification=Value(qualification),
        count=Count('pk')
    ).distinct().values('qualification', 'count')


def get_activity_score_group_summary(activity: models.Activity) -> List:
    qs_np = models.Learner.objects.filter(
        groups__course__activity=activity, learnerresult__isnull=True
    ).values('groups', 'groups__code').annotate(
        group=F('groups'),
        group__code=F('groups__code'),
        qualification=Value('NP'),
        count=Count('pk')
    ).values('group', 'group__code', 'qualification', 'count')

    qs_A = _get_score_group_summary(activity, 'A', lower=90)
    qs_B = _get_score_group_summary(activity, 'B', lower=70, upper=90)
    qs_Cp = _get_score_group_summary(activity, 'C+', lower=50, upper=70)
    qs_Cm = _get_score_group_summary(activity, 'C-', lower=30, upper=50)
    qs_D = _get_score_group_summary(activity, 'D', upper=30)

    return list(qs_np) + list(qs_A) + list(qs_B) + list(qs_Cp) + list(qs_Cm) + list(qs_D)


def get_activity_score_summary(activity: models.Activity) -> List:
    qs_np = [{
        'qualification': 'NP',
        'count': models.Learner.objects.filter(
            groups__course__activity=activity, learnerresult__isnull=True
        ).distinct().count()
    }]

    qs_A = _get_score_summary(activity, 'A', lower=90)
    qs_B = _get_score_summary(activity, 'B', lower=70, upper=90)
    qs_Cp = _get_score_summary(activity, 'C+', lower=50, upper=70)
    qs_Cm = _get_score_summary(activity, 'C-', lower=30, upper=50)
    qs_D = _get_score_summary(activity, 'D', upper=30)

    return list(qs_np) + list(qs_A) + list(qs_B) + list(qs_Cp) + list(qs_Cm) + list(qs_D)

def get_activity_qualification_group_summary(activity: models.Activity) -> List:
    qs_np = models.Learner.objects.filter(
        Q(
            learnerresult__isnull=True
        ) | Q(
            activityfeedback__activity=activity,
            activityfeedback__is_np=True
        ),
        groups__course__activity=activity
    ).values('groups', 'groups__code').annotate(
        group=F('groups'),
        group__code=F('groups__code'),
        qualification=Value('NP'),
        count=Count('pk')
    ).values('group', 'group__code', 'qualification', 'count')

    qs_Pending = activity.learnerresult_set.filter(
        Q(
            activity__activityfeedback__isnull=True
        ) | Q(
            activity__activityfeedback__activity=activity,
            activity__activityfeedback__score__isnull=True,
            activity__activityfeedback__is_np=False
        ),
        learner_id__gte=0,
        learner__groups__course=activity.course
    ).values(
        'learner__groups',
        'learner__groups__code'
    ).annotate(
        group=F('learner__groups'),
        group__code=F('learner__groups__code'),
        qualification=Value('Pending'),
        count=Count('pk')
    ).values('group', 'group__code', 'qualification', 'count')

    qs_A = _get_qualification_group_summary(activity, 'A', lower=90)
    qs_B = _get_qualification_group_summary(activity, 'B', lower=70, upper=90)
    qs_Cp = _get_qualification_group_summary(activity, 'C+', lower=50, upper=70)
    qs_Cm = _get_qualification_group_summary(activity, 'C-', lower=30, upper=50)
    qs_D = _get_qualification_group_summary(activity, 'D', upper=30)

    return list(qs_np) + list(qs_A) + list(qs_B) + list(qs_Cp) + list(qs_Cm) + list(qs_D) + list(qs_Pending)

def get_activity_qualification_summary(activity: models.Activity) -> List:
    qs_np = [{
        'qualification': 'NP',
        'count': models.Learner.objects.filter(
            Q(
                learnerresult__isnull=True
            ) | Q(
                activityfeedback__activity=activity,
                activityfeedback__is_np=True
            ),
            groups__course__activity=activity
        ).distinct().count()
    }]

    qs_Pending = [{
        'qualification': 'Pending',
        'count': activity.learnerresult_set.filter(
            Q(
                activity__activityfeedback__isnull=True
            ) | Q(
                activity__activityfeedback__activity=activity,
                activity__activityfeedback__score__isnull=True,
                activity__activityfeedback__is_np=False
            ),
            learner_id__gte=0,
            learner__groups__course=activity.course
        ).distinct().count()
    }]

    qs_A = _get_qualification_summary(activity, 'A', lower=90)
    qs_B = _get_qualification_summary(activity, 'B', lower=70, upper=90)
    qs_Cp = _get_qualification_summary(activity, 'C+', lower=50, upper=70)
    qs_Cm = _get_qualification_summary(activity, 'C-', lower=30, upper=50)
    qs_D = _get_qualification_summary(activity, 'D', upper=30)

    return list(qs_np) + list(qs_A) + list(qs_B) + list(qs_Cp) + list(qs_Cm) + list(qs_D) + list(qs_Pending)


def get_activity_statistics(activity: models.Activity) -> dict:

    stats = {
        'global': {
            'score': {'NP': 0, 'A': 0, 'B': 0, 'C+': 0, 'C-': 0, 'D': 0},
            'qualification': {'Pending': 0, 'NP': 0, 'A': 0, 'B': 0, 'C+': 0, 'C-': 0, 'D': 0}
        },
        'groups': {}
    }

    for score in get_activity_score_summary(activity):
        stats['global']['score'][score['qualification']] = score['count']

    for qualification in get_activity_qualification_summary(activity):
        stats['global']['qualification'][qualification['qualification']] = qualification['count']

    for group in get_activity_score_group_summary(activity):
        if group['group'] not in stats['groups']:
            stats['groups'][group['group']] = {
                'id': group['group'],
                'code': group['group__code'],
                'score': {'NP': 0, 'A': 0, 'B': 0, 'C+': 0, 'C-': 0, 'D': 0},
                'qualification': {'Pending': 0, 'NP': 0, 'A': 0, 'B': 0, 'C+': 0, 'C-': 0, 'D': 0}
            }
        stats['groups'][group['group']]['score'][group['qualification']] = group['count']

    for group in get_activity_qualification_group_summary(activity):
        if group['group'] not in stats['groups']:
            stats['groups'][group['group']] = {
                'id': group['group'],
                'code': group['group__code'],
                'score': {'NP': 0, 'A': 0, 'B': 0, 'C+': 0, 'C-': 0, 'D': 0},
                'qualification': {'Pending': 0, 'NP': 0, 'A': 0, 'B': 0, 'C+': 0, 'C-': 0, 'D': 0}
            }
        stats['groups'][group['group']]['qualification'][group['qualification']] = group['count']

    return stats

