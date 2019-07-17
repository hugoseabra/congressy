function removeRadioGroupRequirements() {
    "use strict";
    $('input[type=radio]', 'form').each(function(i, el){
        el = $(el);
        var parent = el.closest('.radio').parent();
        var child_radios = parent.find('input[type=radio]');

        child_radios.each(function(ii, radio) {
            radio = $(radio);
            if (radio.attr('required')) {
                radio.removeAttr('required');
            }
        });
    });
}

function removeCheckboxGroupRequirements() {
    "use strict";
    $('input[type=checkbox]', 'form').each(function(i, el){
        el = $(el);
        var parent = el.closest('.radio').parent();
        var child_radios = parent.find('input[type=checkbox]');

        child_radios.each(function(ii, radio) {
            radio = $(radio);
            if (radio.attr('required')) {
                radio.removeAttr('required');
            }
        });
    });
}

function loadPredefinedEvents() {
    window.setTimeout(function () {
        $('[data-field-name=input-number]').addClass('numbers-only');

        $('.numbers-only').on('input', function () {
            this.value = this.value.replace(/[^0-9+-\/.]/g, '').replace(/(\..*)\./g, '$1');
        });

        removeRadioGroupRequirements();
        removeCheckboxGroupRequirements();
    }, 300);
    app.createFileUploadEvents();
}

$(document).ready(function () {
    loadPredefinedEvents();
});
