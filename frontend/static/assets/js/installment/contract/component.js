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
        self = this;

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

            var part_list = _getPartsList(
                limit_date,
                parseInt(data['expiration_day']),
                data['amount'],
                data['minimum_amount']
            );

            var num_installments_field = self.getEl('num-installments-field');
                num_installments_field.empty();
                num_installments_field.unbind('change');
                num_installments_field.on('change', function() {
                    part_list.render($(this).val());
                });

            for (var a = 2; a <= part_list.items.length+1; a++) {
                num_installments_field.append($('<option>').attr('value', a).text(a));
            }

            part_list.render();
        };

        var _getPartsList = function(limit_date, expiration_day, amount, minimum_amount) {
            var exp_date_generator = new installment.service.ExpirationDateGenerator(
                limit_date,
                expiration_day
            );
            var num_parts = exp_date_generator.getNumParts();

            if (!num_parts > 0) {
                return;
            }

            var calc = new installment.service.PriceCalculator(num_parts, amount, minimum_amount);
            var amounts = calc.getAmounts();
            var exp_dates = exp_date_generator.getDates('DD/MM/YYYY');

            num_parts = amounts.length;

            var part_list = new installment.component.ContractPartsList(self.getEl('part-table-list'));

            var counter = 0;
            for (var a = 2; a <= num_parts; a++) {
                part_list.addItem(exp_dates[counter], as_currency(amounts[counter]));
                counter++;
            }

            var exp_day_field_el = self.getEl('expiration-day-field');
                exp_day_field_el.unbind('keyup');
                exp_day_field_el.on('keyup', function() {
                    var v = $(this).val();
                    if (v > 31) {
                        return;
                    };
                    var part_list = _getPartsList(limit_date, v, amount, minimum_amount);
                    part_list.render(self.getEl('num-installments-field').val());
                });

            return part_list;
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
        this.render = function(show) {

            show = show || 2;

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

            var counter = 2;
            self.items.forEach(function(item) {
                table.append(_createRow(
                    counter,
                    item['amount'],
                    item['expiration_date_str'],
                    counter <= show
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
                    .attr('for', 'amount' + num)
                    .addClass('label-control')
                    .css('margin-bottom', 0)
                    .text(num + 'x')
            );

            var col2 = $('<td>').addClass('text-center').append(
                $('<label>')
                    .attr('for', 'amount' + num)
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
                    .attr('name', 'amount' + num)
                    .attr('id', 'amount' + num)
                    .attr('value', expiration_date_str)
                    .attr('readonly', '');

            // input.mask('99/99/9999');

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