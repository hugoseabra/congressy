window.cgsy = window.cgsy || {};
window.cgsy.installment = window.cgsy.installment || {};
window.cgsy.installment.models = window.cgsy.installment.models || {};
window.cgsy.installment.collection = window.cgsy.installment.collection || {};

(function (abstracts, installment) {
    'use strict';

    //=========================== MODELS ======================================

    var uri = new abstracts.uri.APIBaseUrl('/api/', '/api/');
    var uri_manager = new abstracts.uri.URIManager(uri,  '/installment');

    /**
     * Parcela de contrato de parcelamento.
     * @param {number} pk
     * @constructor
     */
    installment.models.Part = function (pk) {
        // Configuration
        abstracts.domain.Model.call(this, pk && pk > 0 ? parseInt(pk) : undefined);
        var self = this;

        this.verbose_name = 'parcela';
        this.verbose_name_plural = 'parcelas';

        /**
         * Próxima parcela a ser paga.
         * @type {boolean}
         */
        this.next = false;

        this.uri_manager = uri_manager;
        this.creation_uri = '/parts/';
        this.uri = '/parts/{{pk}}/';

        // Fields
        this.fields = {
            'contract': {
                'required': true,
                'type': 'integer',
                'submittable': true,
                'blank': true,
                'label': 'Contrato',
                'message': 'Você deve informar o contrato'
            },
            'amount': {
                'required': true,
                'type': 'float',
                'submittable': true,
                'label': 'Valor',
                'message': 'Você deve informar o valor'
            },
            'expiration_date': {
                'required': true,
                'type': 'date',
                'submittable': true,
                'label': 'Data de vencimento',
                'message': 'Você deve a data de vencimento'
            },
            'installment_number': {
                'required': true,
                'type': 'integer',
                'submittable': true,
                'label': 'Número da parcela',
                'message': 'Você deve o número da parcela'
            },
            'paid': {
                'required': false,
                'type': 'boolean',
                'submittable': true,
                'label': 'Pago'
            }
        };
    };
    installment.models.Part.prototype = Object.create(abstracts.domain.Model.prototype);
    installment.models.Part.prototype.constructor = installment.models.Part;

    //=========================== COLLECTIONS =================================

    /**
     * Coleção de parcelas.
     * @param {number} contract_pk
     * @constructor
     */
    installment.collections.PartCollection = function(contract_pk) {
        abstracts.domain.Collection.call(this);
        var self = this;

        if (!contract_pk) {
            console.warn('Nenhum ID de contrato informada.')
        }

        this.model_class = installment.models.Part;
        this.uri_manager = uri_manager;
        this.uri = '/contracts/'+contract_pk+'/parts/';

        this._post_add = function () {
            _sort();
            _setNextPart();
        };

        this._post_remove = function () {
            _sort();
            _setNextPart();
        };

        var _setNextPart = function() {
            self.items.forEach(function(item) {
                item.next = false;
            });

            var unpaids = self.items.filter(function(item) {
                return item.get('paid') === false;
            });

            if (unpaids.length === 0) {
                self.items[0].next = true;
                return;
            }

            var part = unpaids[0];
            part.next = true;
        };

        var _sort = function () {
            function compare(a, b) {
                var comparison = 0;
                if (a.get('expiration_date') > b.get('expiration_date')) {
                    comparison = 1;
                }
                else if (a.get('expiration_date') < b.get('expiration_date')) {
                    comparison = -1;
                }
                return comparison;
            }
            self.items.sort(compare);
        };
    };
    installment.collections.PartCollection.prototype = Object.create(abstracts.domain.Collection.prototype);
    installment.collections.PartCollection.prototype.constructor = installment.collections.PartCollection;

})(window.cgsy.abstracts, window.cgsy.installment);