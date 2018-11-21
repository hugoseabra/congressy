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

        self.addHeader('#', '#', 'text-center', '5%');
        self.addHeader('exp_date', 'Vencimento', 'text-center', null);
        self.addHeader('amount', 'Valor (R$)', 'text-center', '20%');
        self.addHeader('status', 'Status', 'text-center', '10%');

        // self.addActionButton('Pagar', 'fas fa-money', function() {
        //     alert('pagou nada não');
        // });
    };
    installment.component.ContractFormModal.prototype = Object.create(abstracts.element.list.Table.prototype);
    installment.component.ContractFormModal.prototype.constructor = installment.component.ContractFormModal;

})(window.cgsy.abstracts, window.cgsy.installment);