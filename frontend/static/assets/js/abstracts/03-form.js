/**
 * @module
 * @name Congressy Abstracts - FORM
 * @namespace window.cgsy.abstracts.form
 * @description Gerenciamento de Formulário e erros de formulário.
 * @depends
 *  - jQuery
 *  - window.cgsy.abstracts.dom
 *  - window.cgsy.abstracts.error
 *  - window.cgsy.abstracts.alerter
 *  - window.cgsy.abstracts.form.FieldMapper
 */
window.cgsy = window.cgsy || {};
window.cgsy.abstracts = window.cgsy.abstracts || {};
window.cgsy.abstracts.form = window.cgsy.abstracts.form || {};

//=============================== FORMS =======================================
(function ($, abstracts) {
    'use strict';

    /**
     * Formulário.
     * @param {jQuery|string} form_el
     * @constructor
     */
    abstracts.form.Form = function(form_el) {
        abstracts.dom.Component.call(this);
        var self = this;

        self.strict();
        self.dom_manager.domElements['button'] = null;
        self.dom_manager.domElements['close-after-save-switch'] = null;

        /**
         * Flag para evitar processos duplicados.
         * @type {boolean}
         */
        this.processing = false;

        /**
         * Engatilhado após salvar se 'save_and_remain' for FALSE.
         * @type {Function}
         */
        this.afterSaveCallback = function() {};

        /**
         * Se FALSE, após salvar, afterSaveCallback é engatilhado.
         * @type {boolean}
         */
        this.save_and_remain = false;

        /**
         * Texto a ser exibido no botão de salvar.
         * @type {string}
         */
        this.button_text = 'Salvar';

        /**
         * Mensagem de sucesso após salvar.
         * @type {string}
         */
        this.success_message = 'Dados salvos com sucesso.';

        /**
         * Element jQurey do formulário.
         * @type {jQuery}
         */
        this.form_el = $(form_el);

        this.alerter_el = $('.messages', self.form_el);
        this.alerter_el = (self.alerter_el.length) ? self.alerter_el : self.form_el;

        this.alerter = new abstracts.alerter.Alerter(self.alerter_el);

        /**
         * Mapeamento de campos.
         * @type {abstracts.form.FieldMapper}
         */
        this.fields_mapper = new abstracts.form.FieldMapper(self.form_el);

        this.preSaveCallbacks = [];
        this.postSaveCallbacks = [];

        /**
         * Ignora campo informado.
         * @param {string} field_name
         * @param {boolean|undefined} warn
         */
        this.ignore = function(field_name, warn) {
            _init();
            self.fields_mapper.ignore(field_name, warn);
        };

        this.strictModeOn = function() {
            self.fields_mapper.enableStrictMode();
        };

        this.strictModeOff = function() {
            self.fields_mapper.disableStrictMode();
        };

        /**
         * Sincroniza informações do formulário para a instância e da instância
         * para o formulário.
         */
        this.syncDataAndDom = function() {
            _init();
            return self.fields_mapper.syncDataAndDom();
        };

        /**
         * Resgata dados do formulário: chave -> valor
         * @returns {Object}
         */
        this.getData = function() {
            _init();
            return self.fields_mapper.getData();
        };

        /**
         * Limpa capos do formulário.
         */
        this.clear = function() {
            self.fields_mapper.clear();
        };

        /**
         * Resgata valor do campo de acordo com o nome do campo.
         * @param {string} name
         * @returns {string|Array|boolean|number|*}
         */
        this.get = function(name) {
            return self.fields_mapper.get(name);
        };

        /**
         * Seta valor em campo através do nome do campo.
         * @param {string} name
         * @param {string} value
         */
        this.set = function(name, value) {
            return self.fields_mapper.set(name, value);
        };

        /**
         * Preenche os campos do formulário e dados da instância.
         * @param {Object} data
         */
        this.populate = function(data) {
            _init();
            this.fields_mapper.populate(data);
        };

        /**
         * Desabilita botão de sumissão.
         */
        this.disableSubmitButton = function() {
            var button = self.getEl('button');
            if (button) {
                button.attr('disabled', '').text('aguarde ...');
            }
        };

        /**
         * Habilita botão de submissão
         */
        this.enableSubmitButton = function() {
            var button = self.getEl('button');
            if (button) {
                button.removeAttr('disabled');
                button.text(self.button_text);
            }
        };

        this.save = function() {
            // VERIFICAR SUPORTE A USAR ESTE SWITCH COMO OPCIONAL.
            // var remain_switch = self.getEl('close-after-save-switch');
            // if (remain_switch && remain_switch.length) {
            //     self.save_and_remain = remain_switch.prop('checked') === false;
            // }

            return new Promise(function(resolve, reject) {
                if (self.processing === true) {
                    return reject('Ainda processando...');
                }

                self.processing = true;

                self.syncDataAndDom().then(function() {

                    self.alerter.clear();

                    self.preSave();
                    self.preSaveCallbacks.forEach(function(callback) {
                        callback();
                    });

                    self.saveHandler().then(function() {
                        self.save_and_remain = false;
                        self.processing = false;
                        self.enableSubmitButton();

                        self.alerter.renderSuccess(self.success_message);

                        self.postSave();
                        self.postSaveCallbacks.forEach(function(callback) {
                            callback();
                        });

                        resolve(self.getData());

                    }, function(reason) {
                        reject(reason);
                    });

                }, function(reason) {
                    self.alerter.clear();
                    self.save_and_remain = false;
                    self.processing = false;
                    self.enableSubmitButton();

                    reject(reason);
                });
            });
        };

        this.preSave = function() {};
        this.postSave = function() {};

        this.addPreSaveCallback = function(callback) {
            if (typeof callback !== 'function') {
                return;
            }

            self.preSaveCallbacks.push(callback);
        };

        this.addPostSaveCallback = function(callback) {
            if (typeof callback !== 'function') {
                return;
            }

            self.postSaveCallbacks.push(callback);
        };

        /**
         * Callback para tratar da estratégia de salvar.
         * @returns {Promise}
         */
        this.saveHandler = function() {
            return new Promise(function(resolve, reject) {
                console.warn('<form>.saveHandler() not implemented.');
                resolve();
            });
        };

        var _initialized = false;
        var _init = function() {
            var button = self.getEl('button');
            if (button) {
                self.enableSubmitButton();
                button.unbind('click');
                button.on('click', function(e) {
                    e.preventDefault();
                    self.disableSubmitButton();
                    self.save();
                });
            }



            if (_initialized) {
                return;
            }

            self.form_el.append($('<button>').attr('type', 'submit').css('hide'));
            self.form_el.unbind('submit');
            self.form_el.on('submit', function(e) {
                e.preventDefault();
                self.disableSubmitButton();
                self.save();
            });

            _initialized = true;
        };

        window.setTimeout(function () {
            _init()
        }, 10);
    };
    abstracts.form.Form.prototype = Object.create(abstracts.dom.Component.prototype);
    abstracts.form.Form.prototype.constructor = abstracts.form.Form;

    /**
     * @param {jQuery} form_el
     * @param {abstracts.error.Error} error_handler
     * @param {abstracts.domain.ModelError} error_handler
     * @constructor
     */
    abstracts.form.FormErrorAlerter = function(form_el, error_handler) {
        var self = this;

        this.main_message = '<strong>O formulário possui errors:</strong>';
        this.alerter = new abstracts.alerter.ErrorAlerter(form_el, error_handler);

        this.clear = function() {
            self.alerter.clear();
            $('.has-error', form_el).remove();
        };

        this.notify = function() {
            self.clear();

            if (Object.keys(error_handler.key_errors).length > 0 && !error_handler.non_key_errors.includes(self.main_message)) {
                error_handler.non_key_errors.unshift('<strong>O formulário possui errors:</strong>');
            }

            var processed_names = [];
            $.each(error_handler.key_errors, function(name, errors_list) {
                if (processed_names.includes(name)) {
                    return;
                }
                processed_names.push(name);

                var field_el = $('[name='+name+']', form_el);
                if (field_el.length === 0) {
                    return;
                }

                var field_parent_el;
                if (field_el.length > 1) {
                    field_el = $(field_el.get(0));
                }
                field_parent_el = field_el.closest('.form-group');

                errors_list.forEach(function(msg) {
                    field_parent_el.append(self.getErrorEl(field_parent_el, msg));
                });

                delete error_handler.key_errors[name];
            });

            self.alerter.notify();
        };

        this.getErrorEl = function(field_parent_el, msg) {
            var error_el = field_parent_el.find('.has-error');
            if (!error_el.length) {
                error_el = $('<div class="has-error">').css('color', 'darkred');
            }
            error_el.html(msg);

            return error_el;
        };
    };

})(jQuery, window.cgsy.abstracts);