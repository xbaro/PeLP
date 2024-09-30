$(document).ready(function() {
    let canvas = document.getElementById('tag_cloud_canvas');
    let max_val = 1;
    let translated_tags_list = [];
    for(const element of tags_list) {
        if (element[1] > max_val) {
            max_val = element[1];
        }
        let text = element[0];
        if (element[2][document.documentElement.lang] !== undefined) {
            text = element[2][document.documentElement.lang]
        }
        translated_tags_list.push([text, element[1], element[0]]);
    }

    if (canvas != null) {
        canvas.style.display = null;
        WordCloud(canvas, {
            list: translated_tags_list,
            // shape: 'square',
            minSize: 0,
            weightFactor: function (size) {
                return Math.pow((10.0 * size / max_val) , 2) * canvas.width / 1024.0;
            },
            drawOutOfBound: false,
            shrinkToFit: true,
            click: function(item) {
                $("select[name=tags]").append(new Option(item[0], item[2], true, true)).trigger('change');
            },
        });
    }

    $(".rating").on('rating:change', function (event, caption) {
        const faq_id=$(this).data()['faqId'];
        const rating=$(this).val() | 0;
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const url = '/api/faq/' + faq_id + '/rate/';
        $.ajax({
            headers : {
                'Accept' : 'application/json',
                'Content-Type' : 'application/json',
                'X-CSRFToken': csrftoken
            },
            url : url,
            type : 'POST',
            mode : 'same-origin',
            data : JSON.stringify({rate: rating}),
            error : function(jqXHR, textStatus, errorThrown) {
                // log the error to the console
                console.log("The following error occurred: " + textStatus, errorThrown);
            }
        });
    });
});
