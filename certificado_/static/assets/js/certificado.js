window.cert = window.cert || {};

(function (window, $) {

const HOST='';

// Título do certificado
var title = {
    "position_x": 0.00,
    "position_y": 0.00,
    "font_size": "12px",
    "hide": false
};

var date= {
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
    "line_height":"20px",
    "text": "teste"
};

// ====================================
// Save data
// ====================================
// Funcão que analisa os dados recebidos com os dados esperados
function check_data(keys, data) {
    $.each(keys, function(i, key) {
        if (!key in data) {
            return false;
        }
    });
    return true;
}

// =============TITLE==================
// Função que solicita um objeto title
window.cert.getTitle = function() {
    var resource_name = 'mock/title.json';
    $.ajax({
        url: HOST+resource_name,
        method: 'GET',
        crossDomain: true,
        success: function(data) {
            console.log(data);
        }
    });
};

// Função que salva um objeto title
window.cert.saveTitle = function(data) {
    var expected_keys = [
        'font_size',
        'position_x',
        'position_y',
        'hide'
    ];
    var resource_name = 'mock/title.json';
    if (!check_data(expected_keys, data)) {
        console.error('Dados errados em "'+resource_name+'"');
        console.log(data);
        return;
    }

    $.ajax({
        url: HOST+resource_name,
        data: data,
        method: 'PUT',
        success: function(data) {
            title = data;
        }
    });
};

//Função que salva a posição de um objeto title
window.cert.saveTitlePosition = function (x, y) {
    title['position_x'] = x;
    title['position_y'] = y;
    cert.saveTitle(title);
};

//Função que salva o tamanha da fonte de um objeto title
window.cert.saveTitleFontSize = function (font_size){
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
window.cert.getDate = function() {
    var resource_name = 'mock/date.json';
    $.ajax({
        url: HOST+resource_name,
        method: 'GET',
        crossDomain: true,
        success: function(data) {
            console.log(data);
        }
    });
};

// Função que salva um objeto do tipo date
window.cert.saveDate = function(data) {
    var expected_keys = [
        'font_size',
        'position_x',
        'position_y',
        'hide'
    ];
    var resource_name = 'mock/date.json';
    if (!check_data(expected_keys, data)) {
        console.error('Dados errados em "'+resource_name+'"');
        console.log(data);
        return;
    }

    $.ajax({
        url: HOST+resource_name,
        data: data,
        method: 'PUT',
        success: function(data) {
            console.log(data);
        }
    });
};

// Função que salva a posição de um objeto date
window.cert.saveDatePosition = function(x, y){
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
    var resource_name = 'mock/text.json';
    $.ajax({
        url: HOST+resource_name,
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
    if(!check_data(expect_keys, data)){
        console.error('Dados errados em "'+resource_name+'"');
        console.log(data);
        return;
    }
    $.ajax({
        url: HOST+resource_name,
        method: 'PUT',
        crossDomain: true,
        success: function (data) {
            console.log(data);
        }
    });
};

window.cert.saveTextContent = function (textContent){
    text['text'] = textContent;
    cert.saveText(text);
};

//Função que salva a posição de um objeto text
window.cert.saveTextPosition =  function (x, y) {
    text['position_x'] = x;
    text['position_y'] = y;
    cert.saveText(text);
};

//Função que salva o tamanho de um objeto text
window.cert.saveTextSize =  function (height, width) {
    text['height'] = height;
    text['width'] = width;
    cert.saveText(text);
};

//Função que salva o tamanho da fonte de um objeto text
window.cert.saveTextFontSize =  function (font_size) {
    text['font_size'] = font_size;
};

//Função que salva o espaçamento entre linhas de um objeto text
window.cert.saveTextLineHeight =  function (line_height) {
    text['line_height'] = line_height;
};

// ========================================================
window.cert.enableDragDrop = function (){

};

window.cert.disableDragDrop = function (){

};


// ====================Title Functions================================
function showHideTitle(show) {
    show = show === true;
    if (show) {
        $('#titleText').show();
        cert.showTitle();
    } else {
        $('#titleText').hide();
        cert.hideTitle();
    }
}

$('#titleCheckBox').on('change',function () {
    showHideTitle(!this.checked);
});

$('#titleFontSize').change(function () {
    $('#titleText').css('font-size',$(this).val()+'px');
    cert.saveTitleFontSize($(this).val());
});
// ====================Date Functions================================
function showHideDate(show) {
    show = show === true;
    if (show) {
        $('#dateText').show();
        cert.showDate();
    } else {
        $('#dateText').hide();
        cert.hideDate();
    }
}

$('#dateCheckBox').on('change',function () {
    showHideDate(!this.checked);
});

$('#dateFontSize').change(function () {
    $('#dateText').css('font-size',$(this).val()+'px');
    cert.saveDateFontSize($(this).val());
});

// ====================Text Functions================================

$('#textFontSize').change(function () {
    $('#text').css('font-size',$(this).val()+'px');
    cert.saveTextFontSize($(this).val());
});

$('#textLineHeight').change(function () {
    $('#text').css('line-height',$(this).val());
    cert.saveTextLineHeight($(this).val());
});

function autoresize(element){
    var $el = element,
        offset = $el.innerHeight() - $el.height();

    if ($el.innerHeight < element.scrollHeight) {
        //Grow the field if scroll height is smaller
        $el.height(this.scrollHeight - offset);
    } else {
        //Shrink the field and then re-set it to the scroll height in case it needs to shrink
        $el.height(1);
        $el.height(element.scrollHeight - offset);
    }
}

function resizeContent() {
    var text = $('#text');
    var offset = text.innerHeight() - text.height();

    if (text.innerHeight < text[0].scrollHeight) {
        //Grow the field if scroll height is smaller
        text.height(text[0].scrollHeight - offset);
    } else {
        //Shrink the field and then re-set it to the scroll height in case it needs to shrink
        text.height(1);
        text.height(text[0].scrollHeight - offset);
    }
}

$('#text').on('input',function () {
    cert.saveTextContent($(this).val());
    resizeContent();
})
.on('mouseup',function () {
    resizeContent();
});

})(window, jQuery);