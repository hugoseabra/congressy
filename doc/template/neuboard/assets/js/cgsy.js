// Mobile top Menu
$(document).ready(function() {
    $('#mobile-top-menu-button').click(function() {
        var block = $("#mobile-top-menu");
        console.log(block);
        var right = 0;

        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
            right = -285;
        } else {
            $(this).addClass('active');
        }

        block.animate({"right": right}, 300);
    });
});