window.cgsy = window.cgsy || {};
window.cgsy.installment = window.cgsy.installment || {};
window.cgsy.installment.form = window.cgsy.installment.form || {};

(function (abstracts, installment) {
    'use strict';

    installment.form.ContractForm = function(subscription_pk, form_el) {
        abstracts.form.Form.call(this, form_el);
        var self = this;

        this.subscription_pk = subscription_pk;

        /**
         * Engatilhado após salvar.
         * @type {Function}
         */
        this.afterSaveCallback = function(){};

        this.setAfterSaveCallback = function(callback) {
            if (typeof callback === 'function') {
                return;
            }
            self.afterSaveCallback = callback;
        };

        this.postSave = function() {
            window.setTimeout(function() {
                self.disableSubmitButton();
            }, 100);
        };

        /**
         * Callback para tratar da estratégia de salvar.
         * @returns {Promise}
         */
        this.saveHandler = function() {
            return new Promise(function(resolve, reject) {

                var contract = new installment.models.Contract();
                    contract.set('subscription', self.subscription_pk);

                var error_alerter = new abstracts.form.FormErrorAlerter(
                    self.alerter_el,
                    contract.error_handler
                );

                contract.populate(self.getData());

                if (!contract.isValid()) {
                    error_alerter.notify();
                    return reject();
                }

                contract.save().then(function() {

                    if (!contract.isValid()) {
                        error_alerter.notify();
                        return reject();
                    }

                    // // Error handler de PartCollection e de Contract são os mesmos.
                    // // Se PartCollection for inválido, Contract também será.
                    // contract.part_collection.isValid();
                    //
                    // if (!contract.isValid()) {
                    //     return reject();
                    // }

                    // self.saveParts(contract).then(function() {
                    //     self.alerter.clear();
                    //     self.alerter.renderSuccess('Contrato criado com sucesso.');
                    //
                    //     if (self.save_and_remain === false && typeof self.afterSaveCallback === 'function') {
                    //         self.afterSaveCallback();
                    //     }
                    // }, function(reason) {
                    //     error_alerter.notify();
                    //     return reject(reason);
                    // });

                    resolve();
                }, function(reasons) {
                    reject(reasons);
                });
            });
        };

        this.saveParts = function(contract) {
            return new Promise(function(resolve, reject) {
                if (!contract.isValid()) {
                    reject(contract.error_handler);
                    return;
                }
                var parts = contract.part_collection.items;
                if (parts.length) {
                    parts.forEach(function(part) {
                        part.save().then(function() {
                            if (!part.isValid()) {
                                reject(part.error_handler);
                            }
                        });
                    });
                }

                resolve();
            });

        };
    };
    installment.form.ContractForm.prototype = Object.create(abstracts.form.Form.prototype);
    installment.form.ContractForm.prototype.constructor = Object.create(installment.form.ContractForm);

})(window.cgsy.abstracts, window.cgsy.installment);