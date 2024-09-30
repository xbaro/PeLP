const activity_id = parseInt(document.querySelector('input[name=activity_id]').value);

let schema = 'wss';
if (location.protocol !== 'https:') {
    schema = 'ws';
}
let connectionString = schema + '://' + window.location.host + '/ws/activity/' + activity_id + '/my_submissions/';

let projectSocket = null;

function connect() {
    try {
        projectSocket = new WebSocket(connectionString);
    } catch (e) {
        console.log('Error connecting to WebSocket. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function () {
            connect();
        }, 1000);
    }
    projectSocket.onopen = function open() {
        console.log('WebSockets connection created.');
    };

    projectSocket.onclose = function (e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function () {
            connect();
        }, 1000);
    };

    // Sending the info about the room
    projectSocket.onmessage = function (e) {
        // On getting the message from the server
        // Do the appropriate steps on each event.
        let data = JSON.parse(e.data);
        let message = data['message'];
        let event = data["event"];
        console.log(event);
        switch (event) {
            case "NEW_SUBMISSION":
                submission_table.ajax.reload(null, true);
                $('#tests_chart').data('submissionId', message);
                const max_submissions = $('#max_total_submissions').text();
                const max_day_submissions = $('#max_day_submissions').text();
                let total_submissions = $('#num_total_submissions').text();
                let day_submissions = $('#num_day_submissions').text();

                if (max_submissions && total_submissions) {
                    total_submissions = Number.parseInt(total_submissions) + 1;
                    $('#num_total_submissions').text(total_submissions);
                    if (total_submissions >= Number.parseInt(max_submissions)) {
                        $('#submission_upload').hide();
                    }
                }
                if (max_day_submissions && day_submissions) {
                    day_submissions = Number.parseInt(day_submissions) + 1;
                    $('#num_day_submissions').text(day_submissions);
                    if (day_submissions >= Number.parseInt(max_day_submissions)) {
                        $('#submission_upload').hide();
                    }
                }
                plot_results('tests_chart');
                break;
            case "SUBMISSION_NEW_STATE":
                submission_table.ajax.reload(null, false);
                if (message == 'PROCESSED') {
                    plot_results('tests_chart');
                }
                break;
            default:
                console.log("No event")
        }
    };

    if (projectSocket.readyState == WebSocket.OPEN) {
        projectSocket.onopen();
    }
}

//call the connect function at the start.
connect();
