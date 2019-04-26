window.cgsy = window.cgsy || {};
window.cgsy.installment = window.cgsy.installment || {};
window.cgsy.installment.form = window.cgsy.installment.form || {};

(function (abstracts, installment) {
    'use strict';

    installment.form.ContractForm = function(subscription_pk, form_el) {
        abstracts.form.Form.call(this, form_el);
        var self = this;

        self.strictModeOff();

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

                // Extrair dados das parcelas.
                var data = self.getData();
                var part_exp_dates = [];
                for (var part = 1; part <= data['num_installments']; part++) {
                    var f_name = 'exp_date' + part;
                    part_exp_dates.push(data[f_name]);
                    delete data[f_name];
                }

                var part_amount = data['part_amount'];
                var split_amount = part_amount.split(',');
                part_amount = parseFloat(split_amount.join('.'));

                delete data['part_amount'];

                contract.populate(data);

                if (!contract.isValid()) {
                    error_alerter.notify();
                    return reject();
                }

                contract.save().then(function() {

                    if (!contract.isValid()) {
                        error_alerter.notify();
                        return reject();
                    }

                    var factory = new installment.service.PartCollectionFactory(contract);
                    factory.create(part_exp_dates, part_amount).then(function() {
                        resolve();
                    }, function(reasons) {
                        reject(reasons);
                    });

                }, function(reasons) {
                    reject(reasons);
                });
            });
        };
    };
    installment.form.ContractForm.prototype = Object.create(abstracts.form.Form.prototype);
    installment.form.ContractForm.prototype.constructor = installment.form.ContractForm;

})(window.cgsy.abstracts, window.cgsy.installment);