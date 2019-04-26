function send(url, method, data, success_callback, error_callback) {
    // CSRF code
    function getCookie(name) {
        var cookieValue = null;
        var i = 0;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (i; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajax({
        url: url,
        type: method,
        data: data || {},
        encode: true,
        crossDomain: false,
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: success_callback || function (result) {
            console.log(result);
        },
        error: error_callback || function (err) {
            console.error(err)
        }
    });
}

function show_hide_payment_block(action) {
    action = action === true;
    var payment_block = $('#payment-block');

    if (action === true) {
        payment_block.show();
    } else {
        payment_block.hide();
        hide_payment_elements();
    }
}

function fetch_cities(uf_el, city_list_el, city_hidden_el, selected_value, callback) {
    uf_el = $(uf_el);
    city_list_el = $(city_list_el);
    city_hidden_el = $(city_hidden_el);
    selected_value = selected_value || '';
    callback = callback || null;

    $.ajax({
        url: "/api/cities/?uf=" + $(uf_el).val() + '&length=1000',
        success: function (result) {

            var listitems = [];
            var ids = [];

            $.each(result.results, function (key, value) {
                listitems.push('<option value=' + value.id + '>' + value.name + '</option>');
                ids.push(value.id)
            });

            city_list_el.html(listitems.join(''));
            city_list_el.prop('disabled', false);

            if (selected_value) {
                window.setTimeout(function () {
                    city_list_el.val(selected_value);
                    city_hidden_el.val(selected_value);
                }, 500);
            } else {
                city_list_el.val(ids[0]);
                city_hidden_el.val(ids[0]);
            }

            if (callback) {
                callback(result.results)
            }
        },
        error: function (err) {
            throw err;
        }
    });
}

function hotsiteShowHideCepLoader(show) {

    var cep_el = $('#id_person-zip_code');
    if (!cep_el.length) {
        return;
    }
    var el = $('#cep_loader');
    if (show === true) {
        el.fadeIn();
        cep_el.attr('disabled', 'disabled').addClass('disabled');
        cep_el.css('background-color', '#fff');
    } else {
        el.fadeOut();
        cep_el.removeAttr('disabled').removeClass('disabled');
        cep_el.removeAttr('style');
    }
}

function repopulate_cities(uf_el, selected_value, callback) {
    selected_value = selected_value || '';

    city_el = $('#id_city_name');


    $.ajax({
        url: "/api/cities/?uf=" + uf_el + '&length=1000',
        success: function (result) {

            var listitems = [];
            var ids = [];

            $.each(result.results, function (key, value) {
                listitems.push('<option value=' + value.id + '>' + value.name + '</option>');
                ids.push(value.id)
            });

            if (selected_value) {
                window.setTimeout(function () {
                    city_el.val(selected_value);
                    city_el.val(selected_value);
                }, 500);
            } else {
                city_el.val(ids[0]);
            }

            city_el.html(listitems.join(''));
            city_el.prop('disabled', false);

            if (callback) {
                callback(result.results)
            }
        },
        error: function (err) {
            throw err;
        }
    });
}

function hotsiteRepopulate_cities(uf_el, selected_value, callback) {
    selected_value = selected_value || '';

    city_el = $('#id_person-city_name');


    $.ajax({
        url: "/api/cities/?uf=" + uf_el + '&length=1000',
        success: function (result) {

            var listitems = [];
            var ids = [];

            $.each(result.results, function (key, value) {
                listitems.push('<option value=' + value.id + '>' + value.name + '</option>');
                ids.push(value.id)
            });

            if (selected_value) {
                window.setTimeout(function () {
                    city_el.val(selected_value);
                    city_el.val(selected_value);
                }, 500);
            } else {
                city_el.val(ids[0]);
            }

            city_el.html(listitems.join(''));
            city_el.prop('disabled', false);

            if (callback) {
                callback(result.results)
            }
        },
        error: function (err) {
            throw err;
        }
    });
}

var common_lots_content = null;

function load_coupon() {
    var url = $('#id_coupon_url');

    if (!url) {
        return;
    }
    url = url.val();
    if (!url) {
        return;
    }

    var coupon = $('#id_coupon');
    if (!coupon) {
        return;
    }

    var coupon_value = coupon.val();
    if (!coupon_value) {
        return;
    }

    var coupon_block = $('.coupon-block');

    var button = $('#button_coupon');
    button.addClass('disabled').attr('disabled', 'disabled').text('Aguarde...');

    var lot_fields = $('#lots-field');

    common_lots_content = lot_fields.html();

    send(
        url,
        'POST',
        {'coupon': coupon_value},
        function (response) {

            response = JSON.parse(response);

            var lot = response.lot;
            var lot_select = $('#id_lot-lots');

            console.log(response);

            button.removeClass('disabled').removeAttr('disabled').text('Aplicar');
            coupon_block.fadeOut(function() {
                lot_select.append(lot.option);
                lot_select.val(lot.id);
                lot_select.css("pointer-events", "none");
                $('#lot_display_publicly').text(lot.public_display + lot.is_free);
                $('#lot_exhibition_code').text(lot.exhibition_code);

                lot_fields.show();
            });



            // window.setTimeout(function () {
            //     start_popover();
            // }, 300);
        },
        function () {

            coupon.val('');

            alert('Cupom inválido.');
            // hide_coupon();

            coupon.focus();
            button.removeClass('disabled').removeAttr('disabled').text('Aplicar');
            coupon_block.fadeIn();

            // window.setTimeout(function () {
                // start_popover();
            // }, 300);
        }
    );

    $('#coupon_link').popover('hide');
}

function hide_coupon() {

    var lot_fields = $('#lots-field');
    var original_lots_field = $('#original-lots-field');
    var coupon_block = $('.coupon-block');

    lot_fields.hide();
    original_lots_field.show();
    coupon_block.fadeIn();
    $('#id_coupon').val('');

    $.each($('option', '#id_lot-lots'), function() {
        var el = $(this);
        if (el.attr('value'), el.data('coupon-type')) {
            el.remove();
        }
    });

    $('#id_lot-lots').removeAttr('style');
}

function start_popover() {
    $('[data-toggle="popover"]').popover({
        placement: 'bottom',
        container: 'body',
        trigger: 'click'
    });
}

(function ($) {
    $(document).ready(function () {
        window.setTimeout(function () {
            $('#id_person-cpf').mask("999.999.999-99");
            start_popover();

            $(document).on("input", ".numeric", function () {
                this.value = this.value.replace(/\D/g, '');
            });

            var institution_cnpj = $('#id_person-institution_cnpj');
            if (institution_cnpj.length) {
                institution_cnpj.mask("99.999.999/9999-99");
            }

            var city_el = $('#id_person-city_name');
            var submit = $('form').find(':submit');

            $('#id_person-state').change(function () {
                city_el.html($('<option>').text('Carregando...'));
                submit.prop('disabled', true);

                var enableButton = function () {
                    submit.prop('disabled', false);
                };

                var that = $(this);
                window.setTimeout(function () {
                    fetch_cities($(that), $('#id_person-city_name'), $('#id_person-city'), null, enableButton);
                }, 500);
            });

            city_el.change(function () {
                $("#id_person-city").val($(this).val());
            });

        }, 350);
    });
})(jQuery);
