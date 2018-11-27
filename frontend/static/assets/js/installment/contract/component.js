window.cgsy = window.cgsy || {};
window.cgsy.installment = window.cgsy.installment || {};
window.cgsy.installment.component = window.cgsy.installment.component || {};

(function ($, abstracts, installment, moment, as_currency) {
    'use strict';

    /**
     * Modal de formulário de contrato.
     * @param {string} subscription_pk
     * @param {jQuery|string} modal_el
     * @param {jQuery|string} form_el
     * @param {jQuery|string} button_el
     * @constructor
     */
    installment.component.ContractFormModal = function(subscription_pk, modal_el, form_el, button_el) {
        abstracts.modal.Modal.call(this, modal_el);
        var self = this;

        self.dom_manager.domElements['num-installments-field'] = null;
        self.dom_manager.domElements['expiration-day-field'] = null;
        self.dom_manager.domElements['part-table-list'] = null;

        this.form = new window.cgsy.installment.form.ContractForm(subscription_pk, form_el);
        this.form.setEl('button', $(button_el));
        self.form.button_text = 'Criar contrato';

        self.form.addPostSaveCallback(function() {
            var messenger = new abstracts.messenger.Messenger();
                messenger.notifyLoader();
            window.location.reload(true);
        });

        self.loadElement(form_el);
        self.setTitle('NOVO CONTRATO DE PARCELAMENTO');

        this.populate = function(data) {
            var limit_date = data['limit_date_str'];
            if (!moment(limit_date).isValid()) {
                throw "Data limite inválida: " + limit_date;
            }
            limit_date = limit_date.split('-');
            limit_date = new Date(limit_date[0], limit_date[1], limit_date[2]);

            self.form.set('expiration_day', parseInt(data['expiration_day']));
            self.form.set('amount', as_currency(data['amount']));

            var part_list = new installment.component.ContractPartsList(self.getEl('part-table-list'));

            var exp_day_field_el = self.getEl('expiration-day-field');

            var num_installments_field = self.getEl('num-installments-field');
                num_installments_field.empty();
                num_installments_field.unbind('change');
                num_installments_field.on('change', function() {
                    _prepareList(
                        part_list,
                        $(this).val(),
                        limit_date,
                        exp_day_field_el.val(),
                        data['amount'],
                        data['minimum_amount']
                    );
                    part_list.render($(this).val());

                    self.form.syncDataAndDom();
                });

            exp_day_field_el.unbind('change');
            exp_day_field_el.on('change', function() {
                var v = $(this).val();
                if (v < 1 || v > 31) {
                    return;
                }

                _prepareList(
                    part_list,
                    num_installments_field.val(),
                    limit_date,
                    v,
                    data['amount'],
                    data['minimum_amount']
                );

                part_list.render(num_installments_field.val());

                self.form.syncDataAndDom();
            });

            _prepareList(
                part_list,
                1,
                limit_date,
                parseInt(data['expiration_day']),
                data['amount'],
                data['minimum_amount']
            );

            for (var a = 1; a <= part_list.items.length; a++) {
                num_installments_field.append($('<option>').attr('value', a).text(a + 'x'));
            }

            part_list.render();
        };


        var _prepareList = function(part_list, num_installment, limit_date, expiration_day, full_amount, minimum_amount) {
            part_list.reset();

            var dates = _getExpirationDates(limit_date, expiration_day);
            if (!dates.length) {
                return;
            }

            var num_parts = dates.length;

            var amounts = _getAmounts(num_parts, full_amount, minimum_amount);
            num_parts = Object.keys(amounts).length;

            var part_amount = _getAmount(num_installment, amounts);
            self.form.set('part_amount', part_amount);

            var counter = 0;
            dates.forEach(function(exp_date) {
                if (counter < num_parts) {
                    part_list.addItem(exp_date, as_currency(part_amount));
                }
                counter++;
            });
        };

        var _getExpirationDates = function(limit_date, expiration_day) {
            var exp_date_generator = new installment.service.ExpirationDateGenerator(
                limit_date,
                expiration_day
            );
            return exp_date_generator.getDates('DD/MM/YYYY');
        };

        var _getAmounts = function(num_parts, full_amount, minimum_amount) {
            var calc = new installment.service.PriceCalculator(num_parts, full_amount, minimum_amount);
            return calc.getAmounts();
        };

        var _getAmount = function(num_installment, part_amounts) {
            if (!part_amounts.hasOwnProperty(num_installment)) {
                return null;
            }

            return part_amounts[num_installment];
        };

        window.setTimeout(function() {
            $('[name=expiration_day]', form_el  ).focus();
        }, 250);
    };
    installment.component.ContractFormModal.prototype = Object.create(abstracts.modal.Modal.prototype);
    installment.component.ContractFormModal.prototype.constructor = installment.component.ContractFormModal;

    /**
     * Lista e contratos de parcelas.
     * @param {jQuery|string} parent_el
     * @constructor
     */
    installment.component.ContractPartsList = function(parent_el) {
        abstracts.dom.Component.call(this);
        var self = this;

        /**
         * @type {jQuery}
         */
        this.parent_el = $(parent_el);
        this.items = [];

        this.addItem = function(expiration_date_str, amount) {
            self.items.push({
                'expiration_date_str': expiration_date_str,
                'amount': amount
            });
        };

        this.reset = function() {
            self.items = [];
        };

        /**
         * Renderiza componente
         */
        this.render = function(num_parts) {

            num_parts = num_parts || 1;

            var table = $('<table>').addClass('table borderless');
            var header = $('<tr>');
            table.append(header);

            header.append(
                $('<td>')
                    .addClass('col-xs-1 col-sm-3 col-md-3 col-lg-2 text-right')
                    .append($('<small>').text('Parcela'))
            );
            header.append(
                $('<td>')
                    .addClass('col-xs-3 col-sm-2 col-md-2 col-lg-3 text-center')
                    .append($('<small>').text('Valor'))
            );
            header.append(
                $('<td>')
                    .addClass('col-xs-3 col-sm-3 col-md-4 col-lg-3')
                    .append($('<small>').text('Vencimento'))
            );

            var counter = 1;
            self.items.forEach(function(item) {
                table.append(_createRow(
                    counter,
                    item['amount'],
                    item['expiration_date_str'],
                    counter <= num_parts
                ));
                counter++;
            });

            self.parent_el.html(table);
        };


        /**
         * Cria elemento de linha da tabela de parcelas.
         * @private
         */
        var _createRow = function(num, amount, expiration_date_str, show) {

            show = show === true;

            var row = $('<tr>').addClass('row-amount' + num);

            if (show === false) {
                row.addClass('hide');
            }

            var col1 = $('<td>').addClass('text-right').append(
                $('<label>')
                    .attr('for', 'exp_date' + num)
                    .addClass('label-control')
                    .css('margin-bottom', 0)
                    .text(num)
            );

            var col2 = $('<td>').addClass('text-center').append(
                $('<label>')
                    .attr('for', 'exp_date' + num)
                    .addClass('label-control')
                    .css('margin-bottom', 0)
                    .text('R$ ' + amount)
            );


            var col3 = $('<td>').addClass('col-lg-2');

            var input_group = $('<div>').addClass('input-group');
            col3.append(input_group);

            input_group.append(
                $('<span>').addClass('input-group-addon').append(
                    $('<i>').addClass('fas fa-calendar-alt')
                )
            );

            var input = $('<input>')
                    .addClass('form-control')
                    .attr('type', 'tel')
                    .attr('name', 'exp_date' + num)
                    .attr('id', 'exp_date' + num)
                    .attr('value', expiration_date_str)
                    .attr('readonly', '');

            input.mask('99/99/9999');

            input_group.append(input);

            row.append(col1);
            row.append(col2);
            row.append(col3);

            return row;
        };

    };
    installment.component.ContractPartsList.prototype = Object.create(abstracts.dom.Component.prototype);
    installment.component.ContractPartsList.prototype.constructor = installment.component.ContractPartsList;

})(jQuery, window.cgsy.abstracts, window.cgsy.installment, moment, as_currency);