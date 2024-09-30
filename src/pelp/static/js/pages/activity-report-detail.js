const course_id = parseInt(document.querySelector('[name=activity_report_detail_course_id]').value);
const activity_id = parseInt(document.querySelector('[name=activity_report_detail_activity_id]').value);
const submission_id = parseInt(document.querySelector('[name=activity_report_detail_submission_id]').value);
$(document).ready(function() {
	const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
	const table = $('#errors-table').DataTable({
		language: {
            'url': $('#errors-table').data('language-url')
        },
		columnDefs: [
			{
				targets: [3],
				render: function(data, type, row) {
					if (data) {
						return data.filename;
					}
					return '';
                }
			},
			{
				targets: [5],
				render: function(data, type, row) {
					let text = [];
					if (data) {
						try {
							text.push('<ul>');
							data = JSON.parse(data);
							for (let frame of data.stack) {
								text.push('<li>');
								text.push('<strong>' + frame['fn'] + '</strong>');
								if (frame.file) {
									text.push(' ' + frame['file']);
								}
								if (frame.line) {
									text.push(':' + frame['line']);
								}
								text.push('</li>');
							}
							text.push('</ul>');
						} catch {

						}
					}
					return text.join('');
                }
			},
		]
	});
	$("#errors-table_filter.dataTables_filter").append($("#errorFilter"));
	$("#errorFilter").on('change', function () {
        var val = $(this).val();
        var base_url = $('#errors-table').data('ajax').split('?')[0];
        if (val >= 0) {
            base_url = base_url + '?type=' + val + '&format=datatables';
            table.ajax.url(base_url);
            table.ajax.reload();
        } else {
            base_url = base_url + '?format=datatables';
            table.ajax.url(base_url);
            table.ajax.reload();
        }
    });

	if (course_id && activity_id && submission_id) {
		$("#fileexplorer1").jQueryFileExplorer({
			root: "/",
			headers: {
				'X-CSRFToken': csrftoken
			},
			rootLabel: "/",
			script: '/api/course/' + course_id + '/activity/' + activity_id + '/submission/' + submission_id + '/file/getPath/',
			fileScript: '/api/course/' + course_id + '/activity/' + activity_id + '/submission/' + submission_id + '/file/getPath/',
			fileOpenCallback: function (data) {
				$("#code_viewer").text(data);
				hljs.highlightAll();
				$('code#code_viewer.hljs').each(function (i, block) {
					hljs.lineNumbersBlock(block);
				});
			}
		});
	}
	const log_url = $("#log_viewer").data('url');
	if (log_url) {
		$.get(log_url, function (data) {
			$("#log_viewer").text(data);
			hljs.highlightAll();
		});
	} else {
		$("#log_viewer").text("No logs available");
		hljs.highlightAll();
	}
	const file_diff_url = $("#files-diff").data('url');
	if (file_diff_url) {
		$.get(file_diff_url, function (data) {

			let content = [];
			for (const file in data) {
				content.push('<div class="table-responsive m-3">' + data[file] + '</div>')
			}
			$("#files-diff").html(content.join('\n'));
		});
	} else {
		$("#files-diff").text(gettext("No data available"));
	}
	if (course_id && activity_id && submission_id) {
		plot_results('tests_chart', null, null, null, false);
	}

	// Set the PDF viewer height
	let viewer_h = Math.max(500, 1.5 * $("#pdf_viewer").width());
	$("#pdf_viewer").height(viewer_h);
	$("#pdf_viewer").on('load', function() {
		viewer_h = Math.max(500, 1.5 * $("#pdf_viewer").width());
        $("#pdf_viewer").height(viewer_h);
	});
    $(window).resize(function() {
		viewer_h = Math.max(500, 1.5 * $("#pdf_viewer").width());
        $("#pdf_viewer").height(viewer_h);
    });
});
