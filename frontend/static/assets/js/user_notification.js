$(document).ready(function () {
    $(window).off("beforeunload");
    verificarEdicaoForm();

    $("form").on("submit", function (e) {
        $(window).off("beforeunload");
        var submitButton = $('form').find(':submit');
        submitButton.prop('disabled', true);
    });

    $("button").on("click", function (e) {
        $(window).off("beforeunload");
        setTimeout(function () {
            disableButton($('form').find(':submit'));
        }, 0);
    });

    function disableButton(el) {
        el.prop('disabled', true);
    }

    $("input").change(function (event) {
        event.preventDefault();
        verificarEdicaoForm(true)
    });

    $(".radio").click(function (event) {
        event.preventDefault();
        verificarEdicaoForm(true)
    });

    $(".iCheck-helper").click(function (event) {
        event.preventDefault();
        verificarEdicaoForm(true)
    });

    $("select").change(function (event) {
        event.preventDefault();
        verificarEdicaoForm(true)
    });

    $("textarea").change(function (event) {
        event.preventDefault();
        verificarEdicaoForm(true)
    });

    function verificarEdicaoForm(checking_edit) {
        var beforeunload_time = null;
        checking_edit = checking_edit === true;

        $.each($('form'), function(i, form) {
            form = $(form);

            if (checking_edit && !form.hasClass('skip-edition-check')) {
                window.clearTimeout(beforeunload_time);
                beforeunload_time = window.setTimeout(function() {
                    $(window).on("beforeunload", function () {
                        return "Você tem certeza? Você não terminou de preencher o formulário!";
                    });
                }, 300);
            }

            if (!form.hasClass('skip-submition-check')) {
                var submitButton = form.find(':submit');
                if (submitButton.length) {
                    submitButton.prop('disabled', false);
                }
            }
        });
    }
});