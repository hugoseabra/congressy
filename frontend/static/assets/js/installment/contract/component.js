window.cgsy = window.cgsy || {};
window.cgsy.installment = window.cgsy.installment || {};
window.cgsy.installment.component = window.cgsy.installment.component || {};

(function (abstracts, installment) {
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
     * @param {installment.collections.PartCollection} part_collection
     * @constructor
     */
    installment.component.ContractPartsList = function(part_collection) {
        abstracts.dom.Component.call(this);

        this.parent_el = $(parent_el);
        this.part_collection = part_collection;

        var _create_row = function(part_instance) {

        };

    };
    installment.component.ContractPartsList.prototype = Object.create(abstracts.dom.Component.prototype);
    installment.component.ContractPartsList.prototype.constructor = installment.component.ContractPartsList;

})(window.cgsy.abstracts, window.cgsy.installment);