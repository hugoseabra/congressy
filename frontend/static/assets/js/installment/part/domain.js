window.cgsy = window.cgsy || {};
window.cgsy.installment = window.cgsy.installment || {};
window.cgsy.installment.models = window.cgsy.installment.models || {};
window.cgsy.installment.collection = window.cgsy.installment.collection || {};

(function (abstracts, installment) {
    'use strict';

    //=========================== MODELS ======================================

    var uri = new abstracts.uri.APIBaseUrl('', 'http://localhost:8000/api/');
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

        this.uri_manager = uri_manager;
        this.creation_uri = '/parts/';
        this.uri = '/parts/{{pk}}/';

        // Fields
        this.fields = {
            'constract': {
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
            'installment_numbner': {
                'required': true,
                'type': 'integer',
                'submittable': true,
                'label': 'Número da parcela',
                'message': 'Você deve o número da parcela'
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

        if (!contract_pk) {
            console.warn('Nenhum ID de contrato informada.')
        }

        this.model_class = installment.models.Contract;
        this.uri_manager = uri_manager;
        this.uri = '/contracts/'+contract_pk+'/parts/';
    };
    installment.collections.PartCollection.prototype = Object.create(abstracts.domain.Collection.prototype);
    installment.collections.PartCollection.prototype.constructor = installment.collections.PartCollection;

})(window.cgsy.abstracts, window.cgsy.installment);