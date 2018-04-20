(function (window, $) {

    window.app = function () {

        $(function () {
            navToggleRight();
            navToggleLeft();
            navToggleSub();
            profileToggle();
            switcheryToggle();
            tooltips();
            icheckStart();
        });


        var navToggleRight = function () {
            $('#toggle-right').on('click', function () {
                $('#sidebar-right').toggleClass('sidebar-right-open');
                $("#toggle-right .fa").toggleClass("fa-indent fa-dedent");

            });
        };


        var navToggleLeft = function () {
            $('#toggle-left').on('click', function () {
                var bodyEl = $('#main-wrapper');
                ($(window).width() > 767) ? $(bodyEl).toggleClass('sidebar-mini') : $(bodyEl).toggleClass('sidebar-opened');
            });
        };

        var navToggleSub = function () {
            var subMenu = $('.sidebar .nav');
            $(subMenu).navgoco({
                caretHtml: false,
                accordion: true
            });

        };

        var profileToggle = function () {
            $('#toggle-profile').click(function () {
                $('.sidebar-profile').slideToggle();
            });
        };

        var switcheryElements = {};

        var switcheryToggle = function () {
            
            var elems = Array.prototype.slice.call(
                document.querySelectorAll('.js-switch')
            );

            elems.forEach(function (html) {

                if (!html.getAttribute('data-switchery')) {
                    var switchery = new Switchery(html, {
                        size: 'small',
                        color: '#5B8790',
                        secondaryColor: '#B3B8C3'
                    });
                }


                var id = $(html).prop('id');
                if (id) {
                    switcheryElements[id] = switchery;
                }
            });
        };

        var icheckStart = function () {
            $('input[type=radio]').iCheck({
                checkboxClass: 'icheckbox_flat-grey',
                radioClass: 'iradio_flat-blue'
            });
        };

        var setSwitchery = function (elem, isChecked) {
            var checkbox = $(elem);
            if (isChecked === true && checkbox.prop('checked') === false) {
                checkbox.trigger('click').attr("checked", "checked");
            }

            if (isChecked === false && checkbox.prop('checked') === true) {
                checkbox.trigger('click').removeAttr("checked");
            }
        };

        var enableDisableSwitchery = function (elem, disable) {
            var checkbox = $(elem);
            if (disable === true && checkbox.prop('disabled') === false) {
                checkbox.disable();
            }

            if (disable === false && checkbox.prop('disabled') === true) {
                checkbox.enable();
            }
        };

        //tooltips
        var tooltips = function() {
            $('.tooltip-wrapper').tooltip({
                selector: "[data-toggle=tooltip]",
                container: "body"
            })
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
