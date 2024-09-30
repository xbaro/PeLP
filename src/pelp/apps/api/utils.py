import os
import io
import pandas as pd
import tempfile


def _extract_test(x, test_code, field_name):
    if x is None:
        return None
    for test in x:
        if test['test']['code'] == test_code:
            return test[field_name]
    return None


def _add_test_results(df, report, section):

    report[section['code'] + '_passed'] = df['results_detail'].apply(
        lambda x: _extract_test(x, section['code'], 'passed'))

    if section['grouping_node']:
        report[section['code'] + '_num_tests'] = df['results_detail'].apply(
            lambda x: _extract_test(x, section['code'], 'num_tests'))
        report[section['code'] + '_num_passed'] = df['results_detail'].apply(
            lambda x: _extract_test(x, section['code'], 'num_passed'))
        report[section['code'] + '_num_failed'] = df['results_detail'].apply(
            lambda x: _extract_test(x, section['code'], 'num_failed'))

        for sub_section in section['children']:
            _add_test_results(df, report, sub_section)


def export_to_xlsx(queryset, serializer=None, context=None, results_structure=None):

    df = pd.DataFrame.from_records(serializer(queryset, context=context, many=True).data)

    report = df[['username', 'first_name', 'last_name', 'email', 'num_submissions']]
    report['score'] = df['result_summary'].apply(lambda x: x['test_score'] if x is not None else None)
    report['compiled'] = df['result_summary'].apply(lambda x: x['built'] if x is not None else False)
    report['test_passed'] = df['result_summary'].apply(lambda x: x['test_passed'] if x is not None else False)
    report['num_tests'] = df['result_summary'].apply(lambda x: x['num_tests'] if x is not None else 0)
    report['num_passed'] = df['result_summary'].apply(lambda x: x['num_test_passed'] if x is not None else 0)
    report['num_failed'] = df['result_summary'].apply(lambda x: x['num_test_failed'] if x is not None else 0)

    if results_structure is not None:
        for section in results_structure:
            _add_test_results(df, report, section)

    buffer = io.BytesIO()
    report.to_excel(buffer)

    return buffer.getvalue()

def export_feedback_to_xlsx(queryset, serializer=None, context=None):

    df = pd.DataFrame.from_records(serializer(queryset, context=context, many=True).data)

    report = df[['username', 'first_name', 'last_name', 'email']]

    report['score'] = df['feedback'].apply(lambda x: x['score'] if x is not None else None)
    report['summary'] = df['feedback'].apply(lambda x: x['txt_summary'] if x is not None else None)

    # buffer = io.BytesIO()
    # report.to_excel(buffer)

    buffer = io.BytesIO()
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    report.to_excel(writer, sheet_name='Feedback')

    workbook = writer.book
    worksheet = writer.sheets['Feedback']

    id_format = workbook.add_format()
    id_format.set_align('vcenter')

    text_format = workbook.add_format()
    text_format.set_align('vcenter')
    text_format.set_align('left')

    score_format = workbook.add_format({'num_format': '##0.00'})
    score_format.set_align('center')
    score_format.set_align('vcenter')

    feedback_format = workbook.add_format()
    feedback_format.set_text_wrap()
    feedback_format.set_align('justify')
    feedback_format.set_align('top')

    worksheet.set_column('A:A', 6, id_format)
    worksheet.set_column('B:D', 20, text_format)
    worksheet.set_column('E:E', 30, text_format)
    worksheet.set_column('F:F', 10, score_format)
    worksheet.set_column('G:G', 60, feedback_format)

    writer.save()
    return buffer.getvalue()


def get_file_status(status):
    valid_status = [
        'ADDED',
        'SKIPPED',
        'FILTERED',
        'GENERATED',
    ]

    return valid_status[status]


def getPath(path, files_data):
    files = []
    dirs = []

    if not path.endswith('/'):
        path = path + '/'

    for file in files_data:
        filename = file['filename'][len(path)-1:]
        if filename.startswith('/'):
            filename = filename[1:]
        folder = os.path.dirname(filename)
        if len(folder) == 0:
            _, file_extension = os.path.splitext(filename)
            # File
            files.append({
                'label': filename,
                'path': path + filename,
                'ext': file_extension,
                'isDrive': False,
                'isFolder': False,
                'hasSubfolder': False,
                'subitems': [get_file_status(file['status'])]
            })
        else:
            first_level = filename.split('/')[0]
            if first_level not in dirs:
                dirs.append(first_level)
    for item in dirs:
        files.append({
            'label': item,
            'path': path + item,
            'isDrive': False,
            'isFolder': True
        })

    return files
