window.cgsy = window.cgsy || {};

(function ($, cgsy) {

    cgsy.AjaxSender = function (url) {

        url = url || window.location.href;
        var sender_method = null;
        var headers = {};
        var cross_domain = false;
        var data_as_payload = false;

        var beforeSendCallback = function (response) {};
        var success_callback = function (response) {};

        var default_fail_callback = function (response) {
            var msg = 'Failure on request to "' + url + '" with method';
            msg += ' "' + sender_method + '".';

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

        this.addHeader = function(key, value) {
            "use strict";
            headers[key] = value;
        };

        this.setSuccessCallback = function (callback) {
            if (typeof callback !== 'function') {
                console.error('Callback is not a function: ' + callback);
                return;
            }
            success_callback = callback
        };

        this.setFailCallback = function (callback) {
            if (typeof callback !== 'function') {
                console.error('Callback is not a function: ' + callback);
                return;
            }

            fail_callback = function (response) {
                callback(response);
                default_fail_callback(response);
            }
        };

        this.setBeforeSendCallback = function(callback) {
            if (typeof callback !== 'function') {
                console.error('Callback is not a function: ' + callback);
                return;
            }
            beforeSendCallback = callback;
        };

        this.crossDomainMode = function() {
            cross_domain = true;
        };

        this.payloadMode = function() {
            data_as_payload = true;
        };

        this.send = function (method, data) {

            data = data || {};
            sender_method = method;

            if (data_as_payload) {
                this.addHeader('Content-Type', 'application/json');
            }

            var params = {
                url: url,
                type: method,
                encode: true,
                crossDomain: cross_domain,
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type)) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }

                    $.each(headers, function(key, value) {
                        "use strict";
                        xhr.setRequestHeader(key, value);
                    });

                    beforeSendCallback();
                },
                success: success_callback,
                error: fail_callback
            };

            if (data_as_payload) {
                params['dataType'] = 'json';
                params['contentType'] = 'application/json';
                params['data'] = JSON.stringify(data);
            } else {
                params['data'] = data;
            }

            $.ajax(params);
        };

        this.get = function(data) {
            this.send('GET', data || {});
        };

        this.post = function(data) {
            this.send('POST', data || {});
        };

        this.put = function(data) {
            this.send('PUT', data);
        };

        this.patch = function(data) {
            this.send('PATCH', data || {});
        };

        this.delete = function(data) {
            this.send('DELETE', data || {});
        };
    };

    cgsy.AjaxFormDataSender = function (url) {

        url = url || window.location.href;

        var success_callback = function () {
        };
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

        this.setSuccessCallback = function (callback) {
            success_callback = callback
        };

        this.setFailCallback = function (callback) {
            fail_callback = function (response) {
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
                processData: false,
                contentType: false,
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