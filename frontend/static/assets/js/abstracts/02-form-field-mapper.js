/**
 * @module
 * @name Congressy Abstracts - Form
 * @namespace window.cgsy.abstracts.form
 * @description Módulo de Mapeamento de Campos de Formulário
 * @depends
 *  - jQuery
 *  - window.cgsy.abstracts.dom
 *  - window.cgsy.abstracts.error
 */
window.cgsy = window.cgsy || {};
window.cgsy.abstracts = window.cgsy.abstracts || {};

(function ($, abstracts) {
    "use strict";

    abstracts.form = {};

    /**
     * Mapeamento de campos de um formulário.
     * @param {jQuery|string} form_el
     * @constructor
     */
    abstracts.form.FieldMapper = function (form_el) {
        var self = this;

        /**
         * @type {jQuery}
         */
        form_el = $(form_el);

        /**
         * Mapeamento de elementos jQuery: nome do campo -> referência de busca.
         * @type {abstracts.dom.DOMManager}
         */
        this.dom_mapper = new abstracts.dom.DOMManager();

        /**
         * Nome do campo e referência de busca via jQuery do campo.
         * @type {Object}
         */
        this.field_names = {};

        /**
         * Lista campos que possuem multiplos valores.
         * @type {Array}
         */
        this.list_fields = [];

        /**
         * Campos a serem ignorado pelo mapeamento.
         * @type {Array}
         */
        this.ignored = [];

        /**
         * Dados do formulário: campo -> valor
         * @type {Object}
         */
        this.data = {};

        /**
         * Ignora campo informado.
         * @param {string} name
         * @param {boolean|undefined} warn
         */
        this.ignore = function (name, warn) {
            if (self.ignored.includes(name) === true) {
                return;
            }

            if (warn === true) {
                console.warn('Campo ignorado: ' + name);
            }

            self.ignored.push(name);
        };

        /**
         * Verifica se campo informado é ignorado.
         * @param {string} name
         * @returns {boolean}
         */
        this.isIgnored = function(name) {
            return self.ignored.includes(name);
        };

        /**
         * Sincroniza informações do formulário para a instância e da instância
         * para o formulário.
         */
        this.syncDataAndDom = function() {
            self.data = {};

            return new Promise(function(resolve) {
                var normalizeData = function(data) {
                    data = data || [];
                    var normalized_data = {};

                    data.forEach(function(item) {
                        var name = item['name'];
                        var value = item['value'];

                        if (self.isIgnored(name)) {
                            return;
                        }

                        if (!value) {
                            return;
                        }

                        normalized_data[name] = value;
                    });

                    $.each(normalized_data, function(name, values) {
                        self.data[name] = values;
                    });

                    $.each(self.data, function(name, values) {
                        self.set(name, values);
                    });

                    resolve(self.data);
                };

                var data = form_el.serializeArray();
                var file_els = $('input[type=file]');
                var num_files = file_els.length;
                var file_counter = 0;

                if (num_files === 0) {
                    normalizeData(data);
                    return;
                }

                var getBase64 = function (name, reader) {
                    data.push({'name': name, 'value': reader.result});

                    if ((num_files - 1) === file_counter) {
                        normalizeData(data);
                    } else {
                        file_counter++;
                    }
                };

                $.each(file_els, function(i) {
                    var name = $(this).attr('name');
                    var file = $(this).get(0).files[0];

                    if (!file) {
                        if ((num_files - 1) === file_counter) {
                            normalizeData(data);
                        } else {
                            file_counter++;
                        }
                        return;
                    }

                    var reader = new FileReader();
                        reader.onloadend = function() { getBase64(name, reader); };
                        reader.readAsDataURL(file);
                });
            });
        };

        /**
         * Resgata dados do formulário: chave -> valor
         * @returns {Object}
         */
        this.getData = function () {
            if (!self.data) {
                console.warn(
                    'Formulário sem dados. Você deve rodar syncDataAndDom()' +
                    ' para sincronizar os dado do formulário.'
                );
            }
            return self.data;
        };

        /**
         * Limpa capos do formulário.
         */
        this.clear = function() {
            self.sync().then(function(data) {
                Object.keys(data).forEach(function(name) {
                    if (self.isIgnored(name)) {
                        return;
                    }
                    self.dom_mapper.insertValue(name, null, false);
                });

                self.data = {};
            });
        };

        /**
         * Preenche os campos do formulário e dados da instância.
         * @param {Object} data
         */
        this.populate = function(data) {
            Object.keys(data).forEach(function(name) {
                if (self.isIgnored(name)) {
                    return;
                }
                var v = data[name];

                if (v === null || v === undefined) {
                    v = '';
                } else if ($.isArray(v) === false) {
                    v = v.toString();
                }

                self.data[name] = v;
                self.dom_mapper.insertValue(name, v, false);
            });
        };

        /**
         * Seta valor em campo através do nome do campo.
         * @param {string} name
         * @param {string} value
         */
        this.set = function(name, value) {
            if (self.isIgnored(name)) {
                return;
            }
            self.data[name] = value;
            self.dom_mapper.insertValue(name, value, false);
        };

        /**
         * Resgata valor do campo de acordo com o nome do campo.
         * @param {string} name
         * @returns {string|Array|boolean|number|*}
         */
        this.get = function(name) {
            if (self.isIgnored(name)) {
                return;
            }
            return self.dom_mapper.getEl(name).val();
        };

        $.each($('input, select, textarea', form_el), function () {
            var field_el = $(this);
            var name = field_el.attr('name');
            var tag_name = field_el.get(0).tagName;
            var type = field_el.attr('type');

            if (type === 'button') {
                return;
            }

            if (self.isIgnored(name)) {
                return;
            }

            if (!self.field_names.hasOwnProperty(name)) {
                self.field_names[name] = tag_name.toString().toLowerCase() + '[name=' + name + ']';
            }
        });

        Object.keys(self.field_names).forEach(function (name) {
            if (self.isIgnored(name)) {
                return;
            }
            var fields = $(self.field_names[name], form_el);
            if (fields.length > 1) {
                self.list_fields.push(name);
            }

            self.dom_mapper.setElement(name, fields);
        });
        self.dom_mapper.setAsStrictKeys();
        self.syncDataAndDom();
    };

})(jQuery, window.cgsy.abstracts);