window.cert = window.cgsy || {};
window.cgsy.cert = window.cgsy.cert || {};

(function ($, messenger, AjaxSender, cert) {
    "use strict";
    // PERSISTÊNCIA DE CERTIFICADO

    var persistence = {
        'url': undefined
    };

    var save_timer = null;

    var create_sender = function () {

        if (!persistence.hasOwnProperty('url') || !persistence.url) {
            console.log('Você deve informar a URL do certificado em window.cgsy.cert.persistence.url');
        }

        var sender = new AjaxSender(persistence.url);
        sender.setFailCallback(function (response) {
            var msg = 'Failure on request to "' + url + '" with method';
            msg += ' "' + this.method + '".';

            if (response.hasOwnProperty('detail')) {
                msg += ' Detalhes: ' + response.detail;
            }
            messenger.triggerError(msg);
        });

        return sender;
    };

    var setSuccessMessage = function (sender, msg) {
        if (msg) {
            var callback = function () {
                messenger.triggerSuccess(msg);
            }
        } else {
            // limpa mensagem anterior.
            callback = function () {
            };
        }
        sender.setSuccessCallback(callback);
    };

    var save = function (data, success_msg) {
        window.clearTimeout(save_timer);
        save_timer = window.setTimeout(function () {
            var sender = create_sender();
            setSuccessMessage(sender, success_msg);
            sender.send('PATCH', data);
        }, 800);
    };

    var remove_px = function (str) {
        if (typeof(str) === "string") {
            return str.replace("px", "");
        }
        return str;
    };

    persistence.Title = function () {
        this.saveContent = function (content) {
            content = content || 'Certificado';

            save(
                {'title_content': content},
                'Conteúdo do título salvo com sucesso.'
            );
        };

        this.saveFontSize = function (size) {
            size = size || '60';

            save(
                {'title_font_size': remove_px(size)},
                'Tamanho do título salvo com sucesso.'
            );
        };

        this.hide = function () {
            save({'title_hide': true}, 'Título escondido.');
        };

        this.show = function () {
            save({'title_hide': false}, 'Título sendo exibido.');
        };

        this.centralize = function () {
            save({'text_center': true}, 'Texto centralizado');
        };

        this.justify = function () {
            save({'text_center': false}, 'Texto justificado');
        };

        this.savePosition = function (x, y) {
            save(
                {'title_position_x': x, 'title_position_y': y},
                'Posição do título salva com sucesso.'
            );
        };
    };

    persistence.Text = function () {
        this.saveContent = function (content) {
            content = content || '{{NOME}}';

            save(
                {'text_content': content},
                'Conteúdo do texto salvo com sucesso.'
            );
        };

        this.saveFontSize = function (size) {
            size = size || '20';
            save(
                {'text_font_size': remove_px(size)},
                'Tamanho do texto salvo com sucesso.'
            );
        };

        this.saveSize = function (width, height) {
            width = width || '634';
            height = height || '348';
            save(
                {
                    'text_width': remove_px(width),
                    'text_height': remove_px(height)
                },
                'Tamanho do bloco do texto salvo com sucesso.'
            );
        };

        this.saveLineHeight = function (size) {
            size = size || '22';
            save(
                {'text_font_size': remove_px(size)},
                'Espaço entre-linhas do texto salvo com sucesso.'
            );
        };

        this.savePosition = function (x, y) {
            save(
                {'text_position_x': x, 'text_position_y': y},
                'Posição do texto salva com sucesso.'
            );
        };
    };

    persistence.Date = function () {
        this.saveFontSize = function (size) {
            size = size || '60';
            save(
                {'date_font_size': remove_px(size)},
                'Tamanho da data salvo com sucesso.'
            );
        };

        this.hide = function () {
            save({'date_hide': true}, 'Data escondida.');
        };

        this.show = function () {
            save({'date_hide': false}, 'Data sendo exibido.');
        };

        this.savePosition = function (x, y) {
            save(
                {'date_position_x': x, 'date_position_y': y},
                'Posição da data salva com sucesso.'
            );
        };
    };

    cert.persistence = persistence;

})(jQuery, window.cgsy.messenger, window.cgsy.AjaxSender, window.cgsy.cert);

