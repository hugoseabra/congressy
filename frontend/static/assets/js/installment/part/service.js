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

        this.installment_amounts = {};

        this.getAmounts = function() {
            _init();
            return self.installment_amounts;
        };

        var _initialized = false;
        var _init = function() {
            if (_initialized === true) {
                return;
            }

            if (self.num_parts > 0) {
                for (var a = 2; a < self.num_parts+2; a++) {
                    var amount_part = self.amount / a;
                    if (amount_part >= self.minimum_amount) {
                        self.installment_amounts[a] = amount_part;
                    }
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
                if (self.current_date.date() >= self.base_day && self.dates.length === 0) {
                    // console.log('- 2 dias após hoje');
                    self.dates.push(moment([self.current_date.year(), self.current_date.month(), self.current_date.date()+2]));
                } else {
                    // console.log('- dia base');
                    self.dates.push(moment([self.current_date.year(), self.current_date.month(), self.base_day]))
                }
                self.current_date = self.current_date.clone().add(1, 'month');
                _init();
                return;
            }

            if (self.current_date.isSame(self.limit, 'month')) {
                var day_today = self.current_date.date();
                var two_days_after = self.current_date.clone().add(2, 'days');

                if (day_today > self.base_day) {

                    if (day_today <= two_days_after) {
                        self.dates.push(moment([self.current_date.year(), self.current_date.month(), day_today+2]));
                    } else {
                        self.dates.push(moment([self.current_date.year(), self.current_date.month(), day_today]));
                    }

                } else {
                    self.dates.push(moment([self.current_date.year(), self.current_date.month(), self.base_day]));
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

        if (contract.isNew()) {
            throw "Contratos sem identificador não podem criar parcelas."
        }

        /**
         * Contrato de parcelamento.
         * @type {installment.models.Contract}
         */
        this.contract = contract;

        /**
         * Cria coleção de parcelas populando com os dados de acordo com
         * informações fornecidas.
         * @param {Array} expiration_dates
         * @param {number} amount
         * @returns {Promise}
         */
        this.create = function(expiration_dates, amount) {
            return new Promise(function(resolve, reject) {
                var collection = contract.createPartCollection();

                var num_installment = 2;
                expiration_dates.forEach(function(exp_date_str) {
                    var split = exp_date_str.split('/');
                    var data = {
                        'contract': contract.pk,
                        'amount': amount,
                        'expiration_date': new Date(split[2], split[1], split[0]),
                        'installment_number': num_installment
                    };

                    var part = new installment.models.Part();
                        part.populate(data);

                    if (!part.isValid()) {
                        return reject('Erro ao criar parcela');
                    }

                    part.save().then(function() {
                        if (!part.isValid()) {
                            return reject('Erro ao salvar parcela.');
                        }
                        collection.add(part);
                    }, function(reason) {
                        reject(reason);
                    });

                    num_installment++;
                });

                resolve();
            });

        };
    };


})(window.cgsy.abstracts, window.cgsy.installment);