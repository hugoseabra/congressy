"use strict";
window.cgsy.addon = window.cgsy.addon || {};

(function($, addon) {

    var theme_limits = [];

    addon.add_theme_limit = function(id, name, limit) {
        theme_limits.push({
            'id': id,
            'name': name,
            'limit': limit
        });
    };

    addon.get_theme_limit = function(id) {
        var selected_theme = null;

        $.each(theme_limits, function(i, theme_limit) {
           if (parseInt(theme_limit['id']) === parseInt(id)) {
               selected_theme = theme_limit;
           }
        });
        return selected_theme;
    };

    addon.show_theme_limit = function() {
        var theme_limit_block = $('#theme-limit-block');
        var theme_el = $('#id_theme');

        if (!theme_el.val()) {
            theme_limit_block.fadeOut();
            return;
        }

        var theme_limit = addon.get_theme_limit(theme_el.val());
        if (!theme_limit) {
            alert('Erro ao encontrar limite de tema.');
            return;
        }

        if (parseInt(theme_limit.limit) === 0) {
            theme_limit_block.fadeOut();
            return;
        }

        theme_limit_block.fadeIn();

        $('#theme_limit_name').text(theme_limit.name);

        var subs_label;
        subs_label = theme_limit.limit > 1 ? 'inscrições' : 'inscrição';
        $('#theme_limit_limit').text(theme_limit.limit + ' ' + subs_label);
    };

    addon.create_events = function () {
        $('#id_has_price').on('change', function () {
            addon.show_hide_price_block();
        });

        $('#id_theme').on('change', function() {
            addon.show_theme_limit();
        });
    };

    addon.show_hide_price_block = function() {
        var has_price = $('#id_has_price');
        var price_block = $('#price-block');

        if (has_price.prop('checked') === true) {
            price_block.fadeIn();
        } else {
            price_block.fadeOut();
        }
    }

})(jQuery, window.cgsy.addon);