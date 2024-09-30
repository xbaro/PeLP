const qual_scale = {
    NP: {
        text: 'NP',
        backgroundColor: 'rgba(204,204,204,0.39)'
    },
    PENDING: {
        text: '-',
        backgroundColor: 'rgba(204,204,204,0.39)'
    },
    A: {
        text: 'A',
        backgroundColor: '#1cf317'
    },
    B: {
        text: 'B',
        backgroundColor: '#2ba816'
    },
    Cp: {
        text: 'C+',
        backgroundColor: '#c7ae19'
    },
    Cm: {
        text: 'C-',
        backgroundColor: '#ff0600'
    },
    D: {
        text: 'D',
        backgroundColor: '#a90809'
    }
};

function update_computed_score() {
    const test_score = Number.parseFloat($("input[name=activity_report_test_score]").val());
    let rubric_score = 0;
    $('select.rubric_option').each(function(index, value) {
        if (Number.parseInt(value.selectedOptions[0].value) >=0) {
            const parsed_val = Array.from(value.selectedOptions[0].label.matchAll(/^\[(?<value>[+|-][0-9|\.]+)\]/g));
            if (parsed_val != null && parsed_val.length == 1) {
                rubric_score += Number.parseFloat(parsed_val[0].groups.value);
            }
        }
    });
    let final_score = test_score + rubric_score;
    final_score = Math.max(0, Math.min(100, final_score));

    $("#computed_score").text(final_score);
}
function get_qualitative(value) {
    if (value.replace(/ /g, "").length == 0) {
        if ($("#id_is_np").prop('checked')) {
            return 'NP';
        } else {
            return 'PENDING';
        }
    }
    if(isNaN(value)) {
        if ($("#id_is_np").prop('checked')) {
            return 'NP';
        } else {
            return 'PENDING';
        }
    }
    value = Number.parseFloat(value);
    if (value >= 90) {
        return 'A';
    }
    if (value >= 70) {
        return 'B';
    }
    if (value >= 50) {
        return 'Cp';
    }
    if (value >= 30) {
        return 'Cm';
    }
    return 'D';
}
function update_qualitative_value() {
    const is_np = $("#id_is_np").prop('checked');
    if (is_np) {
        $("#final-score > input").val('');
        $("#final-score > input").prop('disabled', true);
    } else {
        $("#final-score > input").prop('disabled', false);
    }
    const numeric_value = $("#final-score > input").val();
    const qual_value = get_qualitative(numeric_value);
    const qual_value_data = qual_scale[qual_value];
    $("#qualitative-score").text(qual_value_data.text);
    $("#qualitative-score").css('backgroundColor', qual_value_data.backgroundColor);
    if (qual_value[0] == 'C') {
        $('#feedback-alert').show();
    } else {
        $('#feedback-alert').hide();
    }
}
$(document).ready(function() {
    if (course_id && activity_id && submission_id) {
        update_qualitative_value();
        plot_results('tests_chart');
        update_computed_score();
        let _modified = false;

        function modified() {
            if (!_modified) {
                _modified = true;
                $('.register-button').hide();
                $('.persistence-button').show();
            }
        }

        CKEDITOR.instances.id_general.on('change', modified);
        $('input').on('change', modified);
        $('.rubric_option').on('change', function () {
            modified();
            update_computed_score();
        });
        $('.discard-changes').on('click', function () {
            window.location.reload();
        });
        $('.save-changes').on('click', function () {
            $('form').submit();
        });
        $('#btn_set_computed_score').on('click', function (event) {
            event.preventDefault();
            $("#id_is_np").prop('checked', false);
            $("#id_score").val($("#computed_score").text());
            update_qualitative_value();
            modified();
        })

        $("#final-score > input").on('change', function () {
            update_qualitative_value();
        });

        $("#id_is_np").on('change', function () {
            update_qualitative_value();
        });
    }
    $("#filter_evaluations_select").on('change', function () {
        let url = new URL(window.location.href);
        url.searchParams.set('filter', $("#filter_evaluations_select").val());
        window.location.href = url.href;
    });

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
