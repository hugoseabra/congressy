window.cgsy = window.cgsy || {};
window.cgsy.installment = window.cgsy.installment || {};
window.cgsy.installment.part = window.cgsy.installment.part || {};

(function (abstracts, installment) {
    'use strict';

    /**
     * Calculadora de preço de parcelas.
     * @param {number} num_parts
     * @param {number} amount
     * @param {number} minimum_price
     * @constructor
     */
    installment.part.PriceCalculator = function (num_parts, amount, minimum_price) {
        this.getPrices = function () {

            var prices = {};

            var price = amount / num_parts;

            if (price > minimum_price && price < amount) {
                num_parts--;
                return this.getPrices();
            }

            var step;
            for (step = 0; step < num_parts; step++) {
                prices[step + 1] = price;
            }

            return prices

        };
    };

    /**
     * Gera lista de datas de vencimento de parcela.
     * @param {Date} current_date
     * @param {Date} limit_date
     * @param {number} base_day
     * @param {number} amount
     * @param {number} minimum_price
     * @constructor
     */
    installment.part.ExpirationDateGenerator = function (current_date, limit_date, base_day, amount, minimum_price) {
        var self = this;

        this.dates = [];
        this.current_date = moment(current_date);

        this.getDates = function () {

            var limit = moment(limit_date);

            // Hoje depois da data limite
            if (self.current_date >= limit) {
                return this.dates;
            }

            // Mesmo mês
            if (self.current_date.isSame(limit, 'month')) {

                // Não passou da data base, então podemos adicionar daqui dois dias
                if (limit.date() >= self.current_date.add(2, 'days')) {
                    dates.push(self.current_date.add(2, 'days'));
                    return this.dates;
                } else if (self.current_date.date() > base_day) {
                    // Já passou da data base então não podemos criar
                    return this.dates;
                }
                dates.push(self.current_date.add(2, 'days'));
                return this.dates;
                
            }

            // Não é esse mês, vamos verificar a data base
            if (self.current_date.date() > base_day) {
                this.dates.push(self.current_date.add(2, 'days'))
            } else {
                this.dates.push(moment([self.current_date.year(), self.current_date.month(), base_day]))
            }

            self.current_date = self.current_date.month().add(1, 'month');
            return this.getDates();

        };

        this.getNumParts = function () {
            return (this.getDates().length)
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