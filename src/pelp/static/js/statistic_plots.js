function plot_submission(data, elementId) {
    const canvas = document.getElementById(elementId);
    return new Chart(canvas, {
        options: {
            responsive: true,
            maintainAspectRatio: false,
        },
        type: "pie",
        data: {
            labels: ["Waiting", "Running", "Processed", "Error", "Invalid", "Timeout"],
            datasets: [
                {
                    data: [
                        data['submissions_waiting'][Object.keys(data['submissions_waiting'])[0]],
                        data['submissions_running'][Object.keys(data['submissions_running'])[0]],
                        data['submissions_processed'][Object.keys(data['submissions_processed'])[0]],
                        data['submissions_error'][Object.keys(data['submissions_error'])[0]],
                        data['submissions_invalid'][Object.keys(data['submissions_invalid'])[0]],
                        data['submissions_timeout'][Object.keys(data['submissions_timeout'])[0]],
                    ],
                    borderWidth: 0,
                    backgroundColor: ["#e3c715", "#c5c4c4", "#3ce122", "#ee0c10", "#96e5ff", "#af1356"],
                    hoverBackgroundColor: ["#9d880c", "#9b9b9b", "#2ba816", "#a90809", "#6ea5b9", "#651433ff"],
                },
            ],
        },
        plugins: [{
            id: 'customPlugin',
            beforeDraw: (chart, args, options) => {
                let height = $("#submission_time_canvas_container").height();
                $("#submission_canvas_container").css('height', height);
            }
        }]
    });
}

function plot_submission_final_status(data, elementId) {
    const canvas = document.getElementById(elementId);
    const plot_data = data['final_status'][Object.keys(data['final_status'])[0]];
    return new Chart(canvas, {
        options: {
            responsive: true,
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    beginAtZero: true,
                }
            }
        },
        type: "bar",
        data: {
            labels: ['Compiled', 'Correct Execution', 'Tests Passed'],
            datasets: [
                {
                    label: 'Last submission execution result',
                    data: [
                        plot_data['built'] * 100.0,
                        plot_data['correct_execution'] * 100.0,
                        plot_data['tests_passed'] * 100.0,
                    ],
                    backgroundColor: "#a47cf3"
                }
            ]
        }
    });
}

function plot_results(data, elementId) {
    const canvas = document.getElementById(elementId);
    const plot_data = data['results'][Object.keys(data['results'])[0]];
    return new Chart(canvas, {
        options: {
            responsive: true,
            scales: {
                y: {
                    title: 'Percentage',
                    min: 0,
                    max: 100,
                    beginAtZero: true

                }
            }
        },
        type: "bar",
        data: {
            labels: plot_data.map(test => test['code']),
            datasets: [
                {
                    label: 'Last submission',
                    data: plot_data.map(test => test['passed'] * 100.0),
                    backgroundColor: "#a47cf3",
                }
            ]
        }
    });
}

function plot_scores(data, elementId) {
    const canvas = document.getElementById(elementId);
    const plot_data = data['scores'][Object.keys(data['scores'])[0]];
    return new Chart(canvas, {
        options: {
            responsive: true,
            scales: {
                y: {
                    title: 'Percentage',
                    min: 0,
                    max: 100,
                    beginAtZero: true
                }
            }
        },
        type: "bar",
        data: {
            labels: plot_data.map(score => score['score']),
            datasets: [
                {
                    label: 'Last score',
                    data: plot_data.map(score => {
                        return {x: score['score'], y: score['count']};
                    }),
                    backgroundColor: "#a47cf3",
                }
            ]
        }
    });
}

function plot_submissions_per_day(data, elementId) {
    const canvas = document.getElementById(elementId);
    const plot_data = data['submissions_date'][Object.keys(data['submissions_date'])[0]];
    return new Chart(canvas, {
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        },
        type: "line",
        data: {
            labels: plot_data.map(score => score['day']),
            datasets: [
                {
                    label: 'Submissions per day',
                    data: plot_data.map(hist => {
                        return {x: new Date(hist['day']), y: hist['count']};
                    }),
                    backgroundColor: "#a47cf3",
                    fill: true,
                    tension: 0.3
                }
            ]
        }
    });
}

function plot_submissions_per_hour(data, elementId) {
    const canvas = document.getElementById(elementId);
    const plot_data = data['submissions_time'][Object.keys(data['submissions_time'])[0]];
    return new Chart(canvas, {
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        },
        type: "line",
        data: {
            labels: plot_data.map(score => score['time']),
            datasets: [
                {
                    label: 'Submissions time',
                    data: plot_data.map(hist => {
                        return {x: hist['time'], y: hist['count']};
                    }),
                    backgroundColor: "#a47cf3",
                    fill: true,
                    tension: 0.3
                }
            ]
        }
    });
}

