window.cgsy = window.cgsy || {};
window.cgsy.installment = window.cgsy.installment || {};
window.cgsy.installment.part = window.cgsy.installment.part|| {};

(function (abstracts, installment) {
    'use strict';

    /**
     * Calculadora de preço de parcelas.
     * @param {number} num_parts
     * @param {number} amount
     * @constructor
     */
    installment.part.PriceCalculator = function(num_parts, amount) {
        this.getPrices = function() {

        };
    };

    /**
     * Gera lista de datas de vencimento de parcela.
     * @param {Date} limit_date
     * @param {number} base_day
     * @param {number} minimum_price
     * @constructor
     */
    installment.part.ExpirationDateGenerator = function(limit_date, base_day, minimum_price) {

        this.getDates = function() {

        };

        this.getTotal = function() {

        };
    };

    /**
     * Cria instância de coleção de parcelas de contrato.
     * @param {installment.models.Contract} contract
     * @constructor
     */
    installment.part.PartCollectionFactory = function(contract) {

        /**
         * Contrato de parcelamento.
         * @type {installment.models.Contract}
         */
        this.contract = contract;

        /**
         * Cria coleção de parcelas populando com os dados de acordo com
         * informações fornecidas.
         * @param {Date} limit_date
         * @param {integer} base_day
         * @param {number} minimum_price
         * @returns {installment.collections.PartCollection|*}
         */
        this.get = function(limit_date, base_day, minimum_price) {

            if (contract.isNew()) {
                return null;
            }

            var collection = new installment.collections.PartCollection(contract.pk);
                collection.error_handler = contract.error_handler;
            contract.part_collection = collection;

            // CRIAR PARTS E INSERIR NO COLLECTION

            return collection;
        };
    };


})(window.cgsy.abstracts, window.cgsy.installment);