window.cgsy = window.cgsy || {};
window.cgsy.installment = window.cgsy.installment || {};
window.cgsy.installment.component = window.cgsy.installment.component || {};

(function (abstracts, installment) {
    'use strict';

    /**
     * Modal de formulário de contrato.
     * @param {jQuery|string} parent_el
     * @constructor
     */
    installment.component.PartTable = function(parent_el) {
        abstracts.element.list.Table.call(this, parent_el);
        var self = this;

        this.createHeader('#', '#', null, '10%');
        this.createHeader('amount', 'Valor (R$)', 'text-center', null);
        this.createHeader('exp_date', 'Vencimento', 'text-center', null);
        this.createHeader('status', 'Status', 'text-center', null);

        this.createActionButton('Pagar', 'fa fa-check', function() {
            alert('pagou nada não');
        });
    };
    installment.component.ContractFormModal.prototype = Object.create(abstracts.element.list.Table.prototype);
    installment.component.ContractFormModal.prototype.constructor = installment.component.ContractFormModal;

})(window.cgsy.abstracts, window.cgsy.installment);