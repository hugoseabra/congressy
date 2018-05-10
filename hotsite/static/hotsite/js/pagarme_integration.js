"use strict";
window.cgsy.pagarme = window.cgsy.pagarme || {};

(function ($, pagarme) {

    var items_list = [];

    pagarme.add_items_list = function (id, name, price, quantity, tangible) {
        items_list.push({
            'id': id,
            'title': name,
            'unit_price': price,
            'quantity': quantity,
            'tangible': tangible
        });
    };
    pagarme.get_list = function () {
        return items_list
    };

    pagarme.create_params = function (amount, interest_rate) {

        return {
            amount: amount,
            createToken: false,
            paymentMethods: ['credit_card', 'boleto'],
            customerData: false,
            interestRate: interest_rate,
            items: items_list,

        };


    };

    pagarme.create_checkout_object = function (params, lot, encryption_key) {


        var allow_installment = lot.allow_installment === true;
        var installment_limit = lot.installment_limit;
        var free_installment = parseInt(lot.free_installment);
        allow_installment = allow_installment === true;

        function handleSuccess(data) {
            hide_payment_elements();

            switch (data.payment_method) {
                case 'boleto':
                    $('#id_boleto').show();
                    break;
                case 'credit_card':
                    $('#id_credit_card').show();
                    break;
                default:
                    var msg = 'Unsupported payment type: ' + data.payment_method;
                    Raven.captureException(msg);
                    alert(
                        "Ocorreu um erro durante o processamento," +
                        " tente novamente depois."
                    );
                    Raven.showReportDialog();
            }

            $('#payment_buttons').show();
            $('#id_button_pay').hide();
            $('#id_remove').show();
            $('#next_btn').attr("disabled", false);
            $('#id_payment-transaction_type').val(data.payment_method);
            $('#id_payment-amount').val(data.amount);
            $('#id_payment-card_hash').val(data.card_hash);
            $('#id_payment-installments').val(data.installments);
        }

        function handleError(data) {
            if (TRACKER_CAPTURE && Raven) {
                Raven.captureException(JSON.stringify(data));
                Raven.showReportDialog();
            } else {
                alert(
                    "Ocorreu um erro durante o processamento," +
                    " tente novamente depois."
                );
            }
        }

        var checkout = new PagarMeCheckout.Checkout({
            encryption_key: encryption_key,
            success: handleSuccess,
            error: handleError
        });

        if (allow_installment) {
            if (parseInt(installment_limit) > 10) {
                installment_limit = 10;
            }
            params['maxInstallments'] = parseInt(installment_limit) || 10;

            if (parseInt(free_installment) > 0) {
                params['freeInstallments'] = parseInt(free_installment);
            }
        }

        return checkout.open(params);

    };

})(jQuery, window.cgsy.pagarme);