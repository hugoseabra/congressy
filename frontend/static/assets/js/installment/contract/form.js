window.cgsy = window.cgsy || {};
window.cgsy.installment = window.cgsy.installment || {};
window.cgsy.installment.form = window.cgsy.installment.form || {};

(function (abstracts, installment) {
    'use strict';

    installment.form.ContractForm = function(form_el) {
        abstracts.form.Form.call(this, form_el);

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

        this.save = function() {
            self.processing = true;

            var remain_switch = self.getEl('close-after-save-switch');
            if (remain_switch && remain_switch.length) {
                self.save_and_remain = remain_switch.prop('checked') === false;
            }

            return new Promise(function(resolve, reject) {
                if (self.processing === true) {
                    reject('Processando');
                    return;
                }

                self.processing = true;

                var contract = new installment.models.Contract();
                var error_alerter = new abstracts.form.FormErrorAlerter(
                    self.alerter_el,
                    contract.error_handler
                );

                self.sync().then(function() {
                    self.alerter.clear();

                    contract.populate(self.getData());

                    // Error handler de PartCollection e de Contract são os mesmos.
                    // Se PartCollection for inválido, Contract também será.
                    contract.part_collection.isValid();

                    if (!contract.isValid()) {
                        return Promise.reject();
                    }

                    contract.save().then(function() {
                        self.alerter.clear();

                        if (!contract.isValid()) {
                            return Promise.reject();
                        }

                        self.saveParts(contract).then(function() {
                            self.alerter.clear();
                            self.alerter.renderSuccess('Contrato criado com sucesso.');

                            if (self.save_and_remain === false && typeof self.afterSaveCallback === 'function') {
                                self.afterSaveCallback();
                            }
                        }).catch(function(error_handler) {
                            return Promise.reject();
                        });

                        self.save_and_remain = false;
                        self.processing = false;
                        self.enableSubmitButton();
                        resolve(self.getData());
                    });

                }).catch(function(reason) {
                    contract.delete();

                    error_alerter.notify();
                    self.save_and_remain = false;
                    self.processing = false;
                    self.enableSubmitButton();
                    reject(reason);
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