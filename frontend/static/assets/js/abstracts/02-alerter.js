/**
 * @module
 * @name Congressy Abstracts - Alerter
 * @namespace window.cgsy.abstracts.alerter
 * @description Módulo que gerencia notificações por alerta.
 * @depends
 *  - jQuery
 *  - window.cgsy.abstracts.error
 */
window.cgsy = window.cgsy || {};
window.cgsy.abstracts = window.cgsy.abstracts || {};

(function ($, abstracts) {
    "use strict";

    abstracts.alerter = {};

    /**
     * Alerta usuário conforme padrões de Boostrap
     * @param {jQuery|string} parent_el - elemento jQuery
     * @constructor
     */
    abstracts.alerter.Alerter = function(parent_el) {
        var self = this;

        /**
         * @type {jQuery}
         */
        parent_el = $(parent_el);

        /**
         * Objeto pai das mensagens exibidas.
         * @type {jQuery|null}
         */
        var alert_parent_el = null;

        /**
         * Último elemento jQuery criado.
         * @type {jQuery|null}
         */
        var alert_el = null;

        /**
         * Se TRUE, o último objeto criado será substituído pelo próximo.
         * @type {boolean}
         */
        this.replace_existing = false;

        /**
         * Ativar substituição de última mensagem.
         */
        this.replaceExisting = function() {
            self.replace_existing = true;
        };

        /**
         * Limpa todas as mensagens já criadas.
         */
        this.clear = function() {
            if (alert_parent_el) {
                alert_parent_el.empty();
            }
            alert_el = null;

        };

        /**
         * Renderiza elemento de alerta.
         * @param {string} type
         * @param {string} msg
         */
        this.render = function(type, msg) {
            if (alert_el === null) {
                getAlertParentEl().append(self.createAlertEl(type, msg));
                return;
            }

            self.createAlertEl(type, msg);
            if (self.replace_existing === false) {
                getAlertParentEl().append(alert_el);
            }
        };

        /**
         * Renderiza alerta do tipo 'success'
         * @param {string} msg
         */
        this.renderSuccess = function(msg) {
            self.render('success', msg);
        };

        /**
         * Renderiza alerta do tipo 'warning'
         * @param {string} msg
         */
        this.renderWarning = function(msg) {
            self.render('warning', msg);
        };

        this.renderInfo = function(msg) {
            self.render('info', msg);
        };

        /**
         * Renderiza alerta do tipo 'error'
         * @param {string} msg
         */
        this.renderError = function(msg) {
            self.render('error', msg);
        };

        /**
         * Renderiza alerta do tipo 'danger'
         * @param {string} msg
         */
        this.renderDanger = self.renderError;

        /**
         * Cria novo elemento de alerta.
         * @param {string} type
         * @param {string} msg
         * @returns {jQuery}
         */
        this.createAlertEl = function(type, msg) {
            var exists = alert_el !== null;
            var create_el = self.replace_existing === false || exists === false;

            if (create_el) {
                alert_el = $('<div>')
                    .css('margin-bottom', '3px')
                    .addClass('alert alert-dismissible')
                    .attr('role', 'alert');
            } else {
                alert_el.removeClass('alert-warning alert-success alert-info alert-danger');
            }

            switch (type) {
                case 'warning':
                    alert_el.addClass('alert-warning');
                    break;
                case 'success':
                    alert_el.addClass('alert-success');
                    break;
                case 'info':
                    alert_el.addClass('alert-info');
                    break;
                case 'danger':
                case 'error':
                default:
                    alert_el.addClass('alert-danger');
            }

            if (create_el) {
                alert_el.append(
                    $('<button>').attr({
                        'class': 'close',
                        'data-dismiss': 'alert',
                        'aria-label': 'Close'
                    }).html(
                        $('<span>').attr('aria-hidden', 'true').html('&times;')
                    )
                );
                alert_el.append($('<span>').addClass('alert-content'));
            }

            alert_el.find('.alert-content').html(msg);

            return alert_el;
        };

        /**
         * Resgata (criando se não houver) elemento jQuery pai de todas os alertas
         * a serem engatilhadas.
         * @returns {jQuery}
         */
        var getAlertParentEl = function() {
            if (!alert_parent_el) {
                alert_parent_el = parent_el.find('.main-alerter');

                if (alert_parent_el.length === 0) {
                    alert_parent_el = $('<div>')
                        .addClass('main-alerter');

                    parent_el.prepend(alert_parent_el);
                }
            }
            return alert_parent_el;
        };
    };

    /**
     * Alerta de erros.
     * @param {jQuery|string} parent_el
     * @param {abstracts.error.Error} error_handler
     * @constructor
     */
    abstracts.alerter.ErrorAlerter = function(parent_el, error_handler) {
        var self = this;

        /**
         * @type {jQuery}
         */
        parent_el = $(parent_el);

        /**
         * @type {abstracts.alerter.Alerter}
         */
        this.alerter = new abstracts.alerter.Alerter(parent_el);

        /**
         * Limpa alertas.
         */
        this.clear = function() {
            self.alerter.clear();
        };

        /**
         * Engatilha notificação.
         */
        this.notify = function() {
            self.clear();

            var alerts = [];
            var type = 'error';

            var msg;
            var num_key_errors = Object.keys(error_handler.key_errors).length;

            error_handler.non_key_errors.forEach(function(error_msg) {
                msg = '<div>' + error_msg + '</div>';

                if (num_key_errors) {
                    msg += '<hr class="hr" />';
                }

                alerts.push(msg);
            });

            var counter = 1;
            $.each(error_handler.key_errors, function(name, errors_list) {
                msg = '<div style="margin-bottom: 4px">';
                msg += '<strong>' + name + ':</strong> ';
                msg += '<ul>';

                errors_list.forEach(function(error_msg) {
                    msg += '<li>' + error_msg + '</li>';
                });
                msg += '</ul>';
                msg += '</div>';

                if (counter < num_key_errors) {
                    msg += '<hr class="hr" />';
                }

                alerts.push(msg);
                counter++;
            });

            self.alerter.render(type, alerts.join(''));
        };
    };

})(jQuery, window.cgsy.abstracts);