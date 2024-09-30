let filesTable = null;
let testsTable = null;
let testsEditor = null;
let edition_enabled = false;
let project_submissions_table = null;

function request_parameters() {
  let url = window.location.href;
  let paramString = new RegExp('(.*)[?](.*)').exec(url);
  if (null == paramString) {
    return {'base': url, 'params': null};
  }

  let paramList = [];
  if (paramString[2].includes("&amp;")) {
    paramList = paramString[2].split("&amp;");
  } else {
    paramList = paramString[2].split("&");
  }

  let params = [];

  for (let i = 0; i < paramList.length; i++) {
    let values = paramList[i].split("=");
    params[values[0]] = values[1];
  }
  return {"base": paramString[1], "params": params};
}

function showProjectModuleForm(data, create=false) {
    if (create) {
        $('#form_project_module').get(0).reset()
        $('#form_project_module :input[name=id]').val('');
        $('#form_project_module :input[name=project]').val(data['project']);
    } else {
        $('#form_project_module :input[name=id]').val(data['id']);
        $('#form_project_module :input[name=project]').val(data['project']);
        //$('#form_project_module :input[id=id_type]').val(data['type']);
        $('#form_project_module :input[name=name]').val(data['name']);
        $('#form_project_module :input[name=base_path]').val(data['base_path']);
        $('#form_project_module :input[name=allowed_files_regex]').val(data['allowed_files_regex']);
    }
    set_initial_files_regex('#form_project_module');
    $('#form_project_module').show();
    $('#btn_save_project_module').addClass('disabled');
    $('#btn_save_project_module').show();
    $("#btn_cancel_project_module").show();
}

function set_initial_files_regex(form) {
    const current_value = $('form' + form + ' :input[name=allowed_files_regex]').val();
    if (current_value == '.*\\\\.(c|h)$') {
        $('form' + form + ' :input[name=allowed_files_regex]').prop("disabled", true);
        $('form' + form + ' :input[name=acceptedFilesOpt][value=files_c_h]').prop('checked', true);
    } else if (current_value == '.*[\\\\.(c|h) | .*README\\\\.(txt)]$') {
        $('form' + form + ' :input[name=allowed_files_regex]').prop("disabled", true);
        $('form' + form + ' :input[name=acceptedFilesOpt][value=files_c_h_readme]').prop('checked', true);
    } else {
        $('form' + form + ' :input[name=allowed_files_regex]').prop("disabled", false);
        $('form' + form + ' :input[name=acceptedFilesOpt][value=custom]').prop('checked', true);
    }
}

