/**
 * @module
 * @name Congressy Abstracts - Coleção de Modelos
 * @namespace window.cgsy.abstracts.domain
 * @description Coleção de modelos e suas interações.
 * @depends
 *  - jQuery
 *  - window.cgsy.AjaxSender
 *  - window.cgsy.abstracts.error
 *  - window.cgsy.abstracts.http
 *  - window.cgsy.abstracts.domain
 */
window.cgsy = window.cgsy || {};
window.cgsy.abstracts = window.cgsy.abstracts || {};

(function (abstracts) {
    'use strict';

    /**
     * Coleção de instância de modelos de domínio
     * @constructor
     */
    abstracts.domain.Collection = function () {
        var self = this;

        /**
         * Lista de instâncias de modelos de domínio.
         * @type {Array}
         */
        this.items = [];

        /**
         * Classe do modelo de domínio
         * @type {abstracts.domain.Model}
         */
        this.model_class = undefined;

        /**
         * @type {abstracts.uri.URIManager}
         */
        this.uri_manager = null;

        /**
         * URI de busca via REST.
         * @type {string}
         */
        this.uri = null;

        /**
         * Gerenciador de erros.
         * @type {abstracts.error.Error}
         */
        this.error_handler = new abstracts.error.Error();

        /**
         * Cliente HTTP.
         * @type {abstracts.http.Client}
         */
        this.client = new abstracts.http.Client(self.error_handler);

        /**
         * Resgata gerenciador de URI.
         * @returns {abstracts.uri.URIManager}
         */
        this.getUriManager = function () {
            var uri_manager = self.uri_manager;
            if (!uri_manager) {
                console.error('<collection>.uri_manager not configured.');
            }
            return uri_manager;
        };

        /**
         * Resgata URI completo de busca via REST.
         * @returns {string}
         */
        this.getUri = function() {
            var uri_manager = self.getUriManager();
            if (!uri_manager) {
                return '';
            }

            var uri = this.uri;
            if (!uri) {
                console.error('<model>.uri not configured.');
                return '';
            }
            return uri_manager.getUri(uri);
        };

        /**
         * Cria instância de modelo de domínio de acordo com objeto com dados
         * informados.
         * @param {Object} data
         * @returns {abstracts.domain.Model|undefined}
         */
        this.create = function (data) {
            var pk_value = null;
            var pk_possibles = ['pk', 'id', 'uuid'];

            pk_possibles.forEach(function (pk) {
                if (data.hasOwnProperty(pk)) {
                    pk_value = data[pk];
                }
            });

            if (!pk_value) {
                console.error('PK não encontrado: ', data);
                return;
            }

            var model_instance = new this.model_class(pk_value);
                model_instance.populate(data);

            return model_instance;
        };

        /**
         * Se coleção é válida.
         * @returns {boolean}
         */
        this.isValid = function() {
            self.items.forEach(function(item) {
                if (!item.isValid()) {
                    if (item.error_handler.non_key_errors.length) {
                        item.error_handler.non_key_errors.forEach(function(msg) {
                            self.error_handler.setNonKeyError(msg);
                        });
                    }

                    if (Object.keys(item.error_handler.key_errors).length) {
                        Object.keys(item.error_handler.key_errors).forEach(function(name) {
                            self.error_handler.setKeyError(name, item.error_handler.key_errors[name]);
                        });
                    }
                }
            });

            var has_key_errors = Object.keys(self.error_handler.key_errors).length > 0;
            var has_errors = self.error_handler.non_key_errors.length > 0;
            return has_errors === false && has_key_errors === false;
        };

        /**
         * Remove instância de modelo de domínio da lista da coleção.
         * @param {abstracts.domain.Model} instance
         */
        this.remove = function (instance) {
            this._pre_remove();
            self.items = self.items.filter(function (item) {
                return item.pk !== instance.pk
            });
            this._post_remove();
        };

        /**
         * Adiciona instância de modelo de domínio à coleção.
         * @param {abstracts.domain.Model} instance
         */
        this.add = function (instance) {
            if (this.model_class === undefined) {
                console.error('<collection>.model_class not configured');
                return;
            }

            if (instance instanceof this.model_class && instance.isValid(false)) {
                this._pre_add();
                this.items.push(instance);
                this._post_add();
            }
        };

        /**
         * Busca dados do servidor via REST.
         * @returns {Promise}
         */
        this.fetch = function () {
            return new Promise(function (resolve, reject) {
                self.items = [];
                var uri = self.getUri();

                if (!uri) {
                    reject();
                    return;
                }

                if (!self.isValid()) {
                    reject();
                    return;
                }

                self.client.fetch(uri).then(function (result) {
                    if (!self.isValid()) {
                        reject();
                        return;
                    }

                    if (result.type === 'success') {
                        $.each(result.result, function (i, item) {
                            var instance = self.create(item);

                            if (!self.isValid()) {
                                reject();
                                return;
                            }

                            self.add(instance);
                        });
                    }
                    resolve(self.items);
                });
            });
        };

        this._pre_add = function() {};
        this._post_add = function() {};

        this._pre_remove = function() {};
        this._post_remove = function() {};
    };

})(window.cgsy.abstracts);
