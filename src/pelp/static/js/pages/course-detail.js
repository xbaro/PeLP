const course_id = parseInt(document.querySelector('[name=course_detail_course_id]').value);

$(document).ready(function() {
    $("#btn_save_activity").removeClass('disabled');
    $("#btn_save_activity").on('click', function() {
        $('#form_activity').submit();
    });
    get_course_data(course_id, function(data) {
        const chart = plot_qualifications(data, "course_plot", true, true);

        $("#spinner").remove();
        $("#plots").css('visibility', 'visible');
    });
});
