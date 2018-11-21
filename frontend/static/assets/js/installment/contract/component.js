window.cgsy = window.cgsy || {};
window.cgsy.installment = window.cgsy.installment || {};
window.cgsy.installment.component = window.cgsy.installment.component || {};

(function ($, abstracts, installment, as_currency) {
    'use strict';

    /**
     * Modal de formulário de contrato.
     * @param {jQuery|string} modal_el
     * @param {installment.form.ContractForm} form
     * @constructor
     */
    installment.component.ContractFormModal = function(modal_el, form) {
        abstracts.modal.Form.call(this, modal_el, form);

    };
    installment.component.ContractFormModal.prototype = Object.create(abstracts.modal.Form.prototype);
    installment.component.ContractFormModal.prototype.constructor = installment.component.ContractFormModal;

    /**
     * Lista e contratos de parcelas.
     * @param {jQuery|string} parent_el
     * @param {installment.collections.PartCollection} part_collection
     * @constructor
     */
    installment.component.ContractPartsList = function(parent_el, part_collection) {
        abstracts.dom.Component.call(this);

        /**
         * @type {jQuery}
         */
        this.parent_el = $(parent_el);

        /**
         * Coleção de modelos de parcela.
         * @type {installment.collections.PartCollection}
         */
        this.part_collection = part_collection;

        /**
         * Renderiza componente
         */
        this.render = function() {

            parent_el.empty();
            
            self.part_collection.items.forEach(function(item) {
                parent_el.append(_createRow(item))
            });
        };


        /**
         * Cria elemento de linha da tabela de parcelas.
         * @param {installment.models.Part} part_instance
         * @returns {jQuery}
         * @private
         */
        var _createRow = function(part_instance) {
            var col1 = $('<span>').text(part_instance.get('installment_number') + 'x');
            var col2 = $('<div>').addClass('form-group').append(
                $('<input>').attr({
                    'type': 'tel',
                    'value': part_instance.get('expiration_date').format('DD/MM/YYYY'),
                    'class': 'form-control'
                }).on('keyup', function() {
                    // setar data com moment no model.
                    console.log($(this).val());
                })
            );
            var col3 = $('<span>').text('R$ ' + as_currency(part_instance.get('amount').toFixed(2)));

            var col4;
            if (part_instance.get('paid') === true) {
                col4 = $('<div>').addClass('text-center').text('Pago');
            } else {
                col4 = $('<div>').addClass('text-center').append(
                    $('<button>').attr({
                        'class': 'btn btn-success btn-sm'
                    }).append($('<span>').text('Pagar')),on('click', function() {
                        alert('preparando para pagar a porra da parcela');
                    })
                );
            }

            return $('<div>').addClass('row')
                .append($('<div>').addClass('col-md-3').html(col1))
                .append($('<div>').addClass('col-md-3').html(col2))
                .append($('<div>').addClass('col-md-3').html(col4))
                .append($('<div>').addClass('col-md-3').html(col3));
        };

    };
    installment.component.ContractPartsList.prototype = Object.create(abstracts.dom.Component.prototype);
    installment.component.ContractPartsList.prototype.constructor = installment.component.ContractPartsList;

})(jQuery, window.cgsy.abstracts, window.cgsy.installment, as_currency);