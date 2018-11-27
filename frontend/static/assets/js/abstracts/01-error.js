/**
 * @module
 * @name Congressy Abstracts - Error
 * @namespace window.cgsy.abstracts.error
 * @description Módulo que gerencia como os erros serão tretados.
 */
window.cgsy = window.cgsy || {};
window.cgsy.abstracts = window.cgsy.abstracts || {};

(function (abstracts) {
    "use strict";

    abstracts.error = {};

    /**
     * Mapa de erros com e sem chaves atreladas.
     * @constructor
     */
    abstracts.error.Error = function() {
        var self = this;

        /**
         * Erros atrelados a uma chave.
         * @type {{string: string}}
         */
        this.key_errors = {};

        /**
         * Erros sem chave atrelada.
         * @type {Array}
         */
        this.non_key_errors = [];

        /**
         * Reseta os erros já inseridos.
         */
        this.reset = function() {
            this.key_errors = {};
            this.non_key_errors = [];
        };

        /**
         * Seta um erro não atrelado a uma chave.
         * @param {string} msg
         */
        this.setNonKeyError = function(msg) {
            if (self.non_key_errors.includes(msg)) {
                return;
            }
            self.non_key_errors.push(msg);
            console.warn(msg);
        };

        /**
         *
         * @param {string} field_name
         * @param {string} msg
         */
        this.setKeyError = function(field_name, msg) {
            if (!self.key_errors.hasOwnProperty(field_name)) {
                self.key_errors[field_name] = [];
            }

            if (self.key_errors[field_name].includes(msg)) {
                return;
            }

            self.key_errors[field_name].push(msg);
            console.warn(field_name, msg);
        };
    };

})(window.cgsy.abstracts);