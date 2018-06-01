window.cert = window.cert || {};

(function (window, $) {

    window.cert.url = undefined;
    window.cert.event = undefined;

    Messenger.options = {
        extraClasses: 'messenger-fixed messenger-on-bottom ' +
        'messenger-on-right',
        theme: 'flat'
    };

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

    // Título do certificado
    var title = {
        "position_x": 0.00,
        "position_y": 0.00,
        "font_size": "12px",
        "hide": false
    };

    var date = {
        "position_x": 0.00,
        "position_y": 0.00,
        "font_size": "12px",
        "hide": false
    };
    var text = {
        "position_x": "0.00",
        "position_y": "12.2",
        "font_size": "12px",
        "width": "340px",
        "height": "300px",
        "line_height": "20px",
        "text": "teste"
    };

    // ====================================
    // Save data
    // ====================================
    // Funcão que analisa os dados recebidos com os dados esperados
    function check_data(keys, data) {
        $.each(keys, function (i, key) {
            if (!key in data) {
                return false;
            }
        });
        return true;
    }

    // =============TITLE==================
    // Função que solicita um objeto title
    window.cert.getTitle = function () {
        $.ajax({
            url: window.cert.url,
            method: 'GET',
            crossDomain: true,
            success: function (data) {
                console.log(data);
            }
        });
    };

    // Função que salva um objeto title
    var save_title_timer = null;
    window.cert.saveTitle = function (data) {
        window.clearTimeout(save_title_timer);
        save_title_timer = window.setTimeout(function () {


            for (var key in data) {
                if (data.hasOwnProperty(key)) {
                    console.log(key + " -> " + data[key]);
                }
            }

            // var form_data = new FormData();
            //
            // form_data.append('event', window.cert.event);
            // form_data.append('title_font_size', data['title_font_size']);
            // form_data.append('title_position_x', data['title_position_x']);
            // form_data.append('title_position_y', data['title_position_y']);
            // form_data.append('title_hide', data['title_hide']);
            //
            // $.ajax({
            //     url: window.cert.url,
            //     processData: false,
            //     contentType: false,
            //     data: form_data,
            //     beforeSend: function (xhr) {
            //         xhr.setRequestHeader("X-CSRFToken", csrftoken);
            //     },
            //     method: 'PATCH',
            //     success: function (data) {
            //         title = data;
            //         Messenger().post({
            //             message: 'Titulo atualizado com sucesso!',
            //             type: 'success'
            //         });
            //     },
            //     error: function (err) {
            //         if (err.responseText !== "") {
            //             console.error(err.responseText)
            //         } else {
            //             console.error(err)
            //         }
            //         Messenger().post({
            //             message: 'Titulo não foi atualizado!',
            //             type: 'danger'
            //         });
            //     }
            // });
        }, 200);
    };

    //Função que salva a posição de um objeto title
    window.cert.saveTitlePosition = function (x, y) {
        title['position_x'] = x;
        title['position_y'] = y;
        cert.saveTitle(title);
    };

    //Função que salva o tamanha da fonte de um objeto title
    window.cert.saveTitleFontSize = function (font_size) {
        title['font_size'] = font_size;
        cert.saveTitle(title);
    };

    //Função que muda o estado de hide pra false em title(deixa visível)
    window.cert.showTitle = function () {
        title['hide'] = false;
        cert.saveTitle(title);
    };

    //Função que muda o estado de hide para true em title(não deixa visível)
    window.cert.hideTitle = function () {
        title['hide'] = true;
        cert.saveTitle(title);
    };

//================= Date====================

// Função que requisita um objeto do tipo date
    window.cert.getDate = function () {
        $.ajax({
            url: window.cert.url,
            method: 'GET',
            crossDomain: true,
            success: function (data) {
                console.log(data);
            }
        });
    };

// Função que salva um objeto do tipo date
    window.cert.saveDate = function (data) {
        var save_date_timer = null;
        window.clearTimeout(save_date_timer);
        save_date_timer = window.setTimeout(function () {
            for (var key in data) {
                if (data.hasOwnProperty(key)) {
                    console.log(key + " -> " + data[key]);
                }
            }
            // var form_data = new FormData();
            // form_data.append('event', window.cert.event);
            // var date_font_size = data['date_font_size'];
            // if (date_font_size !== undefined) {
            //     console.log(date_font_size);
            //     date_font_size = parseInt(data['date_font_size'].replace("px", ""));
            //     console.log(date_font_size);
            //     form_data.append('date_font_size', date_font_size);
            // }
            //
            // form_data.append('date_position_x', parseInt(data['date_position_x']));
            // form_data.append('date_position_y', parseInt(data['date_position_y']));
            //
            // if (data['date_hide']) {
            //     form_data.append('date_hide', true);
            // } else {
            //     form_data.append('date_hide', false);
            // }
            //
            //
            // $.ajax({
            //     url: window.cert.url,
            //     processData: false,
            //     contentType: false,
            //     data: form_data,
            //     beforeSend: function (xhr) {
            //         xhr.setRequestHeader("X-CSRFToken", csrftoken);
            //     },
            //     method: 'PATCH',
            //     success: function (data) {
            //         title = data;
            //         Messenger().post({
            //             message: 'Data atualizada com sucesso!',
            //             type: 'success'
            //         });
            //     },
            //     error: function (err) {
            //         if (err.responseText !== "") {
            //             console.error(err.responseText)
            //         } else {
            //             console.error(err)
            //         }
            //         Messenger().post({
            //             message: 'Data não foi atualizada!',
            //             type: 'danger'
            //         });
            //     }
            // });


        }, 200);
    };

// Função que salva a posição de um objeto date
    window.cert.saveDatePosition = function (x, y) {
        date['position_x'] = x;
        date['position_y'] = y;
        cert.saveDate(date)
    };

// Função que salva o tamanho da fonte de um objeto date
    window.cert.saveDateFontSize = function (font_size) {
        date['font_size'] = font_size;
        cert.saveDate(date);
    };

//Função que muda o estado de hide pra true em date(não deixa visível)
    window.cert.hideDate = function () {
        date['hide'] = true;
        cert.saveDate(date);
    };

//Função que muda o estado de hide para false em date(deixa visível)
    window.cert.showDate = function () {
        title['hide'] = false;
        cert.saveDate(date);
    };

// Text

// Função que requisita um objeto text
    window.cert.getText = function () {
        $.ajax({
            url: window.cert.url,
            method: 'GET',
            crossDomain: true,
            success: function (data) {
                //console.log(data);
                //return JSON.parse(data);
            }
        });
    };

// Função que salva um objeto text
    window.cert.saveText = function (data) {
        var save_text_timer = null;
        var expect_keys = [
            'position_x',
            'position_y',
            'font-size',
            'width',
            'height',
            'line_height',
            'text'
        ];
        var resource_name = 'mock/text.json';
        if (!check_data(expect_keys, data)) {
            console.error('Dados errados em "' + resource_name + '"');
            console.log(data);
            return;
        }
        window.clearTimeout(save_text_timer);
        save_text_timer = window.setTimeout(function () {

            for (var key in data) {
                if (data.hasOwnProperty(key)) {
                    console.log(key + " -> " + data[key]);
                }
            }


            // var form_data = new FormData();
            //
            // form_data.append('event', window.cert.event);
            // form_data.append('text_font_size', data['text_font_size']);
            // form_data.append('text_position_x', data['text_position_x']);
            // form_data.append('text_position_y', data['text_position_y']);
            //
            // $.ajax({
            //     url: window.cert.url,
            //     processData: false,
            //     contentType: false,
            //     data: form_data,
            //     beforeSend: function (xhr) {
            //         xhr.setRequestHeader("X-CSRFToken", csrftoken);
            //     },
            //     method: 'PATCH',
            //     success: function (data) {
            //         title = data;
            //         Messenger().post({
            //             message: 'Texto atualizado com sucesso!',
            //             type: 'success'
            //         });
            //     },
            //     error: function (err) {
            //         if (err.responseText !== "") {
            //             console.error(err.responseText)
            //         } else {
            //             console.error(err)
            //         }
            //         Messenger().post({
            //             message: 'Texto não foi atualizado!',
            //             type: 'danger'
            //         });
            //     }
            // });


        }, 200);
    };

    window.cert.saveTextContent = function (textContent) {
        text['text'] = textContent;
        cert.saveText(text);
    };

//Função que salva a posição de um objeto text
    window.cert.saveTextPosition = function (x, y) {
        text['position_x'] = x;
        text['position_y'] = y;
        cert.saveText(text);
    };

//Função que salva o tamanho de um objeto text
    window.cert.saveTextSize = function (height, width) {
        text['height'] = height;
        text['width'] = width;
        cert.saveText(text);
    };

//Função que salva o tamanho da fonte de um objeto text
    window.cert.saveTextFontSize = function (font_size) {
        text['font_size'] = font_size;
    };

//Função que salva o espaçamento entre linhas de um objeto text
    window.cert.saveTextLineHeight = function (line_height) {
        text['line_height'] = line_height;
    };

// ========================================================
    window.cert.enableDragDrop = function () {

    };

    window.cert.disableDragDrop = function () {

    };


// ====================Title Functions================================
    function showHideTitle(show) {
        show = show === true;
        if (show) {
            $('#titleText').fadeIn();
            $('#navbar-collapse > ul > li.dropdown.open > ul > li:nth-child(3) > a').show();
            $('#navbar-collapse > ul > li.dropdown.open > ul > li.divider').show();
            cert.showTitle();
        } else {
            $('#titleText').fadeOut();
            cert.hideTitle();
            $('#navbar-collapse > ul > li.dropdown.open > ul > li:nth-child(3) > a').hide();
            $('#navbar-collapse > ul > li.dropdown.open > ul > li.divider').hide();
        }
    }

    $('#titleCheckBox').on('change', function () {
        showHideTitle(!this.checked);
    });

    $('#titleFontSize').change(function () {
        $('#titleText').css('font-size', $(this).val() + 'px');
        cert.saveTitleFontSize($(this).val());
        resizeContent('#titleText');
    });

//Funções para redimennsionar o título
    $('#titleText').on('input', function () {
        cert.saveTextContent($(this).val());
        resizeContent((this));
    })
        .on('mouseup', function () {
            resizeContent((this));
        });

//Função para esconder o título
    $('#titleCheckBox').on('change', function () {
        if (this.checked === true) {
            $('#mySidenav > ul > li.dropdown.btn-block.open > ul > li:nth-child(3) > a').hide();
            $('#mySidenav > ul > li.dropdown.btn-block.open > ul > li.divider').hide();
        }
        else {
            $('#mySidenav > ul > li.dropdown.btn-block.open > ul > li:nth-child(3) > a').show();
            $('#mySidenav > ul > li.dropdown.btn-block.open > ul > li.divider').show();

        }
    });

// ====================Date Functions================================
    function showHideDate(show) {
        show = show === true;
        if (show) {
            $('#dateText').fadeIn();
            $('#navbar-collapse > ul > li.dropdown.open > ul > li:nth-child(3) > a').show();
            $('#navbar-collapse > ul > li.dropdown.open > ul > li.divider').show();
            cert.showDate();
        } else {
            $('#dateText').fadeOut();
            $('#navbar-collapse > ul > li.dropdown.open > ul > li:nth-child(3) > a').hide();
            $('#navbar-collapse > ul > li.dropdown.open > ul > li.divider').hide();
            cert.hideDate();
        }
    }

    $('#dateCheckBox').on('change', function () {
        showHideDate(!this.checked);
    });

    $('#dateFontSize').change(function () {
        $('#dateText').css('font-size', $(this).val() + 'px');
        cert.saveDateFontSize($(this).val());
        resizeContent('#dateText');
    });

//Funções alinhamento do texto na data
    $('.glyphicon-align-left').on('click', function () {
        $('#dateText').css('text-align', 'left');
        console.log('left');
    });

    $('.glyphicon-align-center').on('click', function () {
        $('#dateText').css('text-align', 'center');
        console.log('center');
    });

    $('.glyphicon-align-right').on('click', function () {
        $('#dateText').css('text-align', 'right');
        console.log('right');
    });

//Função para esconder a data
    $('#dateCheckBox').on('change', function () {
        if (this.checked === true) {
            $('#mySidenav > ul > li.dropdown.btn-block.open > ul > li:nth-child(3) > a').hide();
            $('#mySidenav > ul > li.dropdown.btn-block.open > ul > li.divider').hide();
            $('#mySidenav > ul > li.dropdown.btn-block.open > ul > li:nth-child(5)').hide();
        }
        else {
            $('#mySidenav > ul > li.dropdown.btn-block.open > ul > li:nth-child(3) > a').show();
            $('#mySidenav > ul > li.dropdown.btn-block.open > ul > li.divider').show();
            $('#mySidenav > ul > li.dropdown.btn-block.open > ul > li:nth-child(5)').show();

        }
    });

// ====================Text Functions================================

    $('#textFontSize').change(function () {
        $('#text').css('font-size', $(this).val() + 'px');
        cert.saveTextFontSize($(this).val());
        resizeContent('#text');
    });

    $('#textLineHeight').change(function () {
        $('#text').css('line-height', $(this).val());
        cert.saveTextLineHeight($(this).val());
        resizeContent('#text');
    });

//Funções de redimensionar altomaticamente a caixa de texto
    $('#text').on('input', function () {
        cert.saveTextContent($(this).val());
        resizeContent((this));
    })
        .on('mouseup', function () {
            resizeContent((this));
        });


//Função que faz o redimensionamento
    function resizeContent(element) {
        element = $(element);
        var offset = element.innerHeight() - element.height();

        if (element.innerHeight < element[0].scrollHeight) {
            //Grow the field if scroll height is smaller
            element.height(element[0].scrollHeight - offset);
        } else {
            //Shrink the field and then re-set it to the scroll height in case it needs to shrink
            element.height(1);
            element.height(element[0].scrollHeight - offset);
        }
    }

//Funções para ativar e desativar o modo de drag and drop e resize
    $('#modoEditar').on('change', function () {
        if (this.checked === true) {
            addDragResize();
        }
        else {
            removeDragResize();
        }
    });

    function removeDragResize() {
        $('#text').removeClass('resize-drag');
        $('#text').css('background-color', 'transparent');
        $('#dateText').removeClass('drag');
        $('#dateText').css('background-color', 'transparent');
        $('#titleText').removeClass('drag');
        $('#titleText').css('background-color', 'transparent');
    }

    function addDragResize() {
        $('#text').addClass('resize-drag');
        $('#text').css('background-color', 'white');
        resizeContent($('#text'));
        $('#dateText').addClass('drag');
        $('#dateText').css('background-color', 'white');
        $('#titleText').addClass('drag');
        $('#titleText').css('background-color', 'white');
    }


// Funções que auxiliam a biblioteca de drag and drop e resize
    window.cert.moveElement = function (element, x, y) {
        element = $(element);

        // translate the element
        var translate = 'translate(' + x + 'px, ' + y + 'px)';
        element.css('webkitTransform', translate);
        element.css('transform', translate);

        // update the posiion attributes
        element.attr('data-x', x);
        element.attr('data-y', y);
    };


})(window, jQuery);