/**
 * @module
 * @name Congressy Abstracts - Formulário de Modelo de Domínio.
 * @namespace window.cgsy.abstracts.form
 * @description Coleção de modelos e suas interações.
 * @depends
 *  - jQuery
 *  - window.cgsy.AjaxSender
 *  - window.cgsy.abstracts.dom
 *  - window.cgsy.abstracts.error
 *  - window.cgsy.abstracts.alerter
 *  - window.cgsy.abstracts.http
 *  - window.cgsy.abstracts.form.FieldMapper
 *  - window.cgsy.abstracts.form
 */
window.cgsy = window.cgsy || {};
window.cgsy.abstracts = window.cgsy.abstracts || {};
window.cgsy.abstracts.form = window.cgsy.abstracts.form || {};

//=============================== FORMS =======================================
(function ($, abstracts) {
    'use strict';

    /**
     * Formulário de modelo de domínio.
     * @param {abstracts.domain.Model} model_instance
     * @param {jQuery|string} form_el
     * @constructor
     */
    abstracts.form.ModelForm = function(model_instance, form_el) {
        abstracts.form.Form.call(this, form_el);
        var self = this;

        self.ignore('pk');

        /**
         * @type {abstracts.domain.Model}
         */
        this.model_instance = model_instance;

        /**
         * Engatilhado após salvar.
         * @type {Function}
         */
        this.afterSaveCallback = function(){};

        /**
         * @type {abstracts.form.FormErrorAlerter}
         */
        this.error_alerter = new abstracts.form.FormErrorAlerter(
            self.alerter_el,
            model_instance.error_handler
        );

        this.setAfterSaveCallback = function(callback) {
            if (typeof callback === 'function') {
                return;
            }
            self.afterSaveCallback = callback;
        };

        /**
         * Verifica se instância do modelo é válida.
         * @returns {boolean}
         */
        this.isValid = function() {
            return self.model_instance.isValid();
        };

        /**
         * Popula formulário a partir dos dados da instância do modelo de
         * domínio.
         */
        this.toForm = function() {
            if (!self.model_instance) {
                return;
            }

            self.populate(self.model_instance.toPlainObject());
        };

        /**
         * Popula a instância do modelo de domínio a partir dos valore do
         * formulário.
         */
        this.toModel = function() {
            if (!self.model_instance) {
                return;
            }

            var data  = self.getData();

            self.model_instance.getFieldNames().forEach(function(name) {
                var field = self.model_instance.getField(name);

                if (!data.hasOwnProperty(name)) {
                    switch (field.type) {
                        case 'boolean':
                            data[name] = false;
                            break;
                    }
                    return;
                }

                var value = data[name];

                switch (field.type) {
                    case 'integer':
                    case 'number':
                        var is_float = value % 1 !== 0;
                        value = (is_float) ? parseFloat(value) : parseInt(value);
                        break;
                    case 'float':
                        value = parseFloat(value);
                        break;
                    case 'boolean':
                        value = value === true || value === 'true' || value === 'on';
                        break;
                }

                data[name] = value;
            });

            self.model_instance.populate(data);
        };

        this.fetch = function() {
            return new Promise(function(resolve) {
                if (!self.model_instance.isFetchable()) {
                    self.error_alerter.notify();
                    resolve();
                    return;
                }

                self.model_instance.fetch().then(function() {
                    if (!self.isValid()) {
                        self.error_alerter.notify();
                        resolve();
                    } else {
                        self.toForm();
                        self.syncDataAndDom().then(function() {
                            resolve();
                        });
                    }
                });
            });
        };

        /**
         * Salva informações do formulário na instância do modelo de domínio
         * e, por sua vez, salva os dados do modelo no servidor.
         * @returns {Promise}
         */
        this.save = function() {
            return new Promise(function(resolve) {
                if (self.processing === true) {
                    resolve(self.getData());
                    return;
                }

                self.processing = true;
                self.syncDataAndDom().then(function() {
                    self.toModel();

                    self.model_instance.save().then(function() {
                        if (!self.isValid()) {
                            self.error_alerter.notify();
                        } else {
                            self.alerter.clear();
                            self.alerter.renderSuccess('Dados salvos com sucesso.');
                        }

                        self.enableSubmitButton();
                        self.processing = false;

                        if (self.save_and_remain === false) {
                            self.afterSaveCallback();
                        }

                        resolve(self.getData());
                    });
                });
            });
        };
    };
    abstracts.form.ModelForm.prototype = Object.create(abstracts.form.Form.prototype);
    abstracts.form.ModelForm.prototype.constructor = abstracts.form.ModelForm;

})(jQuery, window.cgsy.abstracts);