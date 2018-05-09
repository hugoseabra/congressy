"use strict";
window.cgsy.pagarme = window.cgsy.pagarme || {};

(function($, pagarme) {

    var items_list = [];

    pagarme.add_items_list = function(id, name, price, quantity, tangible) {
        items_list.push({
            'id': id,
            'title': name,
            'unit_price': price,
            'quantity': quantity,
            'tangible': tangible
        });
    };
    pagarme.get_list = function (){
        return items_list
    };

    pagarme.create_params = function(amount, interest_rate){

        return {
            amount: amount,
            createToken: 'false',
            paymentMethods: ['credit_card', 'boleto'],
            customerData: false,
            interestRate: interest_rate,
            items: items_list,

        };




    };

})(jQuery, window.cgsy.pagarme);