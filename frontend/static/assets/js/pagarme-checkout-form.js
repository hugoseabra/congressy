window.cgsy = window.cgsy || {};
window.cgsy.raven = window.cgsy.raven || {};
window.cgsy.pagarme = window.cgsy.pagarme || {};

(function ($, pagarme) {
    "use strict";

    pagarme.CheckoutForm = function(form_parent_el) {
        form_parent_el = $(form_parent_el);
        var next_url = null;

        this.setNextUrl = function(url) {
            next_url = url;
        };

        this.send = function(checkout_url) {
            var form = form_parent_el.find('form');
            form.attr({
                'method': 'POST',
                'action': checkout_url
            });

            var next_hidden_field = form.find('input[name="next"]');
            if (next_url) {
                next_hidden_field.val(next_url);
            }
            window.setTimeout(function() { form.submit(); }, 300);
        };

        // @TODO renderizar formulário de maneira padronizada

    };

})(jQuery, window.cgsy.pagarme);
