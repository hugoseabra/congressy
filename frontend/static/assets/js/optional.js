function selectFromHash() {
    var hash = window.location.hash.substring(1);
    var cat_id = hash.replace('cat=', '');
    if (cat_id) {
        select(cat_id);
    }
}

function select(cat_id) {
    $('.cat-tabs .nav-tabs').find('li').removeClass('active');
    $('.cat-tabs .tab-pane').removeClass('active');

    $('#cat-super-' + cat_id).addClass('active');
    $('#cat-' + cat_id).addClass('active');
    window.location.hash = '#cat=' + cat_id;
}

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
        success: success_callback || function () {
        },
        error: error_callback || function () {
        }
    });
}

function render_service_optional_list(selected_cat) {
    var url = window.location.href.replace(window.location.hash, '');
    url += '?template_name=addon/optional/includes/service';

    send(
        url,
        'GET',
        null,
        function (response) {
            $('#main-service-list-block').html(response);

            $('.tooltip').remove();
            app.tooltips();
            createAnchorEvents();

            if (parseInt(selected_cat) > 0) {
                select(parseInt(selected_cat));
            } else {
                selectFromHash();
            }
        },
        function () {
            $('.tooltip').remove();
            app.tooltips();
            createAnchorEvents();
            Messenger().post({
                message: 'Não foi possivel carregar lista de opcionais.',
                type: 'error'
            });
        }
    );
}

function render_product_optional_list(selected_cat) {
    var url = window.location.href.replace(window.location.hash, '');
    url += '?template_name=addon/optional/includes/product';

    send(
        url,
        'GET',
        null,
        function (response) {
            $('#main-product-list-block').html(response);

            $('.tooltip').remove();
            app.tooltips();
            createAnchorEvents();

            if (parseInt(selected_cat) > 0) {
                select(parseInt(selected_cat));
            } else {
                selectFromHash();
            }
        },
        function () {
            $('.tooltip').remove();
            app.tooltips();
            createAnchorEvents();
            Messenger().post({
                message: 'Não foi possivel carregar lista de opcionais.',
                type: 'error'
            });
        }
    );
}

function save_optional(url, data, msg) {
    send(
        url,
        'PATCH',
        data,
        function (response) {
            Messenger().post({
                message: msg,
                type: 'success'
            });

            if (url.indexOf('services') !== -1) {
                render_service_optional_list();
            }

            if (url.indexOf('products') !== -1) {
                render_product_optional_list();
            }
        },
        function (response) {
            response = response.responseJSON;
            console.error(response);
            var msg = 'Não foi possivel processar salvamento de opcional.';

            if (response.hasOwnProperty('detail')) {
                msg += '. Detalhe: ' + response.detail
            }

            Messenger().post({message: msg, type: 'error'});
        }
    );
}

function delete_optional(url, msg) {

    send(
        url,
        'DELETE',
        {},
        function () {
            Messenger().post({
                message: msg,
                type: 'success'
            });

            if (url.indexOf('services') !== -1) {
                render_service_optional_list();
            }

            if (url.indexOf('products') !== -1) {
                render_product_optional_list();
            }
        },
        function (response) {
            response = response.responseJSON;
            console.error(response);
            var msg = 'Não foi possivel processar apagamento de opcional.';

            if (response.hasOwnProperty('detail')) {
                msg += '. Detalhe: ' + response.detail
            }

            Messenger().post({message: msg, type: 'error'});
        }
    );
}

function createAnchorEvents() {
    $('.cat-tab-link').on('click', function () {
        window.location.hash = '#cat=' + $(this).data('cat-id');
    });
}

function publish_optional(type, id) {

    var title = (type === 'service') ? 'Atividade extra' : 'Produto / Serviço';

    if (!confirm('Tem certeza que deseja publicar este ' + title + '?')) {
        return;
    }

    var url;
    if (type === 'service') {
        url = '/api/addon/optionals/services/' + id + '/'
    }

    if (type === 'product') {
        url = '/api/addon/optionals/products/' + id + '/'
    }

    if (!url) {
        return;
    }

    var data = {'published': true};
    save_optional(url, data, 'Opcional publicado com sucesso!');
}

function unpublish_optional(type, id) {

    var title = (type === 'service') ? 'Atividade extra' : 'Produto / Serviço';

    if (!confirm('Tem certeza que deseja despublicar este ' + title + '?')) {
        return;
    }

    var url;
    if (type === 'service') {
        url = '/api/addon/optionals/services/' + id + '/'
    }

    if (type === 'product') {
        url = '/api/addon/optionals/products/' + id + '/'
    }

    if (!url) {
        return;
    }

    var data = {'published': false};
    save_optional(url, data, 'Opcional despublicado com sucesso!');
}

