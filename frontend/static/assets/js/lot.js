function send(url, method, data, success_callback, error_callback) {
    // CSRF code
    function getCookie(name) {
        var cookieValue = null;
        var i = 0;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (i; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajax({
        url: url,
        type: method,
        data: data || {},
        encode: true,
        crossDomain: false,
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: success_callback || function () {
        },
        error: error_callback || function () {
        }
    });
}

function save_lot(url, data, msg) {
    send(
        url,
        'PATCH',
        data,
        function (response) {
            Messenger().post({
                message: msg,
                type: 'success'
            });
        },
        function () {
            Messenger().post({
                message: 'Não foi possivel processar salvamento de lote.',
                type: 'error'
            });
        }
    );
}