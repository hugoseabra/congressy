function hide_payment_elements() {
    $('#id_boleto').hide();
    $('#id_credit_card').hide();
    $('#id_remove').hide();
    $('#payment_buttons').hide();
    $('#id_button_pay').show();
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
    var amount_id = $('#id_lot').val().toString();
    var lot = lots[amount_id];
    var amount = lot.amount * 100;
    var allow_installment = lot.allow_installment === true;
    var installment_limit = lot.installment_limit;
    var free_installment = parseInt(lot.free_installment);

    transactions = transactions || 'credit_card,boleto';
    allow_installment = allow_installment === true;

    function handleSuccess(data) {
        console.log(data);
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
        $('#id_transaction_type').val(data.payment_method);
        $('#id_amount').val(data.amount);
        $('#id_card_hash').val(data.card_hash);
        $('#id_installments').val(data.installments);
    }

    function handleError(data) {
        if(TRACKER_CAPTURE && Raven){
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

$('#id_remove').on('click', function () { hide_payment_elements(); });