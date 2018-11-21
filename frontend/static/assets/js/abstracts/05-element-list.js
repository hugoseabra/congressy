/**
 * @module
 * @name Congressy Abstracts - Elementos de Listas e Tabelas
 * @namespace window.cgsy.abstracts.element.list
 * @description Tabelas e listas.
 * @depends
 *  - jQuery
 *  - DataTables
 *  - window.cgsy.AjaxSender
 *  - window.cgsy.abstracts.dom
 *  - window.cgsy.abstracts.error
 *  - window.cgsy.abstracts.messenger
 *  - window.cgsy.abstracts.http
 *  - window.cgsy.abstracts.domain
 */
window.cgsy = window.cgsy || {};
window.cgsy.abstracts = window.cgsy.abstracts || {};
window.cgsy.abstracts.element = window.cgsy.abstracts.element || {};
window.cgsy.abstracts.element.list = window.cgsy.abstracts.element.list || {};

(function ($, abstracts) {
    'use strict';

    /**
     * Cabeçalho de tabela de dados.
     * @param {string} name
     * @param {string|null|undefined} label
     * @param {string|null|undefined} classes
     * @param {string|null|undefined} width
     * @constructor
     */
    abstracts.element.list.Header = function(name, label, classes, width) {
        var _values = [];

        this.getName = function() {
            return name;
        };

        this.getLabel = function() {
            return label;
        };

        this.getClasses = function() {
            return classes;
        };

        this.getWidth = function() {
            return width;
        };

        this.addValue = function(v) {
            _values.push(v);
        };

        this.getValues = function() {
            return _values;
        };
    };

    /**
     *
     * @param {string} label
     * @param {string} icon_class
     * @param {Function} handler
     * @constructor
     */
    abstracts.element.list.ActionButton = function(label, icon_class, handler) {

        this.getLabel = function() {
            return label;
        };

        this.getIconClass = function() {
            return icon_class;
        };

        /**
         * Resgata handler.
         * @returns {Function}
         */
        this.getHandler = function() {
            return handler || function(item) {};
        };
    };

    /**
     * Tabela de elementos.
     * @param {jQuery|string} parent_el
     * @constructor
     */
    abstracts.element.list.Table = function(parent_el) {
        var self = this;

        var _headers_created = false;

        /**
         * Element onde o componente será carregado.
         * @type {jQuery}
         */
        this.parent_el = $(parent_el);

        /**
         * @type {jQuery}
         */
        this.table_el = null;

        this.after_render_callback = function() {};

        /**
         * Cabeçalho da lista.
         * @type {Array}
         */
        this.headers = [];

        /**
         * Se cabeçalho devm ser exibidos ou não.
         * @type {boolean}
         */
        this.show_headers = true;

        /**
         * Lista de items a serem carregados linha a linha.
         * @type {Array}
         */
        this.items = [];

        /**
         * Função a ser chamada no carregamento de uma coluna.
         * @type {Object}
         */
        this.column_handlers = {};

        /**
         * Botões de ação.
         * @type {Array}
         */
        this.action_buttons = [];

        /**
         * Configura instância para não exibir o cabeçalho.
         */
        this.hideHeaders = function() {
            self.show_headers = false;
        };

        /**
         * Cabeçalho de tabela de dados.
         * @param {string} name
         * @param {string|null|undefined} label
         * @param {string|null|undefined} classes
         * @param {string|null|undefined} width
         * @constructor
         */
        this.addHeader = function(name, label, classes, width) {
            self.headers.push(new abstracts.element.list.Header(
                name,
                label,
                classes,
                width
            ));
        };

        /**
         * Resgata nomes das colunas.
         * @returns {Array}
         */
        this.getHeaderNames = function() {
            return self.headers.map(function(header) {
                return header.getName();
            });
        };

        /**
         * Verifica se nome da coluna existe na lista.
         * @param {string} name
         * @returns {boolean}
         */
        this.hasHeader = function(name) {
            var exists = false;
            self.getHeaderNames().forEach(function(header_name) {
                if (name === header_name) {
                    exists = true;
                }
            });
            return exists;
        };

        /**
         * Cria item de handler de coluna.
         * @param {string} name
         * @param {Function} handler
         */
        this.addColumnHandler = function(name, handler) {
            if (!self.hasHeader(name)) {
                console.warn('Coluna não existe: ' + name);
                return;
            }

            if (typeof handler !== 'function') {
                console.warn('Handler não é uma função: ' + handler);
                return;
            }
            this.column_handlers[name] = handler;
        };

        /**
         * Cria item de botão de ação.
         * @param {string} label
         * @param {string|null} icon_class
         * @param {Function} handler
         */
        this.addActionButton = function(label, icon_class, handler) {
            this.action_buttons.push(new abstracts.element.list.ActionButton(
                label,
                icon_class,
                handler
            ));
        };

        this.showLoader = function() {
            self.parent_el.find('table').hide();
            self.getLoaderEl().fadeIn();
        };

        /**
         * Insere lista de items a serem carregados.
         * @param {Array} items
         */
        this.setItems = function(items) {
            self.items = items || [];
        };

        /**
         * Insere novo item.
         * @param {Object} item
         */
        this.addItem = function(item) {
            self.items.push(item);
        };

        this.setAfterRenderCallback = function(callback) {
            if (typeof callback !== 'function') {
                return;
            }
            self.after_render_callback = callback;
        };

        /**
         * Renderiza componente.
         */
        this.render = function() {
            if (self.headers.length === 0) {
                console.warn('<element.List>.headers não configurado.');
                return;
            }

            var table_el = self.getTableEl();
                table_el.hide();

            self.getLoaderEl().fadeOut(function() {
                table_el.fadeIn(function() {
                    self.after_render_callback();
                });
            });
        };

        /**
         * Renderiza componente.
         * @returns {jQuery}
         */
        this.getTableEl = function() {
            if (self.table_el) {
                return self.table_el;
            }

            self.table_el = $('<table>').addClass('table table-striped table-bordered');
            self.parent_el.append(self.table_el);

            if (self.items.length === 0) {
                self.table_el.append($('<tbody>').append($('<tr>').append(
                    $('<td>')
                        .css('text-align', 'center')
                        .attr('colspan', self.headers.length + 3)
                        .html('Sem registros')
                )));
                return self.table_el;
            }

            _createHeader(self.table_el);
            _normalizeValues();
            _createRows(self.table_el);

            return self.table_el;
        };

        /**
         * Resgata (ou cria se não existir) o elemento de 'carregando' antes
         * de renderizar a tabela.
         * @returns {jQuery}
         */
        this.getLoaderEl = function() {
            var main_div = self.parent_el.find('.list-loader');
            if (main_div.length === 0) {
                main_div = $('<div>')
                    .addClass('list-loader').css('text-align', 'center')
                    .css('display', 'none');
                main_div.append($('<span>').addClass('fas fa-circle-notch fa-spin fa-3x'));
                main_div.append($('<div>').text('carregando'));
                self.parent_el.append(main_div);
            }
            main_div.show();
            return main_div;
        };

        /**
         * Cria elementos de cabeçalho
         * @param {jQuery} table_el
         * @returns {[abstracts.element.list.Header]}
         * @private
         */
        var _createHeader = function(table_el) {
            if (_headers_created === true) {
                return self.headers;
            }

            var reserved_column_names = ['column_conf'];

            self.headers.forEach(function(header) {
                if (reserved_column_names.includes(header.getName())) {
                    console.error(
                        'Nome da coluna não pode ser "'+header.getName()+'".' +
                        ' Nomes reservados: ' + reserved_column_names.join(', ')
                    );
                }
            });

            var headers = self.headers;
            if (self.action_buttons.length > 0) {
                headers.push(new abstracts.element.list.Header(
                    'column_conf',
                    null,
                    'text-center',
                    '1%'
                ));
            }

            var thead = $('<thead>');

            if (self.show_headers === false) {
                thead.addClass('hide');
            }

            var header_row = $('<tr>');

            table_el.append(thead);
            thead.append(header_row);

            headers.forEach(function(header) {
                var column = $('<th>');
                    column.appendTo(header_row);

                if (header.getClasses()) {
                    column.addClass(header.getClasses());
                }

                if (header.getWidth()) {
                    column.css('width', header.getWidth());
                }
                column.html(header.getLabel());
            });

            _headers_created = true;
            self.headers = headers;

            return headers;
        };

        /**
         * Normaliza valores de acordo com as colunas.
         * @private
         */
        var _normalizeValues = function() {

            var last_column = self.headers[self.headers.length - 1];

            var row_counter = 0;
            self.items.forEach(function(item) {
                self.headers.forEach(function(header) {
                    var name = header.getName();

                    if (self.action_buttons.length > 0 && name === last_column.getName()) {
                        return;
                    }

                    if (self.column_handlers.hasOwnProperty(name) && typeof self.column_handlers[name] === 'function') {
                        header.addValue(self.column_handlers[name]);
                    } else {
                        header.addValue(item[name]);
                    }
                });

                if (self.action_buttons.length > 0) {
                    last_column.addValue(_createActionButton(item));
                }
                row_counter++;
            });
        };

        /**
         * Cria elementos de linha da tabela.
         * @param {jQuery} table_el
         * @private
         */
        var _createRows = function(table_el) {
            var tbody = $('<tbody>');
                table_el.append(tbody);

            for (var i = 0; i < self.items.length; i++) {
                var row = $('<tr>');
                var item = self.items[i];

                self.headers.forEach(function(header) {
                    if (header.getValues().length === 0) {
                        return;
                    }
                    var values = header.getValues();
                    if (i > values.length) {
                        return;
                    }
                    var value = values[i];

                    var column = $('<td>');

                    if (header.getClasses()) {
                        column.addClass(header.getClasses());
                    }

                    if (header.getWidth()) {
                        column.css('width', header.getWidth());
                    }

                    if (typeof value === 'function') {
                        value = value(item);
                    }

                    column.html(value);
                    row.append(column);
                });

                tbody.append(row);
            }
        };

        /**
         * Cria elemento de botão de ação da linha do registro da tabela.
         * @param {Object} item
         * @returns {jQuery|undefined}
         * @private
         */
        var _createActionButton = function(item) {
            if (self.action_buttons.length === 0) {
                return undefined;
            }

            var group = $('<div>').addClass('btn-group');
            var main_button = $('<button>')
                .addClass('btn btn-primary btn-trans btn-sm dropdown-toggle')
                .attr({
                    'type': 'button',
                    'data-toggle': 'dropdown',
                    'aria-expanded': 'true'
                })
                .append($('<span>').addClass('fas fa-cog'));
            group.append(main_button);

            if (self.action_buttons.length === 0) {
                main_button.attr('disabled', 'disabled');
                return group;
            }

            var button_list = $('<ul>')
                .addClass('dropdown-menu dropdown-menu-right')
                .attr('role', 'menu');
            group.append(button_list);

            self.action_buttons.forEach(function(action_button) {
                var ab_el = $('<li>');
                var link = $('<a>').attr('href', 'javascript:void(0)');
                ab_el.append(link);

                var icon_class = action_button.getIconClass();
                if (icon_class) {
                    var icon = $('<i>').addClass(icon_class);
                    link.append(icon);
                }
                link.append($('<span>').html(action_button.getLabel()));

                var handler = action_button.getHandler();
                if (typeof handler === 'function') {
                    link.on('click', function(e) {
                        e.preventDefault();
                        handler(item);
                    });
                }
                button_list.append(ab_el);
            });

            return group;
        };
    };
    
    /**
     * Tabela como DataTables
     * @param {abstracts.element.list.Table} table
     * @constructor
     */
    abstracts.element.list.DataTable = function(table) {
        var self = this;

        var _orderable_columns = [];
        var _searchable_columns = [];

        this.table = table;

        this.language = {
            sEmptyTable: "Nenhum registro encontrado",
            sInfo: "Mostrando de _START_ até _END_ de _TOTAL_ registros",
            sInfoEmpty: "Mostrando 0 até 0 de 0 registros",
            sInfoFiltered: "(Filtrados de _MAX_ registros)",
            sInfoPostFix: "",
            sInfoThousands: ".",
            sLengthMenu: "_MENU_ resultados por página",
            sLoadingRecords: "Carregando...",
            sProcessing: "Processando...",
            sZeroRecords: "Nenhum registro encontrado",
            sSearch: "Pesquisar",
            oPaginate: {
                sNext: "Próximo",
                sPrevious: "Anterior",
                sFirst: "Primeiro",
                sLast: "Último"
            },
            oAria: {
                sSortAscending: ": Ordenar colunas de forma ascendente",
                sSortDescending: ": Ordenar colunas de forma descendente"
            }
        };

        /**
         * Seta coluna como ordenável.
         * @param {string} column_name
         */
        this.orderable = function(column_name) {
            if (_orderable_columns.includes(column_name)) {
                return;
            }
            _orderable_columns.push(column_name);
        };

        this.searchable = function(column_name) {
            if (_searchable_columns.includes(column_name)) {
                return;
            }
            _searchable_columns.push(column_name);
        };

        /**
         * Renderiza componente.
         */
        this.render = function() {
            if (self.table.headers.length === 0) {
                self.table.render();
                return;
            }

            // Primeira e última colunas são inseridas pela lib.
            var column_defs = [
                {
                    'orderable': false,
                    'searchable': false,
                    'targets': [-1]
                }
            ];

            var i = 0;
            var first_orderable = null;
            self.table.getHeaderNames().forEach(function(name) {
                if (_orderable_columns.includes(name)) {
                    return;
                }

                if (first_orderable === null && _orderable_columns.includes(name)) {
                    first_orderable = i;
                }

                column_defs.push({
                    'orderable': _orderable_columns.includes(name),
                    'searchable': _searchable_columns.includes(name),
                    'targets': i
                });

                i++;
            });

            var dt_options = {
                'language': self.language,
                'columnDefs': column_defs
            };

            if (first_orderable !== null) {
                // Default order
                dt_options['order'] = [
                    [first_orderable, 'asc']
                ];
            }

            self.table.getTableEl().DataTable(dt_options);

            var datatables_el = self.table.parent_el.find('.dataTables_wrapper');
                datatables_el.hide();

            self.table.showLoader();
            self.table.getLoaderEl().fadeOut(function() {
                datatables_el.fadeIn(function() {
                    self.table.getTableEl().show();
                    self.table.after_render_callback();
                });
            });
        };

    };
    
    /**
     * Tabela de elementos de uma coleção de modelos de domínio.
     * @param {jQuery|string} parent_el
     * @param {abstracts.domain.Collection} collection
     * @constructor
     */
    abstracts.element.list.CollectionTable = function(parent_el, collection) {
        var self = this;

        /**
         * Coleção de modelos de domínio.
         * @type {abstracts.domain.Collection}
         */
        this.collection = collection;
        this.table = new abstracts.element.list.Table(parent_el);

        /**
         * Cria item de botão de ação.
         * @param {string} label
         * @param {string|null} icon_class
         * @param {Function} handler
         */
        this.createActionButton = function(label, icon_class, handler) {
            self.table.createActionButton(label, icon_class, handler);
        };

        this.fetch = function() {

            var messenger = _getMessenger('collection-table-fetch');
                messenger.closeAll();
                messenger.notify_loader();

            return new Promise(function(resolve) {
                self.collection.fetch().then(function(items) {
                    messenger.close();

                    if (!self.collection.isValid()) {
                        var messenger_errors = _getMessenger();

                        var status = self.collection.client.http_status;
                        self.collection.error_handler.non_key_errors.forEach(function(msg) {
                            messenger_errors.notifyError(msg);
                        });

                        if (status === 0 || status >= 500) {
                            messenger.retry(function() { self.fetch() }, 'Tentando novamente.');
                        }
                    }

                    items = items.map(function(item) {
                        return item.toPlainObject();
                    });

                    self.table.render(items);
                });
            });
        };

        var _getMessenger = function(id) {
            return new abstracts.messenger.Messenger(id);
        };
    };


})(jQuery, window.cgsy.abstracts);