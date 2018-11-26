window.cgsy = window.cgsy || {};
window.cgsy.installment = window.cgsy.installment || {};

(function (abstracts, installment) {
    'use strict';

    //=========================== MODELS ======================================

    installment.models = {};

    var uri = new abstracts.uri.APIBaseUrl('', 'http://localhost:8000/api/');
    var uri_manager = new abstracts.uri.URIManager(uri,  '/installment');

    /**
     * Modelo de contrato de parcelamento.
     * @param {number} pk
     * @constructor
     */
    installment.models.Contract = function (pk) {
        // Configuration
        abstracts.domain.Model.call(this, pk && pk > 0 ? parseInt(pk) : undefined);
        var self = this;

        this.verbose_name = 'contrato de parcelamento';
        this.verbose_name_plural = 'contratos de parcelamento';

        this.uri_manager = uri_manager;
        this.creation_uri = '/contracts/';
        this.uri = '/contracts/{{pk}}/';

        /**
         * Coleção de parcelas.
         * @type {installment.collections.PartCollection}
         */
        this.part_collection = null;

        /**
         * Campos
         * @type {Object}
         */
        this.fields = {
            'subscription': {
                'required': true,
                'type': 'string',
                'submittable': true,
                'blank': true,
                'label': 'Inscrição',
                'message': 'Você deve informar a inscrição'
            },
            'amount': {
                'required': true,
                'type': 'float',
                'submittable': true,
                'label': 'Valor',
                'message': 'Você deve informar o valor'
            },
            'num_installments': {
                'required': true,
                'type': 'integer',
                'submittable': true,
                'label': 'Quantidade de Parcelas',
                'message': 'Você deve a quantidade de parcelas'
            },
            'expiration_day': {
                'required': true,
                'submittable': true,
                'label': 'Dia base de vencimento',
                'type': 'integer',
                'message': 'Você deve informar o dia base de vencimento'
            },
            'status': {
                'required': false,
                'submittable': false,
                'label': 'Status',
                'type': 'string'
            }
        };

        this.createPartCollection = function() {
            if (self.isNew()) {
                self.part_collection = null;
                return undefined;
            }
            self.part_collection = new installment.collections.PartCollection(self.pk);
            self.part_collection.error_handler = self.error_handler;

            return self.part_collection;
        };

        /**
         * Busca parcelas.
         * @returns {Promise}
         */
        this.fetchParts = function() {
            if (self.isNew()) {
                return new Promise(function(resolve) { resolve(); });
            }

            return new Promise(function(resolve, reject) {
                self.createPartCollection();

                if (!self.part_collection) {
                    reject();
                    return;
                }

                self.part_collection.fetch().then(function() {
                    if (!self.part_collection.isValid()) {
                        reject(self.error_handler);
                        return;
                    }
                    resolve();
                });
            });
        };
    };
    installment.models.Contract.prototype = Object.create(abstracts.domain.Model.prototype);
    installment.models.Contract.prototype.constructor = installment.models.Contract;

    //=========================== COLLECTIONS =================================
    installment.collections = {};

    /**
     * Coleção de contratos
     * @param {string} subscription_pk
     * @constructor
     */
    installment.collections.ContractCollection = function(subscription_pk) {
        abstracts.domain.Collection.call(this);

        if (!subscription_pk) {
            console.warn('Nenhum UUID de inscrição informada.')
        }

        this.model_class = installment.models.Contract;
        this.uri_manager = uri_manager;
        this.uri = '/contracts/?subscription=' + subscription_pk;

        this.addUriFilter = function(key, value) {
            self.uri += '&{}={}'.format(key, value);
        };
    };
    installment.collections.ContractCollection.prototype = Object.create(abstracts.domain.Collection.prototype);
    installment.collections.ContractCollection.prototype.constructor = installment.collections.ContractCollection;

})(window.cgsy.abstracts, window.cgsy.installment);