$(document).ready(function () {
    project_submissions_table = $('#submissions').dataTable(
        {
            columnDefs: [
                {
                    targets: -1,
                    render: function ( data, type, row ) {
                        let icon = [];
                        const rowData = $('#submissions').data();
                        const url = '/course/' + rowData['pelpCourseId'] + '/activity/' + rowData['pelpActivityId'] + '/report/' + row['id'] + '/';
                        icon.push('<div class="activity-actions"><a className="btn-outline-primary" href="' + url + '">');
                        icon.push('<svg className="svg-icon svg-icon-lg svg-icon-heavy me-xl-2" style="width: 25px;height: 25px;">');
                        icon.push('<use xlink:href="#find-7048"></use>');
                        icon.push('</svg></a></div>');
                        return icon.join('\n');
                    }
                }
            ]
        }
    );
    $('#form_project_module').hide();
    $('#btn_save_project_module').hide();
    $('#btn_cancel_project_module').hide();
    set_initial_files_regex('#form_project');
    var stepper = new Stepper($('.bs-stepper')[0], {
        linear: false,
        animation: true
    });
    const url_pars = request_parameters();
    if (url_pars['params'] && url_pars['params'].hasOwnProperty('step')) {
        $('.step-trigger')[Number.parseInt(url_pars['params']['step'])].click();
    }
    /*var stepperPanList = [].slice.call(stepperFormEl.querySelectorAll('.bs-stepper-pane'))
    stepper.addEventListener('show.bs-stepper', function (event) {

        // form.classList.remove('was-validated')
        var nextStep = event.detail.indexStep;
        var currentStep = nextStep;

        if (currentStep > 0) {
            currentStep--;
        }

        var stepperPan = stepperPanList[currentStep]

        if ((stepperPan.getAttribute('id') === 'test-form-1' && !inputMailForm.value.length) ||
            (stepperPan.getAttribute('id') === 'test-form-2' && !inputPasswordForm.value.length)) {
            event.preventDefault()
            //form.classList.add('was-validated')
        }
    });*/
    filesTable = $('#files').DataTable({
        language: {
            'url': $('#files').data('language-url')
        },
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
    $('#files').on('click', '.lock-button', function () {
        const tr = $(this).closest('tr');
        const selectedRow = filesTable.row(tr).data();
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
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
                console.log("The following error occured: " + textStatus, errorThrown);
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
        language: {
            'url': $('#tests').data('language-url')
        },
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
    });
    for (let inst in CKEDITOR.instances) {
        CKEDITOR.instances[inst].on('change', function () {
            $("#btn_save_activity").removeClass('disabled');
        });
    }
    $('form#form_activity :input').on('change', function () {
        $("#btn_save_activity").removeClass('disabled');
    });
    $('form#form_project :input').on('change', function () {
        $("#btn_save_project").removeClass('disabled');
    });
    $('form#form_project_module :input').on('change', function () {
        $("#btn_save_project_module").removeClass('disabled');
    });
    $('form#form_project .valgrind-selector').on('change', function () {
        if (this.checked) {
            $('#id_valgrind_report_path').val('bin/memcheck.xml');
        } else {
            $('#id_valgrind_report_path').val(null);
        }
    });
    $('form :input[type=radio][name=acceptedFilesOpt]').on('change', function () {
        const form = $(this).closest('form');
        if (this.value == 'files_c_h') {
            form.find('input#id_allowed_files_regex').val('.*\\\\.(c|h)$');
            form.find('input#id_allowed_files_regex').prop("disabled", true);
        } else if (this.value == 'files_c_h_readme') {
            form.find('input#id_allowed_files_regex').val('.*[\\\\.(c|h) | .*README\\\\.(txt)]$');
            form.find('input#id_allowed_files_regex').prop("disabled", true);
        } else {
            form.find('input#id_allowed_files_regex').val(null);
            form.find('input#id_allowed_files_regex').prop("disabled", false);
        }
    });
    $("#btn_save_activity").on('click', function() {
        $('#form_activity').submit();
    });
    $("#btn_save_project").on('click', function() {
        $('#form_project').submit();
    });
    $("#btn_save_project_module").on('click', function() {
        $('#form_project_module').submit();
    });
    $("#btn_cancel_project_module").on('click', function() {
        $("#btn_save_project_module").addClass('disabled');
        $('#form_project_module').hide();
        $("#btn_save_project_module").hide();
        $("#btn_cancel_project_module").hide();
    });
    $("#form_activity").submit(function(event) {
       event.preventDefault();
       for(let inst in CKEDITOR.instances) {
           CKEDITOR.instances[inst].updateElement();
       }
       $.ajax({
           data: $(this).serialize(),
           type: $(this).attr('method'),
           url: $(this).attr('action'),
           success: function(response) {
               const t = new bootstrap.Toast($('#toast_save_success')[0]);
               t.show();
               $("#btn_save_activity").addClass('disabled');
           },
           error: function (request, status, error) {
               $('#toast_save_error .toast-body').html(request.responseText);
               const t = new bootstrap.Toast($('#toast_save_error')[0]);
               t.show();
           }
       });
    });
    $("#form_project").submit(function(event) {
       event.preventDefault();
       let form_data = new FormData(this);
       form_data.set('allowed_files_regex', $(this).find('input#id_allowed_files_regex').val());
       form_data.set('valgrind_report_path', $(this).find('#id_valgrind_report_path').val());
       $.ajax({
           data: form_data,
           method: $(this).attr('method'),
           url: $(this).attr('action'),
           contentType: false,
           cache: false,
           processData: false,
           success: function(response) {
               const t = new bootstrap.Toast($('#toast_save_success')[0]);
               t.show();
               $("#btn_save_project").addClass('disabled');
           },
           error: function (request, status, error) {
               $('#toast_save_error .toast-body').html(request.responseText);
               const t = new bootstrap.Toast($('#toast_save_error')[0]);
               t.show();
           }
       });
   });
   $("#form_project_module").submit(function(event) {
       event.preventDefault();
       let form_data = new FormData(this);
       form_data.set('project', $('#form_project :input[name=id]').val());
       form_data.set('allowed_files_regex', $(this).find('input#id_allowed_files_regex').val());
       let new_module = false;
       if (isNaN(Number.parseInt(form_data.get('id')))) {
           new_module = true;
       }
       $.ajax({
           data: form_data,
           method: $(this).attr('method'),
           url: $(this).attr('action'),
           contentType: false,
           cache: false,
           processData: false,
           success: function(response) {
               const t = new bootstrap.Toast($('#toast_save_success')[0]);
               t.show();
               $("#btn_save_project").addClass('disabled');
               $('#form_project_module').hide();
               if (new_module) {
                   $("#btn_save_project").hide();
                   $('a.module-add').parent('div').hide();
               }
               $('#btn_save_project_module').hide();
               $("#btn_cancel_project_module").hide();
           },
           error: function (request, status, error) {
               $('#toast_save_error .toast-body').html(request.responseText);
               const t = new bootstrap.Toast($('#toast_save_error')[0]);
               t.show();
           }
       });
   });
   $(".module-edit").on('click', function(event) {
       event.preventDefault();
       const course_id = $('#form_activity :input[name=course]').val();
       const activity_id = $('#form_activity :input[name=id]').val();
       const module_id = this.dataset['moduleId'];
       $.get('/api/course/' + course_id + '/activity/' + activity_id + '/module/' + module_id + '/',
           function (data) {
                showProjectModuleForm(data);
           });
   });
   $(".module-add").on('click', function(event) {
       event.preventDefault();
       const course_id = $('#form_activity :input[name=course]').val();
       const activity_id = $('#form_activity :input[name=id]').val();

       showProjectModuleForm({

       }, true);
   });
})
