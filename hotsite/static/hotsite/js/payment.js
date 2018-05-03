function hide_payment_elements() {
    $('#id_boleto').hide();
    $('#id_credit_card').hide();
    $('#id_remove').hide();
    $('#payment_buttons').hide();
    $('#next_btn').attr("disabled", true);
    $('#id_button_pay').show();

    $('#id_payment-card_hash').val('');
    $('#id_payment-installments').val('');
    $('#id_payment-transaction_type').val('');
}

function normalize_amount_as_payment(amount) {
    amount = String(amount);
    var len = amount.length;
    var value = amount.substring(0, len - 2);
    var cents = amount.substr(len - 2);
    value = value.replace('.', '').replace('.', '').replace(',', '');
    return String(value) + String(cents);
}

function process_payment(
    encryption_key,
    interest_rate,
    event_name,
    lots,
    transactions
) {
    if (!interest_rate) {
        alert('Erro: fale com o suporte.');
        Raven.captureException(e);
        return;
    }

    var billing_title = 'Inscrição do evento: ' + event_name;
    var amount = normalize_amount_as_payment($('#id_payment-amount').val());


    var lot = JSON.parse($('#id_payment-lot_as_json').val());
    var allow_installment = lot.allow_installment === true;
    var installment_limit = lot.installment_limit;
    var free_installment = parseInt(lot.free_installment);

    transactions = transactions || 'credit_card,boleto';
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

    var params = {
        amount: amount,
        createToken: 'false',
        paymentMethods: transactions,
        customerData: false,
        interestRate: interest_rate,
        items: [
            {
                id: '1',
                title: billing_title,
                unit_price: amount,
                quantity: 1,
                tangible: false
            }
        ]
    };

    if (allow_installment) {
        if (parseInt(installment_limit) > 10) {
            installment_limit = 10;
        }
        params['maxInstallments'] = parseInt(installment_limit) || 10;

        if (parseInt(free_installment) > 0) {
            params['freeInstallments'] = parseInt(free_installment);
        }
    }

    checkout.open(params);
}

function process_single_lot_payment(
    encryption_key,
    interest_rate,
    event_name,
    lot,
    transactions
) {
    if (!interest_rate) {
        alert('Erro: fale com o suporte.');
        Raven.captureException(e);
        return;
    }

    var billing_title = 'Inscrição do evento: ' + event_name;
    var amount = normalize_amount_as_payment(lot.price);


    var allow_installment = lot.allow_installment === true;
    var installment_limit = lot.installment_limit;
    var free_installment = parseInt(lot.free_installment);

    transactions = transactions || 'credit_card,boleto';
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

    var params = {
        amount: amount,
        createToken: 'false',
        paymentMethods: transactions,
        customerData: false,
        interestRate: interest_rate,
        items: [
            {
                id: '1',
                title: billing_title,
                unit_price: amount,
                quantity: 1,
                tangible: false
            }
        ]
    };

    if (allow_installment) {
        if (parseInt(installment_limit) > 10) {
            installment_limit = 10;
        }
        params['maxInstallments'] = parseInt(installment_limit) || 10;

        if (parseInt(free_installment) > 0) {
            params['freeInstallments'] = parseInt(free_installment);
        }
    }

    checkout.open(params);
}

function process_single_lot_payment_with_optional_products(
    encryption_key,
    interest_rate,
    event_name,
    lot,
    optionals,
    transactions
) {
    if (!interest_rate) {
        alert('Erro: fale com o suporte.');
        Raven.captureException(e);
        return;
    }

    var billing_title = 'Inscrição do evento: ' + event_name;
    var optional_amount = 0;
    var amount = 0;
    var subscription_amount = normalize_amount_as_payment(lot.price);

    jQuery.each(optionals, function (i, val) {
       optional_amount += parseInt(normalize_amount_as_payment(val.price));
    });


    amount += parseInt(subscription_amount);
    amount += parseInt(optional_amount);

    var allow_installment = lot.allow_installment === true;
    var installment_limit = lot.installment_limit;
    var free_installment = parseInt(lot.free_installment);

    transactions = transactions || 'credit_card,boleto';
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

    var params = {
        amount: amount,
        createToken: 'false',
        paymentMethods: transactions,
        customerData: false,
        interestRate: interest_rate,
        items: [
            {
                id: 1,
                title: billing_title,
                unit_price: subscription_amount,
                quantity: 1,
                tangible: false
            }
        ]
    };

    jQuery.each(optionals, function (i, val) {

        var product = {};
        product.id = i;
        product.title = val.name;
        product.unit_price = val.price;
        product.quantity = 1;
        product.tangible = true;
        console.log(product);

        params.items.push(product)

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

    checkout.open(params);
}


$('#id_remove').on('click', function () {
    hide_payment_elements();
});