(function ($, cert) {
    "use strict";
    // GERENCIADOR DE ELEMENTOS DO DOCUMENTO DE CERTIFICADO.

    cert.CertDocument = function (title_el, text_el, date_el) {
        title_el = $(title_el);
        text_el = $(text_el);
        date_el = $(date_el);

        var title_manager = new cert.persistence.Title();
        var text_manager = new cert.persistence.Text();
        var date_manager = new cert.persistence.Date();

        var title_id = $(title_el).attr('id');
        var text_id = $(text_el).attr('id');
        var date_id = $(date_el).attr('id');

        if (!title_id || !text_id || !date_el) {
            console.error(
                'Você deve definir "ID" em todos os elementos que terão' +
                ' interção "drag and drop".'
            );
        }

        this.savePosition = function (element_id, x, y) {
            if (element_id === title_id) {
                title_manager.savePosition(x, y);
            }

            if (element_id === text_id) {
                text_manager.savePosition(x, y);
            }

            if (element_id === date_id) {
                date_manager.savePosition(x, y);
            }
        };

        this.saveTextSize = function (width, height) {
            text_manager.saveSize(width, height);
        };

        this.hideTitle = function () {
            title_el.hide();
            new cert.persistence.Title().hide();
        };

        this.hideDate = function () {
            date_el.hide();
            new cert.persistence.Date().hide();
        };

        this.showTitle = function () {
            title_el.show();
            new cert.persistence.Title().show();
        };

        this.showDate = function () {
            date_el.show();
            new cert.persistence.Date().show();
        };

        this.saveTitleFontSize = function (size) {
            new cert.persistence.Title().saveFontSize(size);
        };

        this.saveDateFontSize = function (size) {
            new cert.persistence.Date().saveFontSize(size);
        };

        this.saveTextFontSize = function (size) {
            new cert.persistence.Text().saveFontSize(size);
        };

        this.saveTextLineHeight = function (size) {
            new cert.persistence.Text().saveLineHeight(size);
        };

        this.centralizeText = function () {
            new cert.persistence.Title().centralize();
        };

        this.justifyText = function () {
            new cert.persistence.Title().justify();
        };

    };

})(jQuery, window.cgsy.cert);

(function ($, interact, cert) {
    "use strict";
    // WRAPPER DE INTERACT

    var cert_document;

    cert.Interact = function (title_el, text_el, date_el) {
        cert_document = new cert.CertDocument(title_el, text_el, date_el);

        // Ativar draggable
        title_el.addClass('drag');
        date_el.addClass('drag');

        // texto deve ser redimensionável
        text_el.addClass('resize-drag');

        this.moveElement = function (element, x, y) {
            moveElement(element, x, y)
        };
    };

    var moveElement = function (element, x, y) {
        element = $(element);

        // translate the element
        var translate = 'translate(' + x + 'px, ' + y + 'px)';
        element.css('webkitTransform', translate);
        element.css('transform', translate);

        // update the posiion attributes
        element.attr('data-x', x);
        element.attr('data-y', y);
    };

    var dragMoveListener = function (event) {
        var target = event.target,
            // keep the dragged position in the data-x/data-y attributes
            x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx,
            y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

        moveElement($(target), x, y)
    };

    var dragResize = function (event) {
        var target = event.target;
        var x = (parseFloat(target.getAttribute('data-x')) || 0);
        var y = (parseFloat(target.getAttribute('data-y')) || 0);

        // update the element's style
        target.style.width = event.rect.width + 'px';
        target.style.height = event.rect.height + 'px';

        // translate when resizing from top or left edges
        x += event.deltaRect.left;
        y += event.deltaRect.top;

        target.style.webkitTransform = target.style.transform =
            'translate(' + x + 'px,' + y + 'px)';

        target.setAttribute('data-x', x);
        target.setAttribute('data-y', y);

        cert_document.saveTextSize(target.style.width, target.style.height);
    };

    var draggable_options = {
        onmove: dragMoveListener,
        restrict: {
            restriction: 'parent',
            elementRect: {top: 0, left: 0, bottom: 1, right: 1}
        },
        onend: function (event) {
            var target = event.target;
            cert_document.savePosition(
                target.id,
                $(target).attr('data-x'),
                $(target).attr('data-y')
            );
        }
    };

    interact('.drag').draggable(draggable_options);
    interact('.resize-drag')
        .draggable(draggable_options)
        .resizable({
            // redimensionamento somente os que não afetam a posição do texto.
            edges: {left: false, right: true, bottom: true, top: false},

            // keep the edges inside the parent
            restrictEdges: {
                outer: 'parent',
                endOnly: true
            },
            // minimum size
            restrictSize: {
                min: {width: 50, height: 50}
            },
            inertia: true
        })
        .on('resizemove', dragResize);

})(jQuery, interact, window.cgsy.cert);

 function save_form() {
    var formEl = $('#certificate_modal_form');
    var formElSaveBtnEl = $('#certificate_modal_form_save_btn');

    formElSaveBtnEl.text('Aguarde...');
    formElSaveBtnEl.addClass('disabled');
    formEl.submit();
    return false;
}
