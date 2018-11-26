/**
 * @module
 * @name Congressy Abstracts - HTTP
 * @namespace window.cgsy.abstracts.form
 * @description Cliente HTTP para requisições REST.
 * @depends
 *  - jQuery
 *  - window.cgsy.AjaxSender
 *  - window.cgsy.abstracts.error
 */
window.cgsy = window.cgsy || {};
window.cgsy.abstracts = window.cgsy.abstracts || {};

(function (abstracts, AjaxSender) {
    "use strict";

    abstracts.http = {};

    abstracts.http.Client = function(error_handler) {
        var self = this;

        this.error_handler = error_handler;
        var error_msg;

        this.http_status = null;
        this.auth_token = null;

        if (self.error_handler) {
            ['setNonKeyError', 'setKeyError'].forEach(function(method) {
                if (!self.error_handler.hasOwnProperty(method) || typeof self.error_handler[method] !== 'function' ) {
                    error_msg = 'Error handler não é possui "'+method+'".';
                    alert(error_msg);
                    console.error(error_msg);
                }
            });
        }

        this.fetch = function(uri) {
            return new Promise(function (resolve) {
                self._getClient(uri, resolve).get();
            });
        };

        this.create = function(uri, data) {
            return new Promise(function (resolve) {
                self._getClient(uri, resolve).post(data);
            });
        };

        this.update = function(uri, data) {
            return new Promise(function (resolve) {
                self._getClient(uri, resolve).put(data);
            });
        };

        this.patch = function(uri, data) {
            return new Promise(function (resolve) {
                self._getClient(uri, resolve).patch(data);
            });
        };

        this.delete = function(uri) {
            return new Promise(function (resolve) {
                self._getClient(uri, resolve).delete();
            });
        };

        this._getClient = function (uri, resolve) {
            self.error_handler.reset();

            var client = new AjaxSender(uri);
                client.auth_token = self.auth_token;
                client.setSuccessCallback(self._getSuccessCallback(resolve));
                client.setFailCallback(self._getFailCallback(uri, resolve));

            return client;
        };

        this._getSuccessCallback = function(resolve) {
            return function (data, status_text, response) {
                self.http_status = response.status;

                if (data.hasOwnProperty('result')) {
                    data = data.result;
                } else if (data.hasOwnProperty('results')) {
                    data = data.results;
                } else if (data.hasOwnProperty('responseJSON')) {

                } else if (!data) {
                    self.error_handler.setNonKeyError(
                        'Requisição bem sucedida, porém com resposta' +
                        ' desconhecida na requisição.'
                    );
                }

                resolve({'type': 'success', 'status': self.http_status, 'result': data});
            };
        };

        this._getFailCallback = function(uri, resolve) {
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

})(window.cgsy.abstracts, window.cgsy.AjaxSender);