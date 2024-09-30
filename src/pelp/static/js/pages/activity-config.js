let filesTable = null;
let testsTable = null;
let testsEditor = null;
let edition_enabled = false;
$(document).ready(function() {
    filesTable = $('#files').DataTable({
        rowGroup: {
            dataSrc: 'module.name',
            emptyDataGroup: 'Main Application'
        },
        columns: [
            { data: "id", visible: false},
            { data: "file", visible: false},
            {
                data: "module",
                searchable: false,
                render: function(data, type) {
                    if (data) {
                        return data.name;
                    }
                    return '-';
                }
            },
            {
                data: "filename",
                render: function(data, type, row) {
                    let link = '<a href="#" data-filename="' + data + '" data-url="' + row.file + '" class="file-link">' + data + '</a>';
                    if (row.locked) {
                        return link;
                    }
                    return '<strong>' + link + '</strong>';
                }
            },
            {
                data: "locked",
                render: function(data, type) {
                    let icon = '<svg class="svg-icon svg-icon-sm svg-icon-heavy me-xl-2 lock-button">';
                    if (data) {
                        icon += '<use xlink:href="#lock-1638"></use>'
                    } else {
                        icon += '<use xlink:href="#unlock-1637"></use>'
                    }
                    icon += '</svg>';
                    return icon;
                }
            }
        ]
    });
    $('#files').on('click', '.file-link', function() {
        loadModalCode(this.dataset.filename, this.dataset.url);
        console.log(this);
    });
    $('.edit').on('click', function() {
       edition_enabled = !edition_enabled;
       if (edition_enabled) {
           $("#edit-icon").css('visibility', 'visible');
           $("#edit-text").html('Stop Editing');
       } else {
           $("#edit-icon").css('visibility', 'hidden');
           $("#edit-text").html('Edit');
       }
    });
    $('#files').on('click', '.lock-button', function () {
        const tr = $(this).closest('tr');
        const selectedRow = filesTable.row(tr).data();
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        if (!edition_enabled) {
            return;
        }
        let url = $("#files").data()['ajax'].split('?')[0] + selectedRow['id'] + '/';
        $.ajax({
            headers : {
                'Accept' : 'application/json',
                'Content-Type' : 'application/json',
                'X-CSRFToken': csrftoken
            },
            url : url,
            type : 'PATCH',
            mode : 'same-origin',
            data : JSON.stringify({locked: !selectedRow['locked']}),
            success : function(response, textStatus, jqXhr) {
                $('#files').DataTable().ajax.reload(null, false);
            },
            error : function(jqXHR, textStatus, errorThrown) {
                // log the error to the console
                console.log("The following error occurred: " + textStatus, errorThrown);
            }
        });
    });

    let tests_url = $("#tests").data()['ajax'].split('?')[0];
    testsEditor = new $.fn.dataTable.Editor( {
        ajax: {
            url: tests_url + '{id}/',
            edit: {
                type: 'PATCH',
                url: tests_url + '{id}/',
                headers: {
                    'Accept' : 'application/json',
                    'Content-Type' : 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                mode : 'same-origin',
                data : function (action_data) {
                    const id = Object.keys(action_data.data)[0];
                    const row_data = action_data.data[id];
                    return JSON.stringify(row_data);
                },
                replacements: {
                    id: function (key, id, action, data) {
                        return id;
                    }
                },
            }
        },
        table: "#tests",
        idSrc:  'id',
        fields: [ {
                label: "Weight",
                name: "weight"
            }
        ]
    } );

    // Activate an inline edit on click of a table cell
    $('#tests').on( 'click', 'tbody td:not(:first-child)', function (e) {
        testsEditor.inline( this );
    } );

    testsTable = $('#tests').DataTable({
        /*rowGroup: {
            dataSrc: 'parent.code',
            emptyDataGroup: 'Root Section'
        },*/
        columns: [
            { data: "id", visible: false},
            { data: "code", visible: true},
            { data: "weight", visible: true},
            {
                data: "parent",
                searchable: false,
                render: function(data, type) {
                    if (data) {
                        return data.code;
                    }
                    return '-';
                }
            },
        ],
        order: [[ 3, 'asc' ]],
        select: true,
    });


});
