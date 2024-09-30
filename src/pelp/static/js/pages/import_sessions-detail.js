let entriesTable = null;
let edition_enabled = false;
const import_session_type = parseInt(document.querySelector('[name=import_session_type]').value);
$(document).ready(function() {
    entriesTable = $('#entries').DataTable({
        columns: [
            { data: "id", visible: false},
            {
                data: "learner",
                searchable: false,
                render: function(data, type) {
                    if (data) {
                        let icon = '<svg class="svg-icon svg-icon-sm svg-icon-heavy me-xl-2 valid-button">';
                        icon += '<use xlink:href="#verify-woman-user-3052"></use>'
                        icon += '</svg>';
                        icon += '</svg>';
                        return icon;
                    }
                    return '-';
                }
            },
            {
                data: "entry_file",
                searchable: false,
                visible: import_session_type === 1,
                render: function(data, type, row) {
                    if (data) {
                        return '<a href="' + data + '" target=_blank>' + row['data']['filename'] + '</a>';
                    }
                    return '-';
                }
            },
            {
                data: "data",
                visible: import_session_type === 0,
                render: function(data, type, row) {
                    return '[' + data.username + '] '+ data.first_name + ' ' + data.last_name;
                }
            },
            {
                data: "is_valid",
                render: function(data, type) {
                    let icon = '<svg class="svg-icon svg-icon-sm svg-icon-heavy me-xl-2 valid-button">';
                    if (data) {
                        icon += '<use xlink:href="#checkbox-square-411"></use>'
                    } else {
                        icon += '<use xlink:href="#dismiss-467"></use>'
                    }
                    icon += '</svg>';
                    return icon;
                }
            }
        ]
    });
    $('.edit').on('click', function() {
       edition_enabled = !edition_enabled;
       if (edition_enabled) {
           $("#upload-button").css('visibility', 'visible');
           $("#edit-text").html('Stop Editing');
       } else {
           $("#upload-button").css('visibility', 'hidden');
           $("#edit-text").html('Edit');
       }
    });
    $('#upload-button').on('click', function () {
        if (!edition_enabled) {
            return;
        }
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        let url = $("#entries").data()['ajax'].split('entry/')[0];
        $.ajax({
            headers : {
                'Accept' : 'application/json',
                'Content-Type' : 'application/json',
                'X-CSRFToken': csrftoken
            },
            url : url,
            type : 'PATCH',
            mode : 'same-origin',
            data : JSON.stringify({valid: true}),
            success : function(response, textStatus, jqXhr) {
                window.location.reload(true);
            },
            error : function(jqXHR, textStatus, errorThrown) {
                // log the error to the console
                console.log("The following error occured: " + textStatus, errorThrown);
            }
        });
    });
});
