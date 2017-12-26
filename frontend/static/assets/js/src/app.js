var app = function () {

    $(function () {
        navToggleRight();
        navToggleLeft();
        navToggleSub();
        profileToggle();
        switcheryToggle();


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


    var switcheryToggle = function () {
        var elems = Array.prototype.slice.call(document.querySelectorAll('.js-switch'));
        elems.forEach(function (html) {
            var switchery = new Switchery(html, {
                size: 'small',
                color: '#5B8790',
                secondaryColor: '#B3B8C3'
            });
        });
    };


    //return functions
    return {};
}();


