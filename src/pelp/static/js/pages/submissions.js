const show_learner_info = parseInt(document.querySelector('[name=show_learner_info]').value);
const submission_prefix = document.querySelector('[name=submission_prefix]').value;
let submission_table = null;
$(document).ready(function() {
    submission_table = $('#submissions').DataTable({
        language: {
            'url': $('#submissions').data('language-url')
        },
        iDisplayLength: 5,
        lengthMenu: [ 5, 10, 25, 50, 100 ],
        columns: [
            {   data: "id" },
            {
                data: "status_desc",
                orderable: false,
                render: function(data, type, row) {
                    return gettext(data);
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
            { data: "num_test_passed" },
            { data: "num_test_failed" },
            { data: "elapsed_time" },
            {
                data: "submitted_at",
                render: $.fn.dataTable.render.moment( null, 'DD/MM/YYYY HH:mm:ss')
            },
            {
                data: "learner",
                visible: show_learner_info === 1,
                render: function(data, type, row) {
                    let icon = [];
                    const url = '#';
                    icon.push('<div class="activity-actions"><a className="btn-outline-primary" id="download-excel" href="' + url + '">');
                    icon.push('<svg className="svg-icon svg-icon-lg svg-icon-heavy me-xl-2" style="width: 25px;height: 25px;">');
                    if (data > 0) {
                        icon.push('<use xlink:href="#read-3126"><title>Learner</title></use>');
                    } else {
                        icon.push('<use xlink:href="#student-3070"><title>Instructor</title></use>');
                    }
                    icon.push('</svg></a></div>');
                    return icon.join('\n');
                }
            },
            {
                data: "submission",
                visible: true,
                orderable: false,
                searchable: false,
                render: function(data, type, row) {
                    if (row.submission) {
                        let icon = [];
                        const url = submission_prefix + row.id + '/';
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
        ],
        "order": [[0, 'desc']]
    });
    plot_results('tests_chart');
    Dropzone.instances[0].on("addedfile", file => {
        submission_table.ajax.reload(null, true);
    });
    const max_submissions = $('#max_total_submissions').text();
    const max_day_submissions = $('#max_day_submissions').text();
    let total_submissions = $('#num_total_submissions').text();
    let day_submissions = $('#num_day_submissions').text();

    if (max_submissions && total_submissions) {
        $('#num_total_submissions').text(total_submissions);
        if (total_submissions >= Number.parseInt(max_submissions)) {
            $('#submission_upload').hide();
        }
    }
    if (max_day_submissions && day_submissions) {
        $('#num_day_submissions').text(day_submissions);
        if (day_submissions >= Number.parseInt(max_day_submissions)) {
            $('#submission_upload').hide();
        }
    }
});
