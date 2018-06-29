$(document).ready(function () {
    $(window).off("beforeunload");
    var submitButton = $('form').find(':submit');
    submitButton.prop('disabled', true);

    $("form").on("submit", function (e) {
        $(window).off("beforeunload");
        var submitButton = $('form').find(':submit');
        submitButton.prop('disabled', true);
    });
    $("button").on("click", function (e) {
        $(window).off("beforeunload");
        var submitButton = $('form').find(':submit');
        setTimeout(function (submitButton) {
            disableButton(submitButton);
        }, 0);
    });

    function disableButton(el) {
        el.prop('disabled', true);
    }

    $("input").change(function (event) {
        event.preventDefault();

        verificarEdicaoForm()
    });

    $(".radio").click(function (event) {

        event.preventDefault();
        verificarEdicaoForm()
    });
    $(".iCheck-helper").click(function (event) {

        event.preventDefault();
        verificarEdicaoForm()
    });

    function verificarEdicaoForm() {
        var submitButton = $('form').find(':submit');
        submitButton.prop('disabled', false);
        $(window).on("beforeunload", function () {
            return "Você tem certeza? Você não terminou de preencher o formulário!";
        });

    }
});