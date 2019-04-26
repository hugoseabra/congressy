/**
 * @module
 * @name Congressy Abstracts - DOM
 * @namespace window.cgsy.abstracts.dom
 * @description Módulo de features relacionados a manipulação de DOM.
 * @depends:
 *  - jQuery
 */
window.cgsy = window.cgsy || {};
window.cgsy.abstracts = window.cgsy.abstracts || {};

//============================= DOM MAP =======================================
(function (abstracts) {
    'use strict';

    abstracts.dom = {};

    /**
     * Gerencia mapa de elementos jQuery e agiliza o resgate do elemento por uma
     * chave especificada e facilita a inserção de valor no elemento.
     *
     * @constructor
     */
    abstracts.dom.DOMManager = function () {
        var self = this;

        /**
         * @type {Object}
         */
        this.domElements = {};

        /**
         * Modo estrito não permite seta, resgatar ou inserir valor em elementos
         * que não tenha as suas chaves previamente cadastradas.
         * @type {boolean}
         */
        var strictKeys = false;

        /**
         * Seta como estrito
         */
        this.setAsStrictKeys = function () {
            strictKeys = true;
        };

        /**
         * Seta como não-estrito
         */
        this.setAsNotStrictKeys = function () {
            strictKeys = false;
        };

        /**
         * Seta um elemento jQuery atrelada a uma chave.
         * @param {string} key
         * @param {jQuery} element - Element jQuery
         */
        this.setElement = function (key, element) {
            if (!element instanceof jQuery) {
                console.error('Element "'+key+'" não é um instância de jQuery.');
                return;
            }

            if (element.length === 0) {
                console.warn('Nenhum elemento DOM encontrado para ' + key);
                console.log(element);
                return;
            }

            self.domElements[key] = element;
        };

        /**
         * Resgata um elemento jQuery atrealada à chave informada.
         * @param {string} key
         * @returns {jQuery|undefined}
         */
        this.getEl = function (key) {
            if (!this.domElements.hasOwnProperty(key)) {
                if (strictKeys === true) {
                    var msg = 'Key "' + key + '" was not defined';
                    console.error(msg);
                    alert(msg);
                }
                return null;
            }
            var el = self.domElements[key];
            if (!el || el.length === 0) {
                return undefined;
            }

            return el;
        };

        /**
         * Insere um valor no elemento jQuery, pondendo ser como HTML ou não,
         * e podendo elemento ser de um formulário ou não.
         * @param {string} key
         * @param {*} value
         * @param {boolean|*} as_html
         */
        this.insertValue = function (key, value, as_html) {
            as_html = as_html === true;
            value = value && value instanceof Array ? value : [value];

            // Forces values as string.
            value = value.map(function(v) {
                if (!v) {
                    return '';
                }
                return (typeof v === 'string') ? v : v.toString();
            });

            var element = this.getEl(key);

            if (!element || element.length === 0) {
                return;
            }


            var form_fields = ['INPUT', 'TEXTAREA', 'SELECT'];
            var tag_name = element.get(0).tagName;

            if (!form_fields.includes(tag_name)) {
                if (as_html) {
                    element.html(value);
                } else {
                    element.text(value);
                }
                return
            }

            var checkable = ['radio', 'checkbox'];
            var type = element.attr('type');

            if (checkable.includes(type)) {

                var normalizeCheckable = function(checkable_el) {
                    var is_checked = value.includes(checkable_el.val());

                    if (type === 'checkbox') {
                        if (is_checked && !checkable_el.prop('checked') || !is_checked && checkable_el.prop('checked')) {
                            checkable_el.trigger('click');
                        }
                    } else if (type === 'radio') {
                        if (typeof checkable_el.iCheck !== 'undefined') {
                            if (is_checked) {
                                checkable_el.iCheck('check');
                            } else {
                                checkable_el.iCheck('uncheck');
                            }
                        } else {
                            checkable_el.prop('checked', is_checked);
                        }
                    }
                };

                if (element.length > 1) {
                    $.each(element, function() {
                        var el = $(this);
                        normalizeCheckable(el);
                    });
                    return;
                }

                normalizeCheckable(element);
                return;
            }
            element.val(value);
        };
    };

    /**
     * Componente a ser gerenciado em tela e que possui elementos jQuery
     * mapeados.
     * @constructor
     */
    abstracts.dom.Component = function () {
        var self = this;

        /**
         * @type {abstracts.dom.DOMManager}
         */
        this.dom_manager = new abstracts.dom.DOMManager();

        /**
         * Seta como estrito
         */
        this.strict = function() {
            self.dom_manager.setAsStrictKeys();
        };

        /**
         * Seta um elemento jQuery atrelada a uma chave.
         * @param {string} key
         * @param {object} element - Element jQuery
         */
        this.setEl = function (key, element) {
            self.dom_manager.domElements[key] = $(element);
        };

        /**
         * Resgata um elemento jQuery atrealada à chave informada.
         * @param {string} key
         * @returns {jQuery}
         */
        this.getEl = function(key) {
            return self.dom_manager.getEl(key);
        };

        /**
         * Insere um valor no elemento jQuery, pondendo ser como HTML ou não,
         * e podendo elemento ser de um formulário ou não.
         * @param {string} key
         * @param {*} value
         * @param {boolean} as_html
         */
        this.insertValue = function(key, value, as_html) {
            self.dom_manager.insertValue(key, value, as_html);
        };

        /**
         * Renderiza componente.
         */
        this.render = function() {
            console.warn('<component>.render() not implemented.');
        };
    };

})(window.cgsy.abstracts);
