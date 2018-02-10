function hide_payment_elements() {
    $('#id_boleto').hide();
    $('#id_credit_card').hide();
    $('#id_remove').hide();
    $('#payment_buttons').hide();
    $('#id_button_pay').show();
}

function process_payment(encryption_key, event_name, lots, transactions) {
    var amount_id = $('#id_lot').val().toString();
    var amount = lots[amount_id] * 100;
    var billing_title = 'Inscrição do evento: ' + event_name;
    console.log(amount);
    transactions = transactions || 'credit_card,boleto';

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
                console.error('Unsupported payment type: ' + data.payment_method);
        }
        console.log(data);
        $('#payment_buttons').show();
        $('#id_button_pay').hide();
        $('#id_remove').show();
        $('#id_transaction_type').val(data.payment_method);
        $('#id_amount').val(data.amount);
        $('#id_card_hash').val(data.card_hash);
    }

    function handleError(data) {
        if(TRACKER_CAPTURE && Raven){
            Raven.showReportDialog();
            Raven.captureException(JSON.stringify(data));
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

    checkout.open({
        amount: amount,
        createToken: 'false',
        paymentMethods: transactions,
        customerData: false,
        items: [
            {
                id: '1',
                title: billing_title,
                unit_price: amount,
                quantity: 1,
                tangible: true
            }
        ]
    });
}

$('#id_remove').on('click', function () { hide_payment_elements(); });