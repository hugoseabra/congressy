window.cgsy = window.cgsy || {};
window.cgsy.abstracts = window.cgsy.abstracts || {};

(function ($, abstracts) {
    'use strict';

    abstracts.modal = {};

    /**
     * Componente de modal.
     * @param {jQuery|string} model_el
     * @constructor
     */
    abstracts.modal.Modal = function (model_el) {
        abstracts.dom.Component.call(this);
        var self = this;
        self.strict();

        /**
         * Element principal.
         * @type {jQuery}
         */
        this.modal_el = $(model_el);

        self.dom_manager.domElements = {
            'loader': null
        };

        /**
         * Resgata elemento de loader do modal.
         * @returns {jQuery|*}
         */
        this.getLoaderEl = function() {
            return self.getEl('loader');
        };

        /**
         * Resgata elemento jQuery do cabeçalho do modal.
         * @returns {jQuery}
         */
        this.getHeaderEl = function() {
            return $('.modal-header', self.modal_el);
        };

        /**
         * Resgata elemento jQuery do título do modal.
         * @returns {jQuery}
         */
        this.getTitleEl = function() {
            return $('.modal-title', self.modal_el);
        };

        /**
         * Resgata elemento jQuery do corpo do modal.
         * @returns {jQuery}
         */
        this.getBodyEl = function() {
            return $('.modal-body', self.modal_el);
        };

        /**
         * Resgata elemento jQuery do rodapé do modal.
         * @returns {jQuery}
         */
        this.getFooterEl = function() {
            return $('.modal-footer', self.modal_el);
        };

        /**
         * Prepara modal para uso, criando os comportamentos devidos.
         */
        this.prepareModalEl = function () {
            self.modal_el.off('show.bs.modal');
            self.modal_el.on('show.bs.modal', function () {
                self.postModalLoad();
            });
        };

        /**
         * Carrega elemento na tela.
         * @param {jQuery} element
         */
        this.loadElement = function(element) {
            var body_el = self.getBodyEl();
            if (!body_el || body_el.length === 0) {
                console.warn('Elemento corpo do modal não informado.');
                return;
            }
            body_el.html(element);
            $(element).show();
        };

        /**
         * Seta o título do modal.
         * @param {jQuery|string} title
         */
        this.setTitle = function(title) {
            var title_el = self.getTitleEl();
            if (!title_el || title_el.length === 0) {
                console.warn('Elemento de título do modal não informado.');
                return;
            }
            title_el.html(title);
        };

        this.open = function () {
            self.prepareModalEl();
            self.preModalLoad();
            self.modal_el.modal();
        };

        this.close = function () {
            self.prepareModalEl();
            self.modal_el.modal('hide');
        };

        this.setAsLoading = function () {
            var loader = self.getLoaderEl();
            var body_el = self.getBodyEl();

            if (!loader || !body_el) {
                return;
            }

            if (loader.length === 0 || body_el.length === 0) {
                return;
            }

            loader.show();
            body_el.hide();

            var header_el = self.getHeaderEl();
            if (header_el && header_el.length){
                header_el.hide();
            }

            var footer_el = self.getFooterEl();
            if (footer_el && footer_el.length){
                footer_el.hide();
            }
        };

        this.setAsReady = function () {
            var loader = self.getLoaderEl();
            var body_el = self.getBodyEl();

            if (!loader || !body_el) {
                return;
            }

            if (loader.length === 0 || body_el.length === 0) {
                return;
            }

            loader.fadeOut(function () {
                body_el.fadeIn();

                var header_el = self.getHeaderEl();
                if (header_el && header_el.length){
                    header_el.fadeIn();
                }

                var footer_el = self.getFooterEl();
                if (footer_el && footer_el.length){
                    footer_el.fadeIn();
                }
            });
        };

        this.preModalLoad = function () {};
        this.postModalLoad = function () {};
    };
    abstracts.modal.Modal.prototype = Object.create(abstracts.dom.Component.prototype);
    abstracts.modal.Modal.prototype.constructor = abstracts.modal.Modal;

    /**
     * Modal de formulário de modelo de domínio.
     * @param {jQuery|string} model_el
     * @param {abstracts.form.ModelForm} form
     * @constructor
     */
    abstracts.modal.Form = function (model_el, form) {
        abstracts.modal.Modal.call(this, model_el);
        var self = this;

        /**
         * Classe do formulário a ser carregado.
         * @type {abstracts.form.ModelForm}
         */
        this.form = form;
        this.form_el = this.form.form_el;

        this.focus_field = null;
        this.title_for_new_model = 'Nova';
        this.title_for_existing_model = 'Editando';

        this.prepareModalEl = function () {
            self.modal_el.off('show.bs.modal');
            self.modal_el.on('show.bs.modal', function () {
                self.postModalLoad();
                window.setTimeout(function () {
                    var f_focus = self.form_el.find('input[name=' + self.focus_field + ']');
                    if (f_focus.length > 0) {
                        f_focus.focus();
                    }
                }, 200);
            });
        };

        window.setTimeout(function() {
            self.loadElement(self.form_el);

            var title;
            var model_instance = self.form.model_instance;

            if (model_instance.isNew() === false) {
                if (model_instance.verbose_name) {
                    title = self.title_for_existing_model+ ' ' + model_instance.verbose_name;
                }
            } else {
                if (model_instance.verbose_name) {
                    title = self.title_for_new_model+ ' ' + model_instance.verbose_name;
                }
            }

            if (!title) {
                title = model_instance.verbose_name;
            }

            if (title.length > 50) {
                title = title.substr(0, 50) + ' ...';
            }
            self.setTitle(title);
        }, 350);
    };
    abstracts.modal.Form.prototype = Object.create(abstracts.modal.Modal.prototype);
    abstracts.modal.Form.prototype.constructor = abstracts.modal.Form;

    abstracts.modal.Delete = function (model_instance) {
        abstracts.modal.LoadableBaseModal.call(this);

        if (!model_instance instanceof abstracts.domain.Model) {
            console.error('model informado não é uma instância de abstracts.domain.Model');
        }

        var self = this;
        var modal = null;

        this.model_instance = model_instance;
        this.messenger_id = 'audience-category';
        this.detail_name_field = 'name';
        this.message = 'Tem certeza que deseja remover esta entidade de ' + model_instance.verbose_name.toUpperCase() + '?';

        this.dom_manager.domElements['title'] = null;
        this.dom_manager.domElements['message_field'] = null;
        this.dom_manager.domElements['details_field'] = null;
        this.dom_manager.domElements['confirmation_button'] = null;
        this.dom_manager.domElements['close_button'] = null;

        var beforeDeleteCallback = function () {
        };
        var afterDeleteCallback = function () {
        };

        this.setBeforeDeleteCallback = function (callback) {
            if (typeof callback !== 'function') {
                return;
            }
            beforeDeleteCallback = callback;
        };

        this.setAfterDeleteCallback = function (callback) {
            if (typeof callback !== 'function') {
                return;
            }
            afterDeleteCallback = callback;
        };

        this.fetch = function () {
            self.setAsLoading();
            self.clearMessages();
            self.triggerMessengerLoader();

            model_instance.fetch().then(function () {
                if (model_instance.is_valid()) {
                    self.sync();
                    self.setAsReady();
                } else {
                    var status_code = model_instance.error_status;
                    if (status_code === 0 || status_code >= 500) {
                        self.retryRequest(
                            self.fetch,
                            model_instance.non_field_errors.join("\n"),
                            self.messenger_instance
                        )
                    } else {
                        self.showErrorMessenger(
                            model_instance.non_field_errors.join("\n"),
                            self.messenger_instance
                        );
                        self.close();
                    }
                }
            });
        };

        this.open = function (fetch) {
            fetch = fetch === true;

            modal = self.getModalElement();
            this.pre_modal_load();
            self.sync();
            modal.modal();

            if (fetch === true) {
                self.fetch();
            }
        };

        this.close = function () {
            modal.modal('hide');
        };

        this.delete = function () {
            beforeDeleteCallback();
            self.clearMessages();
            self.triggerMessengerLoader();

            model_instance.delete().then(function () {
                if (model_instance.is_valid()) {
                    afterDeleteCallback();
                    self.showSuccessMessenger('Excluído com sucesso', self.messenger_instance);
                } else {
                    var status_code = model_instance.error_status;
                    if (status_code === 0 || status_code >= 500) {
                        self.retryRequest(
                            self.delete,
                            model_instance.non_field_errors.join("\n"),
                            self.messenger_instance
                        );
                    } else {
                        self.close();
                        self.showErrorMessenger(
                            model_instance.non_field_errors.join("\n"),
                            self.messenger_instance
                        );
                    }
                }
            });
        };

        this.sync = function () {
            if (!model_instance.pk) {
                alert('Impossível excluir uma entidade sem identificador.');
                return;
            }

            // Verifica se o campo para exibir o detalhe do nome existe no model.
            if (!model_instance.hasField(self.detail_name_field)) {
                console.error(
                    'Campo "' + self.detail_name_field + '" não existe no model informado.'
                );
            }

            var close_button = self.getEl('close_button');
            close_button.off('click');
            close_button.on('click', function (e) {
                e.preventDefault();
                self.close();
            });

            var confirmation_button = self.getEl('confirmation_button');
            confirmation_button.off('click');
            confirmation_button.on('click', function (e) {
                e.preventDefault();
                self.delete();
            });

            var name = model_instance.getValue(self.detail_name_field);
            if (!name) {
                name = 'UNKNONW';
            }

            var title = 'Exclusão de ' + name;
            if (title.length > 50) {
                title = title.substr(0, 50) + ' ...';
            }

            var title_el = $('model-title', self.model_el);
            if (title_el && title_el.length) {
                title_el.text(title.toUpperCase());
            }

            self.getEl('message_field').text(self.message);
            self.getEl('details_field').text(
                name + ' (#ID: ' + model_instance.getValue('pk') + ')'
            );
        };
    };

})(jQuery, window.cgsy.abstracts, window.cgsy.messenger);