function plot_qualifications(data, elementId, show_qualification=true, show_legend=true) {

    const canvas = document.getElementById(elementId);
    const src_data_all = data['qualification_summary'];

    let obj_data_all = {};
    let datasets = [];
    let update_labels = true;
    let labels = ['All'];
    for (const activity in src_data_all) {
        let src_data = null;
        if (!show_qualification || (data['score_summary'][activity]['active'] || data['score_summary'][activity]['self_evaluation'])) {
            src_data = data['score_summary'][activity]['data'];
        } else {
            src_data = data['qualification_summary'][activity]['data'];
        }

        let obj_data = {};
        let total_data = {
            'Pending': 0,
            'NP': 0,
            'A': 0,
            'B': 0,
            'Cp': 0,
            'Cm': 0,
            'D': 0,
            'total': 0
        }
        for (let value in src_data) {
            const row = src_data[value];
            if (!obj_data.hasOwnProperty(row['group__code'])) {
                obj_data[row['group__code']] = {
                    'Pending': 0,
                    'NP': 0,
                    'A': 0,
                    'B': 0,
                    'Cp': 0,
                    'Cm': 0,
                    'D': 0,
                    'total': 0
                }
            }
            total_data[row['qualification']] += row['count'];
            total_data['total'] += row['count'];
            obj_data[row['group__code']][row['qualification']] += row['count'];
            obj_data[row['group__code']]['total'] += row['count'];
        }
        let data_points = {
            'Pending': [total_data['Pending'] / total_data['total'] * 100.0],
            'NP': [total_data['NP'] / total_data['total'] * 100.0],
            'A': [total_data['A'] / total_data['total'] * 100.0],
            'B': [total_data['B'] / total_data['total'] * 100.0],
            'Cp': [total_data['Cp'] / total_data['total'] * 100.0],
            'Cm': [total_data['Cm'] / total_data['total'] * 100.0],
            'D': [total_data['D'] / total_data['total'] * 100.0],
        };
        for (let group in obj_data) {
            if (update_labels) {
                labels.push(group);
            }
            data_points['Pending'].push(obj_data[group]['Pending'] / obj_data[group]['total'] * 100.0);
            data_points['NP'].push(obj_data[group]['NP'] / obj_data[group]['total'] * 100.0);
            data_points['A'].push(obj_data[group]['A'] / obj_data[group]['total'] * 100.0);
            data_points['B'].push(obj_data[group]['B'] / obj_data[group]['total'] * 100.0);
            data_points['Cp'].push(obj_data[group]['Cp'] / obj_data[group]['total'] * 100.0);
            data_points['Cm'].push(obj_data[group]['Cm'] / obj_data[group]['total'] * 100.0);
            data_points['D'].push(obj_data[group]['D'] / obj_data[group]['total'] * 100.0);
        }
        update_labels = false;
        obj_data_all[activity] = obj_data;
        if (show_qualification) {
            datasets.push({
                label: 'Pending',
                data: data_points['Pending'],
                backgroundColor: '#6ea5b9',
                stack: activity + '_0'
            });
        }
        datasets = datasets.concat([
            {
                label: 'NP',
                data: data_points['NP'],
                backgroundColor: 'rgba(204,204,204,0.39)',
                stack: activity + '_0'
            },
            {
                label: 'A',
                data: data_points['A'],
                backgroundColor: '#1cf317',
                stack: activity + '_1'
            },
            {
                label: 'B',
                data: data_points['B'],
                backgroundColor: '#2ba816',
                stack: activity + '_1'
            },
            {
                label: 'C+',
                data: data_points['Cp'],
                backgroundColor: '#c7ae19',
                stack: activity + '_1'
            },
            {
                label: 'C-',
                data: data_points['Cm'],
                backgroundColor: '#ff0600',
                stack: activity + '_1'
            },
            {
                label: 'D',
                data: data_points['D'],
                backgroundColor: '#a90809',
                stack: activity + '_1'
            },
        ]);
    }

    let plot_data = {
        labels: labels,
        datasets: datasets
    };
    let title = 'Final qualification';
    if (!show_qualification) {
        title = 'Automatic score';
    }
    return new Chart(canvas, {
        type: 'bar',
        data: plot_data,
        options: {
            plugins: {
                title: {
                    display: false,
                    text: title
                },
                legend: {
                    display: show_legend,
                    labels: {
                        filter: function (legendItem, data) {
                            if (legendItem.datasetIndex > 6) {
                                return false;
                            }
                            if (legendItem.datasetIndex == 6 && data.datasets[0].label != "Pending") {
                                return false;
                            }
                            return true;
                        }
                    },
                    onClick: function(mouseEvent, legendItem, legend) {
                        for (let datasetIdx = 0; datasetIdx < legend.chart.data.datasets.length; datasetIdx++) {
                            if (legend.chart.data.datasets[datasetIdx].label == legendItem.text) {
                                legend.chart.getDatasetMeta(
                                    datasetIdx
                                ).hidden = legend.chart.isDatasetVisible(datasetIdx);
                            }
                        }
                        legend.chart.update();
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            if (context && context.length > 0) {
                                let activity = context[0].dataset.stack.split('_');
                                activity.splice(-1)
                                return activity.join('_');
                            }
                            return null;
                        }
                    }
                }
            },
            responsive: true,
            interaction: {
                intersect: false,
                mode: 'x'
            },
            scales: {
                x: {
                    stacked: true,
                },
                y: {
                    stacked: true,
                }
            }
        }
    });
}

function get_course_data(course_id, callback) {
    $.get('/api/course/' + course_id + '/statistics/',  callback);
}

function get_activity_data(course_id, activity_id, callback) {
    $.get('/api/course/' + course_id + '/activity/' + activity_id + '/statistics/',  callback);
}
