$(document).ready(function() {
    $('#courses').DataTable({
        columns: [
            { data: "id"},
            { data: "status"},
            { data: "type"},
            { data: "course_group.code"},
            {
                data: "activity",
                render: function(data, type) {
                    if (data) {
                        return data.code;
                    }
                    return '-';
                }
            },
            { data: "created_at"},
            {
                className: 'action-cell',
                data: 'id',
                sortable: false,
                render: function(data, type) {
                    return '<a href="/import/' + data + '/" class="btn btn-primary btn-sm" tabindex="-1" role="button"><i class="far fa-arrow-alt-circle-right"></i></a>';
                }
            }
        ]
    });
});
