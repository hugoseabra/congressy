/**
 * CROP DE IMAGEM
 *
 * DEPENDÊNCIA:
 *  - https://foliotek.github.io/Croppie/
 *
 * Para isso, iremos construir uma biblioteca que já está integrada a um:
 *  - Configuração da imagem:
 *      - viewport (pre-visualiazação do crop):
 *          - width;
 *          - height;
 *          - type: SQUARE, CIRCLE
 *      - boundary (margem fora do crop):
 *          - width;
 *          - height;
 *
 *  - Element Modal:
 *      - element do INPUT[type=FILE] dentro do modal;
 *
 *  - Tipos de processamento:
 *      - async: API URI para submissão da imagem e  nome do campo a ser atualizado na URI;
 *      - submit: Elemento INPUT a inserir o conteúdo da imagem;
 *
 *  - Ações possíveis (callbacks):
 *      - pre-crop callbacks: Callbacks de processamento antes de realizar o crop;
 *      - post-crop callbacks: Callbacks de processamento após de realizar o crop;
 */
window.cgsy = window.cgsy || {};

(function($, cgsy, Croppie) {
    "use strict";

    /**
     * Manipulação de recorte de uma imagem.
     * @param {number} crop_width - Largura do recorte da imagem manipulada.
     * @param {number} crop_height - Altura do recorte da crop da imagem manipulada
     * @param {string} shape
     * @constructor
     */
    cgsy.Cropper = function(crop_width, crop_height, shape) {

        /**
         * Margin do boundary em relação à largura e altura informadas para
         * janela de crop da imagem a ser manipulada.
         * @type {number}
         */
        var boundary_margin = 60;

        /**
         * Tamanho proporcional da janela do crop desejado, na qual o usuário
         * irá manipular o crop.
         * @type {Number}
         */
        var window_proptional_percent = parseFloat(50);

        /**
         * Formato da imagem de crop: daremos suporte a quadrado e circular.
         * @type {Number}
         */
        shape = shape || 'square';

        this.input_file_el = null;
        this.image_el = null;

        var crop_update_callbacks = [];

        var self = this;

        var croppieObject = null;

        if (!crop_width || !crop_height) {
            console.error(
                'You must provide WIDTH and HEIGHT when creating' +
                ' window.cgsy.Cropper instance.'
            );
        }

        if (shape in ['square', 'circle']) {
            console.error('Invalid shape: ' + shape);
        }

        this.setBoundaryMargin = function(margin_value) {
            boundary_margin = parseInt(margin_value);
        };

        this.setWindowProportionalPercent = function(percent) {
            window_proptional_percent = parseFloat(percent);
        };

        this.addCropUpdateCallback = function(callback) {
            if (typeof callback !== 'function') {
                console.error('Invalid callback: ' + callback);
                return;
            }
            crop_update_callbacks.push(callback);
        };

        this.prepare = function(input_file_el, image_el) {
            self.input_file_el = input_file_el;
            self.image_el = image_el;

            self.destroy();

            var width = getProportion(crop_width, window_proptional_percent);
            var height = getProportion(crop_height, window_proptional_percent);

            var enabled_update_callback_triggers = false;
            croppieObject = self.image_el.croppie({
                viewport: {
                    width: width,
                    height: height,
                    type: shape
                },
                boundary: {
                    width: parseInt(width) + parseInt(boundary_margin),
                    height: parseInt(height) + parseInt(boundary_margin)
                },
                update: function() {
                    if (enabled_update_callback_triggers === true) {

                    }
                }
            });

            window.setTimeout(function() {
                croppieObject.croppie('setZoom', 0);
                enabled_update_callback_triggers = true;
            }, 80);
        };

        this.destroy = function() {
            if (!croppieObject) {
                return;
            }
            croppieObject.croppie('destroy');
            croppieObject = null;
        };

        this.crop = function() {

            return new Promise(function (resolve, reject) {
                if (!croppieObject) {
                    reject('No croppie object found.');
                }

                var crop_data = croppieObject.croppie('get');
                var points = crop_data['points'];
                var zoom = crop_data['zoom'];

                var origin_image_parent = $('<div>');
                var original_image = $('<img>');
                    origin_image_parent.append(original_image);
                $('body').append(origin_image_parent);

                self.getBase64(self.input_file_el[0].files[0]).then(function(result) {

                    var crop = original_image.croppie({
                        viewport: {
                            width: crop_width,
                            height: crop_height
                        }
                    });

                    crop.croppie('bind', {
                        points: points,
                        url: result,
                        zoom: zoom
                    });

                    window.setTimeout(function() {
                        crop.croppie('result', 'base64', 'original', 'png', '1', false).then(function (base64_image) {
                            origin_image_parent.remove();
                            resolve(base64_image);
                        });

                    }, 1000);
                });
            });
        };

        this.getBase64 = function (file) {
            return new Promise(function (resolve, reject) {
                var reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onloadend = function () {
                    resolve(reader.result)
                };
                reader.onerror = function (error) {
                    reject(error)
                };
            });
        }

        var getProportion = function(value, percent) {
            return ((parseFloat(value) * parseFloat(percent))/100);
        };
    };
})(jQuery, window.cgsy, window.Croppie);

