window.cgsy = window.cgsy || {};
window.cgsy.installment = window.cgsy.installment || {};
window.cgsy.installment.service = window.cgsy.installment.part || {};

(function (abstracts, installment) {
    'use strict';

    /**
     * Calculadora de preço de parcelas.
     * @param {number} num_parts
     * @param {number} amount
     * @param {number} minimum_amount
     * @constructor
     */
    installment.service.PriceCalculator = function (num_parts, amount, minimum_amount) {
        var self = this;

        if (!num_parts) {
            throw "Você deve informar o número de parcelas";
        }

        this.num_parts = num_parts;
        this.amount = amount;
        this.minimum_amount = minimum_amount;

        this.installment_amount = null;

        this.getAmounts = function() {
            _init();
            var amounts = [];
            for (var a = 0; a < self.num_parts; a++) {
                amounts.push(self.installment_amount);
            }
            return amounts;
        };

        var _initialized = false;
        var _init = function() {
            if (_initialized === true) {
                return;
            }

            if (self.num_parts > 0) {
                self.installment_amount = self.amount / self.num_parts;

                if (self.installment_amount <= self.minimum_amount) {
                    self.num_parts = self.num_parts - 1;
                    _init();
                    return;
                }
            }

            _initialized = true;
        };
        window.setTimeout(function(){ _init(); }, 50);
    };

    /**
     * Gera lista de datas de vencimento de parcela.
     * @param {Date} limit_date
     * @param {number|undefined} base_day
     * @constructor
     */
    installment.service.ExpirationDateGenerator = function (limit_date, base_day) {
        var self = this;

        if (!limit_date) {
            throw "Você deve informar a data limite";
        }

        /**
         * Se nenhuma data limite for informada, assumimos X dias após agora.
         * @type {number}
         */
        this.default_days = 2;

        /**
         * Data atual.
         */
        this.current_date = moment(new Date());

        /**
         * Data limite até onde os parcelamentos podem ir. Se nada for informado
         * assumimos X dias após agora, a partir de default_base_days
         * @type {Date}
         */
        this.limit = moment(limit_date);

        /**
         * Dia base de vencimento. Se nada for informado assumimos 2 dias a
         * partir de hoje
         * @type {number}
         */
        this.base_day = base_day || self.current_date.clone().add(self.default_days, 'days').date();

        this.dates = [];

        // console.log('limit', self.limit.format('DD/MM/YYYY'));

        this.getDates = function(format) {
            _init();
            format = format || 'YYYY-MM-DD';
            return self.dates.map(function(item) {
                return item.format(format);
            })
        };

        this.getNumParts = function () {
            _init();
            return (this.dates.length)
        };

        var _initialized = false;
        var _init = function () {
            if (_initialized === true) {
                return;
            }

            if (self.current_date.isBefore(self.limit, 'month')) {
                // console.log('antes', self.current_date.format('DD/MM/YYYY'));
                // Se o dia de hoje é maior do que o dia base de vencimento
                if (self.current_date.date() >= self.base_day && self.dates.length === 0) {
                    // console.log('- 2 dias após hoje');
                    self.dates.push();
                } else {
                    // console.log('- dia base');
                    self.dates.push(moment([self.current_date.year(), self.current_date.month(), self.base_day]))
                }
                self.current_date = self.current_date.clone().add(1, 'month');
                _init();
                return;
            }

            // console.log('mesmo mês', self.current_date.format('DD/MM/YYYY'));

            // Se agora é antes da data limite.
            if (self.current_date.isBefore(self.limit)) {
                // console.log('- dia antes');
                self.dates.push(moment([self.current_date.year(), self.current_date.month(), self.base_day]));

            // Se a data limite vence hoje.
            } else if (self.current_date.isSame(self.limit, 'day')) {
                // console.log('- limite é hoje');
                if (self.limit.date() > self.base_day) {
                    self.dates.push(moment([self.current_date.year(), self.current_date.month(), self.base_day]));
                } else {
                    self.dates.push(self.current_date);
                }
            }

            // console.log('---');

            // Já atingimos a data limite e nao podemos gerar mais datas.
            _initialized = true;
        };

        window.setTimeout(function(){ _init(); }, 50);
    };

    /**
     * Cria instância de coleção de parcelas de contrato.
     * @param {installment.models.Contract} contract
     * @constructor
     */
    installment.service.PartCollectionFactory = function(contract) {

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