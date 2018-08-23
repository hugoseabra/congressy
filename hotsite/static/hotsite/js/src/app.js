(function(window, $) {

window.app = function () {

    $(function () {
        switcheryToggle();
        icheckStart();
        tooltips();
        createFileUploadEvents();
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
        var radios = $('input[type=radio]');
        var checkboxes = $('input[type=checkbox]');

        radios.iCheck({
            checkboxClass: 'icheckbox_flat-grey',
            radioClass: 'iradio_flat-grey'
        });

        checkboxes.iCheck({
            checkboxClass: 'icheckbox_flat-grey',
            radioClass: 'iradio_flat-grey'
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

    //tooltips
    var tooltips = function() {
        $('.tooltip-wrapper').tooltip({
            selector: "[data-toggle=tooltip]",
            container: "body",
            html:true
        })
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

    var createFileUploadEvents = function() {
            var btn_file_group = $('.btn-file-group');

            var read_only_input = btn_file_group.find('input[readonly]');
                read_only_input.unbind('click');

                read_only_input.on('click', function(e) {
                    e.preventDefault();
                    $(this).parent().parent().find(':file').trigger('click');
                });

            $(document).unbind('change', ':file');
            $(document).on('change', ':file', function () {
                var input = $(this),
                    numFiles = input.get(0).files ? input.get(0).files.length : 1,
                    label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
                input.trigger('fileselect', [numFiles, label]);
            });

            // We can watch for our custom `fileselect` event like this
            var all_files_els = $(':file');
            all_files_els.unbind('fileselect');

            all_files_els.on('fileselect', function(event, numFiles, label) {
                var input = $(this).parents('.input-group').find(':text'),
                    log = numFiles > 1 ? numFiles + ' files selected' : label;

                if( input.length ) {
                    input.val(log);
                } else {
                    if( log ) alert(log);
                }
            });
        };

    //return functions
    return {
        'setSwitchery': setSwitchery,
        'disableSwitchery': enableDisableSwitchery,
        'switcheryToggle': switcheryToggle,
        'switcheryElements': switcheryElements,
        'iCheckStart': icheckStart,
        'tooltips': tooltips,
        'createFileUploadEvents': createFileUploadEvents
    };
}();


})(window, jQuery);
