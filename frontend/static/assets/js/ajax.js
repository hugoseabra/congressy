window.cgsy = window.cgsy || {};

(function ($, cgsy) {

    cgsy.AjaxSender = function (url) {

        url = url || window.location.href;

        var success_callback = function () {};
        var default_fail_callback = function (response) {
            var msg = 'Failure on request to "' + url + '" with method';
                msg += ' "' + this.method + '".';

            if (response.hasOwnProperty('detail')) {
                msg += ' Detalhes: ' + response.detail;
            }

            console.error(msg);
        };

        var fail_callback = default_fail_callback;

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

        this.setSuccessCallback = function(callback) {
            success_callback = callback
        };

        this.setFailCallback = function(callback) {
            fail_callback = function(response) {
                callback(response);
                default_fail_callback(response);
            }
        };

        this.send = function (method, data) {

            data = data || {};

            $.ajax({
                url: url,
                type: method,
                data: data,
                encode: true,
                crossDomain: false,
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type)) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                },
                success: success_callback,
                error: fail_callback
            });
        };
    };

})(jQuery, window.cgsy);