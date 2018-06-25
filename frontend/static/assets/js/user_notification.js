 $(":input").change(function () { //trigers change in all input fields including text type
        $(window).on("beforeunload", function () {
            return "Você tem certeza? Você não terminou de preencher o formulário!";
        });
    });




$(document).ready(function () {
    $("form").on("submit", function (e) {
        $(window).off("beforeunload");
    });
});