function save_service_limit() {
    var service_id = $('#service-limit_service-id').val();

    if (!service_id) {
        Messenger().post({
            message: 'Algo deu errado: Opcional não encontrado. ',
            type: 'error',
            hideAfter: 3
        });
        return;
    }

    var limit = $('#service-limit').val();
    limit = (limit) ? parseInt(limit) : 0;

    save_optional(
        '/api/addon/optionals/services/' + service_id + '/',
        {'quantity': limit},
        'Limite de vagas configurado com sucesso!'
    );

    $('#modal-service-limit-form').modal('toggle');

}

function save_product_limit() {
    var service_id = $('#product-limit_product-id').val();

    if (!service_id) {
        Messenger().post({
            message: 'Algo deu errado: Opcional não encontrado. ',
            type: 'error',
            hideAfter: 3
        });
        return;
    }

    var limit = $('#product-limit').val();
    limit = (limit) ? parseInt(limit) : 0;

    save_optional(
        '/api/addon/optionals/products/' + service_id + '/',
        {'quantity': limit},
        'Limite de estoque configurado com sucesso!'
    );

    $('#modal-product-limit-form').modal('toggle');

}

function set_restrict_unique(type, id) {

    var url;
    if (type === 'service') {
        url = '/api/addon/optionals/services/' + id + '/'
    }

    if (type === 'product') {
        url = '/api/addon/optionals/products/' + id + '/'
    }

    if (!url) {
        return;
    }

    var data = {'restrict_unique': true};
    save_optional(url, data, 'Atividade configurada como restrita!');
}

function unset_restrict_unique(type, id) {

    var url;
    if (type === 'service') {
        url = '/api/addon/optionals/services/' + id + '/'
    }

    if (type === 'product') {
        url = '/api/addon/optionals/products/' + id + '/'
    }

    if (!url) {
        return;
    }

    var data = {'restrict_unique': false};
    save_optional(url, data, 'Atividade configurada como não-restrita!');
}

function service_fetch_data_and_open_delete_modal(optional_id) {


    var url = '/api/addon/optionals/services/' + optional_id + '/';
    send(url, 'GET', {}, function (response) {
        $('#service_optional_delete_id').val(optional_id);
        $('#service_optional_name').text(response.name);
        $('#modal-service-delete').modal('show');
    }, function (response) {
        response = response.responseJSON;
        console.error(response);
        var msg = 'Não foi possivel pegar os dados do opcional.';

        if (response.hasOwnProperty('detail')) {
            msg += '. Detalhe: ' + response.detail
        }
        Messenger().post({message: msg, type: 'error'});
    });
}

function product_fetch_data_and_open_delete_modal(optional_id) {
    var url = '/api/addon/optionals/products/' + optional_id + '/';


    send(url, 'GET', {}, function (response) {
        $('#product_optional_delete_id').val(optional_id);
        $('#product_optional_name').text(response.name);
        $('#modal-product-delete').modal('show');
    }, function (response) {
        response = response.responseJSON;
        console.error(response);
        var msg = 'Não foi possivel pegar os dados do opcional.';

        if (response.hasOwnProperty('detail')) {
            msg += '. Detalhe: ' + response.detail
        }
        Messenger().post({message: msg, type: 'error'});
    });


}

function submit_delete_optional(typeOfOptional) {

    var optional_id;
    var url;

    if(typeOfOptional === "service"){
        $('#modal-service-delete').modal('hide');
        optional_id = $('#service_optional_delete_id');
        url = '/api/addon/optionals/services/' + optional_id.val() + '/';
        console.log(url);
        delete_optional(url, 'Atividade extra deletado com sucesso!');
        optional_id.val("");
    } else if (typeOfOptional === "product"){
        $('#modal-product-delete').modal('hide');
        optional_id = $('#product_optional_delete_id');
        url = '/api/addon/optionals/products/' + optional_id.val() + '/';
        delete_optional(url, 'Produto deletado com sucesso!');
        optional_id.val("");
    }
}

$(document).ready(function () {
    Messenger.options = {
        extraClasses: 'messenger-fixed messenger-on-bottom ' +
        'messenger-on-right',
        theme: 'flat'
    };
});