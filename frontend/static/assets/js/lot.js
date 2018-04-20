function selectFromHash() {
    var hash = window.location.hash.substring(1)
    var cat_id = hash.replace('cat=', '');
    if (cat_id) {
        select(cat_id)
    }
}

function select(cat_id) {
    $('.nav-tabs').find('li').removeClass('active');
    $('.tab-pane').removeClass('active');

    $('#cat-super-' + cat_id).addClass('active');
    $('#cat-' + cat_id).addClass('active');
    window.location.hash='#cat='+cat_id;
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

function render_lot_list(selected_cat) {
    send(
        '/manage/events/9/lots/?template_name=lot/categories-lots-list',
        'GET',
        null,
        function(response) {
            $('#lot-list-main-block').html(response);

            $('.tooltip').remove();
            app.tooltips();
            createAnchorEvents();

            if (parseInt(selected_cat) > 0) {
                select(parseInt(selected_cat));
            } else {
                selectFromHash();
            }
        },
        function() {
            $('.tooltip').remove();
            app.tooltips();
            createAnchorEvents();
            Messenger().post({
                message: 'Não foi possivel carregar lista de lotes.',
                type: 'error'
            });
        }
    );
}

function save_lot(url, data, msg) {
    send(
        url,
        'PATCH',
        data,
        function (response) {
            Messenger().post({
                message: msg,
                type: 'success'
            });
            render_lot_list();
        },
        function (response) {
            console.error(response.responseJSON);
            Messenger().post({
                message: 'Não foi possivel processar salvamento de lote.',
                type: 'error'
            });
        }
    );
}

function createAnchorEvents() {
    $('.cat-tab-link').on('click', function() {
        window.location.hash='#cat='+$(this).data('cat-id');
    });
}

function publishLot(lot_id) {
     if (!confirm(
         'Tem certeza que deseja publicar o lote? Ele será exibido' +
             ' conforme as configurações de data inicial e final.'
         )) {
         return;
     }
     var data = {'active': true};
     save_lot('/api/lots/' + lot_id + '/', data, 'Lote publicado com sucesso!');

}

function unpublishLot(lot_id) {
     if (!confirm(
         'Tem certeza que deseja despublicar o lote?.'
         )) {
         return;
     }
     var data = {'active': false};
     save_lot('/api/lots/' + lot_id + '/', data, 'Lote despublicado com sucesso!');

}