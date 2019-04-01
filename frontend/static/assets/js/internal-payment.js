window.cgsy = window.cgsy || {};
window.cgsy.payment = window.cgsy.payment || {};
window.cgsy.payment_form = window.cgsy.payment_form || {};
window.cgsy.pagarme = window.cgsy.pagarme || {};


(function ($, payment) {
    "use strict";

    payment.Payment = function () {
        var MAX_INSTALLMENTS = 10;

        var allow_installment = true;
        var interest_rate = 0;
        var max_installments = 10;
        var free_rate_installments = 0;

        var total_amount = 0;
        var items = [];
        var enable_boleto = false;

        var _amount_as_payment = function (amount) {
            var split = String(amount.toFixed(2)).split('.');
            var cents = String(split[1]);
            if (split.length === 1) {
                cents = '00';
            }

            if (cents.length === 1) {
                cents += 0;
            }
            return String(split[0]) + String(cents);
        };


        this.enable_boleto = function () {
            enable_boleto = true;
        };

        this.disable_installment = function () {
            allow_installment = false;
        };

        this.set_interest_rate = function (rate) {
            interest_rate = rate;
        };

        this.set_max_installments = function (num) {
            num = parseInt(num);
            if (num > MAX_INSTALLMENTS) {
                num = MAX_INSTALLMENTS;
            }
            max_installments = num;
        };

        this.set_free_rate_installments = function (num) {
            num = parseInt(num);
            if (num > MAX_INSTALLMENTS) {
                num = MAX_INSTALLMENTS;
            }

            free_rate_installments = num;
        };

        this.add_item = function (type, id, title, quantity, amount) {
            total_amount += amount;
            items.push({
                "object": "item",
                "id": type + "-" + id,
                "title": title,
                "unit_price": _amount_as_payment(amount),
                "quantity": quantity,
                "tangible": false
            })
        };

        this.get_items = function () {
            return items;
        };

        this.get_payment_data = function () {

            if (!interest_rate) {
                alert('Erro: fale com o suporte.');
                console.error('Não há taxa de juros no pagamento configurada.');
                return;
            }

            var methods = 'credit_card';
            if (enable_boleto === true) {
                methods += ',boleto';
            }

            var params = {
                amount: _amount_as_payment(total_amount),
                createToken: 'false',
                paymentMethods: methods,
                customerData: false,
                interestRate: interest_rate,
                items: items
            };

            if (allow_installment) {

                max_installments = parseInt(max_installments);

                if (max_installments > MAX_INSTALLMENTS) {
                    max_installments = MAX_INSTALLMENTS;
                }

                params['maxInstallments'] = max_installments;

                if (free_rate_installments) {
                    params['freeInstallments'] = parseInt(free_rate_installments);
                }
            }

            return params;
        };
    };

})(jQuery, window.cgsy.payment);

(function ($, payment_form) {
    "use strict";


    payment_form.success = function (data) {

        var form_el = $('#checkout_form');

        form_el.find('input[name="transaction_type"]').val(data.payment_method);
        form_el.find('input[name="amount"]').val(data.amount);
        form_el.find('input[name="card_hash"]').val(data.card_hash);
        form_el.find('input[name="installments"]').val(data.installments);

        form_el.attr({
            'method': 'POST',
            'action': "/pagarme/checkout/"
        });

        form_el.submit();
    };


    payment_form.error = function (data) {
        alert(
            "Ocorreu um erro durante o processamento," +
            " tente novamente depois."
        );
    };

})(jQuery, window.cgsy.payment_form);

(function ($, payment_form, pagarme, PagarMeCheckout) {
    "use strict";

    pagarme.process_payment = function (encryption_key, payment) {

        var checkout = new PagarMeCheckout.Checkout({
            encryption_key: encryption_key,
            success: payment_form.success,
            error: payment_form.error
        });

        checkout.open(payment.get_payment_data());
    };


})(jQuery, window.cgsy.payment_form, window.cgsy.pagarme, window.PagarMeCheckout);
