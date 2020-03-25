window.integrations = window.integrations || {};

(function(window, $, AjaxSender) {

    window.integrations.Loader = function(target_el,) {
        this.clean = function() {
            target_el.empty();
        };

        this.show = function() {
            var row = $('<div>').addClass('row text-center').append();
            var col = $('<div>').addClass('col-md-12');
            var loader = $('<i>').addClass(
                'info-color fa fa-circle-notch fa-spin fa-2x'
            ).css({
                'margin-top': '5px'
            });
            col.append(loader);
            row.append(col);
            target_el.html(row);
        };
    };


})(window, window.jQuery);

(function(window, $, AjaxSender) {

    window.integrations.MailchimpForm = function(uri, target_el) {
        var self = this;

        self.http_status = null;

        self.load = function() {
            self.reset();

            new Promise(function (resolve) {
                self._getClient(uri, resolve).get();
            });
        };

        self.reset = function() {};

        self._getClient = function (uri, resolve) {
            var client = new AjaxSender(uri);
                client.setSuccessCallback(self._getSuccessCallback(resolve));
                client.setFailCallback(self._getFailCallback(uri, resolve));

            return client;
        };

        self._getSuccessCallback = function(resolve) {
            return function (data, status_text, response) {
                self.http_status = response.status;

                if (data.hasOwnProperty('result')) {
                    data = data.result;
                } else if (data.hasOwnProperty('results')) {
                    data = data.results;
                } else if (data.hasOwnProperty('responseJSON')) {

                } else if (!data) {
                    console.error(
                        'Requisição bem sucedida, porém com resposta' +
                        ' desconhecida na requisição.'
                    );
                }
                target_el.html(data);
                resolve({'type': 'success', 'status': self.http_status, 'result': data});
            };
        };

        self._getFailCallback = function(uri, resolve) {
            return function(response) {
                self.http_status = response.status;

                var original_response = response;
                var msg = 'Erro ao buscar dados de "'+uri+'".';

                if (response.hasOwnProperty('responseJSON')) {
                    var response_json = response.responseJSON;

                    if (response_json.hasOwnProperty('detail')) {
                        msg = response_json.detail;
                    }
                }

                console.error(msg, original_response);

                resolve({'type': 'error', 'status': self.http_status, 'result': original_response});
            }
        };
    };

})(window, window.jQuery, window.cgsy.AjaxSender);

(function(window, $) {

    window.integrations.MailchimpRow = function(row_el) {
        var self = this;
        var opened = false;

        self.row_el = row_el;

        self.isOpened = function() {
            return opened === true;
        };

        self.open = function() {
            opened = true;
            self.row_el.fadeIn();
        };

        this.close = function() {
            opened = false;
            self.row_el.fadeOut();
        };
    };

})(window, window.jQuery);



var Mailchimp = (function() {



})(window.JQuery);