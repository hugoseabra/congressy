window.cgsy.raven = window.cgsy.raven || {};
window.cgsy.payment = window.cgsy.payment || {};
window.cgsy.payment_form = window.cgsy.payment_form || {};
window.cgsy.pagarme = window.cgsy.pagarme || {};

(function(window, raven) {
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

(function($, payment, raven) {
    "use strict";

    payment.Payment = function() {
        const MAX_INSTALLMENTS = 10;

        var allow_installment = true;
        var interest_rate = 0;
        var max_installments = 10;
        var free_rate_installments = 0;

        var total_amount = 0;
        var items = [];
        var enable_boleto = false;

        var _amount_as_payment = function(amount) {
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

        this.enable_boleto = function() { enable_boleto = true; };

        this.disable_installment = function() { allow_installment = false; };

        this.set_interest_rate = function(rate) { interest_rate = rate; };

        this.set_max_installments = function(num) {
            num = parseInt(num);
            if (num > MAX_INSTALLMENTS) { num = MAX_INSTALLMENTS; }
            max_installments = num;
        };

        this.set_free_rate_installments = function (num) {
            num = parseInt(num);
            if (num > MAX_INSTALLMENTS) {
                num = MAX_INSTALLMENTS;
            }

            free_rate_installments = num;
        };

        this.add_item = function(type, id, title, quantity, amount) {
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

        this.get_items = function() {
            return items;
        };

        this.get_payment_data = function() {

            if (!interest_rate) {
                alert('Erro: fale com o suporte.');
                raven.trigger('Não há taxa de juros no pagamento configurada.');
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
                } else {
                    params['freeInstallments'] = 1;
                }
            }

            return params;
        };
    };

})(jQuery, window.cgsy.payment, window.cgsy.raven);

(function ($, payment_form, raven) {
    "use strict";

    var _hide_payment_elements = function () {
        $('#id_boleto').hide();
        $('#id_credit_card').hide();
        $('#id_remove').hide();
        $('#payment_buttons').hide();
        $('#next_btn').attr("disabled", true);
        $('#id_button_pay').show();

        $('#id_payment-card_hash').val('');
        $('#id_payment-installments').val('');
        $('#id_payment-transaction_type').val('');
    };

    payment_form.success = function (data) {
        _hide_payment_elements();

        switch (data.payment_method) {
            case 'boleto':
                $('#id_boleto').show();
                break;
            case 'credit_card':
                $('#id_credit_card').show();
                break;
            default:
                alert(
                    "Ocorreu um erro durante o processamento," +
                    " tente novamente depois."
                );
                var msg = 'Tipo de pagamento não suportado: ' + data.payment_method;
                raven.trigger(msg);
                raven.show_report_dialog();
        }

        $('#payment_buttons').show();
        $('#id_remove').show();
        $('#next_btn').attr("disabled", false);
        $('#id_payment-transaction_type').val(data.payment_method);
        $('#id_payment-amount').val(data.amount);
        $('#id_payment-card_hash').val(data.card_hash);
        $('#id_payment-installments').val(data.installments);

        var payment_btn_el = $('#id_button_pay');
        payment_btn_el.attr('disabled', 'disabled');
        payment_btn_el.text('Aguarde...');

        $('#payment_form').submit();
    };

    payment_form.error = function (data) {
        alert(
            "Ocorreu um erro durante o processamento," +
            " tente novamente depois."
        );

        raven.trigger(JSON.stringify(data));
        raven.show_report_dialog();
    };

})(jQuery, window.cgsy.payment_form, window.cgsy.raven);

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
