function loadModalCode(filename, url) {
    $.ajax({
        url : url,
        dataType: "text",
        success : function (data) {
            $("#modal_filename").html(filename);
            $("#modal_code").text(data);
            //hljs.highlightElement($("#modal-code"));
            hljs.highlightAll();
            $("#source-code-modal").modal('show');
        }
    });
}
