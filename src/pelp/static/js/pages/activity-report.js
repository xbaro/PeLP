/**
 * Format bytes as human-readable text.
 *
 * @param bytes Number of bytes.
 * @param si True to use metric (SI) units, aka powers of 1000. False to use
 *           binary (IEC), aka powers of 1024.
 * @param dp Number of decimal places to display.
 *
 * @return Formatted string.
 */
function humanFileSize(bytes, si=false, dp=1) {
  const thresh = si ? 1000 : 1024;

  if (Math.abs(bytes) < thresh) {
    return bytes + ' B';
  }

  const units = si
    ? ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    : ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'];
  let u = -1;
  const r = 10**dp;

  do {
    bytes /= thresh;
    ++u;
  } while (Math.round(Math.abs(bytes) * r) / r >= thresh && u < units.length - 1);


  return bytes.toFixed(dp) + ' ' + units[u];
}

function submission_table_header() {
    let text = [];
    text.push('<div class="table-responsive">');
    text.push('<table class="table mb-0 table-striped table-sm">');
    text.push('<thead>');
    text.push('<tr>');
    text.push('<th>#</th>');
    text.push('<th></th>');
    text.push('<th>' + gettext("Status") + '</th>');
    text.push('<th>' + gettext("Compile") + '</th>');
    text.push('<th>' + gettext("Submitted") + '</th>');
    text.push('<th>' + gettext("Executed") + '</th>');
    text.push('<th>' + gettext("Elapsed Time") + ' (ms)</th>');
    text.push('<th>' + gettext("Passed") + '</th>');
    text.push('<th>' + gettext("Failed") + '</th>');
    text.push('<th>' + gettext("Score") + '</th>');
    text.push('<th>' + gettext("Leaked Mem") + '</th>');
    text.push('<th>' + gettext("Error") + '</th>');
    text.push('</tr>');
    text.push('</thead>');
    text.push('<tbody>');
    return text.join('\n');
}

function submission_table_footer() {
    let text = [];
    text.push('</tbody>');
    text.push('</table>');
    text.push('</div>');
    return text.join('\n');
}

let _submission_url = null;
function get_submission_link(submission_id) {
    if (_submission_url == null) {
        const base_url = $("#download-excel")[0].href.split('?')[0].split('/download/')[0].replace('/api', '');
        _submission_url = base_url + '/';
    }
    return _submission_url + submission_id + '/';
}

function submission_table_row(row) {
    const status = [
        gettext('CREATING'), gettext('CREATED'), gettext('CLONING'), gettext('CLONED'),
        gettext('MERGING'), gettext('MERGED'), gettext('WAITING'), gettext('TESTING'),
        gettext('PROCESSED'), gettext('INVALID'), gettext('ERROR'), gettext('TIMEOUT')
    ];
    let icons = [];
    if (row['is_instructor_submission']) {
        icons.push('<span className="summary-icon">');
        icons.push('<svg className="svg-icon svg-icon-lg svg-icon-heavy me-xl-2" class="small-icon">');
        icons.push('<use xlink:href="#student-3070"><title>' + gettext('Instructor Submission') + '</title></use>');
        icons.push('</svg>');
        icons.push('</span>');
    }
    if (row['is_mail_submission']) {
        icons.push('<span className="summary-icon">');
        icons.push('<svg className="svg-icon svg-icon-lg svg-icon-heavy me-xl-2" class="small-icon">');
        icons.push('<use xlink:href="#mail-4938"><title>' + gettext('Mail Submission') + '</title></use>');
        icons.push('</svg>');
        icons.push('</span>');
    }
    if (row['is_official']) {
        icons.push('<span className="summary-icon">');
        icons.push('<svg className="svg-icon svg-icon-lg svg-icon-heavy me-xl-2" class="small-icon">');
        icons.push('<use xlink:href="#diploma-3140"><title>' + gettext('Official Submission') + '</title></use>');
        icons.push('</svg>');
        icons.push('</span>');
    }

    let text = [];
    text.push('<tr>');
    text.push('<th scope="row"><a href="' + get_submission_link(row['id']) + '">' + row['id'] + '</a></th>');
    text.push('<td>' + icons.join('\n') + '</td>');
    text.push('<td>' + status[row['status']] + '</td>');
    text.push('<td>' + row['built'] + '</td>');
    text.push('<td>' + row['submitted_at'] + '</td>');
    text.push('<td>' + row['executed_at'] + '</td>');
    text.push('<td>' + row['elapsed_time'] + '</td>');
    text.push('<td>' + row['num_test_passed'] + '</td>');
    text.push('<td>' + row['num_test_failed'] + '</td>');
    text.push('<td>' + row['test_score'] + '</td>');
    if (row['leaked_bytes']) {
        text.push('<td>' + humanFileSize(row['leaked_bytes']) + '</td>');
    } else {
        text.push('<td></td>');
    }
    if (row['error']) {
        text.push('<td>' + row['error'] + '</td>');
    } else {
        text.push('<td></td>');
    }
    text.push('</tr>');

    return text.join('\n');
}

