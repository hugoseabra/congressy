//========================= MOBILE TOP MENU =================================//
$(document).ready(function() {
    $('#mobile-top-menu-button').click(function() {
        var block = $("#mobile-top-menu");

        var right = 0;

        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
            right = -285;
        } else {
            $(this).addClass('active');
        }

        block.animate({"right": right}, 300);
    });
});

//============================ FORM SUBMIT ==================================//
function submit_form(form) {
    form = $(form);

    var button;

    button = form.find('button')
        .not(':button[type=button]')
        .not(':button[type=reset]')
    ;

    if (!button.length) {
        button = form.find('input[type=submit]');
    }

    if (button) {
        button.css('visibility', 'hidden');

        var loader = '<div class="loader-block">';
            loader += '<div class="img-block fa-2x">';
            loader += '<i class="fas info-color fa-circle-notch fa-spin"></i>';
            loader += '</div>';
            loader += '</div>';

        loader = $(loader);
        loader.insertAfter(button);
        loader.fadeIn();

        return true;
    }
}

function submit_form_no_loader(form) {
    var button;
    button = $(form).find('button')
        .not(':button[type=button]')
        .not(':button[type=reset]')
    ;

    if (!button.length) {
        button = $(form).find('input[type=submit]');
    }

    if (button) {
        button.text('Aguarde...');
        window.setTimeout(function() { form.submit(); } , 500);
    }
}
//========================== BUSCA POR CEP ==================================//
function showHideCepLoader(show) {
    var cep_el = $('#id_zip_code');
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

/**
 * Remove acentos de strings
 * @param  {String} string acentuada
 * @return {String} string sem acento
 */

var map = {
    "â":"a",
    "Â":"A",
    "à":"a",
    "À":"A",
    "á":"a",
    "Á":"A",
    "ã":"a",
    "Ã":"A",
    "ê":"e",
    "Ê":"E",
    "è":"e",
    "È":"E",
    "é":"e",
    "É":"E",
    "î":"i",
    "Î":"I",
    "ì":"i",
    "Ì":"I",
    "í":"i",
    "Í":"I",
    "õ":"o",
    "Õ":"O",
    "ô":"o",
    "Ô":"O",
    "ò":"o",
    "Ò":"O",
    "ó":"o",
    "Ó":"O",
    "ü":"u",
    "Ü":"U",
    "û":"u",
    "Û":"U",
    "ú":"u",
    "Ú":"U",
    "ù":"u",
    "Ù":"U",
    "ç":"c",
    "Ç":"C"
};

function removerAcentos(s){
    return s.replace(/[\W\[\] ]/g,function(a){return map[a]||a})
};


var zip_code_el = $('#id_zip_code');
var zip_code_initial_value = zip_code_el.val();
function searchByCep() {
    var el = $('#id_zip_code');
    var cep = el.val().replace(/\D/g, '');

    if (cep.length < 8) {
        return;
    }

    if (cep == zip_code_initial_value.replace(/\D/g, '')) {
        return;
    }

    zip_code_initial_value = cep;

    //Expressão regular para validar o CEP.
    var validacep = /^[0-9]{8}$/;

    //Valida o formato do CEP.
    if(!validacep.test(cep)) {
        alert("Formato de CEP inválido.");
        showHideCepLoader(false);
        window.setTimeout(function() { $('#id_zip_code').focus(); }, 100);
        return;
    }

    var street = $('#id_street');
    var number = $('#id_number');
    var complement = $('#id_complement');
    var village = $('#id_village');
    var state = $('#id_state');
    var city = $('#id_city');

    street.val('');
    number.val('');
    complement.val('');
    village.val('');
    // city.val('');

    var url = "https://viacep.com.br/ws/"+ cep +"/json/?callback=?";

    //Consulta o webservice viacep.com.br/
    showHideCepLoader(true);

    $.getJSON(url, function(response) {
        if ('erro' in response) {
            alert("CEP não encontrado.");
            showHideCepLoader(false);
            window.setTimeout(function() { $('#id_zip_code').focus(); }, 100);
            return;
        }

        street.val(response.logradouro);
        village.val(response.bairro);
        state.val(response.uf);

        var cep_city = removerAcentos(response.localidade).toUpperCase();
        console.log(cep_city);

        fetch_cities(state, null, function(cities) {
            $.each(cities, function(i, city) {
               if (cep_city === removerAcentos(city.name)) {
                   $('#id_city_name').val(city.id);
                   $('#id_city').val(city.id);
               }
            });
        });

        showHideCepLoader(false);
        window.setTimeout(function() { $('#id_street').focus(); }, 100);
    });
}

//========================= CAIXA DE FILTROS ================================//
window.cgsy = window.cgsy || {};
(function(window, $) {
    window.cgsy.Filter = {
        init: function(button_el, box_el, active) {
            this.button_el = $(button_el);
            this.box_el = $(box_el);
            this.active = active === true;

            if (active) {
                this.show(false);
            } else {
                this.hide(false);
            }

            return this;
        },
        show: function(fade) {
            fade = fade === true;
            if (!fade) {
                this.box_el.show();
            } else {
                this.box_el.fadeIn();
            }

            this.button_el.addClass('active');
            this.button_el.removeClass('btn-default');
            this.button_el.addClass('btn-primary');

            var that = this;
            this.button_el.unbind('click');
            this.button_el.on('click', function() {
                that.hide(true);
            });
        },
        hide: function(fade) {
            fade = fade === true;
            if (!fade) {
                this.box_el.hide();
            } else {
                this.box_el.fadeOut();
            }

            this.button_el.removeClass('active');
            this.button_el.addClass('btn-default');
            this.button_el.removeClass('btn-primary');

            var that = this;
            this.button_el.unbind('click');
            this.button_el.on('click', function() {
                that.show(true);
            });
        }
    };
})(window, jQuery);