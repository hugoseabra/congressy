var button = document.querySelector('#id_button_pay');
var remove = document.querySelector('#id_remove');

$(document).ready(function () {
    $('#id_boleto').hide();
    $('#id_credit_card').hide();
    $('#id_remove').hide();
    $('#payment_buttons').hide();
});

remove.addEventListener('click', function () {
    $('#id_boleto').hide();
    $('#id_credit_card').hide();
    $('#id_remove').hide();
    $('#payment_buttons').hide();
    $('#id_button_pay').show();
});