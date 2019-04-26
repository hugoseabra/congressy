/**
 * @module
 * @name Congressy Abstracts - Messenger
 * @namespace window.cgsy.abstracts.messenger
 * @description Módulo que gerencia notificações por mensagens de pop-up.
 * @depends
 *  - window.cgsy.messenger
 */
window.cgsy = window.cgsy || {};
window.cgsy.abstracts = window.cgsy.abstracts || {};

(function ($, abstracts, messenger) {
    "use strict";

    abstracts.messenger = {};

    /**
     * Mensageiro que notifica usuário por pop-up.
     * @param {string|undefined} id
     * @constructor
     */
    abstracts.messenger.Messenger = function(id) {
        var self = this;

        /**
         * Objeto da última notificação criada.
         * @type {object}
         */
        var messenger_instance = null;

        /**
         * ID da mensagem que, ao ser informda, a notificação atrelada é
         * substituída pela próxima engatilhada.
         * @type {string}
         */
        this.id = id;

        /**
         * Engatilha notificação usuário.
         * @param {string} type
         * @param {string} msg
         */
        this.notify = function(type, msg) {
            messenger_instance = messenger.triggerEvent(type, msg, self.id);
        };

        /**
         * Engatilha notificação do tipo 'success'
         * @param {string} msg
         */
        this.notifySuccess = function(msg) {
            self.notify('success', msg);
        };

        /**
         * Engatilha notificação do tipo 'warning'
         * @param {string} msg
         */
        this.notifyWarning = function(msg) {
            self.notify('warning', msg);
        };

        this.notifyInfo = function(msg) {
            self.notify('info', msg);
        };

        /**
         * Engatilha notificação do tipo 'error'
         * @param {string} msg
         */
        this.notifyError = function(msg) {
            self.notify('error', msg);
        };

        /**
         * Fecha notificação existente.
         */
        this.close = function() {
            if (!messenger_instance) {
                return;
            }
            messenger_instance.hide();
        };

        /**
         * Fecha todas as notificações engatilhadas, independente se é a última
         * ou não.
         */
        this.closeAll = function() {
            messenger.closeAll();
        };

        /**
         * Engatilha notificação como 'loader' pedindo usuário para aguardar.
         */
        this.notifyLoader = function() {
            messenger_instance = messenger.triggerLoader('aguarde...', self.id);
        };

        /**
         * Engatilha notificação de retentativa de alguma operação previamente
         * informada em handler.
         * @param {function} handler
         * @param {string} msg
         */
        this.retry = function(handler, msg) {
            messenger.retry(messenger_instance, handler, msg);
        };
    };

})(jQuery, window.cgsy.abstracts, window.cgsy.messenger);