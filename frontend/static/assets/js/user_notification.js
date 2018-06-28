$(document).ready(function () {
    var submitButton = $('form').find(':submit');
    submitButton.prop('disabled', true);

    $("form").on("submit", function (e) {
        $(window).off("beforeunload");
        var submitButton = $('form').find(':submit');
        submitButton.prop('disabled', true);
    });

    $(":input").change(verificarEdicaoForm());
    $(".iCheck-helper").change(verificarEdicaoForm());

    function verificarEdicaoForm() {
        var submitButton = $('form').find(':submit');
        submitButton.prop('disabled', false);
        $(window).on("beforeunload", function () {
            return "Você tem certeza? Você não terminou de preencher o formulário!";
        });

    }
});