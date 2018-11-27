/**
 * @module
 * @name Congressy Abstracts - URI
 * @namespace window.cgsy.abstracts.uri
 * @description Módulo que gerencia como os erros serão tratados.
 */
window.cgsy = window.cgsy || {};
window.cgsy.abstracts = window.cgsy.abstracts || {};

window.cgsy.URI_DEBUG_MODE = false;

//========================= URI MANAGER =======================================
(function (abstracts) {
    'use strict';

    abstracts.uri = {};

    /**
     * Gerenciamento de URL base para APIs.
     * @param {string} prod_base_url
     * @param {string} dev_base_url
     * @constructor
     */
    abstracts.uri.APIBaseUrl = function (prod_base_url, dev_base_url) {
        /**
         * Modo de desenvolvimento.
         * @type {boolean}
         */
        var DEV_MODE = window.cgsy.URI_DEBUG_MODE === true;

        /**
         * Token de autenticação.
         * @type {string|null}
         */
        this.auth_token = null;

        /**
         * Se modo é de produção. Se FALSE, o modo é de desenvolvimento.
         * @returns {boolean}
         */
        this.isProdMode = function() {
            return DEV_MODE === false;
        };

        /**
         * Seta modo como 'produção'
         */
        this.setProdMode = function() {
            DEV_MODE = false;
        };

        /**
         * Resgata URL base de produção.
         * @returns {string}
         */
        this.getProdBaseUrl = function() {
            return prod_base_url;
        };

        /**
         * Resgata URL base de desenvolvimento.
         * @returns {string}
         */
        this.getDevBaseUrl = function() {
            return dev_base_url;
        };

        /**
         * Resgata URL base dependente do modo.
         * @returns {string}
         */
        this.getBaseUrl = function() {
            if (DEV_MODE === true) {
                return dev_base_url;
            }
            return prod_base_url;
        };
    };

    /**
     * Gerenciador de URI
     * @param {abstracts.uri.APIBaseUrl} base_url_instance
     * @param {string} base_project_url
     * @constructor
     */
    abstracts.uri.URIManager = function (base_url_instance, base_project_url) {
        if (!base_url_instance instanceof abstracts.uri.APIBaseUrl) {
            console.error('URI not an instance of "abstracts.uri.APIBaseUrl".');
        }

        if (!base_project_url) {
            console.error('base_project_url not provided.');
        }

        /**
         * Seta token de autenticação.
         * @param {string} auth_token
         */
        this.setAuthToken = function(auth_token) {
            base_url_instance.auth_token = auth_token;
        };

        /**
         * Resgata token de autenticação.
         * @returns {string|null}
         */
        this.getAuthToken = function() {
            return base_url_instance.auth_token;
        };

        /**
         * Se modo o modo ativo é o de 'produção'
         * @returns {boolean}
         */
        this.isProdMode = function() {
            return base_url_instance.isProdMode();
        };

        /**
         * Seta modo como 'produção'
         */
        this.setProdMode = function() {
            base_url_instance.setProdMode();
        };

        /**
         * Resgata URI do Endpoint.
         * @param {string} endpoint
         * @returns {string}
         */
        this.getUri = function (endpoint) {
            var uri = _getBaseUrl();
                uri += '/' + _clearSlash(base_project_url);
                uri += '/' + _clearSlash(endpoint);

            return uri;
        };

        /**
         * Resgata URL de Base normalizada.
         * @returns {string}
         * @private
         */
        var _getBaseUrl = function () {
            var base_url = base_url_instance.getBaseUrl();

            if (base_url.substr(-1) === '/') {
                base_url = base_url.substr(0, base_url.length - 1)
            }

            return base_url;
        };

        /**
         * Normalizada barras de início e fim.
         * @param {string} string
         * @returns {string}
         * @private
         */
        var _clearSlash = function (string) {
            if (string && string.charAt(0) === '/') {
                string = string.substr(1, string.length);
            }

            return string;
        };
    };

})(window.cgsy.abstracts);
