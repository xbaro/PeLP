$(document).ready(function() {
    $('#courses').DataTable({
        language: {
            'url': $('#courses').data('language-url')
        },
        columns: [
            { data: "semester.code"},
            { data: "code"},
            { data: "name"},
            {
                className: 'action-cell',
                data: 'id',
                sortable: false,
                render: function(data, type) {
                    return '<a href="/course/' + data + '/" class="btn btn-primary btn-sm" tabindex="-1" role="button"><i class="far fa-arrow-alt-circle-right"></i></a>';
                }
            }
        ]
    });
});
