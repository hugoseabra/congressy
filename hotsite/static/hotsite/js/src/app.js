(function(window, $) {

window.app = function () {

    $(function () {
        switcheryToggle();
        icheckStart();
    });

    var switcheryElements = {};

    var switcheryToggle = function () {
        var elems = Array.prototype.slice.call(
            document.querySelectorAll('.js-switch')
        );

        elems.forEach(function (html) {
            var switchery = new Switchery(html, {
                size: 'small',
                color: '#5B8790',
                secondaryColor: '#B3B8C3'
            });
            var id = $(html).prop('id');
            if (id) {
                switcheryElements[id] = switchery;
            }
        });
    };

    var icheckStart = function() {
        $('input[type=radio]').iCheck({
            checkboxClass: 'icheckbox_flat-grey',
            radioClass: 'iradio_flat-blue'
        });
    };

    var setSwitchery = function(elem, isChecked) {
        var checkbox = $(elem);
        if (isChecked === true && checkbox.prop('checked') === false) {
            checkbox.trigger('click').attr("checked", "checked");
        }

        if (isChecked === false && checkbox.prop('checked') === true) {
            checkbox.trigger('click').removeAttr("checked");
        }
    };

    var enableDisableSwitchery = function(elem, disable) {
        var checkbox = $(elem);
        if (disable === true && checkbox.prop('disabled') === false) {
            checkbox.disable();
        }

        if (disable === false && checkbox.prop('disabled') === true) {
            checkbox.enable();
        }
    };

    //return functions
    return {
        'setSwitchery': setSwitchery,
        'disableSwitchery': enableDisableSwitchery,
        'switcheryToggle': switcheryToggle,
        'switcheryElements': switcheryElements
    };
}();


})(window, jQuery);
