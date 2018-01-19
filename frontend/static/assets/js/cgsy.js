//========================= MOBILE TOP MENU =================================//
$(document).ready(function() {
    $('#mobile-top-menu-button').click(function() {
        var block = $("#mobile-top-menu");
        console.log(block);
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
    var loader = '<div class="loader-block">';
        loader += '<div class="img-block">';
        loader += '<img src="/static/assets/img/loader.gif" />';
        loader += '</div>';
        loader += '</div>';

    var button;

    button = $(form).find('button')
        .not(':button[type=button]')
        .not(':button[type=reset]')
    ;

    if (!button.length) {
        button = $(form).find('input[type=submit]');
    }

    if (button) {
        loader = $(loader);
        loader.insertAfter(button);

        button.css('visibility', 'hidden');
        window.setTimeout(function() {
            loader.fadeIn('fast', function() {
                window.setTimeout(function() { form.submit(); } , 500);
            });
        }, 160);
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