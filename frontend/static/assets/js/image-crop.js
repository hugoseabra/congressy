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

(function($, cgsy) {
    "use strict";

    /**
     *
     * @param {number} width
     * @param {number} height
     * @param {string} shape
     * @constructor
     */
    cgsy.Cropper = function(crop_width, crop_height, shape) {

        /**
         * Largura do crop a ser realizado na imagem.
         * @type {Number}
         */
        var width = 300;

        /**
         * Altura do crop a ser realizado na imagem.
         * @type {Number}
         */
        var height = 193;

        /**
         * Formato da imagem de crop: daremos suporte a quadrado e circular.
         * @type {Number}
         */
        shape = shape || 'square';
        this.image_el = null;
        var self = this;

        var croppieObject = null;

        if (!width || !height) {
            console.error(
                'You must provide WIDTH and HEIGHT when creating' +
                ' window.cgsy.Cropper instance.'
            );
        }

        if (shape in ['square', 'circle']) {
            console.error('Invalid shape: ' + shape);
        }

        var boundary_width = width + 60;
        var boundary_height = height + 60;

        this.prepare = function(image_el) {
            self.image_el = image_el;

            self.destroy();

            croppieObject = self.image_el.croppie({
                viewport: {
                    width: width,
                    height: height,
                    type: shape
                },
                boundary: {
                    width: boundary_width,
                    height: boundary_height
                }
            });

            window.setTimeout(function() {
                croppieObject.croppie('setZoom', 0);
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

            createCroppieObj();


        };

        var createCroppieObj = function() {

        };
    };
})(jQuery, window.cgsy);

(function($, cgsy, URL) {
    "use strict";

    /**
     * Modal Criado dinamicamente para cada crop a ser realizado.
     * @constructor
     */

    /**
     * @param {Cropper} cropper
     * @param {string} img_src
     * @constructor
     */
    cgsy.ModalBlock = function(cropper, img_src) {

        this.main = null;
        this.input_file_el = null;
        this.img_el = null;
        var self  = this;

        this.open = function() {
            self.main.modal();
        };

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
                'src': img_src,
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

            var switch_button = $('<button>').attr({
                'class': 'btn btn-info',
                'type': 'button',
                'style': 'margin-top: 4px;'
            });

            column_main_buttons.append(switch_button);

            var switch_icon = $('<i>').addClass('fas fa-image');
            switch_button.append(switch_icon);

            switch_button.append($('<span>').text('Enviar imagem'));

            var save_button = $('<button>').attr({
                'class': 'btn btn-success',
                'type': 'button',
                'style': 'margin-top: 4px;margin-left: 4px;'
            });
            column_main_buttons.append(save_button);

            var save_icon = $('<i>').addClass('fas fa-save');
            save_button.append(save_icon);

            save_button.append($('<span>').text('Salvar'));

            var column_delete_buttons = $('<div>').addClass('col-sm-4 text-right');
            row_manage_buttons.append(column_delete_buttons);

            var delete_button = $('<button>').attr({
                'class': 'btn btn-sm btn-trans btn-danger',
                'type': 'button',
                'style': 'margin-top: 4px;margin-left: 4px;'
            });
            column_delete_buttons.append(delete_button);

            var delete_icon = $('<i>').addClass('fas fa-trash');
            delete_button.append(delete_icon);

            // Events
            createModalEvents();
            createChangeEvents();
            selectImageEvent(switch_button);
        };

        var createModalEvents = function() {
            self.main.on('show.bs.modal', function() {
                window.setTimeout(function() {
                    cropper.prepare(self.img_el);
                }, 200);
            });
            self.main.on('hidden.bs.modal', function() {
                cropper.destroy();
            });
        };

        var createChangeEvents = function() {

            // If input_file changes
            self.input_file_el.on('change', function () {

                // Get the first file in the FileList object
                var imageFile = this.files[0];

                // Now use your newly created URL!
                self.img_el[0].src = window.URL.createObjectURL(imageFile);

                cropper.prepare(self.img_el);
            });
        };

        var selectImageEvent = function(send_button_el) {
            send_button_el.on('click', function() {
                self.input_file_el.trigger('click');
            });
        };

        // destroy modal on close =================
        window.setTimeout(function() {
            createModal();
            self.main.appendTo($('body'));
        }, 200);
    };

})(jQuery, window.cgsy, window.URL);