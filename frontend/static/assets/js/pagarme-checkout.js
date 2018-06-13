window.cgsy = window.cgsy || {};
window.cgsy.raven = window.cgsy.raven || {};
window.cgsy.pagarme = window.cgsy.pagarme || {};

(function (window, raven) {
    "use strict";

    var has_raven = window.hasOwnProperty('Raven');

    raven.trigger = function (msg) {
        console.error(msg);
        if (has_raven) {
            window.Raven.captureException(msg);
        }
    };

    raven.show_report_dialog = function () {
        if (has_raven) {
            window.Raven.showReportDialog();
        }
    };

})(window, window.cgsy.raven);

(function ($, PagarMeCheckout, pagarme, raven) {
    "use strict";

    var amount_as_payment = function (amount) {
        var split = String(amount).split('.');
        var cents = String(split[1]);
        if (split.length === 1) {
            cents = '00';
        }

        if (cents.length === 1) {
            cents += 0;
        }
        return String(split[0]) + String(cents);
    };

    var Basket = function () {
        this.total_amount = 0;
        this.items = [];

        this.add = function (type, id, title, quantity, amount) {
            this.total_amount += amount;
            var data = {
                "object": "item",
                "id": type + "-" + id,
                "title": title,
                "unit_price": amount_as_payment(amount),
                "quantity": quantity,
                "tangible": false
            };
            console.log('added item: ' + JSON.stringify(data));
            console.log('amount: ' + this.total_amount);
            console.log('-----------------');
            this.items.push(data)
        };
    };

    var Installments = function (rate, max_installments, free_installments) {
        const MAX_INSTALLMENTS = 10;

        this.rate = rate || 2.29;
        this.max_installments = max_installments || 10;
        this.free_installments = free_installments || 0;

        if (max_installments > MAX_INSTALLMENTS) {
            this.max_installments = MAX_INSTALLMENTS;
        }
    };

    pagarme.Checkout = function (encryption_key, methods, form_el) {
        form_el = $(form_el);

        var installments = null;
        var basket = new Basket();

        var default_error_callback = function (data) {
            alert(
                "Ocorreu um erro durante o processamento," +
                " tente novamente depois."
            );

            raven.trigger(JSON.stringify(data));
            raven.show_report_dialog();
        };
        var error_callback = default_error_callback;

        var default_success_callback = function (data) {
            console.log('checkout success');
            if (form_el) {
                form_el.find('input[name="transaction_type"]').val(data.payment_method);
                form_el.find('input[name="amount"]').val(data.amount);
                form_el.find('input[name="card_hash"]').val(data.card_hash);
                form_el.find('input[name="installments"]').val(data.installments);
            }
        };

        var success_callback = default_success_callback;


        var get_data = function () {

            if (!methods) {
                alert('Erro: métodos de pagamento não encontrado. Fale com o suporte.');
                raven.trigger('Erro: métodos de pagamento não encontrado. Fale com o suporte.');
                return;
            }

            var params = {
                amount: amount_as_payment(basket.total_amount),
                createToken: 'false',
                paymentMethods: methods,
                customerData: false,
                items: basket.items
            };

            if (installments) {
                params['interestRate'] = installments.rate;
                params['maxInstallments'] = installments.max_installments;
                params['freeInstallments'] = installments.free_installments;
            }

            return params;
        };

        this.enable_installments = function (rate, max_installments, free_installments) {
            installments = new Installments(rate, max_installments, free_installments);
        };

        this.add_item = function (type, id, title, quantity, amount) {
            basket.add(type, id, title, quantity, amount);
        };


        this.setSuccessCallback = function (callback) {
            success_callback = function (data) {
                callback(data);
                default_success_callback(data);
            };
        };

        this.setErrorCallback = function (callback) {
            error_callback = function (data) {
                callback(data);
                default_error_callback(data);
            };
        };

        this.run = function () {
            var checkout = new PagarMeCheckout.Checkout({
                encryption_key: encryption_key,
                success: success_callback,
                error: error_callback
            });

            checkout.open(get_data());
        };
    };

})(jQuery, PagarMeCheckout, window.cgsy.pagarme, window.cgsy.raven);
