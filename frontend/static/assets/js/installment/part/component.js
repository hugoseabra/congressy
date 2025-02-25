window.cgsy = window.cgsy || {};
window.cgsy.installment = window.cgsy.installment || {};
window.cgsy.installment.component = window.cgsy.installment.component || {};

(function (abstracts, installment, as_currency) {
    'use strict';

    /**
     * Modal de formulário de contrato.
     * @param {jQuery|string} parent_el
     * @param {installment.models.Contract} contract
     * @constructor
     */
    installment.component.PartTable = function(parent_el, contract) {
        abstracts.dom.Component.call(this);
        abstracts.element.list.Table.call(this, parent_el);
        var self = this;

        self.dom_manager.domElements['cancel-button'] = null;

        this.preRender = function () {
            var button_el = self.getEl('cancel-button');
            if (button_el && button_el.length) {
                button_el.hide();
            }
        };

        this.postRender = function () {
            var button_el = self.getEl('cancel-button');
            if (button_el && button_el.length) {
                button_el.show();

                button_el.unbind('click');
                button_el.on('click', function() {
                    var messenger = new abstracts.messenger.Messenger('deleting-contract');

                    if(confirm('Tem certeza que deseja cancelar este contrato?')) {
                        messenger.notifyLoader();

                        contract.set('status', 'cancelled');
                        contract.save().then(function() {
                            messenger.notifySuccess('Contrato cancelado com sucesso.');
                            messenger.id = null;
                            messenger.notifyLoader();
                            window.location.reload(true);
                        }, function() {
                            messenger.notifyError('Houve um erro ao cancelar contrato.');
                        });
                    }
                });
            }
        };

        self.addHeader('#', '# Parcela', 'text-center', '12%');
        self.addHeader('exp_date', 'Vencimento', 'text-center', null);
        self.addHeader('amount', 'Valor (R$)', 'text-center', '25%');
        self.addHeader('status', 'Status', 'text-center', '10%');

        self.addColumnHandler('#', function(item) {
            var paid = item.get('paid') === true;
            var next_part = item.next === true;
            var value = item.get('installment_number');

            return _getColumnContent(paid, next_part, value);
        });

        self.addColumnHandler('exp_date', function(item) {
            var paid = item.get('paid') === true;
            var next_part = item.next === true;
            var value = item.get('expiration_date').format('DD/MM/YYYY');

            return _getColumnContent(paid, next_part, value);
        });

        self.addColumnHandler('amount', function(item) {
            var paid = item.get('paid') === true;
            var next_part = item.next === true;
            var value = 'R$ ' + as_currency(item.get('amount'));

            return _getColumnContent(paid, next_part, value);
        });

        self.addColumnHandler('status', function(item) {
            var paid = item.get('paid') === true;
            var next_part = item.next === true;

            var button = $('<button>').addClass('btn btn-sm btn-block');

            if (paid === true) {
                button.addClass('btn-success')
                    .attr('disabled', '')
                    .text('Pago');

            } else if (paid === false && next_part === true) {         
                button.addClass('btn-primary')
                    .attr('data-toggle', 'tooltip')
                    .attr('title', 'Registrar o pagamento')
                    .html($('<span>').addClass('far fa-money-bill-alt'));

                button.on('click', function () {
                    $('#id_part').val(item.pk);
                    var amount = item.get('amount');

                    $("#manual-payment-parts-form-modal").find("#id_amount").val(amount.toFixed(2));
                    $('#manual-payment-parts-form-modal').modal('show');
                });

            } else if (paid === false && next_part === false) {
                // Manter estética da linha.
                button.addClass('btn-default invisible').text('-');
            }

            return button;
        });

        /**
         * @param {boolean} paid
         * @param {boolean} next_part
         * @param {string} value
         * @private
         */
        var _getColumnContent = function(paid, next_part, value) {
            var content = $('<span>').text(value);
            if (paid === true) {
                content.addClass('text-muted text-line-through');
            } else if (next_part === true) {
                content.addClass('text-bold danger-color');
            }
            return content;
        };
    };
    installment.component.ContractFormModal.prototype = Object.create(abstracts.element.list.Table.prototype);
    installment.component.ContractFormModal.prototype.constructor = installment.component.ContractFormModal;

})(window.cgsy.abstracts, window.cgsy.installment, as_currency);