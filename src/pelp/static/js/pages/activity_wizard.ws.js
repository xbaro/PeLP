const activity_id = document.getElementById("form_activity").getAttribute("data-activity_id");

let schema = 'wss';
if (location.protocol !== 'https:') {
    schema = 'ws';
}
let connectionString = schema + '://' + window.location.host + '/ws/activity/' + activity_id + '/';

let projectSocket = null;
let current_status = null;
let total_weight = 0;

function show_status() {
    const pre_prepare_states = ['CREATED', 'CLONING', 'UPLOADING'];
    const pre_valid_states = ['CLONED', 'UPLOADED', 'VALIDATING', 'INVALID'];
    const pre_tested_states = ['VALID', 'TESTING', 'FAILED_TEST'];
    const error_states = ['ERROR', 'TIMEOUT'];
    const icon_valid = '<span><i class="fa fa-check"></i></span>';
    const icon_failed = '<span><i class="fa fa-times"></i></span>';
    const icon_unknown = '<span class="font-weight-bold">?</span>';
    const processing = '<div class="sk-circle">\n' +
        '                        <div class="sk-circle1 sk-child"></div>\n' +
        '                        <div class="sk-circle2 sk-child"></div>\n' +
        '                        <div class="sk-circle3 sk-child"></div>\n' +
        '                        <div class="sk-circle4 sk-child"></div>\n' +
        '                        <div class="sk-circle5 sk-child"></div>\n' +
        '                        <div class="sk-circle6 sk-child"></div>\n' +
        '                        <div class="sk-circle7 sk-child"></div>\n' +
        '                        <div class="sk-circle8 sk-child"></div>\n' +
        '                        <div class="sk-circle9 sk-child"></div>\n' +
        '                        <div class="sk-circle10 sk-child"></div>\n' +
        '                        <div class="sk-circle11 sk-child"></div>\n' +
        '                        <div class="sk-circle12 sk-child">     </div>\n' +
        '                      </div>';

    // Initialize the progress bar
    if (error_states.includes(current_status)) {
        $(".progress-steps-line").removeClass('valid');
        $(".progress-steps-line").addClass('failed');
        $(".progress-steps-step").removeClass('valid');
        $(".progress-steps-step").addClass('failed');
        $(".progress-steps-step").html(icon_failed);
        $("#project_status_card").removeClass('border-success');
        $("#project_status_card").addClass('border-danger');
        return;
    } else {
        $("#project_status_card").removeClass('border-success');
        $("#project_status_card").removeClass('border-danger');
        $(".progress-steps-line").removeClass('valid');
        $(".progress-steps-line").removeClass('failed');
        $(".progress-steps-step").removeClass('valid');
        $(".progress-steps-step").removeClass('failed');
        $(".progress-steps-step").html(icon_unknown);
    }

    // Disable advanced steps
    $('#project-files-step-trigger').prop('disabled', true);
    $('#project-weights-step-trigger').prop('disabled', true);
    $("#btn_test").hide();
    $('#project_status_messages p').hide();
    $('#msg_invalid_project').show();

    // Check if activity is still creating
    if (current_status == 'CREATING') {
        $('#step-prepare').html(icon_failed);
        $('#step-prepare').addClass('failed');
        return;
    }

    // Update depending on the state
    if (!pre_prepare_states.includes(current_status)) {
        $('#step-prepare').html(icon_valid);
        $('#step-prepare').addClass('valid');
        $('#line-prepare-valid').addClass('valid');
        if (!pre_valid_states.includes(current_status)) {
            $('#step-valid').html(icon_valid);
            $('#step-valid').addClass('valid');
            $('#line-valid-tested').addClass('valid');
            if (filesTable != null) {
                filesTable.ajax.reload( null, false );
            }
            $('#project_status_messages p').hide();
            $('#msg_testing_project').show();
            $('#project-files-step-trigger').prop('disabled', false);
            $("#btn_test").show();

            if (!pre_tested_states.includes(current_status)) {
                $('#step-tested').html(icon_valid);
                $('#step-tested').addClass('valid');
                $('#line-tested-ready').addClass('valid');
                if (testsTable != null) {
                    testsTable.ajax.reload( null, false );
                }
                $('#project-weights-step-trigger').prop('disabled', false);
                $('#project_status_messages p').hide();
                $('#msg_not_ready_project').show();
                if (total_weight == 100) {
                    $('#step-ready').html(icon_valid);
                    $('#step-ready').addClass('valid');
                    $('#project_status_messages p').hide();
                    $('#msg_project_ready').show();
                } else {
                    $('#step-ready').html(icon_failed);
                    $('#step-ready').addClass('failed');
                }
            }
        }
    }
    if (current_status == 'INVALID') {
        $('#step-valid').html(icon_failed);
        $('#step-valid').addClass('failed');
        $("#project_status_card").addClass('border-danger');
    } else if (current_status == 'FAILED_TEST') {
        $('#step-tested').html(icon_failed);
        $('#step-tested').addClass('failed');
        $("#project_status_card").addClass('border-danger');
    } else if (pre_prepare_states.includes(current_status)) {
        $('#step-prepare').html(processing);
    } else if (current_status == 'VALIDATING') {
        $('#step-valid').html(processing);
    } else if (current_status == 'TESTING') {
        $('#step-tested').html(processing);
    }

    document.getElementById("project_status").innerHTML = current_status;
    document.getElementById("project_total_weight").innerHTML = total_weight;
}

function send_message(data) {
    if (projectSocket != null && projectSocket.readyState == WebSocket.OPEN) {
        projectSocket.send(JSON.stringify(data));
    }
}

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
        switch (event) {
            case "INITIAL_STATUS":
            case "STATUS_CHANGE":
                current_status = message;
                show_status();
                break;
            case "INITIAL_WEIGHT":
            case "WEIGHT_CHANGE":
                total_weight = message;
                show_status();
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

$("#btn_validate").on('click', function () {
    send_message({'event': 'VALIDATE_PROJECT', 'message': activity_id});
})

$("#btn_test").on('click', function () {
    send_message({'event': 'TEST_PROJECT', 'message': activity_id});
})
