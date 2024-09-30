let testsChart = null;

function get_color(percentage) {
    if (percentage > 99.9) {
        return 'hsl(100, 100%, 60%)';
    }
    if (percentage > 80) {
        return 'hsl(68,90%,42%)';
    }
    if (percentage > 60) {
        return 'hsl(44,98%,43%)';
    }
    if (percentage > 40) {
        return 'hsl(0, 100%, 60%)';
    }
    if (percentage > 20) {
        return 'hsl(23,92%,44%)';
    }
    if (percentage > 10) {
        return 'hsl(0,97%,43%)';
    }
    return 'hsl(0, 100%, 35%)';
}

function get_test_datasets(tests, level, initial) {
    if (!initial.hasOwnProperty(level)) {
        initial[level] = {
            labels: [],
            backgroundColor: [],
            data: []
        }
    }
    for (const test in tests) {
        initial[level]['labels'].push(test);
        initial[level]['backgroundColor'].push(get_color(tests[test]['passed'] / tests[test]['count'] * 100.0));
        initial[level]['data'].push(tests[test]['count']);
        if (Object.keys(tests[test]['children']).length > 0) {
            initial = get_test_datasets(tests[test]['children'], level + 1, initial);
        }
    }
    return initial;
}

function get_data(course_id, activity_id, submission_id, callback) {
    const url = '/api/course/' + course_id + '/activity/' + activity_id + '/submission/' + submission_id + '/test/summary/';
    $.get(url, function (data) {
        // Get object representation of tests structure
        let obj = {};

        // Add submission as level 0
        obj[0] = {
            labels: ['S' + data['submission_id']],
            backgroundColor: [get_color(data['passed'] / data['count'] * 100.0)],
            data: [data['count']],
            score: data['score'],
            datalabels: {
                anchor: 'start',
                backgroundColor: get_color(data['passed'] / data['count'] * 100.0),
                //borderWidth: 0
            }
        };

        obj = get_test_datasets(data['tests'], 1, obj);

        // Build datasets from obj
        let labels = [];
        let datasets = [];
        const levels = Array.from(Object.keys(obj)).reverse();
        for (let level = levels[0]; level >= 0; level--) {
            labels = labels.concat(obj[level]['labels']);
            datasets.push({
                backgroundColor: obj[level]['backgroundColor'],
                data: obj[level]['data'],
                datalabels: obj[level]['datalabels'],
                score: obj[level]['score']
            });
        }

        callback({
            labels: labels,
            datasets: datasets
        });
    });
}

function generateLabels(chart) {
    try {
        // Get the default label list
        const original = Chart.overrides.pie.plugins.legend.labels.generateLabels;
        const labelsOriginal = original.call(this, chart);
        //const labelsOriginal = original.call(chart);

        // Build an array of colors used in the datasets of the chart
        let datasetColors = chart.data.datasets.map(function (e) {
            return e.backgroundColor;
        });
        datasetColors = datasetColors.flat();

        // Build accumulative dataset count
        let count_index = [];
        let index_count = 0;
        chart.data.datasets.forEach(dataset => {
            index_count += dataset.data.length;
            count_index.push(index_count);
        });
        count_index.push(Infinity);

        // Modify the color and hide state of each label
        labelsOriginal.forEach(label => {
            // There are twice as many labels as there are datasets. This converts the label index into the corresponding dataset index
            let idx = 0;
            while (label.index >= count_index[idx]) {
                idx++;
            }
            label.datasetIndex = idx;

            // The hidden state must match the dataset's hidden state
            label.hidden = !chart.isDatasetVisible(label.datasetIndex);

            // Change the color to match the dataset
            label.fillStyle = datasetColors[label.index];
        });

        return labelsOriginal;
    } catch (e) {
        return false;
    }

    return false;
}

function get_legend(show_legend) {
    if (show_legend) {
        return {
            labels: {
                generateLabels: generateLabels
            },
            onClick: function (mouseEvent, legendItem, legend) {
                // toggle the visibility of the dataset from what it currently is
                legend.chart.getDatasetMeta(
                    legendItem.datasetIndex
                ).hidden = legend.chart.isDatasetVisible(legendItem.datasetIndex);
                legend.chart.update();
            }
        }
    } else {
        return false;
    }
}

function get_chart_config(course_id, activity_id, submission_id, show_legend, callback) {
    get_data(course_id, activity_id, submission_id, function (data) {
        const conf = {
            type: 'pie',
            data: data,
            plugins: [ChartDataLabels],
            options: {
                responsive: true,
                plugins: {
                    legend: get_legend(show_legend),
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                // Build accumulative dataset count
                                let count_index = [0];
                                let index_count = 0;
                                context.chart.data.datasets.forEach(dataset => {
                                    index_count += dataset.data.length;
                                    count_index.push(index_count);
                                });
                                const labelIndex = count_index[context.datasetIndex] + context.dataIndex;
                                return context.chart.data.labels[labelIndex];
                            }
                        }
                    },
                    datalabels: {

                        color: 'blue',
                        display: function (context) {
                            var dataset = context.dataset;
                            if (dataset.datalabels) {
                                return true;
                            }
                            return false;
                        },
                        font: function(context) {
                            const w = context.chart.width;
                            return {
                                size: w < 300 ? 14 : 16,
                                weight: 'bold',
                            };
                        },
                        padding: 6,
                        formatter: function(value, context) {
                            if (context.dataset['score']) {
                                return Math.round(context.dataset['score'] * 10) / 10;
                            }
                            return ''
                        }
                    }
                },
            },
        };
        callback(conf);
    });
}

function plot_results(element, submission_id, activity_id, course_id, show_legend) {
    const ctx = document.getElementById(element).getContext('2d');
    submission_id = submission_id || Number.parseInt(document.getElementById(element).dataset['submissionId']);
    activity_id = activity_id || Number.parseInt(document.getElementById(element).dataset['activityId']);
    course_id = course_id || Number.parseInt(document.getElementById(element).dataset['courseId']);
    show_legend = show_legend || (document.getElementById(element).dataset['showLegend'] != 'false');
    get_chart_config(course_id, activity_id, submission_id, show_legend, function (config) {
        if (testsChart != null) {
            testsChart.destroy();
            testsChart = null;
        }
        testsChart = new Chart(ctx, config);
        generateLabels(testsChart);
    });
}
