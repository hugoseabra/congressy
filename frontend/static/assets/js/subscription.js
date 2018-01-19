//======================= CONSTANTES GLOBAIS ================================//
var IS_CHROME = false;

//============================= LOADERS =====================================//
/**
 * Mostra/Esconde loaders de processamento de verificação de CPF. Ao exibir
 * o loader, o campo CPF é desativado.
 *
 * @param {boolean} show
 */
function showHideCpfLoader(show) {
    var cpf_el = $('#id_cpf');
    if (!cpf_el.length) {
        return;
    }

    var el = $('#cpf_loader');
    if (show === true) {
        el.fadeIn();
        cpf_el.attr('readonly', 'readonly').addClass('disabled');
        cpf_el.css('background-color', '#fff');
    } else {
        el.fadeOut();
        cpf_el.removeAttr('readonly').removeClass('disabled');
        cpf_el.removeAttr('style')
    }
}

/**
 * Mostra/Esconde loaders de processamento de verificação de E-mail. Ao exibir
 * o loader, o campo E-mail é desativado.
 *
 * @param {boolean} show
 */
function showHideEmailLoader(show) {
    var email_el = $('#id_email');
    if (!email_el.length) {
        return;
    }

    var el = $('#email_loader');
    if (show === true) {
        el.fadeIn();
        email_el.attr('disabled', 'disabled').addClass('disabled');
        email_el.css('background-color', '#fff');
    } else {
        el.fadeOut();
        email_el.removeAttr('disabled').removeClass('disabled');
        email_el.removeAttr('style');
    }
}

//========================= GERENCIAMENTO E CAMPOS ==========================//
/**
 * Habilita todos os campos, possibilitando um campo específico a ter o foco
 * do cursor.
 * @param {object|string} focus - jQuery element ou string
 */
function enableAll(focus) {
    $('input').removeAttr('disabled').removeClass('disabled');
    $('select').removeAttr('disabled').removeClass('disabled');

    $('#check-email-button-block').hide();

    if (focus) {
        $(focus).focus();
    }
}

/**
 * Desabilita todos os campos de um formulario, possibilidade deixar alguns
 * campos como exceção.
 *
 * @param {Array} exception
 */
function disableAll(exception) {
    exception = exception || [];

    var form = $('#subscription-form');
    var inputs = form.find('input').not('input[type=hidden]');
    var selects = form.find('select');

    if (exception) {
        $.each(exception, function (i, field) {
            inputs = inputs.not($(field));
            selects = selects.not($(field));
        });
    }

    inputs.attr('disabled', 'disabled').addClass('disabled');
    selects.attr('disabled', 'disabled').addClass('disabled');
}

/**
 * Cria um tag <div> simulando como se fosse um campo com aparência de
 * "readonly", contudo o campo é removido ficando apenas o valor do campo
 * para verificação do usuário.
 *
 * @param {boolean} forceAll
 */
function setAsReadonly(forceAll) {
    var form = $('#subscription-form');
    var inputs = form.find('input').not('input[type=hidden]');
    var selects = form.find('select');

    $('#check-email-button-block').hide();

    var focused = false;

    function deactivate(el, focus) {
        el = $(el);
        var readonly_field = '<div class="readonly-field">{v}</div>';
        var value = normalize_field_value(el);

        if (forceAll === true || value) {
            value = readonly_field.replace('{v}', value);
            el.parent().append(value);
            el.remove();
        } else if (!forceAll && focus) {
            if (!focused) {
                focused = true;
                el.focus();
            }
        }
    }

    inputs.each(function (i, el) {
        deactivate(el, true);
    });

    selects.each(function (i, el) {
        deactivate(el);
    });
}

/**
 * Normaliza o valor do campo a ser exibido, verificando o tempo do campo
 * e tratando conforme será a apresentação ideal.
 *
 * @param {object} el - jQuery element ou string
 * @returns {*}
 */
function normalize_field_value(el) {
    el = $(el);
    var value = el.val();

    if (!value) {
        return '';
    }
    console.log(value);

    switch (el.prop('tagName')) {
        case 'INPUT':
            switch (el.attr('type')) {
                case 'date':
                    if (IS_CHROME) {
                        var split = value.split('-');
                        value = split[2] + '/' + split[1] + '/' + split[0];
                    }
            }
            break;
        case 'SELECT':
            value = el.find('option:selected').text();
            break;

    }

    return value;
}

//====================== VERIFICADORES / PROCESSADORES ======================//
/**
 * Verifica o e-mail informando, transmitindo-o para um outro formulário e
 * realizando uma submissão do tipo GET para recarregar a página com o estado
 * posterior.
 */
function check_email() {
    var email = $('#id_email');
    var value = email.val();

    if (!value) {
        email.focus();
        return;
    }

    showHideEmailLoader(true);
    var button = $('#check-email-button-block button');
    button.addClass('disabled').attr('disabled', 'disabled');

    var form = $('#check-email-form');
    form.find('input').val(value.toLowerCase());
    form.submit()
}

/**
 * Verifica o CPF informando.
 */
function search_cpf() {
    var el = $('#id_cpf');
    if (!el) {
        return;
    }
}

//========================== MISCELANEA =====================================//
/**
 * Redimensiona a tela da imagem do perfil ou a tela dos blocos ao lado,
 * deixando ambos com uma dimensão simétrica.
 *
 * @param {boolean} has_subscription_form
 */
function resize_status_block(has_subscription_form) {
    if (window.innerWidth > 991) {
        var block_profile_height = $('#block-profile').height();
        var block_form_main_height = $('#block-form-main').height();
        var block_form_lot_height = $('#block-form-lot').height();

        var main_height = block_form_main_height;

        if (has_subscription_form) {
            main_height += block_form_lot_height + 19;
        }

        if (block_profile_height < main_height) {
            $('#block-profile').height(main_height);
        } else {
            $('#block-form-main').height(block_profile_height);
        }
    }
}