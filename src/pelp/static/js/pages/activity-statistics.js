const course_id = parseInt(document.querySelector('[name=activity_results_course_id]').value);
const activity_id = parseInt(document.querySelector('[name=activity_results_activity_id]').value);

$(document).ready(function() {
    get_activity_data(course_id, activity_id, function(data) {
        plot_submission(data, "submissions_canvas");
        plot_submission_final_status(data, "final_result_canvas");
        plot_results(data, "results_canvas");
        plot_scores(data, "scores_canvas");
        plot_submissions_per_day(data, "submission_day_canvas");
        plot_submissions_per_hour(data, "submission_time_canvas");
        plot_qualifications(data, "qualification_canvas");
        plot_qualifications(data, "score_summary_canvas", false);

        $("#spinner").remove();
        $("#plots").css('visibility', 'visible');
    });
});