(function($, cgsy, URL, AjaxSender) {
    "use strict";

    /**
     * Modal Criado dinamicamente para cada crop a ser realizado.
     * @param {cgsy.Cropper} cropper - Cropper de manipulação da imagem
     * @param {string} img_src - Imagem inicial
     * @constructor
     */
    cgsy.ModalBlock = function(cropper, img_src) {

        const SUBMIT_MODE_SYNC = 'sync_mode';
        const SUBMIT_MODE_ASYNC = 'async_mode';

        this.img_src = img_src;

        /**
         * Elemento jQuery da janela pai do modal.
         * @type {Object}
         */
        this.main = null;

        /**
         * Elemento jQuery do "input[type=FILE]" a ser usado para seleção da
         * imagem a ser manipulada.
         * @type {Object}
         */
        this.input_file_el = null;

        /**
         * Elemento jQuery da tag "img" a ser usada para a manipulação da
         * imagem.
         * @type {Object}
         */
        this.img_el = null;

        /**
         * Elemento jQuery para Spinner para mostrar carregamento.
         * @type {Object}
         */
        this.spinner_el = null;

        this.button_switch_el = null;
        this.button_save_el = null;
        this.button_delete_el = null;

        /**
         * Caminho da imagem padrão.
         * @type {string}
         */
        var default_image_src;

        /**
         * Tipo de submissão da imagem recortada.
         * @type {string}
         */
        var submit_mode = null;

        /**
         * Se assíncrono: URI de API no qual o modal irá executar um PATCH de
         * forma assíncrona.
         * @type {string}
         */
        var async_mode_uri = null;

        /**
         * Se assíncrono: Nome do campo no qual o modal deve atrelar o conteúdo
         * base64 da imagem recortada para enviar no PATCH.
         * @type {string}
         */
        var async_mode_field_name = null;

        /**
         * Se síncrono: Elemento jQuery da tag "input[type=FILE]" do formulário
         * principal da aplicação cliente.
         * @type {string}
         */
        var sync_mode_input_file_el = null;

        /**
         *
         * @type {Array}
         */
        var post_crop_callbacks = [];

        var self  = this;

        this.setAsyncMode = function(uri, field_name) {
            if (submit_mode) {
                console.error('Submission mode already set as: ' + submit_mode);
                return;
            }

            submit_mode = SUBMIT_MODE_ASYNC;
            async_mode_uri = uri;
            async_mode_field_name = field_name;
        };

        this.setSyncMode = function(input_file_el) {
            if (submit_mode) {
                console.error('Submission mode already set as: ' + submit_mode);
                return;
            }

            submit_mode = SUBMIT_MODE_SYNC;
            sync_mode_input_file_el = $(input_file_el);
        };

        /**
         * Caminho da imagem padrão.
         * @param {string} img_src
         */
        this.setDefaultImgSrc = function(img_src) {
            default_image_src = img_src;
        };

        this.addPostCropCallback = function(callback) {
            if (typeof callback !== 'function') {
                console.error('Callback invalid: ' + callback);
            }
            post_crop_callbacks.push(callback);
        };

        this.crop = function() {
            self.spinner_el.show();

            cropper.crop().then(function(base64_image) {
                self.send(base64_image).then(function(result) {
                    $.each(post_crop_callbacks, function(i, callback) {
                        callback(base64_image);
                        self.img_src = base64_image;
                        self.img_el.attr('src', base64_image);
                    });
                    window.setTimeout(function() {
                        self.main.modal('hide');
                    }, 200);
                });
            });
        };

        this.send = function(base64_image) {
            if (submit_mode === SUBMIT_MODE_ASYNC) {
                return new Promise(function(resolve, reject) {
                    var sender = new AjaxSender(async_mode_uri);
                    sender.setSuccessCallback(function(response) {
                        resolve(response);
                    });
                    sender.setFailCallback(function(response) {
                        reject(response)
                    });
                    var data = {};
                    data[async_mode_field_name] = base64_image;

                    sender.send('PATCH', data);
                });
            }

            if (submit_mode === SUBMIT_MODE_SYNC) {
                return new Promise(function(resolve) {
                    sync_mode_input_file_el.val(base64_image);
                    resolve(base64_image);
                });
            }
        };

        /**
         * Abre moal
         */
        this.open = function() {
            self.main.modal();
        };

        /**
         * Cria elementos DOM
         */
        var createModal = function() {
            // MAIN BLOCK
            self.main = $('<div>').attr({
                'tabindex': '-1',
                'role': 'dialog',
                'aria-hidden': 'true'
            }).addClass('modal fade');

            var modal_dialog = $('<div>').attr('role', 'document').addClass('modal-dialog');
            self.main.append(modal_dialog);

            // CONTENT -> Modal Dialog
            var modal_content = $('<div>').addClass('modal-content');
            modal_dialog.append(modal_content);

            // HEADER -> Modal Content
            var header = $('<div>').addClass('modal-header');
            modal_content.append(header);

            var button = $('<button>').attr({
                'type': 'button',
                'class': 'close',
                'data-dismiss': 'modal',
                'aria-hidden': 'true'
            }).text('×');
            var title = $('<h3>').addClass('modal-title').text('Recortar imagem').addClass('text-bold');
            header.append(button);
            header.append(title);

            // BODY -> Modal Content
            var body = $('<div>').addClass('modal-body');
            body.appendTo(modal_content);

            // FOOTER -> Modal Content
            var footer = $('<div>').addClass('modal-footer');
            modal_content.append(footer);

            var row_footer_buttons = $('<div>').addClass('row');
            footer.append(row_footer_buttons);

            var column_footer_buttons = $('<div>').addClass('col-md-12 text-right');
            row_footer_buttons.append(column_footer_buttons);

            var footer_button1 = $('<button>').attr({
                'type': 'button',
                'class': 'btn btn-default',
                'data-dismiss': 'modal'
            }).text('Fechar');
            var footer_button2 = $('<button>').attr({
                'type': 'button',
                'class': 'btn btn-success'
            }).text('Enviar');
            column_footer_buttons.append(footer_button1);
            column_footer_buttons.append(footer_button2);

            // MAIN CONTENT -> to Modal Body
            // -- ROW: INPUT[TYPE=FILE] e BUTTON
            var row_input_file = $('<div>').addClass('row');
            body.append(row_input_file);

            var column_input_file = $('<div>').addClass('col-md-12 text-center');
            row_input_file.append(column_input_file);

            var form = $('<form>');
            self.input_file_el = $('<input>').attr({
                'type': 'file',
                'style': 'display:none',
                'accept': 'image/*'
            });

            self.img_el = $('<img>').addClass('image-responsive').attr({
                'src': self.img_src || default_image_src,
                'width': '100%'
            });
            form.append(self.input_file_el);

            column_input_file.append(form);
            column_input_file.append(self.img_el);

            // -- ROW: BUTTONS
            var row_manage_buttons = $('<div>').addClass('row');
            body.append(row_manage_buttons);

            var column_main_buttons = $('<div>').addClass('col-sm-8');
            row_manage_buttons.append(column_main_buttons);

            self.button_switch_el = $('<button>').attr({
                'class': 'btn btn-info',
                'type': 'button',
                'style': 'margin-top: 4px;'
            });

            column_main_buttons.append(self.button_switch_el);

            var switch_icon = $('<i>').addClass('fas fa-image');
            self.button_switch_el.append(switch_icon);
            self.button_switch_el.append($('<span>').text('Selecionar imagem'));

            self.button_save_el = $('<button>').attr({
                'class': 'btn btn-success',
                'type': 'button',
                'style': 'margin-top: 4px;margin-left: 4px;',
                'disabled': ''
            });
            column_main_buttons.append(self.button_save_el);

            var save_icon = $('<i>').addClass('fas fa-save');
            self.button_save_el.append(save_icon);

            self.button_save_el.append($('<span>').text('Salvar'));

            var column_delete_buttons = $('<div>').addClass('col-sm-4 text-right');
            row_manage_buttons.append(column_delete_buttons);

            self.button_delete_el = $('<button>').attr({
                'class': 'btn btn-sm btn-trans btn-danger',
                'type': 'button',
                'style': 'margin-top: 4px;margin-left: 4px;'
            });
            column_delete_buttons.append(self.button_delete_el);

            var delete_icon = $('<i>').addClass('fas fa-trash');
            self.button_delete_el.append(delete_icon);

            // Spinner -> Body
            self.spinner_el = $('<div>').css({
                'background': '#333',
                'color': '#FFF',
                'opacity': '0.9',
                'position': 'absolute',
                'width': '100%',
                'top': '-52px',
                'height': '128%',
                'left': '0',
                'z-index': '1',
                'text-align': 'center',
                'display': 'none'
            });
            body.append(self.spinner_el);

            var spinner_icon = $('<i>')
                .addClass('fas fa-circle-notch fa-spin fa-6x')
                .css('margin-top', '168px');

            self.spinner_el.append(spinner_icon);
            
            // Events
            createModalEvents();
            createChangeEvents();
            selectImageEvent();
            createSaveEvent();
        };

        /**
         * Cria eventos de callbacks relacionados ao modal.
         */
        var createModalEvents = function() {
            self.main.on('show.bs.modal', function() {
                self.spinner_el.hide();
                self.button_save_el.attr('disabled', '');
                self.img_el.attr('src', self.img_src || default_image_src);
            });
            self.main.on('hidden.bs.modal', function() {
                cropper.destroy();
            });
        };

        /**
         * Cria eventos 'change' relacionados a diversos elementos
         */
        var createChangeEvents = function() {
            // If input_file changes
            self.input_file_el.on('change', function () {

                self.button_save_el.removeAttr('disabled');

                // Get the first file in the FileList object
                var imageFile = this.files[0];

                if (!imageFile) {
                    self.button_save_el.attr('disabled', '');
                    return;
                }

                // Now use your newly created URL!
                self.img_el[0].src = URL.createObjectURL(imageFile);

                cropper.prepare($(this), self.img_el);
            });
        };

        var selectImageEvent = function() {
            self.button_switch_el.on('click', function() {
                self.input_file_el.trigger('click');
            });
        };

        var createSaveEvent = function() {
            self.button_save_el.on('click', function() {
                self.crop();
            });
        };

        window.setTimeout(function() {
            cropper.addCropUpdateCallback(function() {
                self.button_save_el.removeAttr('disabled');
            });

            createModal();
            self.main.appendTo($('body'));
        }, 200);
    };

})(jQuery, window.cgsy, window.URL, cgsy.AjaxSender);