function format ( d ) {
    let table = submission_table_header();
    for(let submission of d['submissions']) {
        table += submission_table_row(submission);
    }
    return table + submission_table_footer();
}

$(document).ready(function() {
    const table = $('#learners').DataTable({
        language: {
            'url': $('#learners').data('language-url')
        },
        responsive: {
            details: false
        },
        columns: [
            {
                className: 'details-control all',
                orderable: false,
                searchable: false,
                data: null,
                defaultContent: ''
            },
            {   data: "status",
                render: function(data, type, row) {
                    return gettext(row['status_desc']);
                }
            },
            {
                data: "built",
                render: function(data, type, row) {
                    let icon = '<svg class="svg-icon svg-icon-sm svg-icon-heavy me-xl-2">';
                    if (data) {
                        icon += '<use xlink:href="#checkbox-square-411"></use>'
                    } else {
                        icon += '<use xlink:href="#dismiss-467"></use>'
                    }
                    icon += '</svg>';
                    return icon;
                }
            },
            {
                data: "test_passed",
                className: 'min-tablet-l',
                render: function(data, type, row) {
                    let icon = '<svg class="svg-icon svg-icon-sm svg-icon-heavy me-xl-2">';
                    if (data) {
                        icon += '<use xlink:href="#checkbox-square-411"></use>'
                    } else {
                        if (row['status_desc'] === "VALID" ) {
                            icon += '<use xlink:href="#dismiss-467"></use>'
                        } else if(row['status_desc'] === "TIMEOUT") {
                            icon += '<use xlink:href="#clock-5915"></use>'
                        } else {
                            icon += '<use xlink:href="#unavailable-466"></use>'
                        }
                    }
                    icon += '</svg>';
                    return icon;
                }
            },
            { data: "learner.first_name", className: 'all' },
            { data: "learner.last_name", className: 'all'},
            { data: "learner.email", visible: false},
            { data: "num_test_passed", className: 'desktop' },
            { data: "num_test_failed", className: 'desktop' },
            { data: "elapsed_time", className: 'desktop' },
            { data: "num_submissions", className: 'min-desktop' },
            { data: "test_score", className: 'all'},
            {
                data: "memory_leak",
                className: 'min-tablet-l',
                render: function(data, type, row) {
                    if (data) {
                        return  humanFileSize(data);
                    }
                    return '';
                }
            },
            { data: "id", visible: false, name: 'learner.groups__id'},
            { data: "learner.username", visible: false},
            {
                data: 'last_submission',
                className: 'all',
                visible: true,
                orderable: false,
                searchable: false,
                render: function(data, type, row) {
                    if (row.last_submission) {
                        let icon = [];
                        const base_url = $("#download-excel")[0].href.split('?')[0].split('/download/')[0].replace('/api', '');
                        const url = base_url + '/' + row.last_submission.id + '/';
                        icon.push('<div class="activity-actions"><a className="btn-outline-primary" id="download-excel" href="' + url + '">');
                        icon.push('<svg className="svg-icon svg-icon-lg svg-icon-heavy me-xl-2" style="width: 25px;height: 25px;">');
                        icon.push('<use xlink:href="#find-7048"></use>');
                        icon.push('</svg></a></div>');
                        return icon.join('\n');
                    } else {
                        return '';
                    }
                }
            },
            { data: "submissions", visible: false, searchable: false, orderable: false},
            { data: "status_desc", visible: false, searchable: false, orderable: false},
        ],
        "order": [[5, 'asc']]
    });
    // Add event listener for opening and closing details
    $('#learners tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );

        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child( format(row.data()) ).show();
            tr.addClass('shown');
        }
    } );
    $("#course_group_select").on('change', function () {
        var val = $(this).val();
        var base_url = $('#learners').data('ajax').split('?')[0];
        var download_url = $("#download-excel")[0].href.split('?')[0];
        if (val >= 0) {
            base_url = base_url + '?group=' + val + '&format=datatables';
            table.ajax.url(base_url);
            table.ajax.reload();
            $("#download-excel")[0].href = download_url + '?group=' + val;
        } else {
            base_url = base_url + '?format=datatables';
            $("#download-excel")[0].href = download_url;
            table.ajax.url(base_url);
            table.ajax.reload();
        }
    });
});
